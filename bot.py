# This example requires the 'message_content' intent.

import discord
from dataclasses import dataclass
from strsimpy.cosine import Cosine
import yaml

configFile = open("config.yaml", 'r')
config = yaml.safe_load(configFile)

cosine = Cosine(2)

token = config['BOT']['TOKEN']

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

teamList = []

@dataclass
class TeamData:
    rolename: str
    teamname: str
    answerID: int
    questID: int
    currentPuzzle: int
    members: list[int]

    def __init__(self, **kwargs):
        self.rolename = kwargs['rolename']
        self.teamname = kwargs['teamname']
        self.answerID = kwargs['answerID']
        self.questID = kwargs['questID']
        self.currentPuzzle = kwargs['currentPuzzle']
        self.members = kwargs['members']

    async def fetchMembers(self) -> list[discord.Member]:
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


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user = message.author

    #answerchannel ID vom team rausfinden
    userTeam = None
    for team in teamList:
        for member in await team.fetchMembers():
            if member == user:
                userTeam = team

    if message.channel.id == userTeam.answerID:
        await switch(str(message.content), userTeam, message.channel)

async def switch(answer, userTeam, channel):
    puzzleNr = userTeam.currentPuzzle
    if puzzleNr != '10':
        similarity = cosine.similarity(str(config['Puzzles']['ANTWORT' + str(puzzleNr)]), answer.lower())
        if similarity == 1:
            await channel.send(f'{answer} ist richtig!')
            userTeam.currentPuzzle += 1
            #nächstes Puzzle schicken
        elif similarity >= 1:
            await channel.send(f'{answer} ist nah dran!')
            await channel.send(f'Wert: {similarity}')
        else:
            await channel.send(f'Deine Mudda ist {answer}')
            await channel.send(f'Wert: {similarity}')


client.run(token)



