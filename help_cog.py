import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.help_message = """
```
.help - показать все команды бота
.play (.p) <запрос> - включить песню, возобновляет проигрывание, если стоит пауза
.queue (.q) - показать список ближайших треков в очереди
.skip - пропустить текущий трек
.stop (.s) - выключить плеер и убрать всю музыку из очереди
.pause - поставить паузу, если уже стоит - возобновляет проигрывание
.resume (.r) - возобновить проигрывание
```
"""
        self.text_channel_text = []

    @commands.Cog.listener()
    async def on_read(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)

        await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)

    @commands.command(name="help", help="Показать все команды бота")
    async def help(self, ctx):
        await ctx.send(self.help_message)