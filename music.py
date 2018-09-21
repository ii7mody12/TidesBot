# Doesn't work dis Discord.py Rewrite #
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus
import youtube_dl
from bs4 import BeautifulSoup
import requests

class Music:

	def __init__(self, client):
		self.client = client
		self.players = {}
		self.musicQueue = {}
		self.skipVotes = {}
		self.skipsNeeded = 4
		self.startingPlay = False

	# Join & Leave #
	@commands.command(pass_context=True)
	async def join(self, ctx):
		channel = None

		try:
			channel = ctx.author.voice.channel
		except:
			await ctx.message.channel.send("You must be in a channel.")
			return

		vc = ctx.voice_client

		if vc:
			if vc.channel.id != channel.id:
				try:
					await vc.move_to(channel)
				except:
					await ctx.message.channel.send("Moving to channel timed out.")
		else:
			try:
				await channel.connect()
			except:
				await ctx.message.channel.send("Join channel timed out.")

		await ctx.send(f'Connected to **{channel}**', delete_after=20)

	@commands.command(pass_context=True)
	async def leave(self, ctx):
		vc = ctx.voice_client
		if not vc or not vc.is_connected():
			return await ctx.message.channel.send("Not connected.")
		else:
			try:
				await ctx.guild.voice_client.disconnect()
			except:
				pass

	def getPlaylistLinks(self, url):
		sourceCode = requests.get(url).text
		soup = BeautifulSoup(sourceCode, 'html.parser')
		domain = 'https://www.youtube.com'
		links = []
		for link in soup.find_all("a", {"dir": "ltr"}):
			href = link.get('href')
			if href.startswith('/watch?'):
				links.append(str(domain + href))
		return links

	@commands.command(pass_context=True)
	async def playlist(self, ctx, url):
		if url.find("playlist") == -1:
			await ctx.message.channel.send("This is not a playlist link.")
		else:
			links = self.getPlaylistLinks(str(url))
			await ctx.message.channel.send("Queuing playlist...")
			for x in links:
				li = str(x).split("&")[0].strip()
				await self.realPlay(ctx, li, forceUrl=True)
			await ctx.message.channel.send("Done!")

	# Play Song #
	async def realPlay(self, ctx, url, forceUrl=False):
		if self.startingPlay:
			print("In progress...")
			return
		
		await ctx.trigger_typing()
		vc = ctx.voice_client
		self.startingPlay = True

		# Can't play if not in a voice channel
		if not vc:
			await ctx.invoke(self.join)

		player = self.get_player(ctx)

		if not forceUrl:
			url = ctx.message.content.replace('!play ', '')

		source = await YTDLSource.create_source(ctx, url, download=False)

		print(str(source))

		self.startingPlay = False

		#server = ctx.message.server
		#voice_client = self.client.voice_client_in(server)
		#cal = lambda: self.playNext(server.id)

		#if server.id in self.players:
		#	if self.players[server.id].is_playing():
				# Queue up the song
		#		if not forceUrl:
		#			await ctx.message.channel.send("Queuing link.")
		#		if server.id in self.musicQueue:
					# queue already exist, add to the end of it
		#			self.musicQueue[server.id].append(await voice_client.create_ytdl_player(url, ytdl_options=opts, after=cal))
		#		else:
					# queue doesn't exist, create it
		#			self.musicQueue[server.id] = [await voice_client.create_ytdl_player(url, ytdl_options=opts, after=cal)]
		#	else:
				# Nothing is playing, start playing something
		#		self.players[server.id] = await voice_client.create_ytdl_player(url, ytdl_options=opts, after=cal)
		#		self.players[server.id].start()
		#		await ctx.message.channel.send("Playing {}".format(player.title))
		#else:
			# The server has no player in it, create one.
		#	player = await voice_client.create_ytdl_player(url, ytdl_options=opts, after=cal)
		#	self.players[server.id] = player
		#	player.start()
		#	await ctx.message.channel.send("Playing {}".format(player.title))

	@commands.command(pass_context=True)
	async def play(self, ctx, url):
		await self.realPlay(ctx, url)

	def playNext(self, serverId):
		if serverId in self.musicQueue:
			if len(self.musicQueue[serverId]) > 0:
				player = self.musicQueue[serverId].pop(0)
				self.players[serverId] = player
				player.start()
				self.skipVotes[id] = []
	
	@commands.command(pass_context=True)
	async def skip(self, ctx):
		id = ctx.message.server.id
		if id in self.players:
			if id in self.skipVotes:
				if not (ctx.message.author in self.skipVotes[id]):
					self.skipVotes[id].append(ctx.message.author)
				else:
					await ctx.message.channel.send("You can't vote twice.")
					return
			else:
				self.skipVotes[id] = [ctx.message.author]
			
			if len(self.skipVotes[id]) >= self.skipsNeeded:
				await ctx.message.channel.send("Votes met, skipping!")
				self.players[id].skip()
				self.skipVotes[id] = 0
			else:
				await ctx.message.channel.send("{}/{} votes got to skip.".format(len(self.skipVotes[id]), self.skipsNeeded))

	@commands.command(pass_context=True)
	async def stop(self, ctx):
		id = ctx.message.server.id
		self.musicQueue[id] = []
		self.skipVotes[id] = []
		self.players[id].stop()

	@commands.command(pass_context=True)
	async def pause(self, ctx):
		id = ctx.message.server.id
		self.players[id].pause()

	@commands.command(pass_context=True)
	async def resume(self, ctx):
		id = ctx.message.server.id
		self.players[id].resume()

	@commands.command(pass_context=True)
	async def clearQueue(self, ctx):
		id = ctx.message.server.id
		self.musicQueue[id] = []
		self.skipVotes[id] = []

	@commands.command(pass_context=True)
	async def currentSong(self, ctx):
		if ctx.message.server in self.players:
			await ctx.message.channel.send("Playing {}".format(self.players[ctx.message.server].title))
		else:
			await ctx.message.channel.send("Nothing is playing currently.")

	def get_player(self, ctx):
		player = None
		try:
			player = self.players[ctx.guild.id]
		except KeyError:
			player = MusicPlayer(ctx)
			self.players[ctx.guild.id] = player
		return player

def setup(client):
	client.add_cog(Music(client))