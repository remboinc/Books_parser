import requests
from pathlib import Path

from requests import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError('Redirect')
    else:
        pass



def book_parser(url, books_path):
    ids = 1
    while ids <= 10:
        params = {"id": ids}
        response = requests.get(url, params=params)
        response.raise_for_status()
        check_for_redirect(response)
        filename = Path(books_path) / f"{ids}.txt"
        with open(filename, 'wb') as file:
            file.write(response.content)
        ids += 1


def main():
    books_path = "books"
    Path(books_path).mkdir(parents=True, exist_ok=True)
    url = "https://tululu.org/txt.php"

    try:
        book_parser(url, books_path)
    except HTTPError:
        print("Не удалось скачать книгу")




if __name__ == '__main__':
    main()
