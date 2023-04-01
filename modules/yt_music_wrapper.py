"""Module containing the API wrapper for YouTube Music."""

import json
import time
import threading

import click
from ytmusicapi import YTMusic

from modules import util


class YTMusicAnalyser:
    """Class for the analyser functionality."""

    def __init__(self, ytmusic: YTMusic | None):
        if ytmusic is None:
            return
        self.ytmusic = ytmusic
        self._songs = []
        self._initialise_songs()

    def _fetch_all_songs(self) -> list[dict]:
        """Fetches all songs in the user's library and outputs them to `songs.json`."""
        songs = self.ytmusic.get_library_songs(limit=None)
        with open("songs.json", "w", encoding="utf-8") as file:
            json.dump(songs, file, indent=2, ensure_ascii=False)
        return songs

    def _initialise_songs(self) -> None:
        """Sets the `songs` property to the library cache if it exists, else fetches from API."""
        try:
            with open("songs.json", "r", encoding="utf-8") as file:
                self._songs = json.load(file)
        except FileNotFoundError:
            self.update_cache()

    def _get_search_results(
        self, songs: list[dict], search_query: str, ignore_case: bool, exclude: bool
    ) -> list[dict]:
        """Goes through the user's songs and matches the search query with multiple properties."""

        query = search_query.lower() if ignore_case else search_query

        def test_search_match(song_property: str) -> bool:
            if ignore_case:
                song_property = song_property.lower()

            return query in song_property

        def check_song_match(song: dict) -> bool:
            """Returns a boolean indicating whether or not the song matches the search criteria."""
            song_matched = (
                test_search_match(song["title"])
                or test_search_match(song["album"]["name"])
                or any(
                    (test_search_match(artist["name"]) for artist in song["artists"])
                )
            )
            return not song_matched if exclude else song_matched

        click.echo(f"Searching for '{search_query}'...")

        results = filter(check_song_match, songs)
        return results

    def get_songs(self, update_cache: bool) -> list[dict]:
        """Returns the user's library. Can optionally force to update it from the API."""
        if update_cache:
            self.update_cache()
        return self._songs

    def search(self, update_cache: bool, **kwargs) -> None:
        """Performs a search for songs in the user's library."""

        songs = self.get_songs(update_cache)
        results, time_taken = util.time_function(
            lambda: self._get_search_results(songs, **kwargs)
        )
        num_results = 0
        for song in results:
            num_results += 1
            click.echo(util.serialise_song(song))
        click.secho(
            f'{util.pluralise("result", num_results)} ({round(time_taken, 4)} ms)',
            bold=True,
        )

    def update_cache(self) -> None:
        """Forces the instance to update the library song cache."""

        with click.progressbar(
            length=100, label="Updating the library cache..."
        ) as prg:

            fetch_complete = False

            def increment_progress_bar():
                """Increments the progress bar until it's complete."""
                i = 0
                while not fetch_complete:
                    i += 1
                    time.sleep(0.0005 * i)
                    if i < 100:
                        prg.update(1)
                prg.update(100)

            thread = threading.Thread(target=increment_progress_bar)
            thread.start()
            self._songs = self._fetch_all_songs()
            fetch_complete = True
            thread.join()
