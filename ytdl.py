#!/home/test/.local/venv_ytdl/bin/python

'''
last update 2024.0217
'''

import json
import argparse
import sys
import os
import time
import re

debug = False
playlistDB = None
testMode = False

def get_script_folder():
  import os

  file_path = os.path.realpath(__file__)
  folder_name = os.path.dirname(file_path)
  return folder_name

def get_db_file_path():
  return get_script_folder() + '/' + f'ytdl-playlist-DB.json'

def load_db():
  global playlistDB

  if playlistDB != None and len(playlistDB) != 0:
    return

  db_file = get_db_file_path()
  if os.path.exists(db_file):
    if os.path.getsize(db_file) == 0:
      playlistDB = dict()
      return
    else:
      with open(db_file, 'r') as fileObj:
        playlistDB = json.load(fileObj)
  else:
    open(db_file, 'a').close()
    playlistDB = dict()

def dump_db():
    global playlistDB

    load_db()

    print("\n==== Saved YouTube playlists ====")
    for key, value in playlistDB.items():
      print(f'{key}, {value}\n')

def save_db():
  global playlistDB

  db_file = get_db_file_path()
  with open(db_file, 'w') as fileObj:
    json.dump(playlistDB, fileObj)

def get_split_char(word_pair):
  for char in [ ':', '：' ]:
    if word_pair.find(char) != -1:
      return char

def get_playlist_title(playlistURL):
  from pytube import Playlist

  pl =  Playlist(playlistURL)
  return pl.title

def playlist_exists(playlistURL):
  global playlistDB

  load_db()

  for nickname, value in playlistDB.items():
    url = value['url']
    if playlistURL == url:
      return True

  return False

# return [ True, nickname ] if playlist exists
def playlist_exists_URL(playlistURL):
  global playlistDB

  load_db()

  for nickname, value in playlistDB.items():
    url = value['url']
    if playlistURL == url:
      return [ True, nickname ]

  return [ False, '' ]

def nickname_exists(name):
  global playlistDB

  load_db()

  for nickname in playlistDB.keys():
    if name == nickname:
      return True

  return False

def add_new_playlist(descriptionList):
  global playlistDB

  load_db()

  need_to_update = False
  print(f"Add new playlist:")
  for description in descriptionList:
    split_char = ','
    print(f"  description={description}")

    try:
      nickname, playlistURL = description.split(split_char)
    except:
      print("  !!! exception occured !!!")
      continue

    title = get_playlist_title(playlistURL) # 從 youtube 重新取得 playlist 的 title
    key = nickname

    playlistUrlExists, oldNickname = playlist_exists_URL(playlistURL)
    if playlistUrlExists:
      if nickname != oldNickname:
        need_to_update = True
        del playlistDB[oldNickname]
        playlistDB[key]={'title':title, 'url':playlistURL}
        print(f"  [{nickname}] --> [{title}],{playlistURL} 的記錄已更新!")
    else:
      need_to_update = True
      playlistDB[key]={'title':title, 'url':playlistURL}
      print(f"  [{nickname}] --> [{title}],{playlistURL} 的記錄已更新!")

  if need_to_update:
    save_db()
  print()

def remove_playlist(nicknameList):
  global playlistDB

  load_db()

  need_to_update = False
  print("Remove playlist:")
  for nickname in nicknameList:
    if nickname in playlistDB.keys():
      need_to_update = True
      title = playlistDB[nickname]['title']
      url = playlistDB[nickname]['url']
      del playlistDB[nickname]
      print(f"  {nickname} --> [{title}]:{url} 的記錄已移除!")
    else:
      print(f"\t 無此 {nickname} 的記錄!")

#  print(device_db)
#  print()

  if need_to_update:
    save_db()
  print()

def strToBool(it):
  availableDict = { 'true':True, 'True':True, 'TRUE':True, 'false':False, 'False':False, 'FALSE':False }
  for k, v in availableDict.items():
    if  it == k:
      return v
  return False

def reterivePlaylistData(playlistURL, jsonFile):
  import youtube_dl
  ydl_opts = {
    'dump_single_json': True,
    'extract_flat': True,
  }

  with youtube_dl .YoutubeDL(ydl_opts) as ydl:
    result = ydl.extract_info(playlistURL, False)

  with open(jsonFile, 'w') as fnObj:
    json.dump(result['entries'], fnObj)
  return (result['entries'])

def download_media_as_mp4(title, url, dateString):
  from pytube import YouTube
  from moviepy.editor import AudioFileClip
  from moviepy.editor import VideoFileClip

  #print(f'dateString={dateString}')
  fileName = dateString + '.' + re.sub(r'([0-9]{4})[./-]?([0-9]{2})[./-]?([0-9]{2})', r'\1\2\3', title)
  print(f'  fileName="{fileName}"', end='')

  if not os.path.exists(fileName + ".mp4"):
    yt = YouTube(url)
    #yt.streams.filter(adaptive=True, subtype="mp4", abr="128kbps").last().download(filename=fileName+'.mp4')
    videoFile = fileName + ".mp4" + ".video"
    audioFile = fileName + ".mp4" + ".audio"
    if not os.path.exists(videoFile):
      yt.streams.filter(adaptive=True, subtype="mp4", res="1080p").first().download(filename=videoFile)
      print(f"    video part downloaded!")
    if not os.path.exists(audioFile):
      yt.streams.filter(only_audio=True).first().download(filename=audioFile)
      print(f"    audio part downloaded")
    video = VideoFileClip(videoFile)
    audio = AudioFileClip(audioFile)
    final = video.set_audio(audio)
    print(f"    video and audio part combined")
    final.write_videofile(fileName + ".mp4")
    os.remove(videoFile)
    os.remove(audioFile)
    print(" , Done !")

  else:
    print(", Exists !")

def download_media_as_mp4Low(title, url, dateString):
  from pytube import YouTube
  from moviepy.editor import AudioFileClip
  from moviepy.editor import VideoFileClip

  #print(f'dateString={dateString}')
  fileName = dateString + '.' + re.sub(r'([0-9]{4})[./-]?([0-9]{2})[./-]?([0-9]{2})', r'\1\2\3', title)
  print(f'  fileName="{fileName}"', end='')

  if not os.path.exists(fileName + ".mp4"):
    yt = YouTube(url)
    #yt.streams.filter(adaptive=True, subtype="mp4", abr="128kbps").last().download(filename=fileName+'.mp4')
    videoFile = fileName + ".mp4"
    if not os.path.exists(videoFile):
      yt.streams.filter(mime_type="video/mp4", subtype="mp4", res="480p").first().download(filename=videoFile)
      print(f"    video part downloaded!")
    print(" , Done !")

  else:
    print(" , Exists !")

def download_media_as_mp3(title, url, dateString):
  import pytube
  from pytube import YouTube
  from moviepy.editor import AudioFileClip

  #print(f'dateString={dateString}')
  fileName = dateString + '.' + re.sub(r'([0-9]{2,4})[./-]?([0-9]{2})[./-]?([0-9]{2})', r'\1\2\3', title)
  print(f'  fileName="{fileName}"', end='')

  if not os.path.exists(fileName + ".mp3"):
    yt = YouTube(url)
    #yt.streams.filter(adaptive=True, subtype="mp4", abr="128kbps").last().download(filename=fileName+'.mp4')
    mediaFile = None
    try:
      mediaFile = yt.streams.filter(adaptive=True, only_audio=True, abr="128kbps").last().download()
      print(" , Done !")
      #print(f'mediaFile ={mediaFile}')

    except pytube.exceptions.AgeRestrictedError as e:
      print(f"\n\nSomething went wrong: {str(e)}")
      print(f"yt = YouTube('{url}')\nmediaFile=yt.streams.filter(adaptive=True, only_audio=True, abr='128kps').last().download()\n")
  
    except:
      print(f"\n\nUnknown exception!")
      print(f"yt = YouTube('{url}')\nmediaFile=yt.streams.filter(adaptive=True, only_audio=True, abr='128kps').last().download()\n")
    
    if mediaFile != None and os.path.exists(mediaFile):
      media = AudioFileClip(mediaFile)
      media.write_audiofile(fileName + ".mp3")
      media.close()
      if os.path.exists(mediaFile):
        os.remove(mediaFile)
      print()
    else:
      print(f"Orz : mediaFile does not exists!\n")
      return
  else:
    print(", Exists !\n")

def fixDateString(date):
  date = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\1\2\3', date)
  year = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\1', date)
  month = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\2', date)
  day = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\3', date)

  if len(date) == 6:
    date = re.sub(r'([0-9]{4})([0-9]{1})([0-9]{1})', r'\1.0\2 0\3', date)
    date = re.sub(r' *', r'', date)
  if len(date) == 7:
    if re.match(r'[0-9]{4}(10|11|12)[0-9]{1}', date):
      date = re.sub(r'([0-9]{4})([0-9]{2})([0-9]{1})', r'\1.\2 0\3', date)
      date = re.sub(r' *', r'', date)
    else:
      date = re.sub(r'([0-9]{4})([0-9]{1})([0-9]{2})', r'\1.0\2 \3', date)
      date = re.sub(r' *', r'', date)
  if len(date) == 8:
    date = re.sub(r'([0-9]{4})([0-9]{2})([0-9]{2})', r'\1.\2\3', date)

  return date

def isDate(words):
  '''
  
  '''
  checkType = type(re.match(r'[0-9]{4}.[0-9]{4}', words))
  pass1 = True if checkType != type(None) else False

  if pass1 == False:
    return False

  if len(words) !=9:
    return False

  year = words[0:4]
  if int(year) < 2004 or int(year) > 2100:
    return False

  month = words[5:7]
  if int(month) <= 0 or int(month)>12:
    return False

  day = words[7:9]
  if int(day) <= 0 or int(day)>31:
    return False
  
  result = True
  if debug == True:
    print(f"    isDate(\"{words}\") ==> {result}")
  return result

def getDateString(string):
  begin = string.find('【')
  if begin != -1:
    end = string.find('】') + 1
    banner = string[begin:end]
    string = string.replace(banner, '')

#  string = re.sub(r'[^0-9./-]*', '', string)

  result = re.search(r'(\d{4})[./-]?(\d{1,2})[./-]?(\d{1,2})', string)
  if result != None:
    year = result.group(1)

    month = result.group(2)
    if len(month) == 1:
      month = '0' + month

    day = result.group(3)
    if len(day) == 1:
      day = '0' + day

    date = f"{year}.{month}{day}"

    if debug == True:
      print(f"\ndateFromString={date}")

    return date
  else:
    string = re.sub(r'([^0-9]*)([0-9]{2,4})([./-]?)([0-9]{1,2})([./-]?)([0-9]{1,2})([^0-9]*)([0-9]*)([^0-9]*)$', r'\2\4\6', string)

    date = re.sub(r'(.*)([0-9]{2,4})([./-]+)([0-9]{1,2})([./-]+)([0-9]{1,2})(.*)', r'\2\3\4\5\6', string)

  if debug == True:
    print(f"\ndateFromString={date}")

  year = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\1', date)
  month = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\2', date)
  if len(month) == 1:
    month = '0' + month

  day = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\3', date)
  if len(day) == 1:
    day = '0' + day

  if len(year) == 2:
    year = "20" + year
  date = f"{year}.{month}{day}"

  #print(f"y={year} m={month} d={day}")

  return date

def fixTitle(string):
  global testMode

  # Remove date string
  string = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', '', string)

  # Remove unwanted characters
  string = re.sub(r'[:#@\' ]*', r'', string)
  #string = re.sub(r'^ *', '', string)
  #string = re.sub(r' *$', '', string)
  #string = re.sub(r"'", '', string)

  # Remove Unwanted string or characters
  removeList = ['News98', '中廣流行網', '國立自然科學博物館館長', '國立自然科學博物館長', '國立科學博物館館長', '國立科博館館長', '國立科博館']
  for words in removeList:
    string = string.replace(words, '')

  begin = string.find('【')
  if begin != -1:
    end = string.find('】') + 1
    banner = string[begin:end]
    string = string.replace(banner, '')

  # Substitue / to -
  string = re.sub(r'/', r'-', string)
  #print(f'  title={string}')

  if testMode == False:
    if len(string) > 50:
      string = string[0:49] # 只取前32個字,避免檔太長
  return string

def youtube_url_downloader(url, format):
  from pytube import YouTube

  yt = YouTube(url)
  title = yt.title

  # remove date string
  title = fixTitle(title)

  date = yt.publish_date.strftime('%Y.%m%d')

  print(f"Date:{date} Title:{title}")
  print(f"  URL={url}\n  Downloading ...")

  if format.lower() == "mp3":
    download_media_as_mp3(title, url, date)
  else:
    download_media_as_mp4(title, url, date) 

def youtube_playlist_downloader(keywords, playlistURL, count, format):
  '''
  '''
  from pytube import YouTube
  from pytube import Playlist
  global testMode

  pl =  Playlist(playlistURL)
  if playlist_exists(playlistURL) == False:
    title = fixTitle(pl.title)
    description = f"{title},{playlistURL}"
    add_new_playlist([description])

  jsonFile = pl.title + '.json'
  if debug == True:
    print(f"jsonFile={jsonFile}")

  if os.path.exists(jsonFile):
    # check if file is fresh
    lastModTime = os.path.getmtime(jsonFile)
    currUnixTime = time.time()
    if (currUnixTime - lastModTime) < 86400:
      with open(jsonFile, 'r') as fnObj:
        entries = json.load(fnObj)
    else:
      entries = reterivePlaylistData(playlistURL, jsonFile)
  else:    
    entries = reterivePlaylistData(playlistURL, jsonFile)

  counter = 0
  keywordToDate = ''
  for entry in entries:
    pattern = r'^.*([0-9]{4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2}).*$'
    title = entry['title']
    url = "https://www.youtube.com/watch?v=" + entry['url']

    #date = fixDateString(re.sub(pattern, r'\1.\2\3', title))
    #if date == title:
    yt = YouTube(url)
    dateFromTitle = getDateString(title)

    #date = dateFromTitle if isDate(dateFromTitle) else yt.publish_date.strftime('%Y.%m%d')
    if isDate(dateFromTitle):
      #print(f"date from Title!! {dateFromTitle}")
      date = dateFromTitle
    else:
      date = yt.publish_date.strftime('%Y.%m%d')

    #print(f"title={title}")
    #print(f"dateFromTitle={dateFromTitle}")
    #print(f"date={date}")

    title = fixTitle(title)

    #print(f"\nDate:{date} Title:{title}")

    all_keywords_matched = True
    
    try:
      for keyword in keywords:
        #print('.', end='')
        if debug == True:
          print(f"  checking {keyword}")

        keywordIsDate = isDate(keyword)
        #print(f'\tkeywordIsDate={keywordIsDate}')
        if keywordIsDate == True:
          keywordToDate = fixDateString(keyword)
          if debug == True:
            print(f'    keywordToDate={keywordToDate}')
          if date != keywordToDate:
            all_keywords_matched = False
            if debug == True:
              print(f'    date:{date} NOT MATCH keyword:{keywordToDate} --> BREAK testing keywords')
            break
          else:
            if debug == True:
              print(f'    date:{date} MATCH keyword:{keywordToDate} --> CONTINUE testing keywords')
            continue
        else:
          if not keyword in title:
            all_keywords_matched = False
            if debug == True:
              print(f'    {keyword} NOT IN {title} --> BREAK testing keywords')
            break
          else:
            if debug == True:
              print(f'    {keyword} IN {title}')
    except:
      # Whenever no keywords were given
      print('',end='')

    if all_keywords_matched == False:
      continue

    print(f"Date:{date} Title:{title}")

    if testMode == False:
      if format.lower() == "mp3":
        print(f"  URL={url}\n  Downloading ... ")
        download_media_as_mp3(title, url, date)
      else:
        print(f"  URL={url}\n  Downloading ... ")
        download_media_as_mp4(title, url, date)

      counter+=1
      if counter == count:
        return
      
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='YouTube video downloader')
  parser.add_argument('-u', '--url', type=str, default='', help='YouTube video URL')
  parser.add_argument('-k', '--keywords', nargs='+', required=False, help='keyword')
  parser.add_argument('-p', '--playlistURL', type=str, default='', help='YouTube playlist URL')
  parser.add_argument('-c', '--count', type=int, default=1, help='Number of videos to be download')
  parser.add_argument('-n', '--playlistName', type=str, default='', help='YouTube playlist name')
  parser.add_argument('-f', '--format', type=str, default='mp3', help='media format to save -- mp3/mp4')
  parser.add_argument('-D', '--debug', action='store_true', default=False, help='Enable debug message or not')
  parser.add_argument('-a', '--add_new_playlist', nargs='+', required=False, help='add new YouTube playlist to DB')

  parser.add_argument('-r', '--remove_playlist', nargs='+', required=False, help='remove YouTube playlist from DB')

  parser.add_argument('-d', '--dump_playlistDB', action='store_true', required=False, help='dump playlistDB')

  parser.add_argument('-i', '--importDB', action='store_true', required=False, help='import internalDB')

  parser.add_argument('-t', '--test_mode', action='store_true', default=False, help='Test Mode -- File downloading is disabled')
  
  args = parser.parse_args()

  if len(sys.argv) == 1:
    parser.print_help()
    exit()

  debug = args.debug
  count = args.count
  format = args.format
  playlistName = args.playlistName
  testMode = args.test_mode

  if debug == True:
    print(f"debug={debug}")
    print(f"count={count}")
    print(f"format={format}")

  if args.add_new_playlist != None:
    print(f"add_new_playlist={args.add_new_playlist}")
    print()
    add_new_playlist(args.add_new_playlist)
    exit()

  if args.remove_playlist != None:
    print(f"remove_play_list={args.remove_playlist}")
    print()
    remove_playlist(args.remove_playlist)
    exit()

  url = args.url
  if not url == '' and debug == True:
    print(f"url={url}")

  keywords = args.keywords
  if not keywords == None and not keywords == '' and debug == True:
    print(f"keywords={keywords}")

  playlistURL = args.playlistURL
  if not playlistURL == '' and debug == True:
    print(f"playlistURL={playlistURL}")

  print()

  if url != '':
    youtube_url_downloader(url, format)
    exit()

  if playlistURL != "":
    youtube_playlist_downloader(keywords, playlistURL, count, format)

  playlistDBx = [
    { 'name' : "蘭萱時間",
      'url' : "https://www.youtube.com/playlist?list=PLEnJD0ANVhtU8K0MNeNsvGH-Q7k25VUd-",
      'comment' : "" },
    { 'name' : "朱紅樓夢",
      'url' : "https://www.youtube.com/playlist?list=PLY1N4123UnFEU_XB07WecFpXjTWvNUztU",
      'comment' : "朱嘉雯老師講紅樓夢" },
    { 'name' : "朱蘇東坡",
      'url' : "https://www.youtube.com/playlist?list=PLY1N4123UnFGheRdyjVrc_PnC5oAmMClR",
      'comment' : "朱嘉雯老師講蘇東坡" },
    { 'name' : "蔣勳說唐詩",
      'url' : "https://www.youtube.com/playlist?list=PLfUDQnw6Q8E6TX4X0aAyT1Tkj8fChSyM0",
      'comment' : "" },
    { 'name' : "蔣勳新說紅樓夢",
      'url' : "https://www.youtube.com/playlist?list=PLfUDQnw6Q8E5xeKtHBERovS6B6moFU-zn",
      'comment' : "" },
    { 'name' : "蔣勳孤獨六講",
      'url' : "https://www.youtube.com/playlist?list=PLfUDQnw6Q8E7-0Dl7CQzP4tSh3tkfjsfk",
      'comment' : "" },
    { 'name' : "蔣勳中國文學",
      'url' : "https://www.youtube.com/playlist?list=PLfUDQnw6Q8E5ii1ijeoLx3ENbQZpn34wW",
      'comment' : "" },
    { 'name' : "聽醫生的話",
      'url' : "https://www.youtube.com/playlist?list=PLEnJD0ANVhtXVoLZ5NeJtDCBp0ii8-LsR",
      'comment' : "" },
    { 'name' : "幸福好時光",
      'url' : "https://www.youtube.com/playlist?list=PLEnJD0ANVhtXqYR35gXcp8E-dLfiq6O-3",
      'comment' : "" },
    { 'name' : "科學史沙龍1",
      'url' : "https://www.youtube.com/playlist?list=PLil-R4o6jmGj0rwTK9T91zgX5iKj7Unto",
      'comment' : "科學講古列車" },
    { 'name' : "科學史沙龍2",
      'url' : "https://www.youtube.com/playlist?list=PLil-R4o6jmGg5orDjrjsgF7AjaeAqVamP",
      'comment' : "2014-2018" },
    { 'name' : "科學史沙龍2019",
      'url' : "https://www.youtube.com/playlist?list=PLil-R4o6jmGhO-AmWtLkBLqJQZVhXWFt4",
      'comment' : "2019" },
    { 'name' : "科學史沙龍2020",
      'url' : "https://www.youtube.com/playlist?list=PLil-R4o6jmGikYwk9DcuIwrIVgeNZHYLn",
      'comment' : "2020" },
    { 'name' : "科學史沙龍2021",
      'url' : "https://www.youtube.com/playlist?list=PLil-R4o6jmGj2DyhnFXVFZADgnPYan0kY",
      'comment' : "2021" },
    { 'name' : "科學史沙龍2022",
      'url' : "https://www.youtube.com/playlist?list=PLil-R4o6jmGjxRKafwR7o0Lwmjg12ENIx",
      'comment' : "2022" },
    { 'name' : "科學史沙龍2023",
      'url' : "https://www.youtube.com/playlist?list=PLil-R4o6jmGjlIC2jwHfoUUgq21-hRb_n",
      'comment' : "2023" },
    { 'name' : "熱血科學家",
      'url' : "https://www.youtube.com/playlist?list=PLio8ImdYUsYh3_WijW4Dh95HTfh4w89Nf",
      'comment' : "熱血科學家的閒話加長" }]


  if args.importDB == True:
    for item in playlistDBx:
      description = f"{item['name']},{item['url']}"
      add_new_playlist([description])

  if args.dump_playlistDB == True:
    dump_db()
    exit()

  if playlistName != '':
    print(f"playlistName={playlistName}")
    load_db()
    if nickname_exists(playlistName):
      playlistTitle = playlistDB[playlistName]['title']
      playlistURL = playlistDB[playlistName]['url']
      print(f"playlistTitle={playlistTitle}")
      print(f"playlistURL={playlistURL}")
      print(f"keywords={keywords}")
      youtube_playlist_downloader(keywords, playlistURL, count, format)
    else:
      print(f"No matched playlistName -- {playlistName} !!")



