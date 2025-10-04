import os
import sys
import asyncio
from dotenv import load_dotenv

from bot import AIKunBot
from learning import AILearner

import discord

async def do_research(token, intents):
    """
    データ収集のためにボットを起動し、完了後に終了する
    """
    bot = AIKunBot(intents=intents)

    @bot.event
    async def on_ready():
        await bot.research_and_collect()
        await bot.close()

    await bot.start(token)

def main():
    """
    メイン関数
    """
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")

    if len(sys.argv) < 2:
        print("Usage: python main.py [run|research|learning]")
        return

    command = sys.argv[1]

    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True # メッセージ内容へのアクセスを有効にする

    if command == "run":
        if not token:
            print("Error: DISCORD_BOT_TOKEN not found in .env file.")
            return
        bot = AIKunBot(intents=intents)
        bot.run(token)
    elif command == "research":
        if not token:
            print("Error: DISCORD_BOT_TOKEN not found in .env file.")
            return
        asyncio.run(do_research(token, intents))
    elif command == "learning":
        print("Starting learning...")
        learner = AILearner()
        learner.fine_tune(data_path="data")
        print("Learning finished. You can now run the bot using the 'run' command.")
    else:
        print(f"Unknown command: {command}")
        print("Usage: python main.py [run|research|learning]")


if __name__ == "__main__":
    main()