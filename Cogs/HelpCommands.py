import discord
from discord.ext import commands
import asyncio
import random 

class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        em = discord.Embed(title= "Help", description="Use !help <command> for extended infos", color=random.randint(0, 0xffffff))
        em.add_field(name = "Show", value="profil, show, green", inline=False)
        em.add_field(name = "Create", value="create, add")
        em.add_field(name = "Modify", value="delete, done, join")
        await ctx.send(embed = em)

    @help.command()
    async def profil(self, ctx):
        em = discord.Embed(title="profil", description="shows the number of tasks, lists, achieved task that you have", color=random.randint(0, 0xffffff))
        em.add_field(name="**syntax**", value="!profil")
        await ctx.send(embed = em)

    @help.command()
    async def show(self, ctx):
        em = discord.Embed(title="show", description="shows your lists and tasks", color=random.randint(0, 0xffffff))
        em.add_field(name="**syntax**", value="!show : to see all your lists\n !show [list_name] : to see all the tasks in a specific list")
        await ctx.send(embed = em)

    @help.command()
    async def green(self, ctx):
        em = discord.Embed(title="green", description="the best command ever, renders an energizing green heart to motivate you", color=random.randint(0, 0xffffff))
        em.add_field(name="**syntax**", value="!green")
        await ctx.send(embed = em)

    @help.command()
    async def create(self, ctx):
        em = discord.Embed(title="create", description="creates a solo or party list", color=random.randint(0, 0xffffff))
        em.add_field(name="**syntax**", value="!create [list_name] [optional: @members] \n if you follow your command with @members it will be a shared todo list")
        await ctx.send(embed = em)

    @help.command()
    async def add(self, ctx):
        em = discord.Embed(title="add", description="add a task to a list, also creates a solo list if it doesn't exist", color=random.randint(0, 0xffffff))
        em.add_field(name="**syntax**", value="!add [task_name] [list_name]")
        await ctx.send(embed = em)

    @help.command()
    async def delete(self, ctx):
        em = discord.Embed(title="delete", description="delete", color=random.randint(0, 0xffffff))
        em.add_field(name="**syntax**", value="!delete [list_name] : deletes the entire list \n !delete [list_name] [task_name] : deletes a specific task from the list \n aliases: remove, del")
        await ctx.send(embed = em)

    @help.command()
    async def done(self, ctx):
        em = discord.Embed(title="done", description="marks a task as done", color=random.randint(0, 0xffffff))
        em.add_field(name="**syntax**", value="!done [task_name] [list_name] \n aliases: achieved, finished")
        await ctx.send(embed = em)

    @help.command()
    async def join(self, ctx):
        em = discord.Embed(title="join", description="adds a member to a list", color=random.randint(0, 0xffffff))
        em.add_field(name="**syntax**", value="!join [list_name] [@members] \n the @member will be able to see and modify the party todo list")
        await ctx.send(embed = em)


def setup(bot):
    bot.add_cog(HelpCommands(bot))
    