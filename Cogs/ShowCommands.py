import discord
from discord.ext import commands
import random

class ShowCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ''' Commands '''
    @commands.command(aliases=['p'], case_insensitive=True)
    async def profil(self, ctx):
        user_stats = await self.bot.con.fetchrow("SELECT nb_lists, nb_tasks, nb_achieved FROM users WHERE id_user=$1", ctx.author.id)
        if(user_stats): msg ="listes:{} \n tasks:{} \n achived:{}".format(user_stats[0], user_stats[1], user_stats[2])
        else: msg ="listes: 0 \n tasks: 0 \n achived: 0"
        title= str(ctx.author)
        embed = discord.Embed(
            title = title,
            description= msg,
            color= random.randint(0, 0xffffff)
        )
        embed.set_footer(text='Always deliver more than expected ! mew ^.^')
        embed.set_thumbnail(url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["s"], case_insensitive=True)
    async def show(self, ctx, liste=None):
        if not liste:
            embed = discord.Embed(title="Your lists", color=random.randint(0, 0xffffff))
            listes = await self.bot.con.fetch("SELECT l_name,nb_achieved,nb_tasks FROM main NATURAL JOIN listes WHERE id_user= $1", ctx.author.id)
            msg = ""
            for liste in set(listes): #set to have unique values
                embed.add_field(name="name", value=liste[0])
                embed.add_field(name="done", value=liste[1])
                embed.add_field(name="tasks", value=liste[2])
                msg = msg + "{} {}/{}\n".format(liste[0],liste[1], liste[2])

            if not embed.fields:
                embed.add_field(name="oupsi", value="You have no lists")
            
            embed.set_footer(text="Good things happen when you set your priorities straight ! mew ^.^")
            await ctx.send(embed=embed)
            return
        
        #add smth to show how important a task is // status
        id_liste = await self.bot.con.fetchval("SELECT id_liste FROM main WHERE id_user= $1 AND l_name=$2", ctx.author.id, liste.lower())
        tasks = await self.bot.con.fetch("SELECT t_name, achieved FROM tasks WHERE id_liste=$1", id_liste)

        if not tasks:
            if not id_liste:
                await ctx.send(" You have no liste named: {} ".format(liste))
                return

            await ctx.send(" List {} is empty".format(liste))
            return

        msg = ""
        for task in set(tasks):
            if task[1]:
                msg = msg + "~~"+task[0]+"~~" + "  :white_check_mark: \n" 
            else:                
                msg = msg + task[0] + "\n" 

        embed = discord.Embed(title="{} tasks".format(liste), description=msg, color=random.randint(0, 0xffffff))


            
        if not embed.description:
            embed.add_field(name="oupsi", value="You have no tasks in that list")

        embed.set_footer(text="Happiness inspires productivity ! mew ^.^")
        await ctx.send(embed=embed)

    @commands.command(case_insensitive=True)
    async def green(self, ctx):
        await ctx.send(':green_heart:')
            # add remembers for lists
            # add events reminders
            # tasks indexation
            # propose to del list once all tasks are done ??
            # congratulation message if you achieve all tasks of a list !!!
            # think of ways to make the bot more attractive, and easy to use


def setup(bot):
    bot.add_cog(ShowCommands(bot))

