import asyncio
from bs4 import BeautifulSoup
from src.lib.shortcuts import get, log


async def get_char_urls(session, character_url):
    character_url = f'{character_url}/pictures'
    char_name = character_url.split('/')[-2]
    async with session.get(character_url) as response:
        soup = BeautifulSoup(await response.text(), features='lxml')

        return char_name, set(x['href'] for x in soup.find_all('a', {'class': 'js-picture-gallery'}))


class MALScraper:

    def __init__(self, session):
        self.session = session
        self.BASE_URL = 'https://myanimelist.net'
        self.ANIME_SEARCH_URL = self.BASE_URL + '/anime.php?q='
        self.CHARACTER_SEARCH_URL = self.BASE_URL + '/character.php?q='

    def get_character_url(self, name):
        """Search the character, get the URL"""

        if type(name) != str:
            raise TypeError('Argument `name` must be string.')
        elif len(name) < 3:
            raise ValueError('Argument `name` length must be >= 3.')

        # print(f'Searching character {name}...')
        url = self.CHARACTER_SEARCH_URL + name
        character_url = None

        try:
            res = get(url)
            soup = BeautifulSoup(res.text, features='lxml')

            table = soup.find('div', {'id': 'content'}).find_next(
                'table')
            table_rows = table.find_all('tr')

            for row in table_rows:
                line = row.find(
                    'td', {'class': 'borderClass bgColor2', 'width': '175'})

                if not line:
                    line = row.find(
                        'td', {'class': 'borderClass bgColor1', 'width': '175'})
                    if not line:
                        line = row.find(
                            'td', {'class': 'borderClass bgColor1'})

                try:
                    a = line.find('a')
                except AttributeError:
                    continue

                character_id = a['href'].split('/')[4]
                character_name = '_'.join(a.text.split(', ')[::-1])
                character_url = f'{self.BASE_URL}/character/{character_id}/{character_name}'
                break

        except Exception as e:
            msg = f'Function `get_character_link` exception.\nURL: {url}\nEXCEPTION: {e}\n'
            log(msg)
            print(msg)

        return character_url

    def get_character_image_urls(self, name, url=False):
        if url:
            character_url = self.get_character_url(name=name)
        else:
            character_url = name
        res = get(f'{character_url}/pictures')
        soup = BeautifulSoup(res.text, features='lxml')

        return [x['href'] for x in soup.find_all('a', {'class': 'js-picture-gallery'})]

    async def get_anime_char_urls(self, url):
        url = f'{url}/characters'
        async with self.session.get(url) as res:
            soup = BeautifulSoup(await res.text(), features='lxml')
            all_chars = soup.find_all('a', {'class': 'fw-n'})

            anime_char_urls = asyncio.gather(
                *[get_char_urls(session=self.session, character_url=response['href']) for response in all_chars
                  if 'character' in response['href']])

            return await anime_char_urls

    def search_characters(self, name):
        """Search the character, get an ID"""

        if type(name) != str:
            raise TypeError('Argument `name` must be string.')
        elif len(name) < 3:
            raise ValueError('Argument `name` length must be >= 3.')

        # print(f'Searching character {name}...')
        url = self.CHARACTER_SEARCH_URL + name
        queryset = []

        try:
            res = get(url)
            soup = BeautifulSoup(res.text, features='lxml')

            table = soup.find('div', {'id': 'content'}).find_next(
                'table')
            table_rows = table.find_all('tr')

            for row in table_rows[1:6]:
                line = row.find(
                    'td', {'class': 'borderClass bgColor2', 'width': '175'})

                if not line:
                    line = row.find(
                        'td', {'class': 'borderClass bgColor1', 'width': '175'})
                    if not line:
                        line = row.find(
                            'td', {'class': 'borderClass bgColor1'})

                try:
                    a = line.find('a')
                except AttributeError:
                    continue

                queryset.append((a.text, a['href']))

        except Exception as e:
            msg = f'Function `search_characters` exception.\nURL: {url}\nEXCEPTION: {e}\n'
            log(msg)
            print(msg)

        return queryset
