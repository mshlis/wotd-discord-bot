import discord
from client import AidanClient
from dotenv import dotenv_values

config = dotenv_values(".env")
intents = discord.Intents.default()
intents.message_content = True
client = AidanClient(intents=intents)
client.run(config.get("TOKEN"))
client.save_state()
