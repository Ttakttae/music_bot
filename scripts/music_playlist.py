import random

global playlist

playlist = {}

def playlist_music_count(channel):
    return len(playlist[channel]["list"])

def check_channel_playlist(channel):
    if not channel in playlist:
        reset_channel_playlist(channel)

def reset_channel_playlist(channel):
    playlist[channel] = {"list" : [], "loop" : "off"}

def playlist_set_loop_mode(channel, loop_mode):
    playlist[channel]["loop"] = "{}".format(loop_mode)

def add_playlist(channel, video_key, video_title, length, author, audio_url, title, search_keyword, url): # 플레이리스트 추가하기
    check_channel_playlist(channel)

    video_dic = {"video_key": video_key, "video_title": video_title, "length": length, "author" : author, "audio_url" : audio_url, "title" : title, "search_keyword": search_keyword, "url": url}

    if video_dic in playlist[channel]["list"]:
        playlist[channel]["list"].remove(video_dic)
        playlist[channel]["list"].insert(0, video_dic)
    else:
        playlist[channel]["list"].append(video_dic)

def delete_playlist(channel, number): # 플레이리스트 삭제
    music_number = number - 1

    del playlist[channel]["list"][music_number]


def next_playlist(channel): # 플레이리스트 다음으로 넘기기
    if not playlist[channel]["loop"] == "single":
        next_music = playlist[channel]["list"][0]
        del playlist[channel]["list"][0]

        if playlist[channel]["loop"] == "all":
            playlist[channel]["list"].append(next_music)

        if playlist[channel]["loop"] == "shuffle":
            next_song_number = random.randrange(1, len(playlist[channel]["list"]))
            next_song = playlist[channel]["list"][next_song_number]
            del playlist[channel]["list"][next_song_number]
            playlist[channel]["list"].insert(0, next_song)

    else:
        pass