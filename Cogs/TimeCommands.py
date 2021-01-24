import discord
from discord.ext import commands, tasks
import asyncpg
import asyncio
import random
import time

class TimeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.datas = []
        self.time.add_exception_type(asyncpg.PostgresConnectionError)
        self.time.start()

    def cog_unload(self):
        self.time.cancel()

    ''' Background tasks '''
    @tasks.loop(seconds=1)
    async def time(self):
        t = time.localtime()
        act = time.mktime(t)
        await self.fetch_reminders()
        for data in set(self.datas):
            if(abs(data[2]-int(act)) <= 2):
                await self.set_reminders(data[0], data[1], data[3], data[3]+data[2])
                await self.show_reminder(data[0], data[1])


    ''' Commands '''
    @commands.command(case_insensitive=True)
    async def reminder(self, ctx, liste=None, hours=None):
        print(ctx.author.id)
        if not hours:
            if liste:
                hours = liste
                liste = None
            else:
                await ctx.send("Please specify in how much hours you want to be reminded of your lists\n for instance: !reminder 60 (to be reminded every hour)")
        
        if hours == "NULL" or hours == "0":
            await self.set_reminders(ctx.author.id, liste, 1, 0)
            await ctx.send("Reminder stopped")
            return

        try:
            hours = int(hours)
            if hours < 1:
                await ctx.send("The time must be a number bigger than 1")
                return
        except ValueError:
            await ctx.send("The time must be a number bigger than 1")
            return

        if not liste:
            await ctx.send("Please specify which list you want to be remembered of")
            return
        else:
            #verify that list exists !!
            id_liste = await self.bot.con.fetchval("SELECT id_liste FROM main WHERE id_user=$1 AND l_name=$2", ctx.author.id, liste.lower())
            if not id_liste:
                await ctx.send("You have no list named {}".format(liste))

        t = time.localtime()
        nrem = int(time.mktime(t)) + hours*60*60

        await self.set_reminders(ctx.author.id, liste, hours*60*60, nrem)
        await ctx.send("Reminder sucessfully set next reminder in: {} minutes".format(hours))


    ''' Methods '''
    async def set_reminders(self, user_id, l_name, time, nrem):
        if not l_name:
            await self.bot.con.execute("UPDATE main SET nrem=$1, interv=$2 WHERE id_user=$3", nrem, time, user_id)
            return

        id_liste = await self.bot.con.fetchval("SELECT id_liste FROM main WHERE id_user=$1 AND l_name=$2", user_id, l_name)
        await self.bot.con.execute("UPDATE main SET nrem=$1, interv=$2 WHERE l_name=$3 AND id_liste=$4", nrem, time, l_name, id_liste )

    async def fetch_reminders(self):
        self.datas = []
        self.datas = await self.bot.con.fetch("SELECT id_user, l_name, nrem, interv FROM main WHERE nrem > 1")

    async def show_reminder(self, id_, liste):
        id_liste = await self.bot.con.fetchval("SELECT id_liste FROM main WHERE id_user= $1 AND l_name=$2", id_, liste.lower())
        tasks = await self.bot.con.fetch("SELECT t_name, achieved FROM tasks WHERE id_liste=$1", id_liste)
        
        msg=None
        if tasks:
            msg = ""
            for task in set(tasks):
                if task[1]:
                    msg = msg + "~~"+task[0]+"~~" + "  :white_check_mark: \n" 
                else:                
                    msg = msg + task[0] + "\n" 

        embed = discord.Embed(title="!!! reminder !!! {} tasks ".format(liste), description=msg, color=random.randint(0, 0xffffff))

        
            
        if not embed.description:
            embed.add_field(name="oupsi", value="You have no tasks in that list")

        embed.set_footer(text="Happiness inspires productivity ! mew ^.^")

        author = await self.bot.fetch_user(id_)
        await author.send(embed=embed)

def setup(bot):
    bot.add_cog(TimeCommands(bot))
    