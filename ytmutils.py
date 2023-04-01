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


update_cache_option = click.option(
    "--update-cache",
    "-u",
    is_flag=True,
    default=False,
    help="Forces the library to be retrieved from the YouTube API.",
)


@click.group()
def cli():
    """The base command for YouTube Music library management."""


@cli.command(short_help="Searches in the user's library.")
@click.option(
    "--ignore-case",
    "-i",
    is_flag=True,
    help="Whether or not the search should be case-insensitive.",
)
@click.option(
    "--exclude",
    "-x",
    is_flag=True,
    help="Shows all results except for the matches.",
)
@update_cache_option
@click.argument("search_query")
# pylint: disable=missing-function-docstring
def search(**kwargs):
    analyser.search(**kwargs)


@cli.command("list", short_help="Lists all songs.")
@update_cache_option
def list_songs(update_cache: bool):
    """Lists all songs in the user's library."""
    songs = analyser.get_songs(update_cache)
    for song in songs:
        click.echo(serialise_song(song))
    click.echo(pluralise("result", len(songs)))


if __name__ == "__main__":
    cli()
