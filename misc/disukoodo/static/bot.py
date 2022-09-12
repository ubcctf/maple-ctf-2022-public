import discord
from discord.ext import commands
from discord import utils, errors, channel, User

botmods = []
prem_users = []

intents = discord.Intents.default()
intents.dm_messages = True
bot = commands.Bot(command_prefix='\0', intents=intents) #disable internal command processor to allow customization

@bot.event
async def on_message(msg):
    #allow mentions anywhere in msg to facilitate more natural command invocations in conversations
    if isinstance(msg.channel, channel.DMChannel):   #blame discord 100 server limit for breaking realism :(
        split = msg.content.split(str(bot.user.id) + '> ', 1)
        if len(split) > 1 and any([m.id == bot.user.id for m in msg.mentions]): #has to be a real mention
            msg.content = '\0' + split[1]
        bot._skip_check = lambda x, y: False
        ctx = await bot.get_context(msg)
        await bot.invoke(ctx)

@bot.event
async def on_ready():
    global botmods
    info = await bot.application_info()
    botmods += [info.owner.id, info.id]

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have enough perms!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid arguments specified!')
    else:
        if isinstance(error, commands.errors.CommandInvokeError):
            error = error.original 

        await ctx.send('This command encountered an unexpected `' + str(type(error)) + '` error!')
        debuginfo = 'Debug info:\nCurrent command: `' + str(ctx.command) + '`\n'

        if isinstance(error, errors.HTTPException):   #something went wrong communicating with discord - give more backend info
            debuginfo += '\nBackend info:\nCurrently serving guilds:```\n' + '\n'.join([str(g.id) for g in bot.guilds]) + '```\nLatency: `' + str(bot.latency) + '`\n'
            
        await ctx.send(debuginfo)
        raise error


async def is_privileged(ctx):
    return ctx.author.id in botmods

async def is_prem(ctx):
    return ctx.author.id in prem_users


@bot.command(description='BOT MODS ONLY - manually sets a member as a premium member')
@commands.check(is_privileged)
async def registerprem(ctx, member: User):
    prem_users.append(member.id)
    await ctx.send('Manually added <@!' + str(member.id) + '> as a premium member!')

@bot.command(description='Echos a given message! Premium members gets a special secret feature ;)')
async def echo(ctx, *, msg):
    if len(msg) > 1990:
        await ctx.send('Sorry, your message to be echoed is too long!')
    else:
        val = msg.split(' ')[0]
        to_echo = (msg[len(val)+1:] * min(int(val), 100)) if await is_prem(ctx) and val.isdigit() else msg
        await ctx.send('`' + utils.escape_markdown(to_echo) + '`')


bot.run(open('token.txt').readlines()[0])