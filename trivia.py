import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus
import requests
import json

class Trivia:

    def __init__(self, client):
        self.client = client
        self.openTriviaDBSessionToken = ''
        self.participants = {}
        self.categories = {}
        self.questions = {}
        self.inProgress = False

    def TokenCheck(self):
        if not self.openTriviaDBSessionToken:
            self.GetOpenTriviaDBToken()

    def GetOpenTriviaDBToken(self):
        url = 'https://opentdb.com/api_token.php?command=request'

        # Token
        response = requests.get(url)
        # print(response.text)
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
    async def tCategories(self, ctx):
        self.TokenCheck()

        categ = ''

        for val in self.categories['trivia_categories']:
            categ += val['name'] + ',` `'

        await ctx.message.channel.send('Here are all the categories: \n `' + categ + '`')

    @commands.command(pass_context=True)
    async def trivia(self, ctx, limit=20):
        self.GetOpenTriviaDBToken()
        tp = ctx.message.content.replace("!trivia ", "").replace(str(limit)+" ", "").strip()
        if not self.inProgress:
            for topic in self.categories['trivia_categories']:
                if tp in topic['name']:
                    # Topic actually exist
                    self.inProgress = True
                    self.participants = {ctx.message.author.name}
                    await ctx.message.channel.send("Starting trivia in **{}**, asking a total of **{}** questions.".format(tp, str(limit)))
                    await self.HandleTrivia(ctx, limit, tp)
                    return
            await ctx.message.channel.send("{} is not a valid topic.".format(tp), delete_after=5)
        else:
            await ctx.message.channel.send("Trivia already in progress!", delete_after=5)

    # Trivia Hanlder #
    # Grab Questions
    async def GetQuestions(self, count, categoryID):
        url = 'https://opentdb.com/api.php'
        params = {"amount": count, "category": categoryID}
        response = requests.get(url, params=params)
        self.questions = response.json()["results"]
        #print(self.questions)

    # Handle Trivia
    async def HandleTrivia(self, ctx, count, category):
        # Get Questions
        for cat in self.categories['trivia_categories']:
            if cat["name"] == category:
                await self.GetQuestions(count, cat["id"])
        
        def pred(m):
            return m.channel == ctx.message.channel and m.content in self.questions[x]["correct_answer"]

        # Question Loop
        for x in range(0, count):
            ques = await ctx.message.channel.send(self.questions[x]["question"], delete_after=15)
            try:
                msg = await self.client.wait_for('message', check=pred, timeout=15)
            except:
                await ctx.message.channel.send("Time up, the answer was {}".format(self.questions[x]["correct_answer"]), delete_after=5)
            else:
                await ctx.message.channel.send("Correct!", delete_after=5)
        self.inProgress = False

def setup(client):
	client.add_cog(Trivia(client))
