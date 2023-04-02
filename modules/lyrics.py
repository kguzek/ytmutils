"""Module containing functionality related to retrieving song lyrics."""

import re
from pathlib import Path
from typing import Literal, Callable, Optional

from click import style
from dotenv import load_dotenv
import lyricsgenius

from modules import util


load_dotenv()

# Characters allowed inside filenames
ALLOWED_CHARS = "._- ()[]"

genius = lyricsgenius.Genius()


def get_query_index(search_query: str, line_contents: str, ignore_case: bool) -> int:
    """Determines whether or not the query is present within the current line.

    If so, returns the index of the first character of the search query in the line.
    Otherwise, returns `-1`.
    """
    if ignore_case:
        search_query = search_query.lower()
        line_contents = line_contents.lower()
    try:

        query_start_idx = line_contents.index(search_query)
    except ValueError:
        return -1
    else:
        return query_start_idx


def output_lyrics_preview(
    lines: list[str],
    line: int,
    last_printed_line_no: int | None,
    pop_all_lines_to_print: Callable[[Optional[int]], str],
    *,
    search_query: str,
    ignore_case: bool,
    **_,
) -> tuple[list[str], int, int, bool]:
    """Analyses the song lyrics and compiles a user preview highlighting search query occurences.

    Returns the lines to output, the number of conceding search hits to skip processing,
    the last printed line number, and whether or not the previous block should remove its trailing
    ellipsis.
    """
    num_lines = len(lines)
    max_line_no_digits = len(str(num_lines))
    lines_to_print = []

    def validate_offset(test_offset: int):
        return 0 <= line + test_offset <= num_lines - 1

    def stylise_line(line_contents: str, line_offset: int = 0):
        line_no = str(line + line_offset + 1).rjust(max_line_no_digits, " ")
        query_start_idx = get_query_index(search_query, line_contents, ignore_case)

        def push_current_line(contents: str = line_contents):
            lines_to_print.append(f"{line_no} | {contents}")

        line_contains_query = query_start_idx != -1
        if line_contains_query:
            query_end_idx = query_start_idx + len(search_query)
            capitalised_search_query = line_contents[query_start_idx:query_end_idx]
            contents = (
                line_contents[:query_start_idx]
                + style(capitalised_search_query, fg="bright_green")
                + line_contents[query_end_idx:]
            )
            push_current_line(contents)
        else:
            push_current_line()
        return line_contains_query

    def push_adjacent_lines(increment: Literal[1, -1]) -> None:
        offset = increment
        break_on_next_iteration = False
        adjacent_lines_to_skip = 0

        def push_ellipsis(current_offset: int):
            nonlocal last_printed_line_no
            last_printed_line_no = line + current_offset
            lines_to_print.append("...")

        while validate_offset(offset):
            if break_on_next_iteration:
                if last_printed_line_no is None:
                    push_ellipsis(offset)
                else:
                    match abs(last_printed_line_no - (line + offset - increment)):
                        case 0:
                            # There is a 0-line difference between query-containing lyrics segments
                            pop_all_lines_to_print()
                        case 1:
                            pass
                        case _:
                            push_ellipsis(offset)
                break

            current_line = lines[line + offset]
            line_contains_query = stylise_line(current_line, offset)
            offset += increment
            if line_contains_query:
                adjacent_lines_to_skip += 1
                continue
            if not validate_offset(offset):
                continue
            next_line = lines[line + offset]
            search_query_index = get_query_index(search_query, next_line, ignore_case)
            if search_query_index == -1:
                # Stop adding lines once the next line doesn't contain the search query.
                break_on_next_iteration = True
        return adjacent_lines_to_skip

    push_adjacent_lines(-1)
    lines_to_print.reverse()
    stylise_line(lines[line])
    adjacent_lines_to_skip = push_adjacent_lines(1)
    return (lines_to_print, adjacent_lines_to_skip, last_printed_line_no)


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
