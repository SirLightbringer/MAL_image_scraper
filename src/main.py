import aiohttp
import asyncio
import os
import time
from multiprocessing.dummy import Pool as ThreadPool
from urllib.request import urlretrieve

from lib.mal_scraper import MALScraper

root_dir = './images'


def save_url(url, path_to_save, output):
    print(output)
    urlretrieve(url, path_to_save)
    time.sleep(0.5)


async def main():
    anime_search = input('MAL Link (e.g. https://myanimelist.net/anime/42897/Horimiya): ')
    async with aiohttp.ClientSession() as session:
        scraper = MALScraper(session=session)
        try:
            anime_char_urls = await scraper.get_anime_char_urls(anime_search)
        except aiohttp.InvalidURL:
            print('Please enter a valid URL')
            return

    if not anime_char_urls:
        print('Please enter a valid MAL link')
        return

    try:
        os.mkdir(root_dir)
    except FileExistsError:
        pass

    series_name = anime_search.split('/')[-1].lower().replace('_', '-')
    try:
        os.mkdir(f'{root_dir}/{series_name}')
    except FileExistsError:
        pass

    all_save_dirs = []
    all_save_messages = []
    all_char_urls = []

    pool = ThreadPool(100)
    for char_name, char_urls in anime_char_urls:
        if not char_urls:
            print(f'No images found for {char_name}')
            continue

        dir_name = char_name.lower().replace('_', '-')
        out_dir = f'{root_dir}/{series_name}/{dir_name}'
        try:
            os.mkdir(out_dir)
        except FileExistsError:
            pass

        len_char_urls = len(char_urls)
        urls_range = range(1, len_char_urls + 1)
        save_dirs = [os.path.join(out_dir, f'{dir_name}-{num}.png') for num in urls_range]
        save_messages = [f'Saving image {num}/{len_char_urls} for {char_name}\n' for num in urls_range]

        all_save_dirs.extend(save_dirs)
        all_save_messages.extend(save_messages)
        all_char_urls.extend(char_urls)

    pool.starmap(save_url, zip(all_char_urls, all_save_dirs, all_save_messages))


if __name__ == '__main__':
    asyncio.run(main())
