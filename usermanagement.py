import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus
import requests
import json
from datetime import datetime

class UserManagement:
    def __init__(self, client):
        self.client = client
        self.roleServers = {}
        with open("RoleDef.json") as f:
            self.roleServers = json.load(f)

    @commands.command(pass_context=True)
    async def userinfo(self, ctx):
        user = ctx.message.author
        username = None

        if len(ctx.message.mentions) > 0:
            username = ctx.message.mentions[0].name
        else:
            username = str(ctx.message.content).replace("!userinfo ", "").strip()
        print(username)

        wt = discord.utils.get(user.guild.members, name=username)
        embed = discord.Embed(
	        colour = wt.roles[0].colour
        )

        print(wt)
        daysAgo = datetime.utcnow()-wt.created_at
        daysAgoServer = datetime.utcnow()-wt.joined_at

        embed.set_author(name=str(wt)+" - "+str(wt.name))
        embed.add_field(name="**Joined Discord On:**", value=str(wt.created_at)+" ("+str(daysAgo.days)+" days ago)", inline=False)
        embed.add_field(name="**Joined Server On:**", value=str(wt.joined_at)+" ("+str(daysAgoServer.days)+" days ago)", inline=False)
        embed.add_field(name="**Roles:**", value=str(", ".join(str(x.name) for x in wt.roles)), inline=False)

        message = await ctx.message.channel.send(embed=embed)

    @commands.command(pass_context=True)
    async def addroles(self, ctx, *roleNames):

        user = ctx.message.author
        permissions = user.permissions_in(ctx.message.channel)
        if (not permissions.administrator and not permissions.manage_guild):
            await ctx.message.channel.send("Sorry, you don't have permission to create assignable roles.")
        else:
            for roleName in roleNames:
                # Create Role
                role = discord.utils.get(user.guild.roles, name=str(roleName))
                if role:
                    if not (user.guild.name in self.roleServers):
                        self.roleServers[user.guild.name] = []
                    self.roleServers[user.guild.name].append(roleName)
                    await ctx.message.channel.send("**{}** is now assignable!".format(roleName), delete_after=5)
                else:
                    await ctx.message.channel.send("Sorry, the role {} needs to exist already to add to the list.".format(roleName), delete_after=5)
        self.saveToFile()
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def removeroles(self, ctx, *roleNames):
        user = ctx.message.author
        permissions = user.permissions_in(ctx.message.channel)
        if (not permissions.administrator and not permissions.manage_guild):
            await ctx.message.channel.send("Sorry, you don't have permission to remove assignable roles.")
        else:
            # Remove Role 
            x = 0
            for x in range(0, len(self.roleServers[user.guild.name])):
                if self.roleServers[user.guild.name][x] in roleNames:
                    self.roleServers[user.guild.name].pop(x)
                    await ctx.message.channel.send("Role is not assignable anymore.", delete_after=5)
                    self.saveToFile()
                    return


    @commands.command(pass_context=True)
    async def role(self, ctx, roleName):
        user = ctx.message.author
        if user.guild.name in self.roleServers:
            if str(roleName) in self.roleServers[user.guild.name]:
                role = discord.utils.get(user.guild.roles, name=str(roleName).lower())
                if role in user.roles:
                    await user.remove_roles(role)
                    await ctx.message.channel.send("Removed {} from {}.".format(roleName, user.name))
                else:
                    await user.add_roles(role)
                    await ctx.message.channel.send("Assigned {} to {}.".format(roleName, user.name))

    @commands.command(pass_context=True)
    async def colorme(self, ctx, colorCode):
        try:
            # convert color to hex
            hex_str = "0x" + str(colorCode).replace("#", "")
            hex_int = int(hex_str, 16)
            new_int = hex_int + 0x200

            user = ctx.message.author
            role = discord.utils.get(user.guild.roles, name=str(ctx.message.author)+"ColorMe")
            roleE = discord.utils.get(user.guild.roles, name="@everyone")
            if role:
                await role.edit(colour=discord.Colour(new_int), permissions=roleE.permissions)
                await user.add_roles(role)
            else:
                await ctx.message.guild.create_role(name=str(ctx.message.author)+"ColorMe", colour=discord.Colour(new_int))
                await user.add_roles(role)
        except:
            await ctx.message.channel.send("Sorry. I either don't have permission, or that is not a proper color.")

    @commands.command(pass_context=True)
    async def avatar(self, ctx):
        users = []
        if len(ctx.message.mentions) > 0:
            users = ctx.message.mentions
        else:
            users.append(discord.utils.get(ctx.message.guild.members, name=str(ctx.message.content).replace("!avatar ", "").strip())) 

        for user in users:
            url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(user)
            embed = discord.Embed(colour=discord.Colour.blue())
            embed.set_image(url=url)
            print(ctx.message.author)
            await ctx.message.channel.send(embed=embed)

    def saveToFile(self):
        with open('RoleDef.json', 'w') as outfile:  
            json.dump(self.roleServers, outfile)

def setup(client):
	client.add_cog(UserManagement(client))
