"""Module containing the API wrapper for YouTube Music."""

import json
from types import SimpleNamespace

import click
from ytmusicapi import YTMusic


def serialise_song(song: dict) -> str:
    """Serialises the song to a more human-readable format."""
    artist_names = ", ".join(artist["name"] for artist in song["artists"])
    return f"{song.get('prefix', '')}{artist_names} - {song['title']}"


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

    def _get_search_results(self, search_query: str, ignore_case: bool) -> list[bool]:
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

            match True:
                case match.song_title:
                    prefix = "SONG TITLE"
                case match.album_name:
                    prefix = "ALBUM NAME"
                case match.artist_names:
                    prefix = "ARTIST NAME"
                case _:
                    continue
            song["prefix"] = f"{prefix}: "
            results.append(song)

        return results

    def search(self, search_query: str, ignore_case: bool = False):
        """Performs a search for songs in the user's library."""
        click.echo(f"Searching for '{search_query}'...")
        results = self._get_search_results(search_query, ignore_case)
        for song in results:
            click.echo(serialise_song(song))
        num_results = len(results)
        s = "" if num_results == 1 else "s"
        click.echo(f"({num_results} result{s})")
