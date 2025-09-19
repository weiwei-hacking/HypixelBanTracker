import os
import json
import time
import discord
from discord.ext import commands, tasks
import aiohttp
from datetime import datetime

class BanTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 從 configs.json 讀取 Hypixel API 金鑰
        with open('configs.json', 'r') as f:
            self.config = json.load(f)
        self.api_key = self.config['hypixel_api']
        # 從 channel.txt 讀取多個頻道 ID
        with open('channel.txt', 'r') as f:
            self.channel_ids = [int(line.strip()) for line in f if line.strip()]
        self.channels = []

    async def cog_load(self):
        self.track_bans.start()

    @tasks.loop(seconds=5)
    async def track_bans(self):
        async with aiohttp.ClientSession() as session:
            headers = {'API-Key': self.api_key}
            async with session.get('https://api.hypixel.net/v2/punishmentstats', headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        stats = {
                            'watchdog_total': data.get('watchdog_total', 0),
                            'staff_total': data.get('staff_total', 0),
                            'watchdog_rollingDaily': data.get('watchdog_rollingDaily', 0),
                            'staff_rollingDaily': data.get('staff_rollingDaily', 0)
                        }
                        # 顯示指定格式的日誌
                        current_time = datetime.now().strftime("%D %H:%M:%S")
                        print(f"[{current_time}] Watchdog {stats['watchdog_total']}, Staff {stats['staff_total']}")

                        old_data = None
                        if os.path.exists('punishment_new.json'):
                            with open('punishment_new.json', 'r') as f:
                                old_data = json.load(f)
                            with open('punishment_old.json', 'w') as f:
                                json.dump(old_data, f)

                        with open('punishment_new.json', 'w') as f:
                            json.dump(stats, f)

                        if old_data:
                            # 檢查 watchdog_total 變化
                            new_wd_total = stats['watchdog_total']
                            old_wd_total = old_data['watchdog_total']
                            if new_wd_total != old_wd_total:
                                diff = new_wd_total - old_wd_total
                                if diff > 0:
                                    unix = int(time.time())
                                    msg = f"🐕 `Watchdog` is on <t:{unix}:R> banned {diff} players!"
                                    for channel in self.channels:
                                        await channel.send(msg)
                                        if diff >= 10:
                                            embed = discord.Embed(
                                                title="⚠️ WATCHDOG BAN WAVE WARNING ⚠️",
                                                description=f"🐕 `Watchdog` is on <t:{unix}:R> banned {diff} players!",
                                                color=discord.Color.red()
                                            )
                                            await channel.send(embed=embed)

                            # 檢查 staff_total 變化
                            new_st_total = stats['staff_total']
                            old_st_total = old_data['staff_total']
                            if new_st_total != old_st_total:
                                diff = new_st_total - old_st_total
                                if diff > 0:
                                    unix = int(time.time())
                                    msg = f"🐷 `Staff` is on <t:{unix}:R> banned {diff} players!"
                                    for channel in self.channels:
                                        await channel.send(msg)
                                        if diff >= 10:
                                            embed = discord.Embed(
                                                title="⚠️ STAFF BAN WAVE WARNING ⚠️",
                                                description=f"🐷 `Staff` is on <t:{unix}:R> banned {diff} players!",
                                                color=discord.Color.red()
                                            )
                                            await channel.send(embed=embed)

                            # 檢查每日重置
                            new_wd_daily = stats['watchdog_rollingDaily']
                            new_st_daily = stats['staff_rollingDaily']
                            if new_wd_daily <= 0 and new_st_daily <= 0:
                                old_wd_daily = old_data['watchdog_rollingDaily']
                                old_st_daily = old_data['staff_rollingDaily']
                                unix = int(time.time())
                                embed = discord.Embed(title="Hypixel Ban Daily")
                                desc = f"Watchdog is banned {old_wd_daily} player\nStaff is banned {old_st_daily} player\n\nUpdate on <t:{unix}:R>"
                                embed.description = desc
                                for channel in self.channels:
                                    await channel.send(embed=embed)

    @track_bans.before_loop
    async def before_track_bans(self):
        await self.bot.wait_until_ready()
        # 將頻道 ID 轉換為 Discord 頻道物件
        for channel_id in self.channel_ids:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            if channel:
                self.channels.append(channel)
            else:
                print(f"Error: Channel with ID {channel_id} not found.")
        if not self.channels:
            print("Error: No valid channels found. Please check channel.txt.")

async def setup(bot):
    await bot.add_cog(BanTracker(bot))