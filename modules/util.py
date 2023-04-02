"""Module containing general utility functions."""

import html
import time
from typing import Callable, TypeVar, Optional
import unicodedata

import click


def serialise_song(song: dict) -> str:
    """Serialises the song to a more human-readable format."""
    artist_names = ", ".join(artist["name"] for artist in song["artists"])
    artist_names = click.style(artist_names, fg="bright_yellow")
    song_title = click.style(song["title"], fg="bright_cyan")
    song_album = click.style(song["album"]["name"], fg="bright_magenta")
    return f"{artist_names} - {song_title} ({song_album})"


def pluralise(word: str, quantity: int) -> str:
    """Concatenates the quantity and the word. If needed, adds an 's' to the end of the word."""
    plurality = "" if quantity == 1 else "s"
    return f"{quantity} {word}{plurality}"


T = TypeVar("T")  # pylint: disable=invalid-name


def time_function(func: Callable[..., T]) -> tuple[T, float]:
    """Runs `func` and returns the result with the time taken for it to compute in milliseconds."""
    start_time_s = time.time()
    result = func()
    end_time_s = time.time()
    return result, (end_time_s - start_time_s) * 1000


# Got this from stack overflow
def normalise(value: str, encoding: Optional[str] = None) -> str:
    """
    Normalise unmaintainable characters when encoding.
    The default encoding is "ascii".
    ```
    # は non-latin-1 and not normalisable
    # ő non-latin-1 char but normalisable
    # ó latin-1 char
    # o ascii char
    >>> string = 'は | ő | ó | o'
    >>> normalise(string, 'latin-1')
    ' | o | ó | o'

    >>> normalise(string)
    ' | o | o | o'


    ```
    """
    if encoding is None:
        # Normalize non-encoding characters.
        # 'は | ő | ó | o' input
        return (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        # ' | o | o | o' returned string

    # 'は | ő | ó | o' input
    # Replace with backslashreplace non-encoding characters
    value = value.encode(encoding, "backslashreplace").decode(encoding)
    # '\\u306f | \\u0151 | ó | o' funtion output

    # Replace with xmlcharrefreplace encoding-non-ascii characters
    # and reverce backslashreplace
    value = value.encode("ascii", "xmlcharrefreplace").decode("unicode-escape")
    # 'は | ő | &#243; | o' funtion output

    # Normalize non-encoding characters.
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    # ' | o | &#243; | o' funtion output

    # Reverce xmlcharrefreplace
    #' | o | ó | o' retured string
    return html.unescape(value)
