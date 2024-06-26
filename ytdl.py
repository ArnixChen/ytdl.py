#!/home/test/.local/venv_ytdl/bin/python


'''
#!/home/test/.local/venv3.10.8_audio/bin/python
last update 2024.0603

update list:
  2025.0603
  Add pytube.exceptions.LiveStreamError exception handler.
  Update helper messages.
  Update internal playlist DB.

  2025.0529
  Fix error on reading .json file while it is actually not exist.
  Fix error if playlistURL don't have https:// at its head.
  
  2025.0525
  Fix error if playlistURL don't have https:// at its head.

usage:

列出某個youtube playlist 的全部內容(用 -t 使用測試模式, 而不實際下載)
  ytdl.py -t -p https://www.youtube.com/playlist?list=PLS0SUwlYe8cwN1nni53vQ3uZVTksRokhu

下載某個youtube playlist 全部內容的音檔
  ytdl.py -p https://www.youtube.com/playlist?list=PLS0SUwlYe8cwN1nni53vQ3uZVTksRokhu

將某個youtube playlist 取名為「103生命科學一」,並加入 playlist 資料庫(取名與playlist URL之間用英文逗號連結)
以後下載該 playlist 的內容時,可以用「-n 名稱」取代 「-p 長長一串playlist網址」
  ytdl.py -a 103生命科學一,https://www.youtube.com/playlist?list=PLS0SUwlYe8cyzPZ3zagbHJNSPUcU0sTr7

將取名為「103生命科學一」的 youtube playlist ,自 playlist 資料庫移除
  ytdl.py -r 103生命科學一

列出所有目前有記錄的playlist資料
  ytdl.py -d

自取名為「103生命科學一」的 playlist 中,下載全部內容的音檔
  ytdl.py -n 103生命科學一

將此 playlist https://www.youtube.com/playlist?list=PLEnJD0ANVhtXVoLZ5NeJtDCBp0ii8-LsR
加入 playlist資料庫,並取名為「聽醫生的話」
  ytdl.py -a 聽醫生的話,https://www.youtube.com/playlist?list=PLEnJD0ANVhtXVoLZ5NeJtDCBp0ii8-LsR

自取名為 聽醫生的話 的 playlist 中,查詢所有標題有「腎」關鍵字的內容
  ytdl.py -n 聽醫生的話 -t -k 腎

自取名為 聽醫生的話 的 playlist 中,查詢所有標題有「腎」及「醫師」關鍵字的內容（關鍵字之間用空白區格)
  ytdl.py -n 聽醫生的話 -t -k 腎 醫師

  playlistName=聽醫生的話
  playlistTitle=聽醫生的話／李雅媛、潘懷宗
  playlistURL=https://www.youtube.com/playlist?list=PLEnJD0ANVhtXVoLZ5NeJtDCBp0ii8-LsR
  keywords=['腎']
  Date:2024.0119 Title:icarebcc健康SAYYES｜硬水會造成腎結石？預防腎結石怎麼做？｜潘懷宗＋黃巧妮
  Date:2023.1101 Title:自我檢查！從小便顏色看健康｜專訪：台中童綜合醫院腎臟科簡孝文醫師｜聽醫生的話｜李雅媛
  Date:2023.0823 Title:夏日抗濕疹中醫小叮嚀肝腎保健穴位自己按｜專訪：新店耕莘醫院中醫科主任黃書澐醫師｜聽醫生的話｜李雅媛
  Date:2023.0627 Title:看尿酸看錯科了？痛風破壞腎恐引發尿毒症｜專訪：台中童綜合醫院腎臟科主治醫師簡孝文｜李雅媛
  Date:2023.0525 Title:嘴巴身體有尿騷味小心腎病找上你｜專訪：衛福部立桃園醫院副院長王偉傑醫師｜李雅媛


自取名為 聽醫生的話 的 playlist 中,「下載第1筆」標題有「腎」及「醫師」關鍵字的內容的音檔（-c參數預設值為1)
  ytdl.py -n 聽醫生的話 -k 腎 醫師

自取名為 聽醫生的話 的 playlist 中,「下載全部」標題有「腎」及「醫師」關鍵字的內容的音檔（-c參數設為0, 代表下載全部)
  ytdl.py -n 聽醫生的話 -k 腎 醫師 -c 0

下載指定 youtube playlist https://www.youtube.com/playlist?list=PLEnJD0ANVhtU8K0MNeNsvGH-Q7k25VUd-
中有關鍵字 沈雲驄 及 2023.07.18 的內容 的音檔

  ytdl.py -k 沈雲驄 2023.07.18 -p https://www.youtube.com/playlist?list=PLEnJD0ANVhtU8K0MNeNsvGH-Q7k25VUd-

下載 指定 playlist 中的前8筆內容 的音檔
  ytdl.py -c 8 -p https://www.youtube.com/playlist?list=PLfUDQnw6Q8E7-0Dl7CQzP4tSh3tkfjsfk

給定youtube 連結,直接下載 內容 的音檔
  ytdl.py -u https://www.youtube.com/watch?v=3TZIKISbZvc

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
  
  if not 'https://' in playlistURL:
    playlistURL = 'https://' + playlistURL

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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
  import errno

  #print(f'dateString={dateString}')
  fileName = dateString + '.' + re.sub(r'([0-9]{2,4})[./-]?([0-9]{2})[./-]?([0-9]{2})', r'\1\2\3', title)
  print(f'  fileName="{fileName}"', end='')

  if not os.path.exists(fileName + ".mp3"):
    yt = YouTube(url)
    #yt.streams.filter(adaptive=True, subtype="mp4", abr="128kbps").last().download(filename=fileName+'.mp4')
    mediaFile = None

    try:
      stream = yt.streams.filter(adaptive=True, only_audio=True, abr="128kbps").last()
      mediaFile = stream.download()
      print(" , Done !")
      #print(f'mediaFile ={mediaFile}')

    except pytube.exceptions.AgeRestrictedError as e:
      print(f"\n\nSomething went wrong: {str(e)}")
      print(f"yt = YouTube('{url}')\nmediaFile=yt.streams.filter(adaptive=True, only_audio=True, abr='128kps').last().download()\n")
          
    except pytube.exceptions.LiveStreamError as e:
      print(f"\n\nLive Streaming cannot be download: {str(e)}")
      print(f"yt = YouTube('{url}')\nmediaFile=yt.streams.filter(adaptive=True, only_audio=True, abr='128kps').last().download()\n")

    except OSError as e:
      if e.errno == errno.ENAMETOOLONG:
        try:
          filename = stream.title[0:80] + '.' + stream.subtype
          mediaFile = stream.download(filename=filename)
        except:
          print(f"\n\nOSError exception!")
          print(f"yt = YouTube('{url}')\nmediaFile=yt.streams.filter(adaptive=True, only_audio=True, abr='128kps').last().download('filename={filename}')\n")
  
    except Exception as e:
      print(f"\n\nUnknown exception!")
      print(f"\n{e}")
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
  checkType = type(re.match(r'[0-9]{4}[./-]?[0-9]{2}[./-]?[0-9]{2}', words))
  pass1 = True if checkType != type(None) else False

  if pass1 == False:
    return False

  if len(words) !=9 and len(words) !=10:
    return False
    
  year = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\1', words)
  month = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\2', words)
  day = re.sub(r'([0-9]{2,4})[./-]?([0-9]{1,2})[./-]?([0-9]{1,2})', r'\3', words)

  #year = words[0:4]
  if int(year) < 2004 or int(year) > 2100:
    return False

  #month = words[5:7]
  if int(month) <= 0 or int(month)>12:
    return False

  #day = words[7:9]
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

    date = f"{year}.{month}.{day}"

    if debug == True:
      print(f"\ndateFromString={date}")

    return date
  else:
    string = re.sub(r'([^0-9]*)([0-9]{2,4})([./-]?)([0-9]{1,2})([./-]?)([0-9]{1,2})([^0-9]*)([0-9]*)([^0-9]*)$', r'\2\4\6', string)

    date = re.sub(r'(.*)([0-9]{2,4})([./-]+)([0-9]{1,2})([./-]+)([0-9]{1,2})(.*)', r'\2\3\4\5\6', string)

  if debug == True:
    print(f"\ngetDateString() dateFromString={date}")

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

  removeList = ['News98', '中廣流行網', '國立自然科學博物館館長', '國立自然科學博物館長', '國立科學博物館館長', '國立科博館館長', '國立科博館', '飛碟聯播網']
  
  for words in removeList:
    string = string.replace(words, '')
  
  #移除 粗體括號圍起來的文字 【健康醫療 單元】
  if False:
    begin = string.find('【')
    if begin != -1:
      end = string.find('】') + 1
      banner = string[begin:end]
      string = string.replace(banner, '')

  # Substitue / to -
  string = re.sub(r'/', r'-', string)
  #print(f'  title={string}')

  if testMode == False:
    if len(string) > 70:
      string = string[0:69] # 只取前32個字,避免檔太長
  return string

def youtube_url_downloader(url, format):
  from pytube import YouTube

  yt = YouTube(url)
  url = yt.watch_url
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
    jsonFileSize = os.path.getsize(jsonFile)     
    if debug == True:
      print(f"jsonFileSize={jsonFileSize}")
    if not jsonFileSize == 0:
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
  '''
      sign = sign + 1
    
    if (sign % 4) == 0:
      print("\r|", end="")
    elif (sign % 4) == 1:
      print("\r/", end="")
    elif (sign % 4) == 2:
      print("\r-", end="")
    elif (sign % 4) == 3:
      print("\r\\", end="")
  '''
  
  #signList = [ '꜈', '꜉', '꜊', '꜋', '꜌', '꜑', '꜐', '꜏', '꜎', '꜍']
  signList = [ '˥', '˦', '˧', '˨', '˩', '꜖', '꜕', '꜔', '꜓', '꜒']
  sign = 0;
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
      try:
        date_orig = yt.publish_date
        #print(f"{date_orig}")
        date = date_orig.strftime('%Y.%m%d')
      except:
        pass
      
      #date = yt.publish_date.strftime('%Y.%m%d')

    date = fixDateString(date)
    #print(f"title={title}")
    #print(f"dateFromTitle={dateFromTitle}")
    #print(f"date={date}")

    title = fixTitle(title)

    #print(f"\nDate:{date} Title:{title}")

    all_keywords_matched = True
    
    try:
      for keyword in keywords:
        print(f"\r{signList[sign%10]}", end="")
        sign = sign + 1
        #print('.', end='')
        if debug == True:
          print(f"  checking {keyword}")

        keywordIsDate = isDate(keyword)
        if debug == True:
          print(f'\tkeywordIsDate={keywordIsDate}')
          
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

    print(f"\rDate:{date} Title:{title}")

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
  parser.add_argument('-u', '--url', type=str, default='', help='Download YouTube video with video URL')
  parser.add_argument('-k', '--keywords', nargs='+', required=False, help='keywords seperated by space')
  parser.add_argument('-p', '--playlistURL', type=str, default='', help='Download from YouTube playlist with URL')
  parser.add_argument('-c', '--count', type=int, default=1, help='Number of videos to be download')
  parser.add_argument('-n', '--playlistName', type=str, default='', help='Download  from YouTube playlist with playlist name listed in DB')
  parser.add_argument('-f', '--format', type=str, default='mp3', help='media format to save -- mp3/mp4')
  parser.add_argument('-D', '--debug', action='store_true', default=False, help='Enable debug message or not')
  parser.add_argument('-a', '--add_new_playlist', nargs='+', required=False, help='add new YouTube playlist to DB')

  parser.add_argument('-r', '--remove_playlist', nargs='+', required=False, help='remove YouTube playlist from DB')

  parser.add_argument('-d', '--dump_playlistDB', action='store_true', required=False, help='dump playlistDB')

  parser.add_argument('-i', '--importDB', action='store_true', required=False, help='import playlist DB from script build-in list')

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
    { 'name' : "張大春",
      'url' : "https://www.youtube.com/playlist?list=PL0VpXJuJSa7cGjKnKrK2vYLMQrjGtzcQm",
      'comment' : "張大春泡新聞" },
    { 'name' : "飛碟早餐",
      'url' : "https://www.youtube.com/playlist?list=PLp3iy78ZeKcLJP6rVufLRWZRhDGqoKCrS",
      'comment' : "飛碟早餐 唐湘龍時間" },
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
      print()
      youtube_playlist_downloader(keywords, playlistURL, count, format)
    else:
      print(f"No matched playlistName -- {playlistName} !!")
