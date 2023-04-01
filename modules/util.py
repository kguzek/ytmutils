"""Module containing general utility functions."""

import click


def serialise_song(song: dict) -> str:
    """Serialises the song to a more human-readable format."""
    artist_names = ", ".join(artist["name"] for artist in song["artists"])
    artist_names = click.style(artist_names, fg="bright_yellow")
    prefix = song.get("prefix", "")
    song_title = click.style(song["title"], fg="bright_cyan")
    song_album = click.style(song["album"]["name"], fg="bright_magenta")
    return f"{prefix}{artist_names} - {song_title} ({song_album})"


def pluralise(word: str, quantity: int) -> str:
    """Concatenates the quantity and the word. If needed, adds an 's' to the end of the word."""
    plurality = "" if quantity == 1 else "s"
    return f"{quantity} {word}{plurality}"
