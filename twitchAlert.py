import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus
import requests
import json
from twitch import TwitchClient
import sched, time
import asyncio

class TwitchAlert:
    def __init__(self, client):
        # Grab Token
        self.twitchClientID = ''
        with open('token.json') as f:
            js = json.load(f)
            self.twitchClientID = js["Client_ID"]
        # Variables
        self.client = client
        self.tClient = TwitchClient(client_id=self.twitchClientID)
        self.tAlertInfo = {}
        self.tAlertSessionInfo = {}
        self.currentCheckChannel = None
        with open('twitchAlertInfo.json') as f:
            self.tAlertInfo = json.load(f)
        with open("twitchSessionInfo.json") as g:
            self.tAlertSessionInfo = json.load(g)

    async def getstreams(self):
        for guild in self.client.guilds:
            # In a server we should be twitch alerting to #
            if(guild.name in self.tAlertInfo):
                #Get all twitch channels we should report for
                for channel in self.tAlertInfo[guild.name]["Channels"]:
                    # Make sure alert session exist for this guild
                    if not(guild.name in self.tAlertSessionInfo):
                            self.tAlertSessionInfo[guild.name] = []
                    await self.looptwitchstatus(guild, self.tClient.channels.get_by_id(channel).name)

    
    # Set text channel alerts happen in
    @commands.command(pass_context=True)
    async def twitchalerts(self, ctx, textChannel):
        user = ctx.message.author
        permissions = user.permissions_in(ctx.message.channel)
        if (not permissions.administrator and not permissions.manage_guild):
            await ctx.message.channel.send("Sorry, you don't have permission to do that.")
            return

        self.tAlertInfo[ctx.message.guild.name]["TextChannel"] = int(str(textChannel).replace("<", "").replace(">", "").replace("#", "").strip())
        group = self.tAlertInfo[ctx.message.guild.name]
        await ctx.message.channel.send("Alerts will now happen in {}.".format(textChannel), delete_after=5)
        await ctx.message.delete()
        self.saveToFile()

    # Add twitch to update list #
    @commands.command(pass_context=True)
    async def twitchadd(self, ctx, twitchChannel):
        # Create Slot
        if not (str(ctx.message.guild.name) in self.tAlertInfo):
            self.tAlertInfo[ctx.message.guild.name] = {}
            self.tAlertInfo[ctx.message.guild.name]["Channels"] = []
        group = self.tAlertInfo[ctx.message.guild.name]["Channels"]
        
        msg = None
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        channels = self.tClient.search.channels(twitchChannel, limit=10, offset=0)
        if channels[0].id in group:
            await ctx.message.channel.send('This user is already in the list.', delete_after=5)
            await ctx.message.delete()
            return

        await ctx.message.channel.send("Found {}, is this who you wanted? Respond yes, or no".format(channels[0].url), delete_after=10)
        try:
            msg = await self.client.wait_for('message', check=pred, timeout=10.0)
        except asyncio.TimeoutError:
            await ctx.message.channel.send('Timed out...')
        else:
            if str(msg.content).lower() == "yes":
                await ctx.message.channel.send('Ok! Adding to list.'.format(msg), delete_after=5)
                group.append(channels[0].id)
                if not("TextChannel" in self.tAlertInfo[ctx.message.guild.name]):
                    self.tAlertInfo[ctx.message.guild.name]["TextChannel"] = ctx.message.channel.name
            else:
                await ctx.message.channel.send('Ignoring call.', delete_after=5)
            await msg.delete()
        await ctx.message.delete()
        self.saveToFile()

    # Remove twitch from alert list #
    @commands.command(pass_context=True)
    async def twitchremove(self, ctx, twitchChannel):
        user = self.tClient.users.translate_usernames_to_ids([twitchChannel])

        channels = self.tAlertInfo[ctx.message.guild.name]["Channels"]

        if (self.tAlertInfo[ctx.message.guild.name]):
            for x in range(0, len(channels)):
                if channels[x] == int(user[0].id):
                    channels.pop(x)
                    await ctx.message.channel.send('Removed {} from alerts.'.format(twitchChannel), delete_after=5)
                    self.saveToFile()
                    await ctx.message.delete()
                    return
        await ctx.message.channel.send('{} is not in the list.'.format(twitchChannel), delete_after=5)
        await ctx.message.delete()

    # Remove twitch from alert list #
    @commands.command(pass_context=True)
    async def twitch(self, ctx, twitchChannel=None, Msg=True):
        if twitchChannel != None:
            user = self.tClient.users.translate_usernames_to_ids([twitchChannel])
        else:
            user = [self.currentCheckChannel]

        res = self.tClient.streams.get_stream_by_user(user[0].id)

        if bool(res):
            if Msg:
                await ctx.message.channel.send('{} is live! {}'.format(twitchChannel, res.channel.url))
            await ctx.message.delete()
            return True
        else:
            if Msg:
                await ctx.message.channel.send('{} is offline!'.format(twitchChannel), delete_after=10)
            await ctx.message.delete()
            return False

    # LOOP #
    async def looptwitchstatus(self, guild, twitchChannel):
        user = self.tClient.users.translate_usernames_to_ids([twitchChannel])

        res = self.tClient.streams.get_stream_by_user(user[0].id)
        wantedChannel = self.tAlertInfo[guild.name]["TextChannel"]
        guildChannel = guild.get_channel(int(wantedChannel))

        if bool(res):
            if not(res["created_at"].second in  self.tAlertSessionInfo[guild.name]):
                await guildChannel.send('{} is live! {}'.format(twitchChannel, res.channel.url))
                self.tAlertSessionInfo[guild.name].append(res["created_at"].second)
                return True
        self.saveSessionInfo()

    # Save twitchAlert data to file #
    def saveToFile(self):
        with open('twitchAlertInfo.json', 'w') as outfile:  
            json.dump(self.tAlertInfo, outfile)

    def saveSessionInfo(self):
        with open('twitchSessionInfo.json', 'w') as outfile:  
            json.dump(self.tAlertSessionInfo, outfile)

def setup(client):
    client.add_cog(TwitchAlert(client))