import re
import json
import logging

import requests
import requests.models
from bs4 import BeautifulSoup

from aniworld.aniskip import get_mal_id_from_title
from aniworld.config import DEFAULT_REQUEST_TIMEOUT, RANDOM_USER_AGENT, ANIWORLD_TO
from aniworld.parser import arguments
from aniworld.common import get_season_episode_count, get_movie_episode_count

from aniworld.extractors import (
    get_direct_link_from_vidmoly,
    get_direct_link_from_vidoza,
    get_direct_link_from_voe,
    get_direct_link_from_doodstream,
    get_direct_link_from_speedfiles,
    get_direct_link_from_luluvdo,
    get_direct_link_from_loadx
)


# Implement lazy loading for the Anime and Episode class.
# Initialize variables with None.
# When a variable is accessed, fetch and store its value automatically,
# so it doesn't need to be fetched again on subsequent accesses.


class Anime:
    """
    Represents an anime series with various attributes and methods to fetch and manage its details.

    Example:
        anime = Anime(
            episode_list=[
                Episode(
                    slug="loner-life-in-another-world",
                    season=1,
                    episode=1
                )
            ]
        )

    Required Attributes:
        episode_list (list): A list of Episode objects for the anime.

    Attributes:
        title (str): The title of the anime.
        slug (str): A URL-friendly version of the title used for web requests.
        action (str): The default action to be performed.
                      Must be one of "Download", "Watch", or "Syncplay". 
                      Defaults to "Watch" if not provided.
        provider (str): The provider of the anime content. Defaults to:
                        - DEFAULT_PROVIDER_DOWNLOAD if action is "Download"
                        - DEFAULT_PROVIDER_WATCH if action is not "Download"
                        Set based on the action if not provided.
        language (str): The language code for the anime.
                        Defaults to DEFAULT_LANGUAGE if not provided.
        aniskip (bool): Whether to skip certain actions (default is False).
        output_directory (str): The directory where downloads are saved.
                                Defaults to the user's home "Downloads" directory.
        episode_list (list): A list of Episode objects for the anime.
        description_german (str): The German description of the anime.
        description_english (str): The English description of the anime.
        html (requests.models.Response): The HTML response object for the anime's webpage.
    """

    def __init__(
        self,
        title=None,
        slug=None,
        action=arguments.action,
        provider=arguments.provider,
        language=arguments.language,
        aniskip=arguments.aniskip,
        output_directory=arguments.output_dir,
        episode_list=None,
        description_german=None,
        # description_english=None,
        html=None
    ) -> None:
        if not episode_list:
            raise ValueError("Provide 'episode_list'.")

        self.slug = slug or episode_list[0].slug
        if not self.slug:
            raise ValueError("Slug of Anime is None.")

        self.html = html or requests.get(
            f"{ANIWORLD_TO}/anime/stream/{self.slug}",
            timeout=DEFAULT_REQUEST_TIMEOUT
        )

        self.title = title or get_anime_title_from_html(self.html)
        self.action = action
        self.provider = provider
        self.language = language
        self.aniskip = aniskip
        self.output_directory = output_directory
        self.episode_list = episode_list

        self.description_german = description_german or self._fetch_description_german()
        # This should be fetched manually as its not needed for now
        # self.description_english = description_english or self._fetch_description_english()

    def _fetch_description_german(self):
        soup = BeautifulSoup(self.html.content, 'html.parser')
        desc_div = soup.find('p', class_='seri_des')
        return (
            desc_div.get('data-full-description', '')
            if desc_div else "Could not fetch description."
        )

    def _fetch_description_english(self):
        anime_id = get_mal_id_from_title(self.title, 1)
        response = requests.get(
            f"https://myanimelist.net/anime/{anime_id}",
            timeout=DEFAULT_REQUEST_TIMEOUT
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        desc_meta = soup.find('meta', property='og:description')
        return (
            desc_meta['content']
            if desc_meta else "Could not fetch description."
        )

    def __iter__(self):
        return iter(self.episode_list)

    def __getitem__(self, index: int):
        return self.episode_list[index]

    def to_json(self) -> str:
        data = {
            "title": self.title,
            "slug": self.slug,
            "action": self.action,
            "provider": self.provider,
            "language": self.language,
            "aniskip": self.aniskip,
            "output_directory": str(self.output_directory),
            "episode_list": self.episode_list,
            "description_german": ' '.join(self.description_german.split()[:10]) + ' [...]',
            # "description_english": ' '.join(self.description_english.split()[:10]) + ' [...]',
        }
        return str(data)

    def __str__(self):
        return self.to_json()


class Episode:
    """
    Represents an episode of an anime series with various attributes
    and methods to fetch and manage its details.

    Example:
        Episode(
            slug="loner-life-in-another-world",
            season=1,
            episode=1
        )

    Required Attributes:
        link (str) or slug (str), season (int), episode (int):
        Either a direct link to the episode or a slug with season
        and episode numbers for constructing the link.

    Attributes:
        anime_title (str): The title of the anime the episode belongs to.
        title_german (str): The German title of the episode.
        title_english (str): The English title of the episode.
        season (int): The season number of the episode.
        episode (int): The episode number within the season.
        slug (str): A URL-friendly version of the episode title used for web requests.
        link (str): The direct link to the episode.
        mal_id (int): The MyAnimeList ID for the episode.
        redirect_link (str): The redirect link for streaming the episode.
        embeded_link (str): The embedded link for the episode.
        direct_link (str): The direct streaming link for the episode.
        provider (dict): A dictionary of available providers and their links.
        provider_name (list): A list of provider names.
        language (list): A list of available language codes for the episode.
        language_name (list): A list of available language names for the episode.
        season_episode_count (dict): A dictionary mapping season numbers to episode counts.
        movie_episode_count (int): The count of movie episodes.
        html (requests.models.Response): The HTML response object for the episode's webpage.
        _selected_provider (str): The selected provider for streaming.
        _selected_language (int): The selected language code for streaming.
    """

    def __init__(  # pylint: disable=too-many-locals
        self,
        anime_title: str = None,
        title_german: str = None,
        title_english: str = None,
        season: int = None,
        episode: int = None,
        slug: str = None,
        link: str = None,
        mal_id: int = None,
        redirect_link: str = None,
        embeded_link: str = None,
        direct_link: str = None,
        provider: dict = None,  # available providers
        provider_name: list = None,
        language: list = None,  # available languages
        language_name: list = None,
        season_episode_count: dict = None,
        has_movies: bool = False,
        movie_episode_count: int = None,
        html: requests.models.Response = None,
        _selected_provider: str = arguments.provider,
        _selected_language: str = arguments.language
    ) -> None:
        if not link and (not slug or not season or not episode):
            raise ValueError(
                "Provide either 'link' or 'slug' with 'season' and 'episode'.")

        self.anime_title: str = anime_title
        self.title_german: str = title_german
        self.title_english: str = title_english
        self.season: int = season
        self.episode: int = episode
        self.slug: str = slug
        self.link: str = link
        self.mal_id: int = mal_id
        self.redirect_link = redirect_link
        self.embeded_link = embeded_link
        self.direct_link = direct_link
        self.provider: dict = provider
        self.provider_name: list = provider_name
        self.language: list = language
        self.language_name: list = language_name
        self.season_episode_count: dict = season_episode_count
        self.has_movies: bool = has_movies
        self.movie_episode_count: int = movie_episode_count
        self.html: requests.models.Response = html
        self._selected_provider: str = _selected_provider
        self._selected_language: str = _selected_language

        self.auto_fill_details()

    def _get_episode_title_from_html(self) -> tuple:
        episode_soup = BeautifulSoup(self.html.content, 'html.parser')
        episode_german_title_div = episode_soup.find(
            'span', class_='episodeGermanTitle')
        episode_english_title_div = episode_soup.find(
            'small', class_='episodeEnglishTitle')

        german_title = episode_german_title_div.text if episode_german_title_div else ""
        english_title = episode_english_title_div.text if episode_english_title_div else ""

        return german_title, english_title

    def _get_season_from_link(self) -> int:
        if "/filme/" in self.link:
            return 0  # Set season to 0 for movies

        season = self.link.split("/")[-2]  # e.g. staffel-2
        numbers = re.findall(r'\d+', season)

        if numbers:
            return int(numbers[-1])  # e.g 2

        raise ValueError(
            f"No valid season number found in the link: {self.link}")

    def _get_episode_from_link(self) -> int:
        if self.link.endswith("/"):
            self.link = self.link[:-1]

        episode = self.link.split("/")[-1]  # e.g. episode-2
        numbers = re.findall(r'\d+', episode)

        if numbers:
            return int(numbers[-1])  # e.g 2

        raise ValueError(
            f"No valid episode number found in the link: {self.link}")

    def _get_available_language_from_html(self) -> list[int]:
        """
        Language Codes:
            1: German Dub
            2: English Sub
            3: German Sub
        """

        episode_soup = BeautifulSoup(self.html.content, 'html.parser')
        change_language_box_div = episode_soup.find(
            'div', class_='changeLanguageBox')
        language = []

        if change_language_box_div:
            img_tags = change_language_box_div.find_all('img')
            for img in img_tags:
                lang_key = img.get('data-lang-key')
                if lang_key and lang_key.isdigit():
                    language.append(int(lang_key))
        else:
            return []

        return language  # e.g. [1, 2, 3]

    def _get_provider_from_html(self) -> dict:
        """
            Parses the HTML content to extract streaming providers,
            their language keys, and redirect links.

            Returns a dictionary with provider names as keys
            and language key-to-redirect URL mappings as values.

            Example:

            {
                'VOE': {1: 'https://aniworld.to/redirect/1766412',
                        2: 'https://aniworld.to/redirect/1766405'},
                'Doodstream': {1: 'https://aniworld.to/redirect/1987922',
                               2: 'https://aniworld.to/redirect/2700342'},
                ...
            }

            Access redirect link with:
            print(self.provider["VOE"][2])
        """

        soup = BeautifulSoup(self.html.content, 'html.parser')
        providers = {}

        episode_links = soup.find_all(
            'li', class_=lambda x: x and x.startswith('episodeLink')
        )

        if not episode_links:
            raise ValueError(
                f"{self.link}\nDerzeit keine Streams für diese Episode verfügbar. "
                f"Versuche es später noch einmal oder frage in der Shoutbox etc. nach ;)"
            )

        for link in episode_links:
            provider_name_tag = link.find('h4')
            provider_name = provider_name_tag.text.strip() if provider_name_tag else None

            redirect_link_tag = link.find('a', class_='watchEpisode')
            redirect_link = redirect_link_tag['href'] if redirect_link_tag else None

            lang_key = link.get('data-lang-key')
            lang_key = int(
                lang_key) if lang_key and lang_key.isdigit() else None

            if provider_name and redirect_link and lang_key:
                if provider_name not in providers:
                    providers[provider_name] = {}
                providers[provider_name][lang_key] = f"{ANIWORLD_TO}{redirect_link}"

        if not providers:
            raise ValueError(
                f"Could not get providers from {self.link}"
            )

        logging.debug("Available Episodes for \"%s\":\n%s",
                      self.anime_title, json.dumps(providers, indent=4))
        return providers

    def _get_key_from_language(self, language: str) -> int:
        lang_mapping = {
            "German Dub": 1,
            "English Sub": 2,
            "German Sub": 3
        }

        language_key = lang_mapping.get(language, None)

        if language_key is None:
            raise ValueError(f"Language: {language} not valid.")

        return language_key

    def _get_languages_from_keys(self, keys: list[int]) -> list[str]:
        key_mapping = {
            1: "German Dub",
            2: "English Sub",
            3: "German Sub"
        }

        languages = [key_mapping.get(key, None) for key in keys]

        if None in languages:
            raise ValueError("One or more keys are not valid.")

        return languages

    def _get_direct_link_from_provider(self) -> str:
        """
            providers = {
                "Vidmoly": get_direct_link_from_vidmoly,
                "Vidoza": get_direct_link_from_vidoza,
                "VOE": get_direct_link_from_voe,
                "Doodstream": get_direct_link_from_doodstream,
                "SpeedFiles": get_direct_link_from_speedfiles,
                "Luluvdo": get_direct_link_from_luluvdo
            }

            # first, try the selected provider
            if self._selected_provider in providers:
                try:
                    print(f"Trying selected provider: {self._selected_provider}")
                    return providers[self._selected_provider](self.embeded_link).get_direct_link()
                except ValueError as e:
                    print(f"An error occurred with {self._selected_provider}: {e}")

            # if the selected provider fails, try all other providers
            for provider_name, provider_func in providers.items():
                if provider_name == self._selected_provider:
                    continue  # skip the selected provider since we've already tried it

                try:
                    print(f"Trying {provider_name}")

                    # this fails because self.embeded_link is from the selected_provider
                    # and needs to be set to the next trying provider
                    direct_link = provider_func(self.embeded_link)

                    if direct_link is None:
                        raise ValueError

                except ValueError as e:
                    print(f"An error occurred with {provider_name}: {e}")
                    continue  # try the next provider if this one fails

            # if all providers fail, raise an error
            raise ValueError("All providers have failed.")
        """
        if self.embeded_link is None:
            return None
        if self._selected_provider == "Vidmoly":
            return get_direct_link_from_vidmoly(embeded_vidmoly_link=self.embeded_link)
        if self._selected_provider == "Vidoza":
            return get_direct_link_from_vidoza(embeded_vidoza_link=self.embeded_link)
        if self._selected_provider == "VOE":
            return get_direct_link_from_voe(embeded_voe_link=self.embeded_link)
        if self._selected_provider == "Doodstream":
            return get_direct_link_from_doodstream(embeded_doodstream_link=self.embeded_link)
        if self._selected_provider == "SpeedFiles":
            return get_direct_link_from_speedfiles(embeded_speedfiles_link=self.embeded_link)
        if self._selected_provider == "Luluvdo":
            return get_direct_link_from_luluvdo(embeded_luluvdo_link=self.embeded_link,
                                                arguments=arguments)
        if self._selected_provider == "LoadX":
            return get_direct_link_from_loadx(embeded_loadx_link=self.embeded_link)

        raise ValueError(
            f"{self._selected_provider} is currently not supported.")

    def get_redirect_link(self):
        lang_key = self._get_key_from_language(self._selected_language)

        if (self._selected_provider not in self.provider or
                lang_key not in self.provider[self._selected_provider]
            ):
            for provider_name, lang_dict in self.provider.items():
                if lang_key in lang_dict:
                    self._selected_provider = provider_name
                    self.redirect_link = lang_dict[lang_key]
                    break
            else:
                self.redirect_link = None
                # raise KeyError(
                #    "No provider with the language key '"
                #    f"{lang_key}' found. Checked providers: {list(self.provider.keys())}. "
                #    f"Provider variable: {self.provider}"
                # )
        else:
            self.redirect_link = self.provider[self._selected_provider][lang_key]

    def get_embeded_link(self):
        if not self.redirect_link:
            self.get_redirect_link()
        if not self.redirect_link:
            return None

        self.embeded_link = requests.get(
            self.redirect_link, timeout=DEFAULT_REQUEST_TIMEOUT,
            headers={'User-Agent': RANDOM_USER_AGENT}).url
        return self.embeded_link

    def get_direct_link(self, provider=None, language=None):
        """
        Retrieves the direct streaming link for the episode.

        Example:
            episode.get_direct_link("VOE", "German Sub")

        Note:
            If this method is not being called from a menu or with arguments,
            ensure that 'provider' and 'language' are set before calling.

        Args:
            provider (str): The name of the provider to use for fetching the direct link.
            language (str): The language code to use for fetching the direct link.

        Returns:
            str: The direct streaming link for the episode.
        """
        if provider:
            self._selected_provider = provider

        if language:
            self._selected_language = language

        if not self.embeded_link:
            self.get_embeded_link()

        self.direct_link = self._get_direct_link_from_provider()
        return self.direct_link

    def auto_fill_details(self) -> None:
        if self.slug and self.season and self.episode:
            self.link = (
                f"{ANIWORLD_TO}/anime/stream/{self.slug}/"
                f"staffel-{self.season}/episode-{self.episode}"
            )

        if self.link:
            self.slug = self.slug or self.link.split("/")[-3]
            self.season = self.season or self._get_season_from_link()
            self.episode = self.episode or self._get_episode_from_link()

        self.html = requests.get(self.link, timeout=DEFAULT_REQUEST_TIMEOUT)
        self.anime_title = get_anime_title_from_html(html=self.html)
        self.title_german, self.title_english = self._get_episode_title_from_html()
        self.language = self._get_available_language_from_html()
        self.language_name = self._get_languages_from_keys(self.language)
        self.provider = self._get_provider_from_html()
        self.provider_name = list(self.provider.keys())
        self.season_episode_count = get_season_episode_count(self.slug)
        self.movie_episode_count = get_movie_episode_count(self.slug)

        if self.movie_episode_count:
            # remove last season as its the same as movies and 0
            last_season = list(self.season_episode_count.keys())[-1]
            if self.season_episode_count[last_season] == 0:
                del self.season_episode_count[last_season]

    def to_json(self) -> str:
        data = {
            "anime_title": self.anime_title,
            "title_german": self.title_german,
            "title_english": self.title_english,
            "season": self.season,
            "episode": self.episode,
            "slug": self.slug,
            "link": self.link,
            "mal_id": self.mal_id,
            "redirect_link": self.redirect_link,
            "embeded_link": self.embeded_link,
            "direct_link": self.direct_link,
            "provider": self.provider,
            "provider_name": self.provider_name,
            "language": self.language,
            "language_name": self.language_name,
            "season_episode_count": self.season_episode_count,
            "movie_episode_count": self.movie_episode_count,
            "html": str(self.html)
        }
        return json.dumps(data, indent=4)

    def __str__(self) -> str:
        return self.to_json()


def get_anime_title_from_html(html: requests.models.Response):
    soup = BeautifulSoup(html.content, 'html.parser')
    title_div = soup.find('div', class_='series-title')

    if title_div:
        return title_div.find('h1').find('span').text

    return ""


if __name__ == "__main__":
    pass
