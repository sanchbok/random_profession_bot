import requests
from bs4 import BeautifulSoup
from typing import List


url = 'http://opoccuu.com/goroda.htm'
styles = ['width: 347px; border-left: medium none; border-right: .5pt solid windowtext; '
          'border-top: .5pt solid windowtext; border-bottom: .5pt solid windowtext; padding-left: 5.4pt; '
          'padding-right: 5.4pt; padding-top: 0cm; padding-bottom: 0cm', 'width: 347px; border-left: medium none; '
          'border-right: .5pt solid windowtext; border-top: medium none; border-bottom: .5pt solid windowtext; '
          'padding-left: 5.4pt; padding-right: 5.4pt; padding-top: 0cm; padding-bottom: 0cm']


def get_html(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise ValueError('Request error')


def parse_html(html: bytes, styles: List[str]) -> List[str]:
    soup = BeautifulSoup(html, 'lxml')
    table_rows = soup.find_all('td', style=styles[0]) + soup.find_all('td', style=styles[1])
    cities = []

    for row in table_rows:
        if row.find('p', class_='MsoNormal'):
            city = row.find('p', class_='MsoNormal').get_text()
            cities.append(city.strip())

    return cities


def main():
    html = get_html(url)
    cities = parse_html(html, styles)

    with open('../data/cities.txt', 'w') as file:
        for city in cities:
            file.write(city + '\n')


if __name__ == '__main__':
    main()
