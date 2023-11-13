import os
from urllib.parse import urlsplit
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError
import argparse


def check_for_redirect(response):
    if response.history:
        raise HTTPError('Redirect')


def download_txt(txt_url, filename, folder, ids):
    params = {"id": ids}
    response = requests.get(txt_url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    normal_title = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, f"{ids}. {normal_title}.txt")
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return str(filepath)


def title_parser(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book = soup.find('div', id="content").find('h1').text
    title = book.split('::')[0].strip()
    filename = sanitize_filename(title)
    return filename


def download_image(response):
    folder = "image"
    soup = BeautifulSoup(response.text, 'lxml')
    image_url = soup.find('div', class_='bookimage').find('a').find('img')['src']
    filename = os.path.basename(urlsplit(image_url, scheme='', allow_fragments=True)[2])
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(response):
    all_about_book = {}
    soup = BeautifulSoup(response.text, 'lxml')

    book = soup.find('div', id="content").find('h1').text
    title = book.split('::')[0].strip()
    author = book.split('::')[1].strip()
    book_name = sanitize_filename(title)

    all_books_genres = []
    genres = soup.find('span', class_="d_book").find_all('a')
    for genre in genres:
        all_books_genres.append(genre.text)

    comments = soup.find_all('div', class_='texts')
    all_comments_about_books = []
    for comment in comments:
        comment = comment.find('span', class_="black").text
        all_comments_about_books.append(comment)
    all_about_book[book_name] = {
        'Автор': author,
        'Жанр книги': all_books_genres,
        'Комментарии': all_comments_about_books
    }
    return all_about_book


def main():
    folder = "books"
    txt_url = "https://tululu.org/txt.php"
    parser = argparse.ArgumentParser(description='Программа парсит книги с сайта tululu.org')
    parser.add_argument('--start_id', type=int, help='С какого id начать парсинг', default=1)
    parser.add_argument('--end_id', type=int, help='На каком id закончить парсинг', default=10)
    args = parser.parse_args()

    for ids in range(args.start_id, args.end_id + 1):
        url = f'https://tululu.org/b{ids}'
        response = requests.get(url)
        response.raise_for_status()
        try:
            parse_book_page(response)
            filename = title_parser(response)
            download_image(response)
            download_txt(txt_url, filename, folder, ids)
            print("Скачиваю книгу")
        except HTTPError:
            print("Не удалось скачать книгу -- редирект")
        except AttributeError as e:
            print(f'Такой книги не нашлось. Ошибка: {e}')


if __name__ == '__main__':
    main()
