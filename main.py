import os
from urllib.parse import urlsplit
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError('Redirect')
    else:
        pass


def download_txt(url, filename, folder, ids):
    params = {"id": ids}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    normal_title = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, f"{ids}. {normal_title}.txt")
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return str(filepath)


def title_parser(ids):
    url = f'https://tululu.org/b{ids}'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book = soup.find('div', id="content").find('h1').text
    title = book.split('::')[0].strip()
    filename = sanitize_filename(title)
    return filename


def download_image(ids):
    folder = "image"
    url = f'https://tululu.org/b{ids}'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    image_url = soup.find('div', class_='bookimage').find('a').find('img')['src']
    filename = os.path.basename(urlsplit(image_url, scheme='', allow_fragments=True)[2])
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return image_url


def main():
    folder = "books"
    url = "https://tululu.org/txt.php"

    for ids in range(1, 11):
        try:
            filename = title_parser(ids)
            download_image(ids)
            download_txt(url, filename, folder, ids)
            print("Скачиваю книгу")
        except HTTPError:
            print("Не удалось скачать книгу -- редирект")
        except AttributeError as e:
            print(f'Такой книги не нашлось. Ошибка: {e}')


if __name__ == '__main__':
    main()
