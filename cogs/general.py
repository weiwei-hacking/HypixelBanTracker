import discord
from discord import app_commands
from discord.ext import commands
import time

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show bot command list")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="General", color=0x242429)
        embed.add_field(name="`/help`", value="Show this message", inline=False)
        embed.add_field(name="`/ping`", value="Show this bot latency", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="Show bot latency")
    async def ping(self, interaction: discord.Interaction):
        start_time = time.time()
        embed = discord.Embed(title="Latency testing...", color=0x242429)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        end_time = time.time()
        
        bot_latency = round(self.bot.latency * 1000)
        api_latency = round((end_time - start_time) * 1000)
        
        embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
        embed.add_field(name="BOT latency", value=f"{bot_latency}ms", inline=True)
        embed.add_field(name="API latency", value=f"{api_latency}ms", inline=True)
        await interaction.edit_original_response(content=None, embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))