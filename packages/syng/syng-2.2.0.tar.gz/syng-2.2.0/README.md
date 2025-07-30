<p align="center">
    <img src="https://raw.githubusercontent.com/christofsteel/syng/refs/heads/main/resources/icons/hicolor/512x512/apps/rocks.syng.Syng.png"
        height="130">

_Easily host karaoke events_
<p align="center">

[![Matrix](https://img.shields.io/matrix/syng%3Amatrix.org?logo=matrix&label=%23syng%3Amatrix.org)](https://matrix.to/#/#syng:matrix.org)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/113266262154630635?domain=https%3A%2F%2Ffloss.social&style=flat&logo=mastodon&logoColor=white)](https://floss.social/@syng)
[![PyPI - Version](https://img.shields.io/pypi/v/syng?logo=pypi)](https://pypi.org/project/syng/)
[![Flathub Version](https://img.shields.io/flathub/v/rocks.syng.Syng?logo=flathub)](https://flathub.org/apps/rocks.syng.Syng)
[![PyPI - License](https://img.shields.io/pypi/l/syng)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fsyng.rocks%2F&label=syng.rocks)](https://syng.rocks)
[![Forgejo Pipeline Status](https://git.k-fortytwo.de/christofsteel/syng/badges/workflows/check.yaml/badge.svg?logo=python&label=mypy%2Bruff)](https://git.k-fortytwo.de/christofsteel/syng)


**Syng** is an all-in-one karaoke software, consisting of a *backend server*, a *web frontend* and a *playback client*.
Karaoke performers can search a library using the web frontend, and add songs to the queue.
The playback client retrieves songs from the backend server and plays them in order.

You can play songs from **YouTube**, an **S3** storage or simply share local **files**.

The playback client uses [mpv](https://mpv.io/) for playback and can therefore play a variety of file formats, such as `mp3+cdg`, `webm`, `mp4`, ...

Join our [matrix room](https://matrix.to/#/#syng:matrix.org) or follow us on [mastodon](https://floss.social/@syng) for update notifications and support.

# Screenshots
<img src="https://raw.githubusercontent.com/christofsteel/syng/b963d09aee58531ab7ea61ddf04ee169fba57a63/resources/screenshots/syng.png" alt="Main Window" height=200/> <img src="https://raw.githubusercontent.com/christofsteel/syng/b963d09aee58531ab7ea61ddf04ee169fba57a63/resources/screenshots/syng_advanced.png" alt="Main Window (Advanced)" height=200/>

<img src="https://raw.githubusercontent.com/christofsteel/syng/b963d09aee58531ab7ea61ddf04ee169fba57a63/resources/screenshots/syng_web2.png" alt="Web Interface" height=200/> <img src="https://raw.githubusercontent.com/christofsteel/syng/b963d09aee58531ab7ea61ddf04ee169fba57a63/resources/screenshots/syng_mobile_search.png" alt="Web Interface on Mobile" height=200/> 

<img src="https://raw.githubusercontent.com/christofsteel/syng/b963d09aee58531ab7ea61ddf04ee169fba57a63/resources/screenshots/syng_player_next_up.png" alt="Player (next up)" height=200/> <img src="https://raw.githubusercontent.com/christofsteel/syng/b963d09aee58531ab7ea61ddf04ee169fba57a63/resources/screenshots/syng_player_song.png" alt="Player playing a song" height=200/>

# Client

[![Get in on Flathub](https://flathub.org/api/badge?locale=en)](https://flathub.org/apps/rocks.syng.Syng)

To host a karaoke event, you only need to use the playback client. You can use the publicly available instance at https://syng.rocks as your server.

## Installation

### Linux

The preferred way to install the client is via [Flathub](https://flathub.org/apps/rocks.syng.Syng).

Alternatively Syng can be installed via the _Python Package Index_ (PyPI). When installing the client it is mandatory to include the `client` flag:

    pip install 'syng[client]'

This installs both the playback client (`syng client`) and a configuration GUI (`syng gui`). 

**Note:** When installing via PyPI, you need to have [libmpv](https://mpv.io/) installed on machine of the playback client.

The Syng client is also packaged for Arch Linux in the [Arch Linux user repository](https://aur.archlinux.org/packages/syng-client)

### Windows

Windows support is experimental, but you can download the current version from [Releases](https://github.com/christofsteel/syng/releases). No installation necessary, you can just run the `exe`.


## Configuration

You can host karaoke events using the default configuration. But if you need more advanced configuration, you can either configure Syng using the GUI or via a text editor by editing `~/.config/syng/config.yaml`. There are the following settings:

  * `server`: URL of the server to connect to.
  * `room`: The room code for your karaoke event. Can be chosen arbitrarily, but must be unique. Unused rooms will be deleted after some time. _Note:_ Everyone, that has access to the room code can join the karaoke event.
  * `secret`: The admin password for your karaoke event. If you want to reconnect with a playback client to a room, these must match. Additionally, this unlocks admin capabilities to a web client, when given under "Advanced" in the web client.
  * `waiting_room_policy`: One of `none`, `optional`, `forced`. When a performer wants to be added to the playback queue, but has already a song queued, they can be added to the _waiting room_. `none` disables this behavior and performers can have multiple songs in the queue, `optional` gives the performer a notification, and they can decide for themselves, and `forced` puts them in the waiting room every time. Once the current song of a performer leaves the queue, the song from the waiting room will be added to the queue.
  * `last_song`: `none` or a time in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601). When a song is added to the queue, and its ending time exceeds this value, it is rejected.
  * `preview_duration`: Before every song, there is a short slide for the next performer. This sets how long it is shown in seconds.
  * `key`: If the server, you want to connect to is in _private_ or _restricted_ mode, this will authorize the client. Private server reject unauthorized playback clients, restricted servers limit the searching to be _client only_.
  * `buffer_in_advance`: How many songs should be buffered in advanced.
  * `qr_box_size`: The size of one box (think pixel) of the QR Code in the playback window.
  * `qr_position`: Position of the QR Code in the playback window. One of `bottom-left`, `bottom-right`, `top-left`, `top-right`.
  * `show_advanced`: Show advanced options in the configuration GUI.

In addition to the general config, has its own configuration under the `sources` key of the configuration.

### YouTube

Configuration is done under `sources` → `youtube` with the following settings:

  * `enabled`: `true` or `false`.
  * `channels`: list of YouTube channels. If this is a nonempty list, Syng will only search these channels, otherwise YouTube will be searched as a whole.
  * `tmp_dir`: YouTube videos will be downloaded before playback. This sets the directory, where YouTube videos are stored.
  * `max_res`: Maximum resolution of a video.
  * `start_streaming`: `true` or `false`. If `true`, videos will be streamed directly using `mpv`, if the video is not cached beforehand. Otherwise, Syng waits for the video to be downloaded.  
  * `seach_suffix`: A string that is appended to each search query. Default is "karaoke".
  * `max_duration`: Maximum length of accepted videos in seconds. Default is 1800 (30 minutes)

### S3

Configuration is done under `sources` → `s3` with the following settings:

  * `enabled`: `true` or `false`.
  * `extensions`: List of extensions to be searched. For karaoke songs, that separate audio and video (e.g. CDG files), you can use `mp3+cdg` to signify, that the audio part is a `mp3` file and the video is a `cdg` file. For karaoke songs, that do not separate this (e.g. mp4 files), you can simply use `mp4`.
  * `endpoint`: Endpoint of the s3.
  * `access_key` Access key for the s3.
  * `secret_key`: Secret key for the s3.
  * `secure`: If `true` uses `ssl`, otherwise not.
  * `bucket`: Bucket for the karaoke files.
  * `index_file`: Cache file, that contains the filenames of the karaoke files in the s3.
  * `tmp_dir`: Temporary download directory of the karaoke files.

### Files

Configuration is done under `sources` → `files` with the following settings:

  * `enabled`: `true` or `false`.
  * `extensions`: List of extensions to be searched. For karaoke songs, that separate audio and video (e.g. CDG files), you can use `mp3+cdg` to signify, that the audio part is a `mp3` file and the video is a `cdg` file. For karaoke songs, that do not separate this (e.g. mp4 files), you can simply use `mp4`.
  * `dir`: Directory, where the karaoke files are stored. 

### Default configuration

```
config:
  key: ''
  last_song: null
  preview_duration: 3
  room: <Random room code>
  secret: <Random secret>
  server: https://syng.rocks
  waiting_room_policy: none
  show_advanced: false
  buffer_in_advance: 2
  qr_box_size: 5
  qr_position: bottom-right
  next_up_time: 20
  
sources:
  files:
    dir: .
    enabled: false
    extensions:
    - mp3+cdg
  s3:
    access_key: ''
    bucket: ''
    enabled: false
    endpoint: ''
    extensions:
    - mp3+cdg
    index_file: ${XDG_CACHE_DIR}/syng/s3-index
    secret_key: ''
    secure: true
    tmp_dir: ${XDG_CACHE_DIR}/syng
  youtube:
    channels: []
    enabled: true
    start_streaming: false
    max_res: 720
    tmp_dir: ${XDG_CACHE_DIR}/syng
    search_suffix: karaoke
    max_duration: 1800
```

# Web client

The web client consists of three columns on desktop and three tabs on mobile:

- **Search:** Users can search for karaoke songs and get the results here. You can also directly add a YouTube video by using its link. Search results for YouTube videos have a second button to preview the song.
- **Queue:** Shows the current queue. The current song is highlighted at the top and each item is equipped with an ETA. If you are on an admin connection, you can drag and drop to change the order of the queue and delete items from the queue.
- **Recent:** This shows all previously played songs.

When connecting to the web client, you can give yourself a name with which your songs are queued. You can change your name by changing it in the footer. If no name is selected, a name is queried each time a song is added.

In the advanced options, you can add the admin password, that corresponds with the admin password on the playback client, to elevate this connection to an admin connection.

# Server

If you want to host your own Syng server, you can do that, but you can also use the publicly available Syng instance at https://syng.rocks.

## Python Package Index

You can install the server via pip:

    pip install syng

and then run via:

    syng server

The server is also automatically available if you install the client. 

There exists one optional dependency for the server: `alt-profanity-check`. If this package is installed, each username is checked for profanity, otherwise no such check happens.

## Docker

Alternatively you can run the server using docker. It listens on port 8080 and reads a key file at `/app/keys.txt` when configured as private or restricted.

    docker run --rm -v /path/to/your/keys.txt:/app/keys.txt -p 8080:8080 ghcr.io/christofsteel/syng -H 0.0.0.0

## Arch Linux

The Syng server is also packaged for Arch Linux in the [Arch Linux user repository](https://aur.archlinux.org/packages/syng-server)

## Configuration

Configuration is done via command line arguments, see `syng server --help` for an overview. 

## Public, Restricted, Private and keys.txt

Syng can run in three modes: public, restricted and private. This restricts which playback clients can start an event and what capabilities the event has.
This has no bearing on the web clients. Every web client, that has access to the room code can join the event. 
Authorization is done via an entry in the `keys.txt`

 - Public means, that there are no restrictions. Every playback client can start an event and has support for all features
 - Restricted means, that every playback client can start an event, but server side searching is limited to authorized clients. For unauthorized clients, a search request is forwarded to the playback client, that handles that search.
 - Private means, that only authorized clients can start an event.

The `keys.txt` file is a simple text file holding one `sha256` encrypted password per line. Passwords are stored as their hex value and only the first 64 characters per line are read by the server. You can use the rest to add comments.
To add a key to the file, you can simply use `echo -n "PASSWORD" | sha256sum | cut -d ' ' -f 1 >> keys.txt`.

