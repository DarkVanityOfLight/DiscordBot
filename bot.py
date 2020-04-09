import datetime
import json
import random
import os

import requests
import asyncio

import discord
from discord.ext import commands
from discord.utils import get

TOKEN = os.environ(['DISCORD_TOKE'])
ID = os.environ(['GOOGLE_CSE_ID'])
GOOGLE_TOKEN = os.environ(['GOOGLE_TOKEN'])

bot = commands.Bot(command_prefix='$')


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!!, the test data is {}".format(ctx.author))


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
        _lines = f.readlines()
        line_string = "".join(_lines)
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
    await ctx.guild.create_role(name=name)
    await ctx.author.add_roles(get(ctx.guild.roles, name=name))
    ev = (name, date, int(people), ctx.author.id, ctx.guild.id, ctx.channel.id)

    with open('events.json', 'r') as d:
        data = json.load(d)

    data.append(ev)

    with open('events.json', 'w+') as e:
        e.write(json.dumps(data))


@bot.command()
async def list_events(ctx):
    templ = "{} am {},\nFreie plätze: {},\nErstellt von {}\n\n"
    full = ""

    with open('events.json', 'r') as e:
        evs = json.load(e)

    for e in evs:
        user = get(ctx.guild.members, id=e[3])
        full += templ.format(e[0], e[1], e[2], user)

    await ctx.send(full)


@bot.command()
async def signup(ctx, name):
    with open('events.json', 'r') as e:
        evs = json.load(e)

    for itnum, ev in enumerate(evs):

        if ev[0].lower() == name.lower():
            role = get(ctx.guild.roles, name=name)
            if role not in ctx.author.roles:
                num = int(ev[2])
                if num - 1 > 0:
                    num += -1
                    await ctx.author.add_roles(role)
                    ev[2] = num
                    evs[itnum] = ev
                    with open('events.json', 'w+') as m:
                        m.write(json.dumps(evs))
                else:
                    await ctx.send("Sorry no more places are available")
            else:
                await ctx.send("You are already participating at the event")

        else:
            await ctx.send("The event {} is not available".format(name))


@bot.command()
async def end_event(ctx, name):
    with open('events.json', 'r') as e:
        data = json.load(e)

    for event in data:
        if event[0].lower() == name.lower():
            if event[3] == ctx.author.id:
                _delete_event(name)
                await get(ctx.guild.roles, name=name).delete()


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


def _delete_event(name):
    with open('events.json', 'r') as e:
        data = json.load(e)

    new_data = [event for event in data if event[0] != name]

    with open('events.json', 'w+') as e:
        e.write(json.dumps(new_data))


async def loop():
    await asyncio.sleep(5)
    while True:
        now = datetime.datetime.now()
        with open('events.json', 'r') as e:
            data = json.load(e)

        for ev in data:
            if datetime.datetime.strptime(ev[1], '%d-%m-%y/%H') <= now:
                guild = bot.get_guild(ev[4])
                channel = get(guild.channels, id=ev[5])
                role = get(guild.roles, name=ev[0])
                await channel.send('{} The event {} starts now'.format(role.mention, ev[0]))

        await asyncio.sleep(60 * 60 * 60 * 0.5)


if __name__ == "__main__":
    check_files()
    bot.loop.create_task(loop())
    bot.run(TOKEN)
