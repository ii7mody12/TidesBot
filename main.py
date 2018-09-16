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
import youtube_dl

# OPUS #
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass
	raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))

#Represents a client connection that connects to Discord. Used to interact with the Discord WebSocket and API.
MyBot = commands.Bot(command_prefix='!')

#Logs info to a discord.log file
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# VARIABLES #
TOKEN = 'YOURTOKENHERE'

# TRIVIA VARIABLES #
openTriviaDB_SessionToken = ''


@MyBot.event
async def on_ready():  
    print('Logged in as')
    print(MyBot.user.name)
    print(MyBot.user.id)
    print('------')

@MyBot.command(pass_context=True)
async def purge(ctx, number : int):
    mgs = [] #Empty list to put messages in
    if number > 1:
        async for x in MyBot.logs_from(ctx.message.channel, limit = number):
            mgs.append(x)
    else:
        await MyBot.say('Value must be between 2 and 100')
        return
    await MyBot.delete_messages(mgs)
    await MyBot.say('Deleted' + number + ' messages.')
    await asyncio.sleep(5)
    await MyBot.delete_message(MyBot.get_message())

@MyBot.command()
async def info():
    helpTxt = 'There are a few commands avaliable. \n **!roll NdN** Rolls a dice, with N being any number \n **!purge xx** Removes a amount of messages, with xx being that amount'
    await MyBot.say(helpTxt)

# TRIVIA #
def GetOpenTriviaDBToken():
	url = 'https://opentdb.com/api_token.php?command=request'

	response = requests.get(url)
	print(response.text)
	re = json.loads(response.text)
	openTriviaDB_SessionToken = re['token']

@MyBot.command()
async def tCategories():
	if not openTriviaDB_SessionToken:
		GetOpenTriviaDBToken()
		await MyBot.say('Got OpenTriviaDB token...')

	url = 'https://opentdb.com/api_category.php'
	response = requests.get(url)
	# print(response.text)
	re = json.loads(response.text)

	categ = ''

	for val in re['trivia_categories']:
		categ += val['name'] + ',` `'

	await MyBot.say('Here are all the categories: \n `' + categ + '`')

# MUSIC #
players = {}

@MyBot.command(pass_context=True)
async def join(ctx):
	channel = ctx.message.author.voice.voice_channel
	await MyBot.join_voice_channel(channel)

@MyBot.command(pass_context=True)
async def leave(ctx):
	for x in MyBot.voice_clients:
		if(x.server == ctx.message.server):
			return await x.disconnect()

@MyBot.command(pass_context=True)
async def play(ctx, url):
	server = ctx.message.server
	voice_client = MyBot.voice_client_in(server)
	player = await voice_client.create_ytdl_player(url)
	players[server.id] = player
	player.start()

# RUN BOT #
MyBot.run(os.getenv('TOKEN'))