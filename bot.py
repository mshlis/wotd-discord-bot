import discord
from client import AidanClient
from dotenv import dotenv_values
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args = parser.parse_args()
prefix = "TEST_" if args.test else ""

config = dotenv_values(".env")
intents = discord.Intents.default()
intents.message_content = True
client = AidanClient(
    channel_id=int(config.get(prefix+"CHANNEL_ID")), 
    author_id=int(config.get(prefix+"AUTHOR_ID")),
    intents=intents)
client.run(config.get("TOKEN"))
client.save_state()
