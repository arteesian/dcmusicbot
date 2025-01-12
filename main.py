import discord
from discord.ext import commands
#import logging
import asyncio

#import all of the cogs
from help_cog import help_cog
from music_cog import music_cog

#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

bot.remove_command('help')

async def setup(bot):
  await bot.add_cog(help_cog(bot))
  await bot.add_cog(music_cog(bot))

@bot.event
async def on_ready():
  print('Вы вошли как {0.user}'.format(bot))
  await setup(bot)

async def main():
  async with bot:
    await setup(bot)
    await bot.start("token_name")

asyncio.run(main())

# отлавливать ошибки воспроизведения, пропускать
#
#
#
