from youtube_dl import YoutubeDL
import json
import yt_dlp

YDL_OPTIONS = {'format': 'bestaudio', 'youtube_include_dash_manifest': False}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

link = "https://www.youtube.com/playlist?list=PL5CCDFBBE2143D7CB"
with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
    info = ydl.extract_info(link, download=False)
    if 'entries' in info:
        for i in info['entries']:
            URL = i['webpage_url']
            songinfo = ydl.extract_info(URL, download=False)
            print({'source': songinfo['url'], 'title': i['title']})
