import discord

class Bot(discord.Client):
    
    def __init__(self):
        super().__init__(intents=discord.Intents.all()) # works for now, but we don't need that much power.
        
    async def on_ready(self):
        print("[ONURABOT] Bot started.")

    async def on_message(self, message):
        pass