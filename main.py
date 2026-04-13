import os
import discord
import json
import random
import yt_dlp
import asyncio
from pathlib import Path
from discord import client
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv

def select_random_file_pathlib(folder_path_str):
    folder_path = Path(folder_path_str)
    
    files = [file for file in folder_path.iterdir() if file.is_file()]

    arquivo_selecionado = random.choice(files)
    
    return arquivo_selecionado

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

#opcoes do player de video
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn', 
}


#contador do json
COUNTER_CALL = "contador.json"

def load_counter():
    if os.path.exists(COUNTER_CALL):
        with open(COUNTER_CALL, "r") as f:
            return json.load(f)
    return {"count": 0}
def save_counter(data):
    with open(COUNTER_CALL, "w") as f:
        json.dump(data, f, indent=2)

def increment(name="default", amount=1):
    data = load_counter()
    data[name] = data.get(name, 0) + amount
    save_counter(data)
    return data[name]


GUILDS = [
    discord.Object(id=847631525352701962),
    discord.Object(id=865599468040749058),
]

@bot.event
async def on_ready():
    try:
        for guild in GUILDS:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to {guild.id}")
    except Exception as e:
        print(e)
    print(f"WE NEED TO CLANK, {bot.user.name}")

#contador do dollylinho e ghost
@bot.event
async def on_voice_state_update(member, before, after):
  #sair da call quando estiver vazia
  if before.channel:
        vc = discord.utils.get(bot.voice_clients, guild=member.guild)
        if vc and vc.channel == before.channel:
            human_members = [m for m in before.channel.members if not m.bot]
            if len(human_members) == 0:
                await vc.disconnect()
                
  #toca um audio quando o dolly entra na call e incrementa dolly join
  if not before.channel and after.channel and member.id == 377958153494724618:
    channel = bot.get_channel(865599468954058755)
    vc = await after.channel.connect()
    vc.play(discord.FFmpegPCMAudio('biguy.mp3'), after=lambda e: print('done'))
    increment("dolly_join")
    
  if after.self_mute and member.id == 377958153494724618:
    channel = bot.get_channel(865599468954058755)
    increment("dolly_mute")

  #saidas do ghost
  if before.channel and not after.channel and member.id == 933503403601055804:
    channel = bot.get_channel(865599468954058755)
    increment("ghost_leave")


#troca de perfil do conductor e baunilha
@bot.event
async def on_user_update(before, after):
    if before.avatar != after.avatar and before.id == 727999395282550784:
        increment("troca_de_pfp_do_Conductor")
    elif before.avatar != after.avatar and before.id == 1078041787404402789:
        increment("troca_de_pfp_do_Baunilha")


@bot.tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id == 727999395282550784:
        await bot.tree.sync()
        await interaction.response.send_message('Synced Successfully')
    else:
        await interaction.response.send_message('You must be the owner to use this command!')


@bot.tree.command(name="dolly", description="Quantas vezes o dolly entrou/se mutou na call")
async def dollynator(interaction: discord.Interaction):
   with open('contador.json', 'r') as file_object:
    data = json.load(file_object)

   embed = discord.Embed(title = "Status do dolly")
   embed.add_field(name="Entradas na call", value=str(data['dolly_join']), inline=False)
   embed.add_field(name="Vezes mutado", value=str(data['dolly_mute']), inline=False)
   await interaction.response.send_message(embed=embed)


@bot.tree.command(name="troca_de_pfps", description="Do Conductor e Baunilha")
async def dollynator(interaction: discord.Interaction):
   with open('contador.json', 'r') as file_object:
    data = json.load(file_object)

   embed = discord.Embed(title = "Status dos Baunilha e Conductor")
   embed.add_field(name="Troca de pfp do Baunilha", value=str(data['troca_de_pfp_do_Baunilha']), inline=False)
   embed.add_field(name="Troca de pfp do Conductor", value=str(data['troca_de_pfp_do_Conductor']), inline=False)
   await interaction.response.send_message(embed=embed)


@bot.tree.command(name="saidas_do_ghost", description="Vezes que o ghost saiu da call")
async def dollynator(interaction: discord.Interaction):
   with open('contador.json', 'r') as file_object:
    data = json.load(file_object)

   embed = discord.Embed(title = "Status do ghost")
   embed.add_field(name="Saidas", value=str(data['ghost_leave']), inline=False)
   await interaction.response.send_message(embed=embed) 


#pastas do randomizador
FOLDERS = [
    ("imagens_Comum",    55),  
    ("imagens_Incomum",  37),  
    ("imagens_Raro",      7),
    ("imagens_Epico",  3),
    ("imagens_Lendario",  1),
    ("imagens_Mitico",  0.1),
]


#gambling machine
@bot.tree.command(name="random", description="Manda uma imagem de uma dm aleatoria (com raridade)")
@app_commands.checks.cooldown(1, 1)
async def randomizer(interaction: discord.Interaction):
   folders, weights = zip(*FOLDERS)
   folder = random.choices(folders, weights=weights, k=1)[0]
   arquivo_selecionado = select_random_file_pathlib(folder)
   file = discord.File(arquivo_selecionado, filename = "image.png")
   embed = discord.Embed(title = folder.replace("imagens_",""))
   embed.set_image(url = 'attachment://image.png')
   await interaction.response.send_message(embed=embed, file=file)


#tocar musica
@bot.tree.command(name="tocar", description="Toca uma musica na call apos prover um link do youtube, /kill para parar a musica")
@app_commands.describe(url="Link do youtube")
async def tocar(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Entre em uma chamada primeiro!", ephemeral=True)
        return

    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client

    if vc is None:
        vc = await voice_channel.connect()
    elif vc.channel != voice_channel:
        await vc.move_to(voice_channel)

    if vc.is_playing():
        vc.stop()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        title = info.get('title', 'Unknown')

    source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
    vc.play(source)

    await interaction.followup.send(f"Tocando agora: **{title}**")

#tira o bot da call
@bot.tree.command(name="kill", description="Parar a musica de /tocar")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Musica parada e disconectado")
    else:
        await interaction.response.send_message("Não estou tocando nenhuma musica!.", ephemeral=True)



@randomizer.error
async def randomizer_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message("Commando em cooldown espere 1 segundo", ephemeral=True)




bot.run(token, log_handler=handler, log_level=logging.DEBUG)