import discord
from discord.ext import commands

TOKEN = 'NjkyNDYyMDMzMzk1Nzc3NTY2.Xnu8sQ.nX0UH4jhZrO-nNT9p6gRuCy-I7M'
bot = commands.Bot(command_prefix='$')

@bot.command()
async def ping(ctx):
     await ctx.send("Pong!!")

@bot.command()
async def wiesel(ctx):

    with open('wiesel.jpg', 'r') as f:
        file = discord.File("wiesel.jpg")
        await ctx.send("", file=file)

@bot.event
async def on_ready():
    print("Bot ready")


if __name__ == "__main__":
    bot.run(TOKEN)
