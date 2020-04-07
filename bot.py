import datetime
import json

import requests
import random

import discord
from discord.ext import commands
from discord.utils import get

with open("secret.txt", 'r') as s:
    lines = s.readlines()
    TOKEN = lines[0].strip('\n')
    ID = lines[1].strip('\n')
    GOOGLE_TOKEN = lines[2].strip('\n')

bot = commands.Bot(command_prefix='$')


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!!")


@bot.command()
async def off_wiesel(ctx):
    file = discord.File("wiesel.jpg")
    await ctx.send("", file=file)


@bot.command()
async def wiesel(ctx):

    with open('google_stuff.json', 'r') as f:
        data = json.load(f)

    needed = data[0]
    if needed[0] != datetime.datetime.today().strftime('%d'):
        needed[1] = 0
        needed[0] = datetime.datetime.today().strftime('%d')
        data[0] = needed
        with open('google_stuff.json', 'w+') as f:
            f.write(json.dumps(data))

    elif int(needed[1]) == 100:
        await off_wiesel(ctx)
        return

    else:
        num = int(data[0][1])
        num += 1
        data[0][1] = num
        with open('google_stuff.json', 'w+') as f:
            f.write(json.dumps(data))

    head = {'Accept': 'application/json'}
    r = requests.get(
        'https://customsearch.googleapis.com/customsearch/v1?cx={}&q=weasel&searchType=image&key={}'.format(
            ID, GOOGLE_TOKEN), headers=head)

    result = json.loads(r.text)
    items = result['items']

    chosen = items[random.randint(0, len(items) - 1)]
    link = chosen['link']
    r = requests.get(link)

    for key in r.headers.keys():

        if key.lower() == 'content-type':
            ext = r.headers[key]
            ext = ext.split('/')[1]

            with open('tmp.{}'.format(ext), 'wb') as p:
                p.write(r.content)

            pic = discord.File('tmp.{}'.format(ext))
            await ctx.send(file=pic)
            break


@bot.command()
async def quote(ctx, _quote, time=None):
    if time is None:
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
    with open('quotes.txt', 'a') as q:
        q.write(_quote + '/' + time + '\n')

    await ctx.send("Quote saved")


@bot.command()
async def clear(ctx, amount=100):
    for role in ctx.author.roles:

        if role == "Moderator" or discord.ext.commands.has_permissions(administrator=True):
            await ctx.channel.purge(limit=amount)
            await ctx.send("Channel cleared")
            return


@bot.command()
async def show_quotes(ctx):
    with open('quotes.txt') as f:
        lines = f.readlines()
        line_string = "".join(lines)
        await ctx.send(line_string)


@bot.command()
async def ban(ctx, _):
    await ctx.message.delete()
    if "Moderator" in ctx.author.roles or discord.ext.commands.has_permissions(administrator=True):
        user = ctx.message.mentions[0]
        _id = user.id
        roles = user.roles
        unremoveable = [635131535997141004, 635129654029713448, 635129654029713448, 635119155414302731]

        with open('roles.json', 'r') as r:
            try:
                data = json.load(r)
            except json.decoder.JSONDecodeError:
                data = {}

        with open('roles.json', 'w+') as r:
            data[_id] = [role.id for role in roles if role.id not in unremoveable]
            r.write(json.dumps(data))

        for role in roles:
            if role.id not in unremoveable:
                await user.remove_roles(role)

        await user.add_roles([role for role in ctx.guild.roles if role.id == 690519972123770880][0])
        await ctx.send("I brought {}, where he belongs".format(user.mention))


@bot.command()
async def unban(ctx, _):
    await ctx.message.delete()
    if "Moderator" in ctx.author.roles or discord.ext.commands.has_permissions(administrator=True):
        user = ctx.message.mentions[0]
        _id = user.id
        with open('roles.json', 'r') as r:
            data = json.load(r)

        roles = data[str(_id)]
        for role_id in roles:
            await user.add_roles(get(ctx.guild.roles, id=role_id))

        await user.remove_roles(get(ctx.guild.roles, id=690519972123770880))

        del data[str(_id)]
        with open('roles.json', 'w+') as r:
            r.write(json.dumps(data))


@bot.command()
async def create_event(ctx, name, date, people):

    ev = (name, date, people, ctx.author.id)

    with open('events.json', 'r') as d:
        data = json.load(d)

    data.append(ev)

    with open('events.json', 'w+') as e:
        e.write(data)


@bot.event
async def on_ready():
    print("Bot ready")


def check_files():
    try:
        with open("quotes.txt", 'r'):
            pass

    except FileNotFoundError:
        with open('quotes.txt', 'w+'):
            pass

    try:
        with open("roles.json", 'r'):
            pass

    except FileNotFoundError:
        with open('roles.json', 'w+') as r:
            r.write(json.dumps({}))

    try:
        with open('google_stuff.json', 'r'):
            pass
    except FileNotFoundError:
        with open('google_stuff.json', 'w+') as r:
            con = [[datetime.datetime.today().strftime('%d'), 0]]
            r.write(json.dumps(con))

    try:
        with open('events.json', 'r'):
            pass
    except FileNotFoundError:
        with open('events.json', 'w+') as e:
            con = []
            e.write(json.dumps(con))


if __name__ == "__main__":
    check_files()
    bot.run(TOKEN)
