import uuid
import time
from pathlib import Path
from .youtube_search import YoutubeSearch
import json
import argparse
from tqdm import tqdm
import re
import sys
import requests
import os
import logging
import html
import urllib.parse


def YT_authordata(yt_id):
    try:
        if yt_id[0] == "_":
            return YoutubeSearch('https://www.youtube.com/watch?v=//'+yt_id, max_results = 1).to_dict()[0]
        return YoutubeSearch('https://www.youtube.com/watch?v='+yt_id, max_results = 1).to_dict()[0]
    except IndexError:
        logger.warning(f"Youtube-search failed for https://www.youtube.com/watch?v={yt_id}")
        return None


def yt_video_data_fallback(url):
    logger.debug(f"fallback fundtion called: https://www.youtube.com/watch?v={url}")
    url_quoted = urllib.parse.quote_plus(url)
    web_request = requests.get("https://www.youtube.com/watch?v="+url_quoted)
    site_html = web_request.text
    try:
        title = re.search(r'<title\s*.*?>(.*?)</title\s*>', site_html, re.IGNORECASE)
        if title:
            title = html.unescape(title.group(1).split("- YouTube")[0])
        if len(title) < 2:
            logger.warning(f"{url}: Fallback function. getting video title failed")
            return None

        author = re.search(r'"author":"(.*?)"', site_html, re.IGNORECASE)
        if author:
            author = author.group(1)
        else:
            author = "channel"
            logger.warning(f"{url}: Fallback function. getting channel name failed")

        channelId = re.search(r'"channelId":"(.*?)"', site_html, re.IGNORECASE)
        if channelId:
            channelId = channelId.group(1)
        else:
            channelId = "UCGBhVKHvwL386p13_-n3YPg"
            logger.warning(f"{url}: Fallback function. getting channel Id failed")

        endTimeMs = re.search(r'"endTimeMs":"(.*?)"', site_html, re.IGNORECASE)
        if endTimeMs:
            endTimeMs = int(endTimeMs.group(1))/1000
        else:
            endTimeMs = "0:00"
            logger.warning(f"{url}: Fallback function. getting video duration failed")

    except Exception as e:
        logger.error(f"yt_video_data_fallback() failed: {e}")
        return None
    return dict(title=title,
                author=html.unescape(author),
                channelId=channelId,
                lengthSeconds=endTimeMs
                )


def get_duration(time):
    try:
        time_parts = re.split(r"[.:]", time)
        seconds = int(time_parts[-1])
        minutes = int(time_parts[-2])
        hours = 0
        if len(time_parts) == 3:
            hours = int(time_parts[0])
        return seconds+minutes*60+hours*3600
    except Exception as e:
        logger.error(f"get_duration() failed {e}")
        return "0:00"


def process_txt(path):
    with open(path, "r") as inputfile:
        Videos = inputfile.readlines()
        Video_IDs = []
        for i in Videos:
            id = re.split(r"\?v=|youtu\.be/|shorts/", i)
            try:
                id = id[1].rstrip()
                Video_IDs.append(id)
            except IndexError:
                pass
    logger.debug(f"{path} .txt file processed")
    return Video_IDs


def process_csv(path):
    with open(path, "r") as inputfile:
        Videos = inputfile.readlines()
        Video_IDs = []
        data_start = False
        for i in Videos:
            if not data_start:
                data_start = True
                continue
            if data_start:
                if not len(i.split(",")[0].strip()) == 11:
                    continue
                Video_IDs.append(i.split(",")[0].strip())
    logger.debug(f"{path} .csv file processed")
    return Video_IDs


# Does the actual parsing and writing
def process_playlist(playlist_filepath, log_errors=False, list_broken_videos=False):
    if not Path(playlist_filepath).is_file():
        logger.critical(f"{playlist_filepath} is not a file.")
        return
    playlistname = str(Path(playlist_filepath).name)
    # a playlist name could have a dot in it so use splitext instead of splitting on a '.'
    playlistformat = os.path.splitext(playlistname)[1][1:].strip().lower()
    playlistname = os.path.splitext(playlistname)[0]
    Video_IDs = []
    if playlistformat == "txt":
        Video_IDs = process_txt(playlist_filepath)
    elif playlistformat == "csv":
        Video_IDs = process_csv(playlist_filepath)
    else:
        logger.critical(f"{playlistformat} is invalid file format.")
        return
    print(f"Reading file {playlist_filepath}, the playlistfile has {len(Video_IDs)} entries")
    print(f"writing to file {playlistname}.db")
    playlist_UUID = uuid.uuid4()
    current_time_ms = int(time.time() * 1000)
    playlist_dict = dict(
        playlistName = playlistname,
        videos = [],
        _id = "ft-playlist--" + str(playlist_UUID),
        createdAt = current_time_ms,
        lastUpdatedAt = current_time_ms
    )
    write_counter = 0
    failed_yt_search = []
    failed_ID = []
    for i in tqdm(Video_IDs, disable=logging.getLogger(__name__).isEnabledFor(logging.DEBUG)):
        # for i in Video_IDs:
        video_UUID = uuid.uuid4()
        current_time_ms = int(time.time()*1000)
        videoinfo = YT_authordata(i)
        if videoinfo:
            video_title = videoinfo['title']
            channel_name = videoinfo['channel']
            channel_id = videoinfo['channelId']
            if not channel_id:
                channel_id = "UC2hkwpSfrl6iniQNbwFXMog"
            video_duration = get_duration(videoinfo["duration"])
        try:
            try:
                videoinfo_ID = videoinfo['id']
            except TypeError:
                pass
            if videoinfo_ID != i:
                logger.info(f"Youtube-search: {videoinfo_ID} and input Id: {i} missmatch")
                # fetches the metadata directly from the video site when YoutubeSearch fails
                fallback_data = yt_video_data_fallback(i)
                if fallback_data["title"]:
                    video_title = fallback_data["title"]
                    channel_name = fallback_data["author"]
                    channel_id = fallback_data["channelId"]
                    video_duration = fallback_data["lengthSeconds"]
                if not video_title:
                    failed_ID.append(i)
                    logger.error(f"video {i} failed")
                    continue
                failed_yt_search.append(i)
        except Exception as e:
            failed_ID.append(i)
            logger.error(f"{e} err, with https://www.youtube.com/watch?v={i}")
            continue
        video_dict = dict(
            videoId=i,
            title=video_title,
            author=channel_name,
            authorId=channel_id,
            published="",
            lengthSeconds=video_duration,
            timeAdded=current_time_ms,
            type="video",
            playlistItemId=str(video_UUID)
        )
        playlist_dict["videos"].append(video_dict)
        write_counter += 1
        logger.info(f"https://www.youtube.com/watch?v={i} written successfully")
    if len(playlist_dict["videos"]) != 0:
        outputfile = open(playlistname+".db", "w")
        outputfile.write(json.dumps(playlist_dict, separators = (',', ':'))+"\n")
        outputfile.close()
        logger.info(f"{playlistname}.db written({write_counter}/{len(Video_IDs)})")
        print(f"Task failed successfully! {playlistname}.db written, with {write_counter} entries")
    else:
        print("No entries to write")
    if len(failed_ID) != 0 and log_errors:
        print("[Failed playlist items]")
        for i in failed_ID:
            print('https://www.youtube.com/watch?v='+i)
    if len(failed_yt_search) != 0 and list_broken_videos:
        print("[Videos with possibly broken metadata]")
        for i in failed_yt_search:
            print('https://www.youtube.com/watch?v='+i)


def main():
    # set logging to DEBUG for debug mode
    logger.setLevel(logging.ERROR)
    parser = argparse.ArgumentParser(description="Import youtube playlists")
    parser.add_argument("filepath", type=str, help="path to a valid .txt or .csv playlist file or files", nargs="*")
    parser.add_argument('-a', '--list-all',action='store_true', help="Takes all .txt and csv files as input from the current working directory.")
    parser.add_argument('-b', '--list-broken-videos',action='store_true', help="Lists videos that were added but have possibly broken metadata (for debugging).")
    parser.add_argument('-e', '--log-errors',action='store_true', help="Also lists the videos that failed the metadata fetch")

    flags = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    playlist_files = flags.filepath
    log_errors = flags.log_errors
    list_broken_videos = flags.list_broken_videos
    # list txt and csv files in current working directory
    if flags.list_all:
        playlist_files = []
        for i in os.listdir(os.getcwd()):
            if os.path.isfile(i):
                if i.split(".")[-1] in ("txt", "csv"):
                    playlist_files.append(i)

    if len(playlist_files) == 1:
        process_playlist(playlist_files[0], log_errors, list_broken_videos)
        exit(0)
    for i, playlist in enumerate(playlist_files, start=1):
        filename = str(Path(playlist).name)
        print(f"[{i}/{len(playlist_files)}] {filename}")
        try:
            process_playlist(playlist, log_errors, list_broken_videos)
        except Exception as e:
            logger.critical(f"{filename} Failed: {e}")
        print(" ")


if __name__ == "__main__":
    logging.basicConfig(format='[%(levelname)s] - %(message)s')
    logger = logging.getLogger(__name__)
    main()
