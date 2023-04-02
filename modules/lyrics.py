"""Module containing functionality related to retrieving song lyrics."""

import re
from pathlib import Path
from typing import Literal

import click
from dotenv import load_dotenv
import lyricsgenius

from modules import util


load_dotenv()

# Characters allowed inside filenames
ALLOWED_CHARS = "._- ()[]"

genius = lyricsgenius.Genius()


def output_lyrics_preview(
    lyrics: str, line: int, *, search_query: str, ignore_case: bool, **_
):
    """Outputs where in the song's lyrics the search query appears."""
    lines = lyrics.splitlines()
    max_line_no_digits = len(str(len(lines)))
    lines_to_print = []

    query = search_query.lower() if ignore_case else search_query

    def stylise_line(line_contents: str, line_offest: int = 0):
        line_no = str(line + line_offest + 1).rjust(max_line_no_digits, " ")
        contents = line_contents.lower() if ignore_case else line_contents
        try:
            query_start_idx = contents.index(query)
        except ValueError:
            contents = line_contents
            return False
        else:
            query_end_idx = query_start_idx + len(search_query)
            capitalised_search_query = line_contents[query_start_idx:query_end_idx]
            contents = (
                line_contents[:query_start_idx]
                + click.style(capitalised_search_query, fg="bright_green")
                + line_contents[query_end_idx:]
            )
            return True
        finally:
            lines_to_print.append(f"{line_no} | {contents}")

    def push_adjacent_lines(increment: Literal[1, -1]) -> None:
        offset = increment
        break_on_next_iteration = False
        adjacent_lines_to_skip = 0
        while 0 <= line + offset <= len(lines) - 1:
            if break_on_next_iteration:
                lines_to_print.append("...")
                break
            current_line = lines[line + offset]
            line_contains_query = stylise_line(current_line, offset)
            if line_contains_query:
                adjacent_lines_to_skip += 1
            elif current_line:
                # Stop adding lines once we find the first non-empty line
                break_on_next_iteration = True
            offset += increment
        return adjacent_lines_to_skip

    push_adjacent_lines(-1)
    lines_to_print.reverse()
    stylise_line(lines[line])
    adjacent_lines_to_skip = push_adjacent_lines(1)
    click.echo("\n".join(lines_to_print))
    return adjacent_lines_to_skip


def sanitise_song_title(song_title: str) -> str:
    """Removes 'featuring' from song titles, etc."""
    blacklist = ["Anniversary", "Remaster", "Extended", "Version", "Soundtrack"]
    song_title = song_title.split("(f")[0]
    for phrase in blacklist:
        song_title = re.sub(rf"\(.*{phrase}.*\)", "", song_title)
    return song_title.strip()


def get_valid_filename(unsanitised_string: str) -> str:
    """Converts the string into a valid filename."""
    temp = util.normalise(unsanitised_string)
    new = (x for x in temp if (x.isalnum() or x in ALLOWED_CHARS))
    return "".join(new).strip() or "__invalid_filename__"


def get_song_lyrics(song_name: str, artist: str) -> str:
    """Gets the song lyrics from the Genius API."""
    song_title = sanitise_song_title(song_name)
    artist_filename = get_valid_filename(artist)
    song_title_filename = f"{get_valid_filename(song_title)}.txt"
    lyrics_path = Path(f"lyrics/{artist_filename}")
    lyrics_filepath = str(lyrics_path / song_title_filename)
    try:
        with open(lyrics_filepath, "r", encoding="utf-8") as file:
            lyrics = file.read()
    except FileNotFoundError:
        lyrics_path.mkdir(parents=True, exist_ok=True)
    else:
        return lyrics
    song = genius.search_song(song_title, artist)
    if song is None:
        return ""
    with open(lyrics_filepath, "w", encoding="utf-8") as file:
        file.write(song.lyrics)
    return song.lyrics


if __name__ == "__main__":
    x = get_song_lyrics("Zanim pójdę", "Happysad")
    print(x)
