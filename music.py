import asyncio, youtube_dl, discord, yt_search, time, googleapiclient

from discord_slash import SlashCommand, SlashContext
from googleapiclient import discovery
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord_slash.utils.manage_commands import create_option
import billboard
import lyricsgenius



FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
option = {
    'extractaudio':True,
    'audioformat':'mp3',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320k',
    }]
}


# scripts
from scripts.music_player import *
from scripts.music_playlist import *
from scripts.language import *

try:
    load_dotenv("./token.env")
    token = os.getenv('token')
except:
    token = os.environ['token']

try:
    load_dotenv("./token.env")
    google_api_key = os.getenv('google_api_key')
except:
    google_api_key = os.environ['google_api_key']

try:
    load_dotenv("./token.env")
    genius_api_key = os.getenv('genius_api_key')
except:
    genius_api_key = os.environ['genius_api_key']

print(token)
intents = discord.Intents.default()
client = discord.Client(intents=intents)
slash = SlashCommand(client, sync_commands=True)
genius = lyricsgenius.Genius(genius_api_key, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)
### 클래스------------------###


lng = Language()
lng.load_all_language()
lng.load_server_language()

mp_dic = {}
keyword_search_dic = {}
### -----------------------###

### 함수------------###
async def get_lyrics(songname, artist):
    if artist == None:
        song = genius.search_song(songname)
        lyric = song.lyrics
    else:
        song = genius.search_song(title=songname, artist=artist)
        lyric = song.lyrics
    lyric = str(lyric).replace("EmbedShare URLCopyEmbedCopy", "")
    a = True
    while a:
        if lyric[-1].isdecimal():
            lyric = lyric[:-1]
        else:
            a = False
    if len(lyric) > 4096:
        lyric = lyric[:4000] + "\n이하 생략"
    return lyric, song.artist


async def add_playlist_videos(video_key, voice_channel, author_id, channel, voice):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = google_api_key)

    request = youtube.playlistItems().list(part = "snippet", playlistId = video_key)
    response = request.execute()

    playlist_items = []
    video_ids = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    for t in playlist_items:
        video_ids.append(t["snippet"]["resourceId"]["videoId"])
    await playing(voice)
    for vi in video_ids:
        url = "https://www.youtube.com/watch?v={}".format(vi)
        information = await downloading(url)
        audio_url = information['formats'][0]['url']
        title = information["title"]
        length = information['duration']
        add_playlist(voice_channel, vi, title, length, author_id, audio_url, title, None, url)
    await asyncio.sleep(3)

async def playing(voice):
    if not voice.is_playing():
        source = FFmpegPCMAudio("https://r4---sn-3u-bh2s7.googlevideo.com/videoplayback?expire=1629832599&ei=N_EkYajNH97L2roP5v-b0A8&ip=61.82.94.169&id=o-AEvHPPL25gEUs3AdBtl2gipL9aO-9TyXjFJ_CIv98TA5&itag=249&source=youtube&requiressl=yes&mh=GS&mm=31%2C26&mn=sn-3u-bh2s7%2Csn-ogul7n7z&ms=au%2Conr&mv=m&mvi=4&pcm2cms=yes&pl=21&initcwndbps=923750&vprv=1&mime=audio%2Fwebm&ns=2fAfMr3m_WnyRxenquBLl4QG&gir=yes&clen=16305248&dur=36000.681&lmt=1613258125691959&mt=1629810770&fvip=4&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=5431432&n=wDkGEwjSeysiIyzKF&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAPjmG4PjSHDyYcvu3nHH9rdjetuTJFVHe2VQ8CYdNbf9AiEAvCR1hK6sVdRn0D8_ektxEYYf7xVCafEypUaZKGvNwUY%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpcm2cms%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRAIgRFtwJLSyMau3eYGI2866quzY2d-50EVy_sdAfMbcpWkCIGCjkTWcltDxwsZW9wSdOfTTS7oTJbPc7RXX-lvxbaHB", **FFMPEG_OPTIONS)# converts the youtube audio source into a source discord can use
        voice.play(source)  # play the source
    else:
        pass

async def downloading(url):
    with youtube_dl.YoutubeDL(option) as ydl:
        information = ydl.extract_info(url, download=False)
    return information

async def keyword_download(url, video_key, message, billboard=False):
    yt = yt_search.build(google_api_key)
    search_result = yt.search("{}".format(video_key), sMax=15, sType=["video"])
    while True:
        try:
            search_result.videoId.remove(None)
        except:
            break
    if billboard:
        vk = search_result.videoId[0]
        url = "https://www.youtube.com/watch?v={}".format(vk)
        information = await downloading(url)
        audio_url = information['formats'][0]['url']
        title = information["title"]
        length = information['duration']
        return audio_url, title, length, url
    else:
        try:
            try:
                if message.channel in keyword_search_dic:
                    await keyword_search_dic[message.channel]["message"].delete()
            except:
                pass
            keyword_search_dic[message.channel] = {"songs" : [], "message" : "", "author": message.author.id, "search_keyword": video_key}
            number = 1
            text = ""
            for vk in search_result.videoId:
                if number <= 9 :
                    url = "https://www.youtube.com/watch?v={}".format(vk)
                    information = await downloading(url)
                    audio_url = information['formats'][0]['url']
                    title = information["title"]
                    length = information['duration']
                    song_dic = {"video_key": vk, "url": url, "audio_url": audio_url, "title": title, "length": length, "url": url}
                    keyword_search_dic[message.channel]["songs"].append(song_dic)
                    text += f"{number}. {title}\n"
                    number += 1
            return text
        except:
            await message.send(content=lng.tl("download.error", str(message.guild.id)))
            return "error"

### ------------------------###

@slash.slash(name="ping", description="pong!")
async def ping(message):
    await message.send(content=f"Pong! {client.latency*1000}ms")

@slash.slash(name="madeby", description="만든이")
async def madeby(message):
    await message.send(content=lng.tl("made_by", str(message.guild.id)))

@slash.slash(name="join", description="음성 채널에 입장합니다")
async def join(message):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))

    if author_in_voice_chanel:
        try:
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    voice = vc
            if voice.channel == voice_channel:
                await message.send(content=lng.tl("already.in.channel", str(message.guild.id)))
            else:
                pass
        except:
            if discord.Permissions(permissions=int(str(voice_channel.permissions_for(member=message.guild.me)).split("=")[1].replace(">", ""))).connect:
                await message.author.voice.channel.connect()
                reset_channel_playlist(voice_channel)
                await message.send(content=lng.tl("voice.connect", str(message.guild.id)).format(voice_channel))
                try:
                    del mp_dic[str(message.channel.id)]
                except:
                    pass
                mp_dic[str(message.channel.id)] = music_playing()
            else:
                await message.send(content=lng.tl("no.permission", str(message.guild.id)))

@slash.slash(name="leave", description="음성채널에서 나갑니다")
async def leave(message):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
    if author_in_voice_chanel:
        voice_channel = message.author.voice.channel
        try:
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    voice = vc
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:
            if voice_channel == voice.channel:
                reset_channel_playlist(voice_channel)

                await voice.disconnect()
                await message.send(content=lng.tl("voice.disconnect", str(message.guild.id)).format(voice_channel))
                try:
                    await mp_dic[str(message.channel.id)].task_kill()
                except:
                    pass

                del mp_dic[str(message.channel.id)]
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="play", description="노래를 재생합니다", options=[create_option(name="song", description="유튜브 링크나 검색 키워드(라이브 스트리밍, 플레이리스트, 그냥 동영상 모두 가능)", option_type=3, required=True)])
async def play(message, song: str):
    url = song
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
    if author_in_voice_chanel:
        voice_channel = message.author.voice.channel
        no_permission = False
        try:
            if discord.Permissions(permissions=int(str(voice_channel.permissions_for(member=message.guild.me)).split("=")[1].replace(">", ""))).connect:
                await message.author.voice.channel.connect()
                await message.send(content=lng.tl("voice.connect", str(message.guild.id)).format(voice_channel))
                try:
                    del mp_dic[str(message.channel.id)]
                except:
                    pass
                mp_dic[str(message.channel.id)] = music_playing()
                no_permission = False
            else:
                await message.send(content=lng.tl("no.permission", str(message.guild.id)))
                no_permission = True
        except:
            pass
        if no_permission:
            pass
        else:
            try:
                for vc in client.voice_clients:
                    if vc.guild == message.guild:
                        voice = vc
                print(voice.channel)
                bot_not_in_channel = False
            except:
                await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
                bot_not_in_channel = True
            if bot_not_in_channel:
                pass
            else:

                if voice_channel == voice.channel:
                    ### mp3 다운로드-----------###
                    now_play = False
                    url_search = False
                    playlist_search = False
                    not_youtube_search = False
                    if "https://" in url:
                        if "youtu.be" in url: # 인풋받은 링크가 모바일 유튜브 링크인가?
                            video_key = url.split("/")[3]
                            url_search = True
                        elif "playlist" in url:
                            video_key = url.split("=")[1]
                            playlist_search = True
                            url_search = False
                        else:
                            try:
                                video_key = url.split("=")[1]
                                try:
                                    video_key = video_key.replace("&list", "")
                                except:
                                    pass
                                url_search = True
                            except:
                                url_search = False
                                not_youtube_search = True

                    else:
                        video_key = url

                    if url_search:
                        now_play = True
                        await message.send(content=lng.tl("finding.song", str(message.guild.id)))
                        url = "https://www.youtube.com/watch?v={}".format(video_key)
                        information = await downloading(url)
                        await asyncio.sleep(1)
                        audio_url = information['formats'][0]['url']
                        title = information["title"]
                        length = information['duration']
                        add_playlist(voice_channel, video_key, title, length, message.author.id, audio_url, title, None, url)

                    elif not_youtube_search:
                        now_play = True
                        information = await downloading(url)
                        await asyncio.sleep(1)
                        audio_url = information['formats'][0]['url']
                        title = information["title"]
                        try:
                            length = information['duration']
                            video_key = url.split("/")[4]
                            await asyncio.sleep(2)
                        except:
                            length = 0
                            video_key = url.split("/")[3]
                            await asyncio.sleep(2)
                        add_playlist(voice_channel, video_key, title, length, message.author.id, audio_url, title, None, url)

                    elif playlist_search:
                        now_play = True
                        await message.send(content=lng.tl("checking.playlist", str(message.guild.id)))
                        await add_playlist_videos(video_key, voice_channel, message.author.id, message, voice)
                        await message.send(content=lng.tl("playlist.add", str(message.guild.id)))

                    else: # keyword search!
                        await message.send(content=lng.tl("finding.song", str(message.guild.id)))
                        text = await keyword_download(url, video_key, message, False)
                        if text == "error":
                            pass
                        else:
                            embed = discord.Embed(title=lng.tl("song.search.result", str(message.guild.id)), description=text, color=0xECDDC3)
                            await asyncio.sleep(1)
                            msg = await message.send(embed=embed)
                            keyword_search_dic[message.channel]["message"] = msg
                            await msg.add_reaction("1️⃣")
                            await msg.add_reaction("2️⃣")
                            await msg.add_reaction("3️⃣")
                            await msg.add_reaction("4️⃣")
                            await msg.add_reaction("5️⃣")
                            await msg.add_reaction("6️⃣")
                            await msg.add_reaction("7️⃣")
                            await msg.add_reaction("8️⃣")
                            await msg.add_reaction("9️⃣")
                            await msg.add_reaction("❌")

                    if now_play:
                        if not vc.is_playing():
                            source = FFmpegPCMAudio(playlist[voice_channel]["list"][0]["audio_url"], **FFMPEG_OPTIONS)# converts the youtube audio source into a source discord can use
                            voice.play(source)  # play the source
                            await message.send(content=lng.tl("voice.play", str(message.guild.id)).format(playlist[voice_channel]["list"][0]["title"])) # ``text`` 진하기로 노래 제목 강조
                            await message.send(content=url)
                            if playlist[voice_channel]["list"][0]["length"] == 0:
                                pass
                            else:
                                time[voice_channel] = {"now-remaining" : playlist[voice_channel]["list"][0]["length"], "paused-time" : 0}
                                await mp_dic[str(message.channel.id)].create_task(voice, voice_channel, message, playlist, str(message.guild.id))
                        else:
                            await message.send(content=lng.tl("song.add", str(message.guild.id)))
                    else:
                        pass
                else:
                    await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="pause", description="노래를 잠시 중지합니다")
async def pause(message):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
    if author_in_voice_chanel:
        voice_channel = message.author.voice.channel
        try:
            voice = discord.utils.get(client.voice_clients, guild = message.guild) #봇의 음성 관련 정보
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:
            if voice_channel == voice.channel:
                if voice.is_playing(): #노래가 재생중이면
                    if playlist[voice_channel]["list"][0]["length"] == 0:
                        pass
                    else:
                        time[voice_channel]["paused-time"] = time[voice_channel]["now-remaining"]
                        await mp_dic[str(message.channel.id)].task_kill()
                        time[voice_channel]["now-remaining"] = time[voice_channel]["paused-time"]

                    voice.pause() #일시정지
                    await message.send(content=lng.tl("voice.pause", str(message.guild.id)))
                else:
                    await message.send(content=lng.tl("voice.pause.voice_not_playing", str(message.guild.id)))
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="resume", description="노래를 다시 재생합니다")
async def resume(message):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
    if author_in_voice_chanel:
        voice_channel = message.author.voice.channel
        try:
            voice = discord.utils.get(client.voice_clients, guild = message.guild) #봇의 음성 관련 정보
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:
            if voice.channel == voice_channel:
                if voice.is_paused(): #일시정지 상태이면
                    voice.resume()
                    await message.send(content=lng.tl("voice.replay", str(message.guild.id)))
                    if playlist[voice_channel]["list"][0]["length"] == 0:
                        pass
                    else:
                        await mp_dic[str(message.channel.id)].create_task(voice, voice_channel, message, playlist, str(message.guild.id))
                else:
                    await message.send(content=lng.tl("voice.replay.voice_playing", str(message.guild.id)))
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="playlist", description="재생목록을 보여줍니다")
async def queue(message):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
    if author_in_voice_chanel:
        try:
            voice = discord.utils.get(client.voice_clients, guild = message.guild) #봇의 음성 관련 정보
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:
            if voice_channel == voice.channel:
                voice_channel = message.author.voice.channel
                check_channel_playlist(voice_channel)

                result = ""
                for playlist_number, music_info in enumerate(playlist[voice_channel]["list"]):
                    result += "{}. {} queued by <@{}>\n".format(playlist_number + 1, music_info["video_title"], music_info["author"])
                result = result[:-1]


                if len(result) < 4000:
                    embed = discord.Embed(title = lng.tl("voice.playlist.title", str(message.guild.id)).format(playlist[voice_channel]["loop"]), description = "{}".format(result), color = 0xECDDC3)
                    await message.send(embed = embed)
                else:

                    results = {} # result 모아두는 리스트
                    result_number = 1 # result list의 index지정


                    for music_number, music in enumerate(playlist[voice_channel]["list"]):
                        music_info = "{}. {} queued by <@{}>\n".format(music_number + 1, music["video_title"], music["author"])

                        if result_number > len(results): results[result_number] = ""

                        if len(results[result_number]) + len(music_info) > 4096:
                            result_number += 1
                            results[result_number] = ""

                        results[result_number] += music_info

                    for result_number in results:
                        embed = discord.Embed(title = lng.tl("voice.playlist.title", str(message.guild.id)).format(playlist[voice_channel]["loop"]), description = "{}".format(results[result_number]), color = 0xECDDC3)
                        await message.send(embed=embed)

            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="skip", description="노래를 건너뜁니다")
async def skip(message):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
    if author_in_voice_chanel:
        try:
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    voice = vc
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:

            if voice.channel == voice_channel:

                if playlist_music_count(voice_channel) >= 1:
                    if playlist_music_count(voice_channel) > 1 or playlist[voice_channel]["loop"] == "single" or playlist[voice_channel]["loop"] == "all":
                        await message.send(content=lng.tl("voice.skip", str(message.guild.id)))
                        voice.stop()
                        if playlist[voice_channel]["list"][0]["length"] == 0:
                            pass
                        else:
                            await mp_dic[str(message.channel.id)].task_kill()
                        next_playlist(voice_channel)
                        source = FFmpegPCMAudio(playlist[voice_channel]["list"][0]["audio_url"], **FFMPEG_OPTIONS)  # converts the youtube audio source into a source discord can use
                        voice.play(source)
                        await message.send(content=lng.tl("voice.play", str(message.guild.id)).format(playlist[voice_channel]["list"][0]["video_title"]))
                        await message.send(content=playlist[voice_channel]["list"][0]["url"])
                        if playlist[voice_channel]["list"][0]["length"] == 0:
                            pass
                        else:
                            time[voice_channel] = {"now-remaining" : playlist[voice_channel]["list"][0]["length"], "paused-time" : 0}
                            await mp_dic[str(message.channel.id)].create_task(voice, voice_channel, message, playlist, str(message.guild.id))
                    else:
                        voice.stop()
                        if playlist[voice_channel]["list"][0]["length"] == 0:
                            pass
                        else:
                            await mp_dic[str(message.channel.id)].task_kill()
                        delete_playlist(voice_channel, 1)
                        await message.send(content=lng.tl("voice.skip", str(message.guild.id)))
                else:
                    await message.send(content=lng.tl("delete.no.song", str(message.guild.id)))
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="delete", description="노래를 삭제합니다", options=[create_option(name="number", description="삭제할 노래의 숫자(재생목록에 나온 숫자 기준)", option_type=4, required=True)])
async def delete(message, number: int):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))

    if author_in_voice_chanel:
        music_number = number - 1

        try:
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    voice = vc
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:

            if voice.channel == voice_channel:

                if 1 <= music_number < playlist_music_count(voice_channel):
                    await message.send(content=lng.tl("voice.delete", str(message.guild.id)).format(playlist[voice_channel]["list"][music_number]["video_title"]))
                    delete_playlist(voice_channel, music_number + 1)

                elif 0 == music_number < playlist_music_count(voice_channel):
                    if music_number+1 == playlist_music_count(voice_channel):
                        if playlist[voice_channel]["list"][0]["length"] == 0:
                            pass
                        else:
                            await mp_dic[str(message.channel.id)].task_kill()
                        await message.send(lng.tl("voice.delete", str(message.guild.id)).format(playlist[voice_channel]["list"][music_number]["video_title"]))
                        voice.stop()
                        delete_playlist(voice_channel, music_number + 1)
                        loop = "off"
                        playlist_set_loop_mode(voice_channel, loop)
                    else:
                        if playlist[voice_channel]["loop"] == "single":
                            await message.send(content=lng.tl("voice.delete", str(message.guild.id)).format(playlist[voice_channel]["list"][music_number]["video_title"]))
                            voice.stop()
                            if playlist[voice_channel]["list"][0]["length"] == 0:
                                pass
                            else:
                                await mp_dic[str(message.channel.id)].task_kill()
                            loop = "off"
                            playlist_set_loop_mode(voice_channel, loop)
                            delete_playlist(voice_channel, music_number + 1)
                            source = FFmpegPCMAudio(playlist[voice_channel]["list"][0]["audio_url"], **FFMPEG_OPTIONS)  # converts the youtube audio source into a source discord can use
                            voice.play(source)  # play the source
                            await message.send(content=lng.tl("voice.play", str(message.guild.id)).format(playlist[voice_channel]["list"][0]["video_title"]))
                            await message.send(content=playlist[voice_channel]["list"][0]["url"])
                            await asyncio.sleep(playlist[voice_channel]["list"][0]["length"]+1)
                            if playlist[voice_channel]["list"][0]["length"] == 0:
                                pass
                            else:
                                time[voice_channel] = {"now-remaining" : playlist[voice_channel]["list"][0]["length"], "paused-time" : 0}
                                await mp_dic[str(message.channel.id)].create_task(voice, voice_channel, message, playlist, str(message.guild.id))
                        else:
                            await message.send(content=lng.tl("voice.delete", str(message.guild.id)).format(playlist[voice_channel]["list"][music_number]["video_title"]))
                            voice.stop()
                            if playlist[voice_channel]["list"][0]["length"] == 0:
                                pass
                            else:
                                await mp_dic[str(message.channel.id)].task_kill()
                            delete_playlist(voice_channel, music_number + 1)
                            source = FFmpegPCMAudio(playlist[voice_channel]["list"][0]["audio_url"], **FFMPEG_OPTIONS)  # converts the youtube audio source into a source discord can use
                            voice.play(source)  # play the source
                            await message.send(content=lng.tl("voice.play", str(message.guild.id)).format(playlist[voice_channel]["list"][0]["video_title"]))
                            await message.send(content=playlist[voice_channel]["list"][0]["url"])
                            await asyncio.sleep(playlist[voice_channel]["list"][0]["length"]+1)
                            if playlist[voice_channel]["list"][0]["length"] == 0:
                                pass
                            else:
                                time[voice_channel] = {"now-remaining" : playlist[voice_channel]["list"][0]["length"], "paused-time" : 0}
                                await mp_dic[str(message.channel.id)].create_task(voice, voice_channel, message, playlist, str(message.guild.id))

                else:
                    await message.send(content=lng.tl("delete.no.song", str(message.guild.id)))# 삭제하려는 노래가 플레이 리스트 범위를 넘거나 0보다 작음
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="loop", description="노래 한곡이나 전체를 반복하거나, 반복을 끕니다", options=[create_option(name="mode", description="한곡: single, 전체: all, 셔플(무작위 재생): shuffle, 끄기: off", option_type=3, required=True)])
async def loop(message, mode: str):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
    if author_in_voice_chanel:
        try:
            voice = discord.utils.get(client.voice_clients, guild = message.guild) #봇의 음성 관련 정보
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:
            if voice_channel == voice.channel:
                voice_channel = message.author.voice.channel
                if mode == "single":
                    if len(playlist[voice_channel]["list"]) >= 1:
                        loop = "single"
                        playlist_set_loop_mode(voice_channel, loop)
                        await message.send(content=lng.tl("voice.loop.one", str(message.guild.id)).format(playlist[voice_channel]["list"][0]["video_title"]))
                    else:
                        await message.send(content=lng.tl("no.song.loop", str(message.guild.id)))

                if mode == "all":
                    if len(playlist[voice_channel]["list"]) >= 1:
                        loop = "all"
                        playlist_set_loop_mode(voice_channel, loop)
                        await message.send(content=lng.tl("voice.loop.all", str(message.guild.id)))
                    else:
                        await message.send(content=lng.tl("no.song.loop", str(message.guild.id)))

                if mode == "shuffle":
                    if len(playlist[voice_channel]["list"]) >= 1:
                        loop = "shuffle"
                        playlist_set_loop_mode(voice_channel, loop)
                        await message.send(content=lng.tl("voice.shuffle", str(message.guild.id)))
                    else:
                        await message.send(content=lng.tl("no.song.shuffle", str(message.guild.id)))

                if mode == "off":
                    loop = "off"
                    playlist_set_loop_mode(voice_channel, loop)
                    await message.send(content=lng.tl("voice.loop.off", str(message.guild.id)))
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="language_change", description="출력되는 언어(slash command 이름이나 설명 아님)를 변경합니다", options=[create_option(name="language", description="다음중 선택(korean, english, chinese, japanese)", option_type=3, required=True)])
async def language_change(message, language: str):
    if language == "korean":
        lng.channel_language[str(message.guild.id)] = 'ko-KR'
        await message.send(content=lng.tl("voice.set_language", str(message.guild.id)))
        lng.save_server_language()
    elif language == "english":
        lng.channel_language[str(message.guild.id)] = 'en-US'
        await message.send(content=lng.tl("voice.set_language", str(message.guild.id)))
        lng.save_server_language()
    elif language == "chinese":
        lng.channel_language[str(message.guild.id)] = 'zh-CN'
        await message.send(content=lng.tl("voice.set_language", str(message.guild.id)))
        lng.save_server_language()
    elif language == "japanese":
        lng.channel_language[str(message.guild.id)] = 'ja-JP'
        await message.send(content=lng.tl("voice.set_language", str(message.guild.id)))
        lng.save_server_language()
    else:
        await message.send(content=lng.tl("no.lang", str(message.guild.id)).format(language))

@slash.slash(name="billboard", description="빌보드 차트를 출력합거나, 숫자를 입력하면 그 숫자에 해당하는 노래를 재생합니다", options=[create_option(name="number", description="빌보드 차트 숫자(중복 선택 가능 ex: 30, 20, 15 또는 1~4)", option_type=3, required=False)])
async def billboard_show(message, number: str = None):
    chart = billboard.ChartData('hot-100')
    if number == None:
        result = ""
        number = 0
        for song in chart:
            result += f"{number+1}. ``{song.title}`` BY ``{song.artist}``\n"
            number += 1


        if len(result) < 4000:
            embed = discord.Embed(title="Billboard Hot 100", description=f"{result}", color=0xECDDC3)
            await message.send(embed=embed)
        else:
            results = {} # result 모아두는 리스트
            result_number = 1 # result list의 index지정
            number_a = 0
            music_info = ""


            for song in chart:
                music_info = f"{number_a+1}. ``{song.title}`` BY ``{song.artist}``\n"
                number_a += 1

                if result_number > len(results): results[result_number] = ""

                if len(results[result_number]) + len(music_info) > 4096:
                    result_number += 1
                    results[result_number] = ""

                results[result_number] += music_info

            for result_number in results:
                embed = discord.Embed(title="Billboard Hot 100", description=f"{results[result_number]}", color=0xECDDC3)
                await message.send(embed=embed)
    elif "~" in number:
        try:
            voice_channel = message.author.voice.channel
            author_in_voice_chanel = True
        except:
            author_in_voice_chanel = False
            await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
        if author_in_voice_chanel:
            no_permission = False
            try:
                if discord.Permissions(permissions=int(str(voice_channel.permissions_for(member=message.guild.me)).split("=")[1].replace(">", ""))).connect:
                    await message.author.voice.channel.connect()
                    await message.send(content=lng.tl("voice.connect", str(message.guild.id)).format(voice_channel))
                    try:
                        del mp_dic[str(message.channel.id)]
                    except:
                        pass
                    mp_dic[str(message.channel.id)] = music_playing()
                else:
                    await message.send(content=lng.tl("no.permission", str(message.guild.id)))
                    no_permission = True
            except:
                pass
            if no_permission:
                pass
            else:
                try:
                    for vc in client.voice_clients:
                        if vc.guild == message.guild:
                            voice = vc
                    print(voice.channel)
                    bot_not_in_channel = False
                except:
                    await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
                    bot_not_in_channel = True
                if bot_not_in_channel:
                    pass
                else:
                    number_list = []
                    a = int(number.split("~")[0])
                    b = int(number.split("~")[1])
                    if len(list(range(a, b+1))) > 5:
                        await message.send(content=lng.tl("sorry.to.many.songs", str(message.guild.id)))
                    else:
                        if voice.channel == voice_channel:
                            number_list = list(range(a, b+1))
                            await message.send(content=lng.tl("finding.song", str(message.guild.id)))
                            for n in number_list:
                                song = chart[int(n)-1]
                                search_keyword = f"{song.title} {song.artist}"
                                audio_url, title, lenth = await keyword_download(search_keyword, search_keyword, message, True)
                                add_playlist(voice_channel, search_keyword, title, lenth, message.author.id, audio_url, title, song.title)
                            if not voice.is_playing():
                                source = FFmpegPCMAudio(playlist[voice_channel]["list"][0]["audio_url"], **FFMPEG_OPTIONS)# converts the youtube audio source into a source discord can use
                                voice.play(source)  # play the source
                                await message.send(content=lng.tl("voice.play", str(message.guild.id)).format(playlist[voice_channel]["list"][0]["title"])) # ``text`` 진하기로 노래 제목 강조
                                await message.send(content=playlist[voice_channel]["list"][0]["url"])
                                if playlist[voice_channel]["list"][0]["length"] == 0:
                                    pass
                                else:
                                    time[voice_channel] = {"now-remaining" : playlist[voice_channel]["list"][0]["length"], "paused-time" : 0}
                                    await mp_dic[str(message.channel.id)].create_task(voice, voice_channel, message, playlist, str(message.guild.id))
                            else:
                                await message.send(content=lng.tl("song.add", str(message.guild.id)))
                        else:
                            await message.send(content=lng.tl("different.channel", str(message.guild.id)))

    else:
        try:
            voice_channel = message.author.voice.channel
            author_in_voice_chanel = True
        except:
            author_in_voice_chanel = False
            await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))
        if author_in_voice_chanel:
            no_permission = False
            try:
                if discord.Permissions(permissions=int(str(voice_channel.permissions_for(member=message.guild.me)).split("=")[1].replace(">", ""))).connect:
                    await message.author.voice.channel.connect()
                    await message.send(content=lng.tl("voice.connect", str(message.guild.id)).format(voice_channel))
                    try:
                        del mp_dic[str(message.channel.id)]
                    except:
                        pass
                    mp_dic[str(message.channel.id)] = music_playing()
                else:
                    await message.send(content=lng.tl("no.permission", str(message.guild.id)))
                    no_permission = True
            except:
                pass
            if no_permission:
                pass
            else:
                try:
                    for vc in client.voice_clients:
                        if vc.guild == message.guild:
                            voice = vc
                    print(voice.channel)
                    bot_not_in_channel = False
                except:
                    await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
                    bot_not_in_channel = True
                if bot_not_in_channel:
                    pass
                else:
                    if "," in number:
                        number = number.split(", ")
                    if voice.channel == voice_channel:
                        if type(number) == str:
                            song = chart[int(number)-1]
                            search_keyword = f"{song.title} {song.artist}"
                            audio_url, title, lenth, url = await keyword_download(search_keyword, search_keyword, message, True)
                            add_playlist(voice_channel, search_keyword, title, lenth, message.author.id, audio_url, title, song.title, url)
                        else:
                            await message.send(content=lng.tl("finding.song", str(message.guild.id)))
                            for n in number:
                                song = chart[int(n)-1]
                                search_keyword = f"{song.title} {song.artist}"
                                audio_url, title, lenth, url = await keyword_download(search_keyword, search_keyword, message, True)
                                add_playlist(voice_channel, search_keyword, title, lenth, message.author.id, audio_url, title, song.title, url)
                        if not voice.is_playing():
                            source = FFmpegPCMAudio(playlist[voice_channel]["list"][0]["audio_url"], **FFMPEG_OPTIONS)# converts the youtube audio source into a source discord can use
                            voice.play(source)  # play the source
                            await message.send(content=lng.tl("voice.play", str(message.guild.id)).format(playlist[voice_channel]["list"][0]["title"])) # ``text`` 진하기로 노래 제목 강조
                            await message.send(content=playlist[voice_channel]["list"][0]["url"])
                            if playlist[voice_channel]["list"][0]["length"] == 0:
                                pass
                            else:
                                time[voice_channel] = {"now-remaining" : playlist[voice_channel]["list"][0]["length"], "paused-time" : 0}
                                await mp_dic[str(message.channel.id)].create_task(voice, voice_channel, message, playlist, str(message.guild.id))
                        else:
                            await message.send(content=lng.tl("song.add", str(message.guild.id)))
                    else:
                        await message.send(content=lng.tl("different.channel", str(message.guild.id)))


@slash.slash(name="lyrics", description="현재 재생중인 곡(플레이 리스트의 가장 상위 곡)의 가사를 보여줍니다(링크 사용했을시 작동 거의 안됨)", options=[create_option(name="artist", description="더 정확한 검색을 위한 아티스트 변수", option_type=3, required=False), create_option(name="title", description="더 정확한 검색을 위한 제목 변수(키워드 검색 사용자들은 필요 없음)", option_type=3, required=False)])
async def lyrics(message, artist: str = None, title: str = None):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))

    if author_in_voice_chanel:
        search = True
        if title == None:
            try:
                print(playlist[voice_channel]["list"][0]["title"])
                if playlist[voice_channel]["list"][0]["search_keyword"] == None:
                    songname = playlist[voice_channel]["list"][0]["title"]
                else:
                    songname = playlist[voice_channel]["list"][0]["search_keyword"]
            except:
                await message.send(content=lng.tl("no.song.to.search", str(message.guild.id)))
                search = False
        else:
            songname = title
        if search:
            await message.send(content=lng.tl("finding.lyrics", str(message.guild.id)))
            lyric, artist_name = await get_lyrics(songname, artist)
            embed = discord.Embed(title=f"``{songname} by {artist_name}`` 가사", description=f"{lyric}", color=0xECDDC3)
            embed.set_footer(text="Genius Lyrics API", icon_url="https://yt3.ggpht.com/ytc/AKedOLRsMBYiaqZw_CwNdarpzchzNsPOF9aQLqxLqhFaDw=s900-c-k-c0x00ffffff-no-rj")
            await message.send(embed=embed)
        else:
            pass

@slash.slash(name="clear", description="재생목록의 노래들을 초기화합니다")
async def clear(message):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))

    if author_in_voice_chanel:
        try:
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    voice = vc
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:

            if voice.channel == voice_channel:

                if voice.is_playing():
                    voice.stop()
                    await mp_dic[str(message.channel.id)].task_kill()
                reset_channel_playlist(voice_channel)
                await message.send(content=lng.tl("playlist.clear", str(message.guild.id)))
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="seek", description="입력한 초에 해당하는 시간으로 이동합니다", options=[create_option(name="number", description="이동할 초", option_type=4, required=True)])
async def seek(message, number: int):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))

    if author_in_voice_chanel:
        try:
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    voice = vc
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:
            if voice.channel == voice_channel:

                if voice.is_playing(): #노래가 재생중이면
                    if playlist[voice_channel]["list"][0]["length"] == 0:
                        await message.send(content=lng.tl("live.no.seek", str(message.guild.id)))
                    else:
                        await mp_dic[str(message.channel.id)].task_kill()
                        time[voice_channel]["now-remaining"] = playlist[voice_channel]["list"][0]["length"] - number
                        time[voice_channel]["paused-time"] = 0
                        print(time[voice_channel]["now-remaining"])
                        print(time[voice_channel]["paused-time"])
                        voice.stop() #정지
                        source = FFmpegPCMAudio(source=playlist[voice_channel]["list"][0]["audio_url"], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options=f'-vn -ss {number}')# converts the youtube audio source into a source discord can use
                        voice.play(source)  # play the source
                        await message.send(content=lng.tl("time.seek", str(message.guild.id)).format(number))
                        await mp_dic[str(message.channel.id)].create_task(voice, voice_channel, message, playlist, str(message.guild.id))
                else:
                    await message.send(content=lng.tl("voice.pause.voice_not_playing", str(message.guild.id)))
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))

@slash.slash(name="move", description="채널을 이동합니다(플레이 리스트 유지)", options=[create_option(name="channel", description="이동할 채널", option_type=7, required=True)])
async def move(message, channel: str):
    try:
        voice_channel = message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
        await message.send(content=lng.tl("enter.voice_channel", str(message.guild.id)).format(str(message.author.id)))

    if author_in_voice_chanel:
        try:
            for vc in client.voice_clients:
                if vc.guild == message.guild:
                    voice = vc
            print(voice.channel)
            bot_not_in_channel = False
        except:
            await message.send(content=lng.tl("bot.not.voice.channel", str(message.guild.id)))
            bot_not_in_channel = True
        if bot_not_in_channel:
            pass
        else:
            if voice_channel == voice.channel:
                if channel == voice:
                    await message.send(content=lng.tl("this.channel", str(message.guild.id)))
                else:
                    if discord.Permissions(permissions=int(str(channel.permissions_for(member=message.guild.me)).split("=")[1].replace(">", ""))).connect:
                        voice_was_playing = False
                        if voice.is_playing():
                            await mp_dic[str(message.channel.id)].task_kill()
                            time[channel] = {"now-remaining" : time[voice_channel]["now-remaining"], "paused-time" : playlist[voice_channel]["list"][0]["length"] - time[voice_channel]["now-remaining"]}
                            voice_was_playing = True
                        else:
                            pass
                        await voice.disconnect()
                        await channel.connect()
                        reset_channel_playlist(channel)
                        playlist[channel]["list"] = playlist[voice_channel]["list"]
                        playlist[channel]["loop"] = playlist[voice_channel]["loop"]
                        reset_channel_playlist(voice_channel)
                        for vc in client.voice_clients:
                            if vc.guild == message.guild:
                                voice = vc
                        if voice_was_playing:
                            source = FFmpegPCMAudio(source=playlist[channel]["list"][0]["audio_url"], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options=f'-vn -ss {time[channel]["paused-time"]}')# converts the youtube audio source into a source discord can use
                            voice.play(source)  # play the source
                            await message.send(content=lng.tl("move.successful", str(message.guild.id)))
                            await mp_dic[str(message.channel.id)].create_task(voice, channel, message, playlist, str(message.guild.id))
                        else:
                            await message.send(content=lng.tl("move.successful", str(message.guild.id)))
                    else:
                        await message.send(content=lng.tl("no.permission", str(message.guild.id)))
            else:
                await message.send(content=lng.tl("different.channel", str(message.guild.id)))


@client.event
async def on_ready():
    print('봇시작')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/명령어")) #상태설정
    discord.Permissions.use_slash_commands = True

@client.event
async def on_reaction_add(reaction, member):
    if member.bot == 1: #봇이면 패스
        return None
    for vc in client.voice_clients:
        if vc.guild == reaction.message.guild:
            voice = vc
    try:
        voice_channel = reaction.message.author.voice.channel
        author_in_voice_chanel = True
    except:
        author_in_voice_chanel = False
    if author_in_voice_chanel:
        if str(member.id) == str(keyword_search_dic[reaction.message.channel]["author"]):
            if str(reaction.emoji) == "❌":
                await keyword_search_dic[reaction.message.channel]["message"].delete()
            else:
                if str(reaction.emoji) == "1️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][0]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][0]["title"]
                    length = keyword_search_dic[reaction.message.channel]["songs"][0]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][0]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][0]["url"]

                if str(reaction.emoji) == "2️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][1]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][1]["title"]
                    length = keyword_search_dic[reaction.message.channel]["songs"][1]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][1]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][1]["url"]

                if str(reaction.emoji) == "3️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][2]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][2]["title"]
                    length = keyword_search_dic[reaction.message.channel]["songs"][2]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][2]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][2]["url"]

                if str(reaction.emoji) == "4️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][3]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][3]["title"]
                    length = keyword_search_dic[reaction.message.channel]["songs"][3]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][3]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][3]["url"]

                if str(reaction.emoji) == "5️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][4]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][4]["title"]
                    length = keyword_search_dic[reaction.message.channel]["songs"][4]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][4]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][4]["url"]

                if str(reaction.emoji) == "6️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][5]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][5]["title"]
                    length = keyword_search_dic[reaction.message.channel]["songs"][5]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][5]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][5]["url"]

                if str(reaction.emoji) == "7️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][6]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][6]["title"]
                    length = keyword_search_dic[reaction.message.channel]["songs"][6]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][6]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][6]["url"]

                if str(reaction.emoji) == "8️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][7]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][7]["title"]
                    length = keyword_search_dic[reaction.message.channel]["songs"][7]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][7]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][7]["url"]

                if str(reaction.emoji) == "9️⃣":
                    video_key = keyword_search_dic[reaction.message.channel]["songs"][8]["video_key"]
                    title = keyword_search_dic[reaction.message.channel]["songs"][8]["title"]
                    length = keyword_search_dic[reaction.message.channel]=["songs"][8]["length"]
                    audio_url = keyword_search_dic[reaction.message.channel]["songs"][8]["audio_url"]
                    url = keyword_search_dic[reaction.message.channel]["songs"][8]["url"]


                add_playlist(voice_channel, video_key, title, length, str(keyword_search_dic[reaction.message.channel]["author"]), audio_url, title, keyword_search_dic[reaction.message.channel]["search_keyword"], url)
                if not vc.is_playing():
                    source = FFmpegPCMAudio(playlist[voice_channel]["list"][0]["audio_url"], **FFMPEG_OPTIONS)# converts the youtube audio source into a source discord can use
                    voice.play(source)  # play the source
                    embed = discord.Embed(title=lng.tl("song.play", str(reaction.message.guild.id)), description=lng.tl("voice.play", str(reaction.message.guild.id)).format(title), color=0xECDDC3)
                    await keyword_search_dic[reaction.message.channel]["message"].edit(content="", embed=embed)
                    await reaction.message.channel.send(url)
                    await asyncio.sleep(2)
                    await keyword_search_dic[reaction.message.channel]["message"].clear_reactions()
                    if playlist[voice_channel]["list"][0]["length"] == 0:
                        pass
                    else:
                        time[voice_channel] = {"now-remaining" : playlist[voice_channel]["list"][0]["length"], "paused-time" : 0}
                        await mp_dic[str(reaction.message.channel.id)].create_task(voice, voice_channel, reaction.message.channel, playlist, str(reaction.message.guild.id))
                else:
                    embed = discord.Embed(title=lng.tl("music.add", str(reaction.message.guild.id)), description=lng.tl("song.add", str(reaction.message.guild.id)), color=0xECDDC3)
                    await keyword_search_dic[reaction.message.channel]["message"].edit(content="", embed=embed)
                    await asyncio.sleep(3)
                    await keyword_search_dic[reaction.message.channel]["message"].clear_reactions()

client.run(token)