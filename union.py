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

# Event: Bot is ready
@bot.event
async def on_ready():
    global initialized 
    global unionthread
    global outputchannel

    outputchannel = None
    initialized = False
    unionthread = None

    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')


union_members = set()


#Handle bot commands (only in bot-testing channel)
async def handle_bot_command(message):
    global initialized
    global union_members
    global unionthread

    command_prefixes = ["!unionoutput", "!ununionize", "!setunionchannel", "!unionsay", "!init", "!uninit"]
    content = message.content
    command = ""

    for prefix in command_prefixes:
        if content.startswith(prefix):
            command = prefix
            param = content[len(prefix)+1:] if len(content)>len(prefix) else ""
            break
        
    match command:
        case "!unionoutput":
            for channel in message.guild.channels:
                if channel.name == param:
                    global outputchannel 
                    outputchannel = channel
                    break
            return
        case "!ununionize":
            role = discord.utils.get(message.guild.roles, name="Unionizing")
            for member in union_members:
                if role in member.roles:
                    await member.remove_roles(role)
            union_members = set()
            return
        case "!setunionchannel":
            for channel in message.guild.channels:
                if channel.name == param:
                    unionthread = channel
                    break
            return
        case "!unionsay":
            if(outputchannel is not None):
                await outputchannel.send(param)
            return
        case "!init":
            if not initialized:
                initialized = True
            return
        case "!uninit":
            if initialized:
                initialized = False
            return

#Event: Message is received
@bot.event
async def on_message(message):
    global union_members
    global initialized
    global unionthread
    if message.channel.name == 'bot-testing':
        await handle_bot_command(message)
        return
    if initialized:
        if message.content == "!unionize" :
            role = discord.utils.get(message.guild.roles, name="Unionizing")
            user = discord.utils.get(message.guild.members, id=message.author.id)
            if role not in user.roles:
                await user.add_roles(role)
                union_members.add(user)
                await unionthread.send(f'{message.author.display_name} has joined the Union! Together, we are stronger. - WolverineSoft Union')


# Run the bot
bot.run('get ur own token')