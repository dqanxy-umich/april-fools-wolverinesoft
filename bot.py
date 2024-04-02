import discord
import os
import random
import asyncio
import datetime
import threading

from discord.ext import commands

# Create a new bot instance
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

recent_users = set()
blacklist = set()
whitelist = set()
initialized = False
banthread = None

# Event: Bot is ready
@bot.event
async def on_ready():
    global initialized 
    global recent_users 
    global banthread
    global outputchannel
    outputchannel = None
    recent_users = set()
    initialized = False
    banthread = None
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

#Collect recent users from channel
async def getmessages(channelname, server):
    global recent_users
    print(f"Collecting recent messages...")
    six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
    channel = discord.utils.get(bot.get_all_channels(), name=channelname)
    if(channel is None):
        print("Channel not found")
        return recent_users
    messages = [ i async for i in channel.history(limit=None, after=six_months_ago)]

    print(f"Total messages in the last 6 months: {len(messages)}")
    for message in messages:
        if(message.author.name=='WolverineSoft Human Resources'): continue
        recent_users.add(discord.utils.get(server.members, id=message.author.id))
    print(recent_users)
    return recent_users


async def ban(amt,serverref, user_pool):
    print(f"Ban thread started")
    global blacklist
    global whitelist
    role = discord.utils.get(serverref.roles, name="Fired")
    banned_people = []
    for user in user_pool:
        if (random.random() < amt or user.name in blacklist) and role not in user.roles:
            if user.name in whitelist:
                continue
            print(f"Banning {user.name}")
            await user.add_roles(role)
            banned_people.append(user)

    print(f"Ban thread finished")
    peoplestring = ""

    for person in banned_people:
        peoplestring+=f"{person.mention}, "
        
    global outputchannel
    if(outputchannel is not None) and peoplestring != "":
        await outputchannel.send(f'''Hello WolverineSoft,
                                    
It is with our greatest regret that we have decided to layoff the following people: 
                                    
{peoplestring}

We are grateful for the hard work and dedication of all of our members, and we are deeply saddened to see them go. We proceed with heavy hearts, and we wish them the best of luck in their future endeavors. - WolverineSoft HR''')
            

async def unban(amt,serverref, user_pool):
    print(f"Unban thread started")
    global blacklist
    global whitelist
    role = discord.utils.get(serverref.roles, name="Fired")
    unbanned_people = []
    for user in user_pool:
        try:
            if (random.random() < amt or user.name in whitelist) and role in user.roles and user.name not in blacklist:
                print(f"Unbanning {user.name}")
                await user.remove_roles(role)
                unbanned_people.append(user)
        except:
            continue
    print(f"Unban thread finished")


async def banovertime(amt,delay,serverref, user_pool):
    while True:
        await ban(amt,serverref, user_pool)
        await asyncio.sleep(delay)

#Handle bot commands (only in bot-testing channel)
async def handle_bot_command(message):
    global banthread
    global recent_users 
    global blacklist
    global whitelist
    global initialized

    command_prefixes = ["!ban", "!unban", "!blacklist", "!clearblacklist", "!whitelist", "!clearwhitelist", "!bovertime", "!output", "!say", "!getmessages", "!init", "!uninit"]
    content = message.content
    command = ""

    for prefix in command_prefixes:
        if content.startswith(prefix):
            command = prefix
            param = content[len(prefix)+1:] if len(content)>len(prefix) else ""
            break
    match command:
        case "!ban":
            await ban(float(param),message.guild, recent_users)
            return
        case "!unban":
            await unban(float(param),message.guild, recent_users)
            return
        case "!blacklist":
            blacklist.add(param)
            await message.reply(f"Blacklisted {param}")
            return
        case "!clearblacklist":
            blacklist = set()
            await message.reply(f"Cleared blacklist")
            return
        case "!whitelist":
            whitelist.add(param)
            await message.reply(f"Whitelisted {param}")
            return
        case "!clearwhitelist":
            whitelist = set()
            await message.reply(f"Cleared whitelist")
            return
        case "!bovertime":
            if banthread is not None:
                banthread.cancel()
            tokens = content.split(" ")
            banthread = asyncio.get_event_loop().create_task(banovertime(float(tokens[1]),float(tokens[2]),message.guild, recent_users))
            return
        case "!output":
            for channel in message.guild.channels:
                if channel.name == param:
                    global outputchannel 
                    outputchannel = channel
                    break
            return
        case "!say":
            if(outputchannel is not None):
                await outputchannel.send(param)
            return
        case "!getmessages":
            await getmessages(param, message.guild)
            return
        case "!init":
            if not initialized:
                initialized = True
            return
        case "!uninit":
            if initialized:
                recent_users = set()
                initialized = False
            return

#Event: Message is received
@bot.event
async def on_message(message):
    global initialized
    if message.author == bot.user:
        return
    if message.channel.name == 'bot-testing':
        await handle_bot_command(message)
        return
    if initialized:
        role = discord.utils.get(message.author.roles, name="Fired")
        if message.content == "!unionize" :
            await asyncio.sleep(.2)
            if role is not None and role.name == "Fired":
                await message.channel.send(f'Sorry! I ({message.author.display_name}) have been laid off and can no longer speak in WolverineSoft. We also noticed your attempt to unionize and wanted to let you know that unfortunately no one cares about your feelings, and your attempt is futile. Regardless, we wish you the best of luck finding employment elsewhere! - WolverineSoft HR');
            await message.delete()
            return
        if role is not None and role.name == "Fired":
            await message.reply(f'Sorry! I ({message.author.display_name}) have been laid off and can no longer speak in WolverineSoft. We wish you the best of luck finding employment elsewhere! - WolverineSoft HR')
            await message.delete()

#Handle editing previous messages
@bot.event
async def on_message_edit(message_before, message_after):
    if initialized:
        role = discord.utils.get(message_after.author.roles, name="Fired")
        if role is not None and role.name == "Fired":
            await message_after.reply(f'Sorry! I ({message_after.author.display_name}) have been laid off and can no longer speak in WolverineSoft. We wish you the best of luck finding employment elsewhere! - WolverineSoft HR')
            await message_after.delete()


# Run the bot
bot.run('get ur own token')