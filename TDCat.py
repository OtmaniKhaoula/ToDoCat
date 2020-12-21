import discord
from discord.ext import commands

import asyncpg 

bot = commands.Bot(command_prefix='$')


def read_token():
    with open("TDCat.env", "r") as f:
        lines = f.readlines()
        return lines[0].strip() 

def read_mdp():
    with open("TDCat.env", "r") as f:
        lines = f.readlines()
        return lines[1].strip() 

mdp = read_mdp()

async def create_db_pool():
    bot.con = await asyncpg.create_pool(database="TDLCat", user="postgres", password=mdp)


@bot.event
async def on_ready():
    print('We have logged in as {} {}'.format(bot.user.name, bot.user.id))

@bot.command(aliases=['a'], help='$add "task_name" "list_name add a task to a to do list', case_insensitive=True)
async def add(ctx, task=None, liste=None):
    if(task == None or liste == None):
        await ctx.send('Please write the commands as such :\n $add "task_name" "list_name"')
        return
    liste = liste.lower()
    task = task.lower()

    sql = "SELECT * FROM users WHERE id_user=$1"
    user = await bot.con.fetch(sql, ctx.author.id)

    #if not user create a new user
    if not user:
        await add_user(ctx.author.id)

    sql = "SELECT * FROM main WHERE id_user=$1 AND l_name=$2"
    l_name = await bot.con.fetchrow(sql, ctx.author.id, liste)

    #if not _name for user, create list and add task
    if not l_name:
        await add_liste(ctx.author.id, ctx.message.id,liste, task)
        await ctx.send('{} successfully added to {} !'.format(task, liste))
        return

    sql = "SELECT id_task FROM main WHERE id_user=$1 AND l_name=$2 AND t_name=$3"
    t_exists = await bot.con.fetch(sql, ctx.author.id, liste, task)

    if t_exists:
        await ctx.send("Task {} already exists in {}".format(task,liste))    
        return

    #add task to an existing liste
    await add_task(ctx.author.id, liste, ctx.message.id, task)
    await ctx.send('{} successfully added to {} !'.format(task, liste))

async def add_user(id):
        await bot.con.execute("INSERT INTO users (id_user, nb_tasks, nb_lists,nb_achieved) VALUES ($1,0,0,0)",id)

async def add_liste(id_user, id, liste, task):
        #insert list in list
        await bot.con.execute("INSERT INTO listes (id_liste, nb_tasks, nb_achieved, l_name) VALUES ($1,1,0,$2)",id,liste)

        #insert all in main
        await bot.con.execute("INSERT INTO main (id_user, id_liste, l_name, id_task, t_name) VALUES ($1,$2,$3,$4,$5)",id_user,id,liste,id,task)

        #insert task in tasks
        await bot.con.execute("INSERT INTO tasks (id_task, t_name, important, urgent, status) VALUES ($1,$2,False,False,False)",id,task)

        #find user_id and upading the user's stats
        user = await bot.con.fetchrow("SELECT * FROM users WHERE id_user=$1", id_user)
        await bot.con.execute("UPDATE users SET nb_tasks=$1, nb_lists=$2 WHERE id_user=$3", user['nb_tasks']+1, user['nb_lists'], user['id_user'])


async def add_task(id_user, liste, id_task, task):
        #upading the user's stats
        user = await bot.con.fetchrow("SELECT * FROM users WHERE id_user=$1", id_user)
        await bot.con.execute("UPDATE users SET nb_tasks=$1, nb_lists=$2 WHERE id_user=$3", user['nb_tasks']+1, user['nb_lists']+1, user['id_user'])


        #find id_liste to udapte mains and liste table#
        id_liste = await bot.con.fetchrow("SELECT id_liste FROM main WHERE id_user=$1 AND l_name=$2", id_user, liste)
        await bot.con.execute("INSERT INTO main (id_user, id_liste, l_name, id_task, t_name) VALUES ($1,$2,$3,$4,$5)",id_user,id_liste[0],liste,id_task,task)
        liste = await bot.con.fetchrow("SELECT * FROM listes WHERE id_liste=$1", id_liste[0])
        await bot.con.execute("UPDATE listes SET nb_tasks=$1 WHERE id_liste=$2", liste['nb_tasks']+1, id_liste[0])
        ####

        #Insert task
        await bot.con.execute("INSERT INTO tasks (id_task, t_name, important, urgent, status) VALUES ($1,$2,False,False,False)",id_task,task)



@bot.command()
async def show(ctx, liste=None):
    if not liste:
        listes = await bot.con.fetch("SELECT l_name FROM main WHERE id_user= $1", ctx.author.id)
        msg = ""
        for liste in set(listes):
            msg = msg + liste[0] + "\n"
        await ctx.send(msg)
        return
   
    tasks = await bot.con.fetch("SELECT t_name FROM main WHERE id_user= $1 AND l_name=$2", ctx.author.id, liste.lower())

    if not tasks:
        await ctx.send(" You have no liste named: {} ".format(liste))
        return

    msg = ""
    for task in set(tasks):
        msg = msg + task[0] + "\n"

    await ctx.send(msg)
     



@bot.command(help='best command ever', case_insensitive=True)
async def green(ctx):
    await ctx.send(':green_heart:')
    #commande to add list ($create)
    
    #command to delete a list

    #command to delete a task

    #command to show a list
    
    #command to set task status (current, done or not)
    
    #help command

    #send to do lists to other members ! (DM)

    #multiplayer to do liste

bot.loop.run_until_complete(create_db_pool())
token = read_token()

bot.run(token)