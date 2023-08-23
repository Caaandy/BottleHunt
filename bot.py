# This example requires the 'message_content' intent.

import discord
from dataclasses import dataclass
from strsimpy.levenshtein import Levenshtein
import yaml
from typing import List
from random import randint
import time
import math

configFile = open("config.yaml", 'r', encoding='UTF-8')
config = yaml.safe_load(configFile)
spruchFile = open("spruch.yaml", 'r', encoding='UTF-8')
spruch = yaml.safe_load(spruchFile)

simAlg = Levenshtein()

token = config['BOT']['TOKEN']

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

teamList = []


@dataclass
class TeamData:
    rolename: str
    timer: float
    answerID: int
    questID: int
    currentPuzzle: int
    members: list[int]

    def __init__(self, **kwargs):
        self.rolename = kwargs['rolename']
        self.timer = time.time()
        self.answerID = kwargs['answerID']
        self.questID = kwargs['questID']
        self.currentPuzzle = kwargs['currentPuzzle']
        self.members = kwargs['members']

    async def fetchMembers(self) -> List[discord.Member]:
        returnMembers = []
        for memberID in self.members:
            returnMembers.append(await guild.fetch_member(memberID))
        return returnMembers


@client.event
async def on_ready():
    global guild, roles, roleDict, teamList
    print(f'We have logged in as {client.user}')
    guild = await client.fetch_guild(1138386909199081562)
    roles = guild.roles
    roleDict = {}

    for role in roles:
        roleDict[role.name] = role

    for team in config['Teams']:
        teamList.append(TeamData(**team))

    # for team in teamList:
    #     channel = await guild.fetch_channel(team.questID)
    #     await channel.send('**Aufgabe 1 - Classic:**')
    #     await channel.send(config['AUFGABE1'])

@client.event
async def on_message(message):
    if message.author == client.user: #or message.author.id == 472509126010994689:
        return

    user = message.author

    # answerchannel ID vom team rausfinden
    userTeam = None
    for team in teamList:
        for member in await team.fetchMembers():
            if member == user:
                userTeam = team

    if message.channel.id == userTeam.answerID:
        await message.channel.typing()
        await switch(str(message.content), userTeam, message.channel)


async def switch(answer, userTeam, channel):
    puzzleNr = userTeam.currentPuzzle
    timer = userTeam.timer
    if puzzleNr != '10':
        distance = simAlg.distance(str(config['Puzzles']['ANTWORT' + str(puzzleNr)]), answer.lower())
        if distance == 0:
            await channel.send(f'{answer} ist richtig!')

            #timer
            minuten = math.floor((time.time() - timer) / 60)
            sekunden = round((time.time() - timer) % 60, 2)
            await channel.send(f'Zeit für Puzzle ' + str(puzzleNr) + ': ' + str(minuten) + ' Minuten ' + str(sekunden) + ' Sekunden')

            userTeam.currentPuzzle += 1

            # nächstes Puzzle schicken
            for aufgabe in config['AUFGABE' + str(userTeam.currentPuzzle)]:
                questChannel = await guild.fetch_channel(userTeam.questID)
                await questChannel.send(str(aufgabe))

            if userTeam.currentPuzzle == 6:
                #await channel.send(file=discord.File(r'C:\Users\phili\Pictures\0_PuzzleHunt\Audio.mp3'))
                # await channel.send(file=discord.File(r'C:\Users\phili\Pictures\0_PuzzleHunt\Text.docx'))
                await questChannel.send(file=discord.File(r'C:\Users\phili\Music\Youtube\Dune_OST_–_Main_Theme_Suite_ _Hans_Zimmer.mp3'))
                await questChannel.send(file=discord.File(r'C:\Users\phili\Documents\PnP\blood on the clocktower\bad-moon-rising.character-reference.pdf'))

            userTeam.timer = time.time()

        elif distance <= round(len(answer) * 0.2):
            await channel.send(f'{answer} ist nah dran!')
        else:
            if (puzzleNr == 5 and config['Zwischenantworten']['ZA5'] == answer.lower()) or (puzzleNr == 8 and config['Zwischenantworten']['ZA8'] == answer.lower()):
                await channel.send(f'Das ist korrekt, aber noch nicht ganz die Lösung...')
                return
            else:
                zufallszahl = randint(1, 24)
                await channel.send(spruch['SPRUCH'+ str(zufallszahl)].format(answer))


client.run(token)
