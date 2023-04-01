"""Module containing the API wrapper for YouTube Music."""

import json
import time
from types import SimpleNamespace

import click
from ytmusicapi import YTMusic


def serialise_song(song: dict) -> str:
    """Serialises the song to a more human-readable format."""
    artist_names = ", ".join(artist["name"] for artist in song["artists"])
    artist_names = click.style(artist_names, fg="bright_yellow")
    prefix = song.get("prefix", "")
    song_title = click.style(song["title"], fg="bright_cyan")
    song_album = click.style(song["album"]["name"], fg="bright_magenta")
    return f"{prefix}{artist_names} - {song_title} ({song_album})"


class YTMusicAnalyser:
    """Class for the analyser functionality."""

    def __init__(self, ytmusic: YTMusic | None):
        if ytmusic is None:
            return
        self.ytmusic = ytmusic
        self.songs = self._read_all_songs()

    def _fetch_all_songs(self) -> list[dict]:
        """Fetches all songs in the user's library and outputs them to `songs.json`."""
        songs = self.ytmusic.get_library_songs(limit=None)
        click.echo(songs)
        with open("songs.json", "w", encoding="utf-8") as file:
            json.dump(songs, file, indent=2, ensure_ascii=False)
        return songs

    def _read_all_songs(self) -> list[dict]:
        """Reads the user's library or makes a request to retrieve it."""
        try:
            with open("songs.json", "r", encoding="utf-8") as file:
                songs = json.load(file)
        except FileNotFoundError:
            songs = self._fetch_all_songs()
        return songs

    def _get_search_results(
        self, search_query: str, ignore_case: bool, exclude: bool
    ) -> list[bool]:
        """Goes through the user's songs and matches the search query with multiple properties."""

        if ignore_case:
            search_query = search_query.lower()

        def test_search_match(song_property: str) -> bool:
            if ignore_case:
                song_property = song_property.lower()

            return search_query in song_property

        results = []

        for song in self.songs:
            match = SimpleNamespace(
                song_title=test_search_match(song["title"]),
                album_name=test_search_match(song["album"]["name"]),
                artist_names=any(
                    (test_search_match(artist["name"]) for artist in song["artists"])
                ),
            )

            if exclude:
                if not (match.song_title or match.album_name or match.artist_names):
                    results.append(song)
                continue

            match True:
                case match.song_title:
                    prefix = "SONG TITLE"
                    prefix_colour = "cyan"
                case match.album_name:
                    prefix = "ALBUM NAME"
                    prefix_colour = "magenta"
                case match.artist_names:
                    prefix = "[CREATORS]"
                    prefix_colour = "yellow"
                case _:
                    continue
            song["prefix"] = click.style(prefix, bg=prefix_colour) + click.style(": ")
            results.append(song)

        return results

    def search(
        self, search_query: str, ignore_case: bool = False, exclude: bool = False
    ):
        """Performs a search for songs in the user's library."""
        click.echo(f"Searching for '{search_query}'...")
        start_time_s = time.time()
        results = self._get_search_results(search_query, ignore_case, exclude)
        end_time_s = time.time()
        for song in results:
            click.echo(serialise_song(song))
        num_results = len(results)
        plurality = "" if num_results == 1 else "s"
        time_taken = round((end_time_s - start_time_s) * 1000, 3)
        click.secho(f"{num_results} result{plurality} ({time_taken} ms)", bold=True)
