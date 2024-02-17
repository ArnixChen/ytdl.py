# ytdl.py
Yet another command line YouTube downloader.

## Installation
### Create virtual environment
```bash
python3 -m venv ~/.local/venv_ytdl
```
### Upgrade pip
```bash
pip install --upgrade pip
```
### Install requirements
```bash
pip install -r requirements.txt
```
### Copy ytdl.py to your local bin folder
```bash
cp ytdl.py ~/.local/bin
chmod u+x ~/.local/bin/ytdl.py
```

## Examples of YouTube media downloading.
### Get media from a YouTube link URL.
```bash
ytdl.py -u <your YouTube link URL>
```
### List all medias from a YouTube Playlist.
... -t means just testing , no downloading.
```bash
ytdl.py -p <your YouTube Playlist URL> -t
```
### List all medias from a YouTube Playlist with some keywords matched.
Keywords are seperated by space.
```bash
ytdl.py -p <your YouTube Playlist URL> -t -k keyword1 keyword2
```
### Download the first media from a YouTube Playlist with keywords.
... remove -t parameter, then downloading begin.
... By default, ytdl.py will just download the audio part of medias to mp3
... If you needs video downloading, use parameter -f mp4 (very slow)
```bash
ytdl.py -p <your YouTube Playlist URL> -k keyword1 keyword2
```
### Download the first 3 media from a YouTube Playlist with keywords.

... parameter -c controls the amount of medias to be download, and its default value is 1.
```bash
ytdl.py -p <your YouTube Playlist URL> -k keyword1 keyword2 -c 3
```

### Download all medias from a YouTube Playlist with keywords matched.

... Give parameter -c to 0 means download all medias.

```bash
ytdl.py -p <your YouTube Playlist URL> -k keyword1 keyword2 -c 0
```
## Use nickname instead of a long YouTube playlist URL
### Give YouTube playlist URL a nickname to simplify your download command.

```bash
# paremeter -a could be used to register or update nickname of YouTube Playlist
# Note: A comma is used to seperate nickname with YouTube Playlist URL.
ytdl.py -a <nickname>,<your YouTube Playlist URL>

# Then you can do all above jobs with nickname like this.
ytdl.py -n <nickname> -k keyword1 keyword2 -c 0
```
### Dump all registered YouTube playist URL.
```bash
ytdl.py -d
```

### Remove registered playlist with nickname
```bash
ytdl.py -r <nickname>
```
