import os
import time
from urllib.parse import urlsplit
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError
import argparse


class BookNotFoundError(Exception):
    def __init__(self, message="Книга не найдена"):
        self.message = message
        super().__init__(self.message)


class DownloadError(Exception):
    def __init__(self, message="Ошибка загрузки"):
        self.message = message
        super().__init__(self.message)


class Redirect(HTTPError):
    def __init__(self, message="Редирект"):
        self.message = message
        super().__init__(self.message)


def check_for_redirect(response):
    if response.history:
        raise Redirect


def download_txt(txt_url, filename, folder, id_):
    params = {"id": id_}
    response = requests.get(txt_url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    normal_title = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, f"{id_}. {normal_title}.txt")
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return str(filepath)


def title_parser(response):
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        book_content = soup.find('div', id="content")
        if book_content is None:
            raise BookNotFoundError
        else:
            book = book_content.find('h1').text
            title = book.split('::')[0].strip()
            filename = sanitize_filename(title)
            return filename
    except BookNotFoundError as e:
        print(e)


def download_image(response):
    folder = "image"
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        book_image = soup.find('div', class_='bookimage')
        if book_image is None:
            pass
        else:
            image_url = book_image.find('a').find('img')['src']
            filename = os.path.basename(urlsplit(image_url, scheme='', allow_fragments=True)[2])
            Path(folder).mkdir(parents=True, exist_ok=True)
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as file:
                file.write(response.content)
    except BookNotFoundError as e:
        print(e)


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        book_content = soup.find('div', id="content")
        if book_content is None:
            raise BookNotFoundError
        else:
            h1 = book_content.find('h1').text
            title = h1.split('::')[0].strip()
            author = h1.split('::')[1].strip()
            book = sanitize_filename(title)
            genres = [genre.text for genre in soup.find('span', class_="d_book").find_all('a')]
            comments = [block.find('span', class_="black").text for block in soup.find_all('div', class_='texts')]
            return {
                'Название книги': book,
                'Автор': author,
                'Жанр книги': genres,
                'Комментарии': comments
            }
    except BookNotFoundError as e:
        print(e)


def main():
    folder = "books"
    txt_url = "https://tululu.org/txt.php"
    parser = argparse.ArgumentParser(description='Программа парсит книги с сайта tululu.org')
    parser.add_argument('--start_id', type=int, help='С какого id начать парсинг', default=1)
    parser.add_argument('--end_id', type=int, help='На каком id закончить парсинг', default=10)
    args = parser.parse_args()

    for id_ in range(args.start_id, args.end_id + 1):
        url = f'https://tululu.org/b{id_}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            filename = title_parser(response)
            download_image(response)
            download_txt(txt_url, filename, folder, id_)
            print("Книга скачана")
        except requests.exceptions.ConnectionError:
            print('Не удалось отправить запрос, проверьте соединение с интернетом')
            time.sleep(60)
        except DownloadError as e:
            print(f"Не удалось скачать книгу. Ошибка: {e}")
            continue
        except BookNotFoundError as e:
            print(f'Такой книги не нашлось. Ошибка: {e}')
            continue
        except Redirect as e:
            print(e)
            continue


if __name__ == '__main__':
    main()
