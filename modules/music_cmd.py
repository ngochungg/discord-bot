# Options cho yt-dlp để lấy audio stream URL
import asyncio
import os
import platform
import discord
import yt_dlp

from utils.check_text_type import is_url

# Config ytdl
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind IPv4
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
ffmpeg_options = {
    'options': '-vn'
}

music_queues = {}  # guild_id -> list of YTDLSource

# --- Config playing music from url or name ---
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # playlist, take first one
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# --- !play: playing music from url/text ---
async def play (ctx, *, message_text: str, loop=None):
    # Check input query
    query = ctx.content[len('!play'):].strip()
    if not query:
        await ctx.channel.send(f"❗ Please enter name or url after !play.")
        return

    # Check client voice chat
    if not ctx.author.voice:
        await ctx.channel.send(f"❗You need to be in a voice channel to use this command.")
        return

    # Config bot
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.guild.voice_client

    # Bot join voice if not ready yet
    if voice_client is None:
        try:
            voice_client = await voice_channel.connect()
        except Exception as e:
            await ctx.channel.send(f"❌ Failed to join voice channel: {e}")
            return
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    await ctx.channel.send(f"🔎 Searching: `{query}`...")

    # Check url or text
    if is_url(message_text):
        async with ctx.channel.typing():
            loop = loop or asyncio.get_event_loop()
            music_player = await YTDLSource.from_url(message_text, stream=True, loop=loop)

            # Load lib opus
            load_opus_lib()

            guild_id = ctx.guild.id
            if guild_id not in music_queues:
                music_queues[guild_id] = []

            if voice_client.is_playing():
                music_queues[guild_id].append(music_player.title)
                await ctx.channel.send(f"📥 Add to queue: {music_player.title}")
            else:
                voice_client.play(music_player, after=lambda e: play_next(ctx))
                await ctx.channel.send(f"🎶 Playing: {music_player.title}")
    else:
        async with ctx.channel.typing():
            loop = loop or asyncio.get_event_loop()
            music_player = await YTDLSource.from_url(query, stream=True, loop=loop)

            # Load lib opus
            load_opus_lib()

            guild_id = ctx.guild.id
            if guild_id not in music_queues:
                music_queues[guild_id] = []

            if voice_client.is_playing():
                music_queues[guild_id].append(music_player.title)
                await ctx.channel.send(f"📥 Add to queue: {music_player.title}")
            else:
                voice_client.play(music_player, after=lambda e: play_next(ctx))
                await ctx.channel.send(f"🎶 Playing: {music_player.title}")

async def skip(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # after callback sẽ tự gọi play_next
        await ctx.channel.send("⏭️ Skipped.")
    else:
        await ctx.channel.send("❗ No song is playing.")

async def show_queue(ctx):
    guild_id = ctx.guild.id
    queue = music_queues.get(guild_id, [])
    if not queue:
        await ctx.channel.send("📭 Empty queue.")
    else:
        msg = "\n".join([f"{idx+1}. {song.title}" for idx, song in enumerate(queue)])
        await ctx.channel.send(f"📜 Queue:\n{msg}")

# --- !stop ---
async def stop(ctx):
    # Config bot
    voice_client = ctx.guild.voice_client

    if voice_client:
        await voice_client.disconnect()
        await ctx.channel.send("🛑 Stop playing music and leave voice channel.")
    else:
        await ctx.channel.send("❗ Bot doesn't connect any voice channel.")

def play_next(ctx):
    guild_id = ctx.guild.id
    if music_queues.get(guild_id):
        next_song = music_queues[guild_id].pop(0)
        vc = ctx.guild.voice_client
        vc.play(next_song, after=lambda e: play_next(ctx))

def load_opus_lib():
    system = platform.system()
    paths_to_try = []

    if system == "Darwin":  # macOS
        paths_to_try = [
            "/opt/homebrew/lib/libopus.dylib",
            "/usr/local/opt/opus/lib/libopus.dylib",
        ]
    elif system == "Linux":  # Raspberry Pi
        paths_to_try = [
            "/usr/lib/arm-linux-gnueabihf/libopus.so.0",
            "/usr/lib/x86_64-linux-gnu/libopus.so.0",
            "/usr/lib/libopus.so.0"
        ]

    for path in paths_to_try:
        if os.path.exists(path):
            discord.opus.load_opus(path)
            if discord.opus.is_loaded():
                print(f"🔁 Loaded Opus from {path}")
                return True
        else:
            print(f"⚠️ Failed to load Opus from {path}")

    print("Could not load Opus library.")
    return False