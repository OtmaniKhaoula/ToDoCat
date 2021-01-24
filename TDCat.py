import os
import os.path
import discord
from discord.ext import commands

import asyncpg 
import asyncio
import random
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='!')

mdp = os.getenv("MDP")
async def create_db_pool():
    bot.con = await asyncpg.create_pool(database="TDLCat", user="postgres", password=mdp)

@bot.event
async def on_ready():
    print('We have logged in as {} {}'.format(bot.user.name, bot.user.id))


bot.remove_command("help")


bot.loop.run_until_complete(create_db_pool())

extensions = ['Cogs.ShowCommands', 'Cogs.ModificationCommands', 'Cogs.HelpCommands', 'Cogs.TimeCommands']

if __name__ == '__main__':
    for ext in extensions:
        bot.load_extension(ext)

token = os.getenv("BOT_TOKEN")
bot.run(token)