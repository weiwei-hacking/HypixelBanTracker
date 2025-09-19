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

DISCORD_TOKEN = os.getenv("BOT_TOKEN")
HYPIXEL_API_KEY = os.getenv("HYPIXEL_API")

if not DISCORD_TOKEN or not HYPIXEL_API_KEY:
    with open("configs.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        DISCORD_TOKEN = DISCORD_TOKEN or config.get("bot_token")
        HYPIXEL_API_KEY = HYPIXEL_API_KEY or config.get("hypixel_api")

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="Hypixel Punishment"))
    print(f'{bot.user} is online!')
    await load_cogs()
    await bot.tree.sync()


bot.run(config['bot_token'])
