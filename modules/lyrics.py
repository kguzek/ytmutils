"""Module containing functionality related to retrieving song lyrics."""

import re
from pathlib import Path

import lyricsgenius
from dotenv import load_dotenv

from modules import util


load_dotenv()

# Characters allowed inside filenames
ALLOWED_CHARS = "._- ()[]"

genius = lyricsgenius.Genius()


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
