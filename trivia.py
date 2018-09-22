import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus
import requests
import json
import operator
from html.parser import HTMLParser
import random

class Trivia:

    def __init__(self, client):
        self.client = client
        self.openTriviaDBSessionToken = ''
        self.categories = {}
        #self.participants = {}
        #self.questions = {}
        #self.inProgress = False
        self.guilds = {}

    def TokenCheck(self):
        if not self.openTriviaDBSessionToken:
            self.GetOpenTriviaDBToken()

    def GetOpenTriviaDBToken(self):
        url = 'https://opentdb.com/api_token.php?command=request'

        # Token
        response = requests.get(url)
        re = json.loads(response.text)
        self.openTriviaDBSessionToken = re['token']
        # Categories
        url = 'https://opentdb.com/api_category.php'
        response = requests.get(url)
        self.categories = json.loads(response.text)

    @commands.command()
    async def getToken(self, ctx):
        self.TokenCheck()

    @commands.command()
    async def tcategories(self, ctx):
        self.TokenCheck()

        categ = ''

        for val in self.categories['trivia_categories']:
            categ += val['name'] + ',` `'

        await ctx.message.channel.send('Here are all the categories: \n `' + categ + '`')

    @commands.command(pass_context=True)
    async def triviastop(self, ctx):
        if self.guilds[ctx.message.guild.name]["InProgress"]:
            self.guilds[ctx.message.guild.name]["InProgress"] = False
            await ctx.message.channel.send("Stopped trivia.")
        else:
            await ctx.message.channel.send("No trivia is happening.")

    @commands.command(pass_context=True)
    async def trivia(self, ctx, limit=20):
        # Get needed token
        self.GetOpenTriviaDBToken()
        # Get topic
        tp = ctx.message.content.replace("!trivia ", "").replace(str(limit)+" ", "").strip()

        # Setup group
        if not(ctx.message.guild.name in self.guilds):
            self.guilds[ctx.message.guild.name] = {}
            self.guilds[ctx.message.guild.name]["InProgress"] = False
            self.guilds[ctx.message.guild.name]["Participants"] = {}
        self.guilds[ctx.message.guild.name]["Questions"] = {}
        group = self.guilds[ctx.message.guild.name]

        if (not group["InProgress"]):
            for topic in self.categories['trivia_categories']:
                if tp in topic['name']:
                    # Topic actually exist
                    group["InProgress"] = True
                    group["Participants"][ctx.message.author.name] = 0
                    await ctx.message.channel.send("Starting trivia in **{}**, asking a total of **{}** questions.".format(tp, str(limit)))
                    await self.HandleTrivia(ctx, limit, tp)
                    return
            await ctx.message.channel.send("{} is not a valid topic.".format(tp), delete_after=5)
        else:
            await ctx.message.channel.send("Trivia already in progress!", delete_after=5)

    # Trivia Hanlder #
    # Grab Questions
    async def GetQuestions(self, count, categoryID, guildName):
        url = 'https://opentdb.com/api.php'
        params = {"amount": count, "category": categoryID}
        response = requests.get(url, params=params)
        self.guilds[guildName]["Questions"] = response.json()["results"]
        random.shuffle(self.guilds[guildName]["Questions"])

    # Handle Trivia
    async def HandleTrivia(self, ctx, count, category):
        group = self.guilds[ctx.message.guild.name]
        # Get Questions
        for cat in self.categories['trivia_categories']:
            if cat["name"] == category:
                await self.GetQuestions(count, cat["id"], ctx.message.guild.name)
        
        if len(group["Questions"]) <= 0:
            group["InProgress"] = False
            await ctx.message.channel.send("That category does not exist!")
            return

        def pred(m):
            global lastRes
            lastRes = m
            h = HTMLParser()
            return m.channel == ctx.message.channel and str(m.content).lower() == str(h.unescape(group["Questions"][x]["correct_answer"])).lower()

        # Question Loop
        for x in range(0, count):
            h = HTMLParser()
            ques = h.unescape(group["Questions"][x]["question"]) + "\n"
            anws = []
            # Give the answers to multiple question type
            if str(group["Questions"][x]["type"] == "multiple"):
                anws.append(str(h.unescape(group["Questions"][x]["correct_answer"])))
                for aw in group["Questions"][x]["incorrect_answers"]:
                    anws.append(str(h.unescape(aw)))

            random.shuffle(anws)
            await ctx.message.channel.send(str(ques) + ", ".join(anws))

            if group["InProgress"] == False:
                break

            try:
                msg = await self.client.wait_for('message', check=pred, timeout=15)
            except:
                if group["InProgress"] == False:
                    break
                await ctx.message.channel.send("**Time up**, the answer was {}".format(group["Questions"][x]["correct_answer"]))
            else:
                if group["InProgress"] == False:
                    break
                if not(lastRes.author.name in group["Participants"]):
                    group["Participants"][lastRes.author.name] = 0
                group["Participants"][lastRes.author.name] += 1
                await ctx.message.channel.send("**Correct!** {} gets 1 point.".format(lastRes.author))


        # Print final results
        await ctx.message.channel.send("**Final Results**".format(lastRes.author))
        sorted_Parts = sorted(group["Participants"].items(), key=lambda kv: kv[1], reverse=True)
        embed = discord.Embed(
	        colour = discord.Colour.blue()
        )
        embed.set_author(name="Participants")
        embed.add_field(name="Results", value=' '.join(map(str, sorted_Parts)).replace(")", "\n").replace("(", "").replace("'", "").replace(",", ":").strip(), inline=False)
        message = await ctx.message.channel.send(embed=embed)

        group["InProgress"] = False

def setup(client):
	client.add_cog(Trivia(client))
