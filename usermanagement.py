import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus
import requests
import json

class UserManagement:
    def __init__(self, client):
        self.client = client
        self.roleServers = {}
        with open("RoleDef.json", "a+") as f:
            self.roleServers = json.load(f)

    @commands.command(pass_context=True)
    async def createrole(self, ctx, roleName):
        user = ctx.message.author
        permissions = user.permissions_in(ctx.message.channel)
        if (not permissions.administrator):
            await ctx.message.channel.send("Sorry, you don't have permission to create assignable roles.")
        else:
            # Create Role
            role = discord.utils.get(user.guild.roles, name=str(roleName))
            if role:
                if not (user.guild.name in self.roleServers):
                    self.roleServers[user.guild.name] = []
                self.roleServers[user.guild.name].append(roleName)
                await ctx.message.channel.send("**{}** is now assignable!".format(roleName), delete_after=5)
            else:
                await ctx.message.channel.send("Sorry, the role needs to exist already to add to the list.", delete_after=5)
        self.saveToFile()

    @commands.command(pass_context=True)
    async def removerole(self, ctx, roleName):
        user = ctx.message.author
        permissions = user.permissions_in(ctx.message.channel)
        if (not permissions.administrator):
            await ctx.message.channel.send("Sorry, you don't have permission to create assignable roles.")
        else:
            # Remove Role 
            x = 0
            for x in range(0, len(self.roleServers[user.guild.name])):
                if self.roleServers[user.guild.name][x] == roleName:
                    self.roleServers[user.guild.name].pop(x)
                    await ctx.message.channel.send("Role is not assignable anymore, you might want to delete it.", delete_after=5)
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
        author = ctx.message.author
        try:
            # convert color to hex
            hex_str = "0x" + str(colorCode).replace("#", "")
            hex_int = int(hex_str, 16)
            new_int = hex_int + 0x200

            user = ctx.message.author
            role = discord.utils.get(user.server.roles, name=str(ctx.message.author)+"ColorMe")
            if role:
                role.colour = discord.Colour(new_int)
                await self.client.edit_role(author.server, role, colour=discord.Colour(new_int))
                await self.client.add_roles(user, role)
            else:
                await self.client.create_role(author.server, name=str(ctx.message.author)+"ColorMe", colour=discord.Colour(new_int))
                await self.client.add_roles(user, role)
        except:
            await ctx.message.channel.send("Sorry. I either don't have permission, or that is not a proper color.")

    @commands.command(pass_context=True)
    async def avatar(self, ctx):
        for user in ctx.message.mentions:
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
