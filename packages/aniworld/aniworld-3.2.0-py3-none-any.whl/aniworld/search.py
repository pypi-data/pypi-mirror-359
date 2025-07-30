import json
import html
import webbrowser
from urllib.parse import quote
import logging
import re

import curses
import requests

from aniworld.ascii_art import display_ascii_art
from aniworld.config import DEFAULT_REQUEST_TIMEOUT, ANIWORLD_TO


def search_anime(keyword: str = None, only_return: bool = False) -> str:
    if not only_return:
        print(display_ascii_art())
    if not keyword:
        logging.debug("Prompting user for search.")
        keyword = input("Search for a series: ").strip()
        if keyword.strip().lower() == "boku no piko":
            raise ValueError("Really? This is not on AniWorld...")

    search_url = f"{ANIWORLD_TO}/ajax/seriesSearch?keyword={quote(keyword)}"
    anime_list = fetch_anime_list(search_url)

    if only_return:
        return anime_list

    if len(anime_list) == 1:
        return anime_list[0].get("link", None)

    if not anime_list:
        raise ValueError("Could not get valid anime")

    return curses.wrapper(show_menu, anime_list)


def fetch_anime_list(url: str) -> list:
    response = requests.get(url, timeout=DEFAULT_REQUEST_TIMEOUT)
    response.raise_for_status()

    clean_text = response.text.strip()

    try:
        decoded_data = json.loads(html.unescape(clean_text))
        return decoded_data if isinstance(decoded_data, list) else []
    except json.JSONDecodeError:
        try:
            # Remove BOM and problematic characters
            clean_text = clean_text.encode('utf-8').decode('utf-8-sig')
            # Remove problematic characters
            clean_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', clean_text)
            # Parse the new text
            decoded_data = json.loads(clean_text)
            return decoded_data if isinstance(decoded_data, list) else []
        except (requests.RequestException, json.JSONDecodeError) as exc:
            raise ValueError("Could not get valid anime: ") from exc


def show_menu(stdscr: curses.window, options: list) -> str:
    current_row = 0
    konami_code = ['UP', 'UP', 'DOWN', 'DOWN',
                   'LEFT', 'RIGHT', 'LEFT', 'RIGHT', 'b', 'a']
    entered_keys = []
    key_map = {
        curses.KEY_UP: 'UP',
        curses.KEY_DOWN: 'DOWN',
        curses.KEY_LEFT: 'LEFT',
        curses.KEY_RIGHT: 'RIGHT',
        ord('b'): 'b',
        ord('a'): 'a'
    }

    try:
        while True:
            stdscr.clear()
            for idx, anime in enumerate(options):
                name = anime.get('name', 'No Name')
                year = anime.get('productionYear', 'Unknown Year')
                highlight = curses.A_REVERSE if idx == current_row else 0
                stdscr.attron(highlight)
                stdscr.addstr(idx, 0, f"{name} {year}")
                stdscr.attroff(highlight)

            stdscr.refresh()
            key = stdscr.getch()

            if key in key_map:
                entered_keys.append(key_map[key])
                if len(entered_keys) > len(konami_code):
                    entered_keys.pop(0)
                if entered_keys == konami_code:
                    webbrowser.open(
                        'https://www.youtube.com/watch?v=PDJLvF1dUek')
                    entered_keys.clear()
            else:
                entered_keys.clear()

            if key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(options)
            elif key == curses.KEY_UP:
                current_row = (current_row - 1 + len(options)) % len(options)
            elif key == ord('\n'):
                return options[current_row].get('link', 'No Link')
            elif key == ord('q'):
                break
    except curses.error:
        pass

    return None


if __name__ == '__main__':
    print(search_anime())
