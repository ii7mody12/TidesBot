import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus
import logging
import random
import asyncio
import time
import os, os.path
import requests
import json
from pprint import pprint
import atexit
from random import randint
import aiohttp
import asyncio

#Represents a client connection that connects to Discord. Used to interact with the Discord WebSocket and API.
MyBot = commands.Bot(command_prefix='!')
MyBot.remove_command("help")

#Logs info to a discord.log file
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# VARIABLES #
token = ''
botOwner = ''

with open('token.json') as f:
    js = json.load(f)
    token = js["Token"]
    botOwner = js["BotOwner"]

# METHODS #
@MyBot.event
async def on_ready():  
    print('Logged in as')
    print(MyBot.user.name)
    print(MyBot.user.id)
    print('------')

    async with aiohttp.ClientSession() as session:
        while True:
            await MyBot.cogs["TwitchAlert"].getstreams()
            await asyncio.sleep(600)

@MyBot.command(pass_context=True)
async def purge(ctx, number : int, target=None):
    await ctx.trigger_typing()
    tarID = str(target).replace("<", "").replace(">", "").replace("@", "").strip()
    if target != None and tarID:
        msgsDel = 0
        async for li in ctx.message.channel.history().filter(lambda m: str(m.author.id).replace("<", "").replace(">", "").replace("@", "").strip() == tarID):
            permissions = ctx.message.author.permissions_in(ctx.message.channel)
            tm = str(li.author.id).replace("<", "").replace(">", "").replace("@", "").strip()
            
            if tm == str(ctx.message.author.id).strip():
                # Target is self
                if msgsDel < (number+1):
                    if li:
                        await li.delete()
                        msgsDel += 1
            else:
                # target is someone else
                if (not permissions.manage_messages) and str(tm).strip() != str(MyBot.user.id).strip():
                    await ctx.message.channel.send("You don't have permission to manage messages.", delete_after=5)
                    return
                if msgsDel < (number+1):
                    if li:
                        await li.delete()
                        msgsDel += 1

        try:
            await ctx.message.delete()
        except:
            print(".")
        message = await ctx.message.channel.send('Deleted ' + str(number) + ' message(s).', delete_after=5)
    else:
        permissions = ctx.message.author.permissions_in(ctx.message.channel)
        if not permissions.manage_messages:
            await ctx.message.channel.send("You don't have permission to manage messages.", delete_after=5)
            return

        messages = await ctx.message.channel.history().flatten()
        x = 0
        while x < (number+1):
            await messages[x].delete()
            x += 1
        await ctx.message.channel.send('Deleted ' + str(number) + ' message(s).', delete_after=5)

# EXTENSIONS #
extensions = ['rewriteMusic', 'trivia', 'usermanagement', 'twitchAlert', 'pokedex']

@MyBot.command(pass_context=True)
async def reloadmodules(ctx):
    if str(ctx.message.author) != botOwner:
        await ctx.message.channel.send("You must be the bot owner to call this command.", delete_after=5)
        return

    for extension in extensions:
        try:
            MyBot.unload_extension(extension)
        except Exception as error:
            print("Cannot unload {}. [{}]".format(extension, error))

    for extension in extensions:
        try:
            MyBot.load_extension(extension)
        except Exception as error:
            print("Cannot load {}. [{}]".format(extension, error))

    await ctx.message.channel.send("Reloaded all modules.", delete_after=5)
    await ctx.message.delete()

@MyBot.command(pass_context=True)
async def load(ctx, extension):
    if str(ctx.message.author) != botOwner:
        await ctx.message.channel.send("You must be the bot owner to call this command.", delete_after=5)
        return

    try:
        MyBot.load_extension(extension)
    except Exception as error:
        print("Cannot load {}. [{}]".format(extension, error))

@MyBot.command(pass_context=True)
async def choose(ctx):
	con = ctx.message.content.replace('!choose ', '')
	conList = con.split(" ")
	await ctx.message.channel.send(conList[randint(0, len(conList)-1)])

@MyBot.command(pass_context=True)
async def say(ctx):
	print("Say by user: " + str(ctx.message.author))
	await ctx.message.channel.send(str(ctx.message.content).replace("!say ", ""))
	try:
		ctx.message.delete()
	except:
		print("No permission.")

@MyBot.command(pass_context=True)
async def unload(ctx, extension):
    if ctx.message.author != botOwner:
        await ctx.message.channel.send("You must be the bot owner to call this command.", delete_after=5)
        return

    try:
        MyBot.unload_extension(extension)
        print("Unloaded {}".format(extension))
    except Exception as error:
        print("Cannot unload extension.")

@MyBot.command(pass_context=True)
async def help(ctx):
    gr = ctx.message.content.replace("!help", "")
    gr = gr.strip()
    embed = discord.Embed(
	    colour = discord.Colour.blue()
    )
    if not str(gr).replace("!help ", "").strip():
        embed.set_author(name="Help")
        embed.add_field(name="!help General", value="General commands, such as unloading modules.", inline=False)
        embed.add_field(name="!help Music", value="Music commands.", inline=False)
        embed.add_field(name="!help Twitch", value="Twitch commands.", inline=False)
        embed.add_field(name="!help User", value="User-related commands, such as changing color.", inline=False)
        embed.add_field(name="!help Trivia", value="Trivia commands.", inline=False)
        embed.add_field(name="!help Modules", value="List all current modules.", inline=False)
        embed.add_field(name="!help Pokemon", value="List all pokemon commands.", inline=False)
        message = await ctx.message.channel.send(embed=embed)
    else:
        if str(gr).lower() == "general":
            embed.set_author(name="General Commands")
            embed.add_field(name="!Purge x user(optional)", value="deletes x amount of messages. Optionally you can delete the messages of a certain user.", inline=False)
            embed.add_field(name="!reloadmodules", value="Reloads all modules. Owner only.", inline=False)
            embed.add_field(name="!load x", value="Load a module. Owner only.", inline=False)
            embed.add_field(name="!unload x", value="Unloads a module. Owner only.", inline=False)
            embed.add_field(name="!Choose a b c...", value="Choose one of the options given.", inline=False)
            embed.add_field(name="!say x", value="Bot says whatever you type after.", inline=False)
        if str(gr).lower() == "music":
            embed.set_author(name="Music Commands")
            embed.add_field(name="!join", value="Joins the user's voice channel.", inline=False)
            embed.add_field(name="!leave", value="Leaves voice channel.", inline=False)
            embed.add_field(name="!play x", value="Plays the link given, or searches youtube for whatever is typed. Can also play twitch streams.", inline=False)
            embed.add_field(name="!playList x", value="Plays the playlist link given.", inline=False)
            embed.add_field(name="!stop", value="Stops playing whatever is currently playing.", inline=False)
            embed.add_field(name="!pause", value="Pauses whatever is playing.", inline=False)
            embed.add_field(name="!resume", value="Resumes whatever was paused.", inline=False)
            embed.add_field(name="!currentSong", value="Prints the name of whatever is playing.", inline=False)
            embed.add_field(name="!skip", value="Vote to skip the current song. Certain roles can skip the vote.", inline=False)
            embed.add_field(name="!clearQueue", value="Clear the song queue.", inline=False)
            embed.add_field(name="!queue", value="List the next 5 songs.", inline=False)
            embed.add_field(name="!volume", value="Clear the volume. The value must be inbetween 1 and 100.", inline=False)
        if str(gr).lower() == "user":
            embed.set_author(name="User Commands")
            embed.add_field(name="!addrole a b c d....", value="**Admin Only** Add a role that users can assign themselves to.", inline=False)
            embed.add_field(name="!removerole a b c d....", value="**Admin Only** Remove a role that users can assign themselves to.", inline=False)
            embed.add_field(name="!role x", value="Assign/Remove role x to yourself.", inline=False)
            embed.add_field(name="!colorme x", value="Assign color x to yourself.", inline=False)
            embed.add_field(name="!userinfo @a", value="Gives info on the user. Optionally you can use their name without the @.", inline=False)
            embed.add_field(name="!avatar @a @b @c...", value="Get the avatars of (a) user(s). Optionally you can type their username without the @, however this only works one at a time.", inline=False)
        if str(gr).lower() == "modules":
            embed.set_author(name="Module Commands")
            embed.add_field(name="Current Modules", value=', '.join(extensions), inline=False)
        if str(gr).lower() == "trivia":
            embed.set_author(name="trivia Commands")
            embed.add_field(name="!tCategories", value="List all possible trivia categories.", inline=False)
            embed.add_field(name="!trivia (number of questions) (category)", value="Start a trivia in a specific category.", inline=False)
        if str(gr).lower() == "twitch":
            embed.set_author(name="Twitch Commands")
            embed.add_field(name="!twitch (channel name)", value="Report's the channel's online status.", inline=False)
            embed.add_field(name="!twitchadd (channel name)", value="Add a channel to the alert list.", inline=False)
            embed.add_field(name="!twitchremove (channel name)", value="Remove a channel from the alert list.", inline=False)
            embed.add_field(name="!twitchalerts (channel name)", value="Specify which text channel the alerts happen in.", inline=False)
        if str(gr).lower() == "pokemon":
            embed.set_author(name="pokemon Commands")
            embed.add_field(name="!pokemon dex (pokemon name)", value="Gives info on the pokemon requested.", inline=False)
            embed.add_field(name="!pokemon item (item name)", value="Gives info on the item requested.", inline=False)
            embed.add_field(name="!pokemon moves (pokemon name)-(generation number)", value="Gives the moves the pokemon can learn.", inline=False)
            embed.add_field(name="!pokemon location (pokemon name)", value="Gives info on the item requested.", inline=False)
            embed.add_field(name="!pokemon tmset (pokemon name)", value="This command currently does not work.", inline=False)
        message = await ctx.message.channel.send(embed=embed)
    try:
        await ctx.message.delete()
    except:
        print("Can't delete message.")


# RUN BOT #

if __name__ == '__main__':
    for extension in extensions:
        try:
            MyBot.load_extension(extension)
        except Exception as error:
            print("Cannot load {}. [{}]".format(extension, error))

MyBot.run(token)