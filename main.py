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


def genre_parser(response, filename):
    soup = BeautifulSoup(response.text, 'lxml')
    genres = soup.find('span', class_="d_book").find_all('a')
    all_books_genres = []
    for genre in genres:
        all_books_genres.append(genre.text)
    print(filename, '\n', all_books_genres)


def download_image(response):
    folder = "image"
    soup = BeautifulSoup(response.text, 'lxml')
    image_url = soup.find('div', class_='bookimage').find('a').find('img')['src']
    filename = os.path.basename(urlsplit(image_url, scheme='', allow_fragments=True)[2])
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_comments(response, filename):
    folder = "comments"
    Path(folder).mkdir(parents=True, exist_ok=True)
    soup = BeautifulSoup(response.text, 'lxml')
    comments = soup.find_all('div', class_='texts')
    all_comments_about_books = []
    for comment in comments:
        comment = comment.find('span', class_="black").text
        all_comments_about_books.append(comment)
    filepath = os.path.join(folder, f"{filename}.txt")
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write('\n'.join(all_comments_about_books))


def main():
    folder = "books"
    txt_url = "https://tululu.org/txt.php"

    for ids in range(1, 11):
        url = f'https://tululu.org/b{ids}'
        response = requests.get(url)
        response.raise_for_status()
        try:
            filename = title_parser(response)
            genre_parser(response, filename)
            download_image(response)
            download_comments(response, filename)
            download_txt(txt_url, filename, folder, ids)
            print("Скачиваю книгу")
        except HTTPError:
            print("Не удалось скачать книгу -- редирект")
        except AttributeError as e:
            print(f'Такой книги не нашлось. Ошибка: {e}')


if __name__ == '__main__':
    main()
