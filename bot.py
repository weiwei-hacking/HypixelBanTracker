import discord
from discord.ext import commands
import json
import os

# Load configs.json
with open('configs.json', 'r') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Load cogs
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="Hypixel Punishment"))
    print(f'{bot.user} is online!')
    await load_cogs()
    await bot.tree.sync()


bot.run(config['bot_token'])

