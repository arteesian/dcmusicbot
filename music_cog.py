import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import yt_dlp


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False
        self.is_connected = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'ignoreerrors': True, 'youtube_include_dash_manifest': False, 'quiet': True, 'verbose': True, 'nocheckcertificate': True, 'age_limit': 54}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.current_track = ""
        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False
        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                self.is_connected = True

                if self.vc == None:
                    await ctx.send("Не удалось подключиться к голосовому каналу")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.current_track = self.music_queue[0][0]['title']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p"], help="Включить трек из YouTube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send(
                "Ты не в голосовом канале! Зайди, или единственная музыка, которую ты услышишь, будет звучать из твоей больной головы")
            return

        if 'https://www.youtube.com/playlist?list' in query:
            await ctx.send("Плейлист загружается. Пожалуйста, подождите")
            with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(query, download=False)
                await ctx.send(f"Включаю плейлист \"{info['title']}\"")
                if 'entries' in info:
                    count = 0
                    for i in info['entries']:
                        URL = i['webpage_url']
                        songinfo = ydl.extract_info(URL, download=False)
                        song = {'source': songinfo['url'], 'title': i['title']}
                        if type(song) == type(True):
                            await ctx.send("Мне не удалось воспроизвести эту песню :(")
                        else:
                            self.music_queue.append([song, voice_channel])
                            if not self.is_playing:
                                await self.play_music(ctx)
                                await ctx.send(f"Включаю трек: \"{self.current_track}\"")
                                count += 1
                            else:
                                count += 1
                    await ctx.send(f"Плейлист \"{info['title']}\" загружен. В очередь добавлено {count} треков")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Мне не удалось воспроизвести эту песню :(")
            else:
                self.music_queue.append([song, voice_channel])
                if not self.is_playing:
                    await self.play_music(ctx)
                    await ctx.send(f"Включаю трек: \"{self.current_track}\"")
                else:
                    await ctx.send(f"Трек \"{song['title']}\" добавлен в очередь")

    @commands.command(name="pause", help="Ставит текущий трек на паузу")
    async def pause(self, ctx, *args):
        if self.is_connected:
            if self.is_playing:
                self.is_playing = False
                self.is_paused = True
                self.vc.pause()
                await ctx.send("Воспроизведение музыки приостановлено")
            elif self.is_paused:
                self.is_playing = True
                self.is_paused = False
                self.vc.resume()
                await ctx.send(f"Воспроизведение музыки возобновлено. Сейчас играет: {self.current_track}")

    @commands.command(name="resume", aliases=["r"], help="Возобновляет проигрывание текущего трека")
    async def resume(self, ctx, *args):
        if self.is_connected:
            if self.is_paused:
                self.is_playing = True
                self.is_paused = False
                self.vc.resume()
                await ctx.send(f"Воспроизведение музыки возобновлено. Сейчас играет: {self.current_track}")

    @commands.command(name="skip", help="Пропускает текущий трек")
    async def skip(self, ctx, *args):
        if self.vc is not None and self.vc:
            self.vc.stop()

            m_url = self.music_queue[0][0]['source']
            self.current_track = self.music_queue[0][0]['title']
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            await ctx.send(f"Трек пропущен\nСейчас играет: {self.current_track}")

    @commands.command(name="queue", aliases=["q"], help="Показывает список ближайших треков в очереди")
    async def queue(self, ctx):
        retval = ""
        if self.is_connected:
            for i in range(0, len(self.music_queue)):
                retval += f"{i + 1}. " + self.music_queue[i][0]['title'] + '\n'

            if retval != "":
                await ctx.send(f"Сейчас играет: {self.current_track}\n"
                               + "Список треков в очереди:\n"
                               + retval)
            else:
                await ctx.send(f"Сейчас играет: {self.current_track}\n" +
                               "В очереди нет музыки")

    @commands.command(name="stop", aliases=["s"], help="Останавливает плеер и выключает всю музыку в очереди")
    async def stop(self, ctx, *args):
        if self.is_connected:
            if self.vc is not None and self.is_playing:
                self.vc.stop()
            self.music_queue = []
            self.is_playing = False
            self.is_paused = False
            self.is_connected = False
            await self.vc.disconnect()
            await ctx.send("Плеер выключен")
