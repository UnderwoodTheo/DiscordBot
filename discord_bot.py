import asyncio
import discord
import main
from discord.ext import commands
import re
from dotenv import load_dotenv
import os
import numpy as np
import time
import requests

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Bot is ready')

@bot.command('p')
async def activePlayers(ctx):
    rep = requests.get('https://euw1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key=RGAPI-f01061d4-1004-4cc4-8270-1f1a56fe560b')
    data = rep.json()['entries']
    for i in range(len(data)):
        if data[i]['summonerName'] == 'F9 Wayzix':
            index = i 
    filtered = data[index-50:index+49]
    c = 0
    for p in filtered:
        game = requests.get(f'https://euw1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{p["summonerId"]}?api_key=RGAPI-f01061d4-1004-4cc4-8270-1f1a56fe560b')
        if 'gameId' in game.json().keys():
            c += 1
    await ctx.send(c)
    time.sleep(120)
    return await activePlayers(ctx)

@bot.command('cmds')
async def help(ctx):
    embed = discord.Embed(title='Commands', description="Here are the commands I can answer to. If one of them does not work, it's probably that the api key is not valid anymore. Ask the boss to update it.", color=discord.Color.green())
    embed.set_thumbnail(url='https://www.mobafire.com/images/champion/square/singed.png')
    embed.add_field(name='Available every time', value='.', inline=False)
    embed.add_field(name='!champ <championName>', value='Details about any champion', inline=False)
    embed.add_field(name='!champions', value='List available champions by role', inline=False)
    embed.add_field(name='!cmds', value='List the commands', inline=False)
    embed.add_field(name='!hello', value='Greet me', inline=False)   
    embed.add_field(name='!items', value='List in-game items by id, then pick one for more details', inline=False)
    embed.add_field(name='!ranks', value='Ranks you can reach in ranked games', inline=False)
    embed.add_field(name='!summonerSpells', value='Details about a specific summoner spell', inline=False)
    embed.add_field(name='!version', value='Current version', inline=False)
    embed.add_field(name='Requiring the api key to be valid', value='.', inline=False)
    embed.add_field(name='!chest <championName>', value='Know if a chest is granted on a champion', inline=False)
    embed.add_field(name='!history <summonerName>', value='Last 3 games of a player', inline=False)
    embed.add_field(name='!status', value='Know if there are issues of the server', inline=False)
    embed.add_field(name='!summoner <summonerName>', value='Profile of a player', inline=False)
    embed.add_field(name='!weekly', value='List weekly free champions', inline=False)
    await ctx.send(embed=embed)

@bot.command('hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}')

@bot.command('champ')
async def champ(ctx, champ: str):  
    champ = ctx.message.content.split()[1:]
    new_str_champ = " ".join(champ)
    champion_info = main.getChampFromMongo(new_str_champ)

    embed=discord.Embed(title=champion_info['name'], url=champion_info['link'], description=champion_info['title'], color=discord.Color.green())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=champion_info['image'])
    for r in range(len(champion_info['role'])):
        embed.add_field(name=f'Role {r+1}', value=champion_info['role'][r], inline=True)  
    embed.add_field(name='Lore', value=champion_info['lore'], inline=False)

    embedPassive=discord.Embed(title="Passive", color=discord.Color.green())
    embedPassive.set_thumbnail(url=champion_info['spells']['passive']['image'])
    embedPassive.add_field(name=champion_info['spells']['passive']['name'], value=champion_info['spells']['passive']['description'])

    embedQ=discord.Embed(title="Q", color=discord.Color.green())
    embedQ.set_thumbnail(url=champion_info['spells']['Q']['image'])
    embedQ.add_field(name=champion_info['spells']['Q']['name'], value=champion_info['spells']['Q']['description'])
    embedQ.add_field(name='Cooldowns', value=champion_info['spells']['Q']['cooldownBurn'])
    embedQ.add_field(name='Cost', value=champion_info['spells']['Q']['costBurn'])
    
    embedW=discord.Embed(title="W", color=discord.Color.green())
    embedW.set_thumbnail(url=champion_info['spells']['W']['image'])
    embedW.add_field(name=champion_info['spells']['W']['name'], value=champion_info['spells']['W']['description'])
    embedW.add_field(name='Cooldowns', value=champion_info['spells']['W']['cooldownBurn'])
    embedW.add_field(name='Cost', value=champion_info['spells']['W']['costBurn'])

    embedE=discord.Embed(title="E", color=discord.Color.green())
    embedE.set_thumbnail(url=champion_info['spells']['E']['image'])
    embedE.add_field(name=champion_info['spells']['E']['name'], value=champion_info['spells']['E']['description'])
    embedE.add_field(name='Cooldowns', value=champion_info['spells']['E']['cooldownBurn'])
    embedE.add_field(name='Cost', value=champion_info['spells']['E']['costBurn'])

    embedR=discord.Embed(title="R", color=discord.Color.green())
    embedR.set_thumbnail(url=champion_info['spells']['R']['image'])
    embedR.add_field(name=champion_info['spells']['R']['name'], value=champion_info['spells']['R']['description'])
    embedR.add_field(name='Cooldowns', value=champion_info['spells']['R']['cooldownBurn'])
    embedR.add_field(name='Cost', value=champion_info['spells']['R']['costBurn'])

    await ctx.send(embed=embed)
    await ctx.send(embed=embedPassive)
    await ctx.send(embed=embedQ)
    await ctx.send(embed=embedW)
    await ctx.send(embed=embedE)
    await ctx.send(embed=embedR)

@bot.command('summoner')
async def summoner(ctx, name: str):
    try:
        name = ctx.message.content.split()[1:]
        new_str_name= " ".join(name)
        summoner = main.summonerByName(new_str_name)
        id = summoner['id']
        icon = summoner['profileIconId']
        mastery_score = main.masteryScore(id)
    
        embed = discord.Embed(title=new_str_name, url=f'https://euw.op.gg/summoners/euw/{new_str_name.replace(" ", "%20")}', color=discord.Color.green())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/12.5.1/img/profileicon/{icon}.png')
        embed.add_field(name='Summoner level', value=summoner['summonerLevel'], inline=False)  
        embed.add_field(name='Mastery score', value=mastery_score, inline=False)
        await ctx.send(embed=embed)

        ranks = main.rank(id)

        if len(ranks) == 0:
            embedUnranked = discord.Embed(title='Unranked', color=discord.Color.green())
            embedUnranked.set_thumbnail(url='https://lolslaves.com/wp-content/uploads/2022/02/bitmap2132.png')
            await ctx.send(embed=embedUnranked)

        if len(ranks) == 1:
            ranks = ranks[0]
            emblem = main.emblemUrl(ranks['tier'])
            if re.search('solo', ranks['queueType'].lower()):
                embedRank = discord.Embed(title='Ranked Solo', description=f'{ranks["tier"]} {ranks["rank"]} - {ranks["leaguePoints"]} lp', color=discord.Color.green())
                embedRank.set_thumbnail(url=emblem)
                embedRank.add_field(name='Wins', value=ranks['wins'], inline=True)
                embedRank.add_field(name='Defeats', value=ranks['losses'], inline=True)
                embedRank.add_field(name='Winrate', value=f'{np.around(ranks["wins"]/(ranks["wins"]+ranks["losses"])*100, decimals=2)} %', inline=True)
            else:
                embedRank = discord.Embed(title='Ranked Flex', description=f'{ranks["tier"]} {ranks["rank"]} - {ranks["leaguePoints"]} lp', color=discord.Color.green())
                embedRank.set_thumbnail(url=emblem)
                embedRank.add_field(name='Wins', value=ranks['wins'], inline=True)
                embedRank.add_field(name='Defeats', value=ranks['losses'], inline=True)
                embedRank.add_field(name='Winrate', value=f'{np.around(ranks["wins"]/(ranks["wins"]+ranks["losses"])*100, decimals=2)} %', inline=True)
            await ctx.send(embed=embedRank)

        if len(ranks) == 2:
            if re.search('solo', ranks[0]['queueType'].lower()):
                solo = ranks[0]
                flex = ranks[1]
            else:
                solo = ranks[1]
                flex = ranks[0]
            solo_emblem = main.emblemUrl(solo['tier'])
            flex_emblem = main.emblemUrl(flex['tier'])

            embedSolo = discord.Embed(title='Ranked Solo', description=f'{solo["tier"]} {solo["rank"]} - {solo["leaguePoints"]} lp', color=discord.Color.green())
            embedSolo.set_thumbnail(url=solo_emblem)
            embedSolo.add_field(name='Wins', value=solo['wins'], inline=True)
            embedSolo.add_field(name='Defeats', value=solo['losses'], inline=True)
            embedSolo.add_field(name='Winrate', value=f'{np.around(solo["wins"]/(solo["wins"]+solo["losses"])*100, decimals=2)} %', inline=True)

            embedFlex = discord.Embed(title='Ranked Flex', description=f'{flex["tier"]} {flex["rank"]} - {flex["leaguePoints"]} lp', color=discord.Color.green())
            embedFlex.set_thumbnail(url=flex_emblem)
            embedFlex.add_field(name='Wins', value=flex['wins'], inline=True)
            embedFlex.add_field(name='Defeats', value=flex['losses'], inline=True)
            embedFlex.add_field(name='Winrate', value=f'{np.around(flex["wins"]/(flex["wins"]+flex["losses"])*100, decimals=2)} %', inline=True)

            await ctx.send(embed=embedSolo)
            await ctx.send(embed=embedFlex)

        top_played = main.mostPlayed(new_str_name)
        embedMasteries = discord.Embed(title='Most Played', color=discord.Color.green())
        embedMasteries.set_thumbnail(url='https://dragon.championmastery.gg/img/masteryIcon.png')
        for c in top_played:
            embedMasteries.add_field(name=c[0], value=f'{c[1]} pts')
        await ctx.send(embed=embedMasteries)
    except:
        await ctx.send('This summoner does not exist or the boss needs to update the API key')

@bot.command('status')
async def status(ctx):
    status = main.status()
    if len(status.split()) == 2:
        await ctx.send('Nothing to report')
    else:
        await ctx.send(status)

@bot.command('version')
async def version(ctx):
    version = main.currentVersion()
    embed = discord.Embed(title='Current version', description=version, color=discord.Color.green())
    embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/LoL_icon.svg/1200px-LoL_icon.svg.png')
    await ctx.send(embed=embed)

@bot.command('champions')
async def allChampsByRole(ctx):
    champs = main.champsByRole()
    images = ['https://static.wikia.nocookie.net/leagueoflegends/images/2/28/Slayer_icon.png/revision/latest/scale-to-width-down/200?cb=20181117143556', 
    'https://static.wikia.nocookie.net/leagueoflegends/images/8/8f/Fighter_icon.png/revision/latest/scale-to-width-down/200?cb=20181117143554', 
    'https://static.wikia.nocookie.net/leagueoflegends/images/2/28/Mage_icon.png/revision/latest/scale-to-width-down/200?cb=20181117143555',
    'https://static.wikia.nocookie.net/leagueoflegends/images/7/7f/Marksman_icon.png/revision/latest/scale-to-width-down/200?cb=20181117143555',
    'https://static.wikia.nocookie.net/leagueoflegends/images/5/58/Controller_icon.png/revision/latest/scale-to-width-down/200?cb=20181117143552',
    'https://static.wikia.nocookie.net/leagueoflegends/images/5/5a/Tank_icon.png/revision/latest/scale-to-width-down/200?cb=20181117143558']
    for c, (k, v) in enumerate(champs.items()):
        embed = discord.Embed(title=k, description=', '.join(v), color=discord.Color.green())
        embed.set_thumbnail(url=images[c])
        await ctx.send(embed=embed)

@bot.command('weekly')
async def weeklyChamps(ctx):
    free_champs_ids = main.freeChampions()
    champ_list = [main.getChampByIdMongo(i)['name'] for i in free_champs_ids]
    embed = discord.Embed(title='Weekly free champions', description=', '.join(champ_list), color=discord.Color.green())
    embed.set_thumbnail(url='https://opgg-static.akamaized.net/images/profile_icons/profileIcon29.jpg')
    await ctx.send(embed=embed)

@bot.command('chest')
async def chest(ctx, champ_name):
    champ_name = ctx.message.content.split()[1:]
    new_champ_name= " ".join(champ_name)
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    await ctx.send('Enter summoner name')
    try:
        msg = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send('You did not reply in time')
    summoner_name = msg.content
    granted = main.isChestGranted(summoner_name, new_champ_name)
    result = 'granted' if granted else 'not granted'
    embed = discord.Embed(description=f'Chest {result} for {new_champ_name}', color=discord.Color.green())
    embed.set_thumbnail(url='https://static.wikia.nocookie.net/leagueoflegends/images/6/60/Hextech_Crafting_Chest.png/revision/latest/scale-to-width-down/250?cb=20191203123712')
    await ctx.send(embed=embed)

@bot.command('ranks')
async def ranks(ctx):
    embed = discord.Embed(title='Ranks', color=discord.Color.green())
    embed.set_image(url='https://leaguefeed.net/wp-content/uploads/2022/01/mmr-lol-1024x470.jpg')
    await ctx.send(embed=embed)

@bot.command('summonerSpells')
async def summonerSpells(ctx):
    spells = main.summonerSpells()
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    await ctx.send('Enter a summoner spell')
    try:
        msg = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send('You did not reply in time')
    msg = msg.content.lower()
    spell = dict()
    for s in spells:
        if s['name'].lower() == msg:
            spell = s
    embed = discord.Embed(title=spell['name'], description=spell['description'], color=discord.Color.green())
    embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/12.5.1/img/spell/{spell["id"]}.png')
    embed.add_field(name='Cooldown', value=spell['cooldownBurn'])
    await ctx.send(embed=embed)

@bot.command('items')
async def items(ctx):
    all_items = sorted(main.getItems(), key=lambda x: x['name'])
    items_list = []
    for i in all_items:
        items_list.append(f'{i["name"]}: {i["_id"]}')
    items_str = '\n'.join(items_list)
    items1 = items_str[:4089]
    items2 = items_str[4089:]
    embedItems1 = discord.Embed(title='Items', description=items1, color=discord.Color.green())
    embedItems1.set_thumbnail(url='https://static.wikia.nocookie.net/leagueoflegends/images/1/10/Gold.png/revision/latest/scale-to-width-down/20?cb=20181122055358')
    embedItems2 = discord.Embed(description=items2, color=discord.Color.green())
    await ctx.send(embed=embedItems1)
    await ctx.send(embed=embedItems2)

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    await ctx.send('Enter an item id')
    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
    except asyncio.TimeoutError:
        await ctx.send('You did not reply in time')
    id = int(msg.content)
    item = main.getItemFromMongo(id)
    embedItem = discord.Embed(title=item['name'], description=item['description'], color=discord.Color.green())
    embedItem.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/12.5.1/img/item/{item["_id"]}.png')
    embedItem.add_field(name='Purchasable', value=item['gold']['purchasable'], inline=True)
    embedItem.add_field(name='Purchase', value=item['gold']['total'], inline=True)
    embedItem.add_field(name='Sale', value=item['gold']['sell'], inline=True)
    embedItem.add_field(name='Type', value=", ".join(item['tags']), inline=False)
    embedItem.add_field(name='Stats', value=", ".join(item['stats']), inline=True)
    if 'from' in item.keys():
        embedItem.add_field(name='Items needed', value=", ".join(map(str, item['from'])),inline=False)
    if 'into' in item.keys():
        embedItem.add_field(name='Items needing it', value=', '.join(map(str, item['into'])),inline=True)
    await ctx.send(embed=embedItem)

@bot.command("history")
async def history(ctx, summonerName):
    summonerName = ctx.message.content.split()[1:]
    new_summoner_name = " ".join(summonerName)
    games = main.history(new_summoner_name)
    embed = discord.Embed(title='History', url=f'https://euw.op.gg/summoners/euw/{new_summoner_name.replace(" ", "%20")}', description=f'3 last games of {new_summoner_name}', color=discord.Color.green())
    await ctx.send(embed=embed)
    for g in games:
        mapName = main.getMap(g['mapId'])
        spell1 = main.getSpell(g['summoner1Id'])
        spell2 = main.getSpell(g['summoner2Id'])
        win = "Victory" if g['win'] else "Defeat"
        embedGame = discord.Embed(title=win, description=f'{mapName} {g["gameType"]}', color=discord.Color.green())
        champ_img = main.getChampByIdMongo(g['championId'])['image']
        embedGame.set_thumbnail(url=champ_img)
        embedGame.add_field(name='Kills', value=g['kills'], inline=True)
        embedGame.add_field(name='Deaths', value=g['deaths'], inline=True)
        embedGame.add_field(name='Assists', value=g['assists'], inline=True)
        embedGame.add_field(name="Lane", value=g['lane'], inline=True)
        embedGame.add_field(name="Champion", value=g['championName'], inline=True)
        embedGame.add_field(name="Damage", value=g['totalDamageDealtToChampions'], inline=True)
        embedGame.add_field(name="CS", value=g['totalMinionsKilled'], inline=True)
        embedGame.add_field(name="Game duration", value=g['duration'], inline=True)
        embedGame.add_field(name="Time dead", value=g['totalTimeSpentDead'], inline=True)
        embedGame.add_field(name="Summoner spell 1", value=spell1, inline=True)
        embedGame.add_field(name="Summoner spell 2", value=spell2, inline=True)
        await ctx.send(embed=embedGame)

load_dotenv(dotenv_path='config')
bot.run(os.getenv('TOKEN'))