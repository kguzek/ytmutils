#!/usr/bin/env python
"""The entry point for accessing the YT Music API."""

import os
import webbrowser

import click
from ytmusicapi import YTMusic

from modules.yt_music_wrapper import YTMusicAnalyser
from modules.util import serialise_song, pluralise

HEADERS_AUTH_FILENAME = "headers_auth.json"


def log_in() -> YTMusic:
    """Attempts to use the provided credentials, or prompts the user to generate them."""
    if not os.path.exists(HEADERS_AUTH_FILENAME):
        webbrowser.open("https://music.youtube.com/explore")
        YTMusic.setup(HEADERS_AUTH_FILENAME)
    try:
        ytmusic = YTMusic(HEADERS_AUTH_FILENAME)
    except AttributeError as error:
        click.echo("Invalid headers auth file.", error)
        ytmusic = None
    return ytmusic


analyser = YTMusicAnalyser(log_in())


@click.group()
def cli():
    """The base command for YouTube Music library management."""


cli.add_command(YTMusicAnalyser.search)


@cli.command("list", short_help="Lists all songs.")
def list_songs():
    """Lists all songs in the user's library."""
    for song in analyser.songs:
        click.echo(serialise_song(song))
    click.echo(pluralise("result", len(analyser.songs)))


if __name__ == "__main__":
    cli()
