"""Module containing the API wrapper for YouTube Music."""

import json
import time
import threading
from typing import Literal
from requests.exceptions import Timeout

import click
from ytmusicapi import YTMusic

from modules import util
from modules.lyrics import get_song_lyrics


def _get_search_results(
    songs: list[dict], search_query: str, ignore_case: bool, exclude: bool
) -> list[tuple[dict, str]]:
    """Goes through the user's songs and matches the search query with multiple properties."""

    query = search_query.lower() if ignore_case else search_query

    results: list[tuple[dict, str]] = []
    songs_processed = 0

    def check_song_match(song: dict) -> bool:
        """Returns a boolean indicating whether or not the song matches the search criteria."""
        nonlocal songs_processed

        song_name = song["title"]
        artist_names = ", ".join(artist["name"] for artist in song["artists"])
        try:
            lyrics = get_song_lyrics(song_name, artist_names)
        except Timeout:
            click.echo(f"Searching lyrics for '{song_name}' timed out.")
            return None
        else:
            lines_matched = []
            for i, line in enumerate(
                (lyrics.lower() if ignore_case else lyrics).split("\n")
            ):
                if query in line:
                    lines_matched.append(i)
            lyrics_matched = len(lines_matched) > 0
            match = not lyrics_matched if exclude else lyrics_matched
            if match:
                results.append((song, lyrics, lines_matched))
        finally:
            songs_processed += 1
        return match

    click.echo(f"Searching for '{search_query}'...")

    for song in songs:
        threading.Thread(target=check_song_match, args=[song]).start()
    while songs_processed < len(songs):
        continue
    return results


def output_lyrics_preview(
    lyrics: str, line: int, *, search_query: str, ignore_case: bool, **_
):
    """Outputs where in the song's lyrics the search query appears."""
    lines = lyrics.splitlines()
    max_line_no_digits = len(str(len(lines)))
    lines_to_print = []

    query = search_query.lower() if ignore_case else search_query

    def stylise_line(line_offest: int, line_contents: str):
        line_no = str(line + line_offest + 1).rjust(max_line_no_digits, " ")
        contents = line_contents.lower() if ignore_case else line_contents
        try:
            query_start_idx = contents.index(query)
        except ValueError:
            contents = line_contents
        else:
            query_end_idx = query_start_idx + len(search_query)
            contents = (
                line_contents[:query_start_idx]
                + click.style(search_query, fg="bright_green")
                + line_contents[query_end_idx:]
            )
        lines_to_print.append(f"{line_no} | {contents}")

    def push_adjacent_lines(increment: Literal[1, -1]) -> None:
        offset = increment
        break_on_next_iteration = False
        while line + offset >= 0 and line + offset <= len(lines) - 1:
            if break_on_next_iteration:
                lines_to_print.append("...")
                break
            current_line = lines[line + offset]
            stylise_line(offset, current_line)
            if current_line:
                # Stop adding lines once we find the first non-empty line
                break_on_next_iteration = True
                continue
            offset += increment
        return offset

    final_offset = push_adjacent_lines(-1)
    lines_to_print.reverse()
    stylise_line(0, lines[line])
    push_adjacent_lines(1)
    click.echo("\n".join(lines_to_print))


class YTMusicAnalyser:
    """Class for the analyser functionality."""

    def __init__(self, ytmusic: YTMusic | None):
        if ytmusic is None:
            return
        self._ytmusic = ytmusic
        self._songs = []
        self._initialise_songs()

    def _fetch_all_songs(self) -> list[dict]:
        """Fetches all songs in the user's library and outputs them to `songs.json`."""
        songs = self._ytmusic.get_library_songs(limit=None)
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

    def get_songs(self, update_cache: bool) -> list[dict]:
        """Returns the user's library. Can optionally force to update it from the API."""
        if update_cache:
            self.update_cache()
        return self._songs

    def search(self, update_cache: bool, **kwargs) -> None:
        """Performs a search for songs in the user's library."""

        songs = self.get_songs(update_cache)
        results, time_taken = util.time_function(
            lambda: _get_search_results(songs, **kwargs)
        )
        num_results = 0
        for song, lyrics, lines in results:
            num_results += 1
            click.echo(util.serialise_song(song))
            for line in lines:
                output_lyrics_preview(lyrics, line, **kwargs)
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
