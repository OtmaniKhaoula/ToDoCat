import discord
from discord.ext import commands

class ShowCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['p'], case_insensitive=True)
    async def profil(self, ctx):
        nb_listes = await self.bot.con.fetchval("SELECT nb_lists FROM users WHERE id_user=$1", ctx.author.id)
        nb_tasks = await self.bot.con.fetchval("SELECT nb_tasks FROM users WHERE id_user=$1", ctx.author.id)

        msg ="{}\n listes:{} \n tasks:{}".format(ctx.author, nb_listes, nb_tasks)
        await ctx.send(msg)
    @commands.command(aliases=["s"], case_insensitive=True)
    async def show(self, ctx, liste=None):
        if not liste:
            listes = await self.bot.con.fetch("SELECT l_name,nb_achieved,nb_tasks FROM main NATURAL JOIN listes WHERE id_user= $1", ctx.author.id)
            msg = ""
            for liste in set(listes): #set to have unique values
                msg = msg + "{} {}/{}\n".format(liste[0],liste[1], liste[2])

            if not msg:
                msg = "You have no lists"
            await ctx.send(msg)
            return
            
        #add smth to show how important a task is // status
        id_liste = await self.bot.con.fetchval("SELECT id_liste FROM main WHERE id_user= $1 AND l_name=$2", ctx.author.id, liste.lower())
        tasks = await self.bot.con.fetch("SELECT t_name FROM main WHERE id_liste=$1", id_liste)
        if not tasks:
            await ctx.send(" You have no liste named: {} ".format(liste))
            return

        msg = ""
        for task in set(tasks):
            if task[0]:
                msg = msg + task[0] + "\n"
            
        if not msg:
            msg = "You have no tasks in that list"

        await ctx.send(msg)

    @commands.command(help='best command ever', case_insensitive=True)
    async def green(self, ctx):
        await ctx.send(':green_heart:')
            #commande to add list ($create)
            
            #command to delete a list

            #command to delete a task

            #command to show a list
            
            #command to set task status (current, done or not)
            
            #help command

            #send to do lists to other members ! (DM)

            #multiplayer to do liste

def setup(bot):
    bot.add_cog(ShowCommands(bot))