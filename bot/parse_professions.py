import requests
from bs4 import BeautifulSoup


url = 'https://equity.today/neobychnye-professij.html'


def get_html(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise ValueError('Request error')


def get_professions(html: bytes) -> list:
    soup = BeautifulSoup(html, 'lxml')
    professions = soup.find_all('h4')
    professions = list(map(lambda x: x.get_text(), professions))
    return professions


def main():
    html = get_html(url)
    professions = get_professions(html)

    with open('../data/professions.txt', 'w') as file:
        for profession in professions:
            file.write(profession + '\n')


if __name__ == '__main__':
    main()
