import requests
from pathlib import Path


def book_parser(url, books_path):
    try:
        ids = 1
        while ids != 11:
            params = {"id": ids}
            response = requests.get(url, params=params)
            response.raise_for_status()
            filename = Path(books_path) / f"{ids}.txt"
            with open(filename, 'wb') as file:
                file.write(response.content)
            ids += 1
    except Exception:
        print(f"Не удалось скачать книгу {filename}")


def main():
    books_path = "books"
    Path(books_path).mkdir(parents=True, exist_ok=True)
    url = "https://tululu.org/txt.php"
    book_parser(url, books_path)


if __name__ == '__main__':
    main()
