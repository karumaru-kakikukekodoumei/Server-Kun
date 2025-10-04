import discord
import os
from learning import AILearner
from discord.ext import tasks
import datetime

class AIKunBot(discord.Client):
    """
    Discordボットのメインクラス
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.ai_enabled_channels = set()
        self.is_ai_running = False
        self.learner = AILearner()
        self.weekly_learning_task.start()

    @tasks.loop(hours=24 * 7)  # 7日に1回実行
    async def weekly_learning_task(self):
        if not self.is_ai_running:
            print("Weekly learning task skipped: AI is not running.")
            return

        print("Starting weekly learning task...")
        try:
            # 1週間前の日時を取得
            one_week_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(weeks=1)

            # 直近1週間のデータを収集
            weekly_data_dir = "data/weekly"
            await self.research_and_collect(output_dir=weekly_data_dir, after=one_week_ago)

            # 新しいデータでモデルを再学習
            print("Re-training model with new weekly data...")
            self.learner.fine_tune(data_path=weekly_data_dir, epochs=1)  # 追加学習は1エポックで十分な場合が多い

            # 新しいモデルを即座に反映させるために再読み込み
            print("Reloading the updated model...")
            self.learner.load_model()

            print("Weekly learning task finished successfully.")
        except Exception as e:
            print(f"An error occurred during weekly learning task: {e}")

    @weekly_learning_task.before_loop
    async def before_weekly_learning_task(self):
        print('Waiting for bot to be ready before starting weekly learning task...')
        await self.wait_until_ready()

    async def on_ready(self):
        """
        ボットが起動したときに呼び出される
        """
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        """
        メッセージを受信したときに呼び出される
        """
        # 自分自身のメッセージは無視する
        if message.author == self.user:
            return

        # コマンド処理
        if message.content.startswith('!AI-KUN'):
            await self.handle_command(message)
            return

        # AIが稼働中で、対象チャンネルであれば応答する
        if self.is_ai_running and message.channel.id in self.ai_enabled_channels:
            async with message.channel.typing():
                response = self.learner.predict(message.content)
                await message.channel.send(response)

    async def handle_command(self, message):
        """
        !AI-KUN コマンドを処理する
        """
        parts = message.content.split()
        command = parts[1] if len(parts) > 1 else None

        if command == 'Run':
            await message.channel.send('Loading AI model...')
            self.learner.load_model()
            if self.learner.model is not None:
                self.is_ai_running = True
                self.ai_enabled_channels.add(message.channel.id)
                await message.channel.send('AI-KUN is now running in this channel.')
            else:
                await message.channel.send('Failed to load AI model. Please run `learning` first.')

        elif command == 'Stop':
            self.is_ai_running = False
            await message.channel.send('AI-KUN has been stopped.')

        elif command == 'NO':
            if message.channel.id in self.ai_enabled_channels:
                self.ai_enabled_channels.remove(message.channel.id)
            await message.channel.send('AI-KUN will no longer be active in this channel.')

        else:
            await message.channel.send('Unknown command. Available commands: Run, Stop, NO')

    async def research_and_collect(self, output_dir="data", after=None):
        """
        ボットが参加しているサーバーの会話履歴を収集して保存する
        `after`が指定された場合、その日時以降のメッセージのみを収集する
        """
        print("Starting data collection...")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for guild in self.guilds:
            print(f"Collecting data from guild: {guild.name} (ID: {guild.id})")
            for channel in guild.text_channels:
                # チャンネルにアクセス権があるか確認
                if channel.permissions_for(guild.me).read_messages:
                    print(f"  - Channel: {channel.name}")
                    try:
                        history_messages = [message.content async for message in channel.history(limit=None, after=after)]
                        if not history_messages:
                            continue

                        # `after`が指定されていない場合、履歴は新しい順なので時系列にするために逆順にする
                        if after is None:
                            history_messages.reverse()

                        # ファイルに書き込み
                        file_path = os.path.join(output_dir, f"{guild.id}_{channel.id}.txt")
                        with open(file_path, "w", encoding="utf-8") as f:
                            for line in history_messages:
                                f.write(line + "\n")
                    except discord.Forbidden:
                        print(f"    - Could not access channel: {channel.name} (Forbidden)")
                    except Exception as e:
                        print(f"    - An error occurred in {channel.name}: {e}")

        print("Data collection finished.")