import os
from dotenv import load_dotenv
from bot.bot import Bot

def main():
    load_dotenv()
    client = Bot()
    client.run(os.getenv('BOT_TOKEN'))

if __name__ == "__main__":
    main()

