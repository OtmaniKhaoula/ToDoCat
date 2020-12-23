import discord
from discord.ext import commands
import asyncio

class ModificationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['c'], case_insensitive=True)
    async def create(self, ctx, liste=None, *members: discord.Member):
        if not liste:
            await ctx.send("Please enter the liste name you want to create")
            return
        
        #check if the list exists
        l_exists = await self.check_liste(ctx.author.id, liste)
        if l_exists:
            await ctx.send("You already have a liste named {}".format(liste))
            return

        #check if the main user exists
        user = await self.check_user(ctx.author.id)

        await self.create_liste(ctx.author.id, user, ctx.message.id, liste.lower(), ctx.author.id)

        not_added_member = 0
        if members:
            msg = ""
            for member in members:
                l_exists_for_member = await self.check_liste(member.id, liste)
                if l_exists_for_member:
                    msg = msg + "Member {} already has a list with that name, he hasn't been added to the party".format(member.name)
                    not_added_member = not_added_member + 1
                else:
                    await self.check_user(member.id)
                    await self.create_liste(member.id, user, ctx.message.id, liste.lower(), ctx.author.id)

            await ctx.send("{} \n Party List {} successfully created! {} users have access".format(msg, liste.lower(), len(members) + 1 - not_added_member))
            return
        
        await ctx.send("Liste {} successfully created, let's be productif miaw ;)".format(liste))

    @commands.command(aliases=['a'], help='$add "task_name" "list_name add a task to a to do list', case_insensitive=True)
    async def add(self, ctx, task=None, liste=None):
        if(task == None or liste == None):
            await ctx.send('Please write the commands as such :\n $add "task_name" "list_name"')
            return
        liste = liste.lower()
        task = task.lower()
    
        user = await self.check_user(ctx.author.id)

        l_name = await self.bot.con.fetchrow("SELECT * FROM main WHERE id_user=$1 AND l_name=$2", ctx.author.id, liste)
        #if not _name for user, create list and add task
        if not l_name:
            await self.create_liste(ctx.author.id, user, ctx.message.id,liste)

        t_exists = await self.bot.con.fetch("SELECT id_task FROM main WHERE id_user=$1 AND l_name=$2 AND t_name=$3", ctx.author.id, liste, task)

        if t_exists:
            await ctx.send("Task {} already exists in {}".format(task,liste))    
            return

        #add task to an existing liste
        await self.add_task(ctx.author.id, user, liste, ctx.message.id, task)
        await ctx.send('{} successfully added to {} !'.format(task, liste))

    @commands.command(aliases=["remove", "del"], case_insensitive=True)
    async def delete(self, ctx,liste=None,task=None):
        if not liste:
            await ctx.send("Enter the liste, task you want to remove")
            return

        id_liste = await self.bot.con.fetchval("SELECT id_liste FROM main WHERE id_user=$1 AND l_name=$2", ctx.author.id, liste.lower())
        if not id_liste:
            await ctx.send(" You have no liste named: {} ".format(liste))
            return

        if not task:
            await ctx.send("Are you sure you want to remove the entire {} liste ? type y or n".format(liste))
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=17,
                    check=lambda message: message.author == ctx.author 
                                        and message.channel == ctx.channel
                )
                if msg.content.lower() == "y" or msg.content.lower() == "yes":
                    await self.delete_liste(id_liste, ctx.author.id) #DONNER DIRECTEMENT ID LISTE
                    await ctx.send("{} successfully deleted".format(liste))
                    return

                await ctx.send("{} has not been deleted".format(liste))

            except asyncio.TimeoutError:
                await ctx.send("{} has not been deleted".format(liste))
            return

        id_task = await self.bot.con.fetchval("SELECT id_task FROM main WHERE id_liste=$1 AND t_name=$2", id_liste, task.lower())
        if not id_task:
            await ctx.send(" You have no task named: {} ".format(task))
            return

        await self.delete_task(id_task, id_liste, ctx.author.id)
        await ctx.send("{} successfully deleted".format(task))
    
    ''' Database calls '''
    async def check_user(self,id):
        user = await self.bot.con.fetch("SELECT * FROM users WHERE id_user=$1", id)

        #if not user create a new user
        if not user:
            await self.bot.con.execute("INSERT INTO users (id_user, nb_tasks, nb_lists,nb_achieved) VALUES ($1,0,0,0)",id)
            
        return await self.bot.con.fetchrow("SELECT * FROM users WHERE id_user=$1", id)

    async def check_liste(self, id, liste):
        return await self.bot.con.fetchval("SELECT id_liste FROM main WHERE id_user=$1 AND l_name=$2", id, liste)

    async def create_liste(self,id_user, user, id_liste, liste, admin):
            #insert list in list
            if id_user == admin:
                await self.bot.con.execute("INSERT INTO listes (id_liste, nb_tasks, nb_achieved, l_name, admin, mode) VALUES ($1,0,0,$2,$3,False)",id_liste,liste, admin)

            #insert liste in main
            await self.bot.con.execute("INSERT INTO main (id_user, id_liste, l_name, id_task, t_name) VALUES ($1,$2,$3,NULL,NULL)",id_user,id_liste,liste)

            #upading the user's stats
            await self.bot.con.execute("UPDATE users SET nb_lists=$1 WHERE id_user=$2", user['nb_lists']+1, id_user)

    async def add_task(self,id_user, user, liste, id_task, task):
            #upading the user's stats
            await self.bot.con.execute("UPDATE users SET nb_tasks=$1 WHERE id_user=$2", user['nb_tasks']+1, id_user)


            #find id_liste to udapte mains and liste table#
            id_liste = await self.bot.con.fetchval("SELECT id_liste FROM main WHERE id_user=$1 AND l_name=$2", id_user, liste)
            await self.bot.con.execute("INSERT INTO main (id_user, id_liste, l_name, id_task, t_name) VALUES ($1,$2,$3,$4,$5)",id_user,id_liste,liste,id_task,task)
            liste = await self.bot.con.fetchrow("SELECT * FROM listes WHERE id_liste=$1", id_liste)
            await self.bot.con.execute("UPDATE listes SET nb_tasks=$1 WHERE id_liste=$2", liste['nb_tasks']+1, id_liste)
            ####

            #Insert task
            await self.bot.con.execute("INSERT INTO tasks (id_task, id_liste, t_name, important, urgent, status) VALUES ($1,$2,$3,False,False,False)",id_task,id_liste,task)

    async def delete_liste(self,id_liste, id_user):
        nb_tasks = await self.bot.con.fetchval("SELECT nb_tasks FROM listes WHERE id_liste=$1", id_liste)

        await self.bot.con.execute("DELETE FROM listes WHERE id_liste=$1", id_liste)
        await self.bot.con.execute("DELETE FROM main WHERE id_liste=$1", id_liste)
        await self.bot.con.execute("DELETE FROM tasks WHERE id_liste=$1", id_liste)

        #find user_id and upading the user's stats
        user = await self.bot.con.fetchrow("SELECT * FROM users WHERE id_user=$1", id_user)
        await self.bot.con.execute("UPDATE users SET nb_tasks=$1, nb_lists=$2 WHERE id_user=$3", (user['nb_tasks']-nb_tasks), user['nb_lists']-1, id_user)

    async def delete_task(self,id_task, id_liste, id_user):
        await self.bot.con.execute("DELETE FROM tasks WHERE id_task=$1", id_task)

        #find liste row and upading the liste's stats
        liste_row = await self.bot.con.fetchrow("SELECT * FROM listes WHERE id_liste=$1", id_liste)
        await self.bot.con.execute("UPDATE listes SET nb_tasks=$1 WHERE id_liste=$2", liste_row['nb_tasks']-1, id_liste)

        #find user row and upading the user's stats
        user = await self.bot.con.fetchrow("SELECT * FROM users WHERE id_user=$1", id_user)
        await self.bot.con.execute("UPDATE users SET nb_tasks=$1 WHERE id_user=$2", user['nb_tasks']-1, id_user)


        if liste_row['nb_tasks'] <= 1:
            await self.bot.con.execute("UPDATE main SET id_task=NULL, t_name=NULL WHERE id_liste=$1",id_liste)
            return

        await self.bot.con.execute("DELETE FROM main WHERE id_task=$1", id_task)

def setup(bot):
    bot.add_cog(ModificationCommands(bot))