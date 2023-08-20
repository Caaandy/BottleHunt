# This example requires the 'message_content' intent.

import discord
from dataclasses import dataclass
from strsimpy.jaro_winkler import JaroWinkler
import yaml

global client, guild, roles, roleDict

configFile = open("config.yaml", 'r')
config = yaml.load(configFile)

jarowinkler = JaroWinkler()

token = config['BOT']['TOKEN']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    guild = await client.fetch_guild(1138386909199081562)
    roles = guild.roles
    roleDict = {}

    for role in roles:
        roleDict[role.name] = role


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #if message.content.startswith('$hello'):
    #    await message.channel.send('Hello!')

    if message.channel.id == 1142794606673674320:
        similarity = jarowinkler.similarity(config['Puzzle1']['ANTWORT1'], message.content.lower())
        if similarity == 1:
            await message.channel.send(f'{message.content} ist richtig!')
        elif similarity >= 0.95:
            await message.channel.send(f'{message.content} ist nah dran!')
        else:
            await message.channel.send(f'Deine Mudda ist {message.content}')

    #loki = await message.guild.fetch_member(165955907488972800)

client.run(token)

@dataclass
class TeamData:
    rolename: str
    teamname: str
    answerID: int
    questID: int
    currentPuzzle: int
    members: list[discord.Member]
