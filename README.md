# YouTube Music Utilities

## About

YTMUtils is a command line interface which helps you analyse and manage your YouTube Music library. It has functions such as displaying all your liked songs, searching for songs by lyrics, and more.

## Prerequisites

You need to have Python installed on your system to use YTMUtils. This program was developed and tested using Python `3.10.5`, however it should work on all Python versions `>=3.10`. Older versions will be incompatible as the code makes use of match-case statements. To install python, visit https://www.python.org/downloads/.

The list of additional Python dependencies is in [`requirements.txt`](/requirements.txt). The `pip install` command below will automatically read this file and install all packages globally automatically. If you do not wish to install them globally, you should [use a virtual environment](https://docs.python.org/3/library/venv.html).

## Installation

First, clone the GitHub repository.
```shell
git clone git@github.com:kguzek/ytmutils.git
```
Then, enter the repository on your local machine, optionally activate a virtual environment, and install the dependencies using pip.
```shell
cd ytmutils
python -m pip install -r requirements.txt
```

## Usage

You can invoke the script just like any other Python script, using your Python 3 executable. In order to use the script your working directory must be in the repository root folder.
```shell
python ytmutils.py [command] <args>
```

## Authentication

On your first invocation of YTMUtils, you will be prompted to paste your request headers and the YouTube Music webpage should open in a new tab in your default browser. This is in order for the program to connect to the YouTube Music API as you, instead of having to log in every time.

You must open the developer console, find a request to an endpoint looking like `https://music.youtube.com/youtubei/v1/browse`, and copy its request headers. Then, return to the terminal and follow the instructions.
For more information, refer to the [YouTube Music API documentation](https://ytmusicapi.readthedocs.io/en/stable/setup.html).

## Commands

This is a list of all commands you can use on the command line. For more information on the various arguments you can use, run:
```shell
python ytmutils.py [command] --help
```
You can also view a list of all available commands by running:
```shell
python ytmutils.py --help
```

### `list`

This command outputs all songs that are in your library.

### `search <lyrics>`

This command searches for all songs which have lyrics that contain the provided phrase.


###### Thank you for reading!