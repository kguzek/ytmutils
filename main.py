#!/usr/bin/env python
"""The entry point for accessing the YT Music API."""

import os
import webbrowser

import click
from ytmusicapi import YTMusic

from yt_music_analyser import YTMusicAnalyser


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


@cli.command(short_help="Searches in the user's library.")
@click.option(
    "--ignore-case",
    "-i",
    is_flag=True,
    help="Whether or not the search should be case-insensitive.",
)
@click.option(
    "--exclude", "-x", is_flag=True, help="Shows all results except for the matches."
)
@click.argument("query")
def search(query: str, ignore_case: bool, exclude: bool):
    """Searches for the given string in all songs within the user's library."""
    analyser.search(query, ignore_case, exclude)


if __name__ == "__main__":
    cli()
