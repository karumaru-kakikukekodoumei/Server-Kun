import os
import sys
import asyncio
from dotenv import load_dotenv

# --- Dependency Checker ---
import subprocess
try:
    import pkg_resources
except ImportError:
    print("[ERROR] Package 'setuptools' is not installed. Please install it using: pip install setuptools")
    sys.exit(1)

def check_and_install_dependencies():
    """
    Checks if required packages from requirements.txt are installed.
    If not, it attempts to install them.
    """
    # Correctly locate requirements.txt in the project root, relative to this script's location.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    requirements_path = os.path.join(project_root, 'requirements.txt')

    try:
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"[ERROR] requirements.txt not found. Looked for it at: {requirements_path}")
        sys.exit(1)

    print("Checking for required packages...")
    try:
        pkg_resources.require(requirements)
        print("All required packages are already installed.")
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
        print(f"[WARNING] A package is missing or has a version conflict: {e}")
        print(f"Attempting to install/update packages from {requirements_path}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
            print("\nPackages installed successfully.")
            print("Please restart the application for the changes to take effect.")
            sys.exit(0)
        except subprocess.CalledProcessError as install_error:
            print(f"\n[ERROR] Failed to install packages: {install_error}")
            print("Please try running the following command manually in your terminal:")
            print(f"    pip install -r {requirements_path}")
            sys.exit(1)

# --- End of Dependency Checker ---


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
    # 引数がない場合は、依存関係のチェックだけ実行して終了する
    if len(sys.argv) < 2:
        check_and_install_dependencies()
        print("\nDependency check complete. Please provide a command to continue.")
        print("Usage: python src/main.py [run|research|learning]")
        return

    check_and_install_dependencies()
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")

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
        print("Usage: python src/main.py [run|research|learning]")


if __name__ == "__main__":
    main()