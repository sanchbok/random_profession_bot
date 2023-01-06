import os
import requests
import pandas as pd
from typing import List
from bs4 import BeautifulSoup
from sqlalchemy import create_engine


url = 'https://equity.today/neobychnye-professij.html'


def get_html(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise ValueError('Request error')


def get_professions(html: bytes) -> List[str]:
    soup = BeautifulSoup(html, 'lxml')
    professions = soup.find_all('h4')
    professions = list(map(lambda x: x.get_text(), professions))
    return professions


def save_to_database(data: List[str]) -> None:
    params = {
        'dialect': 'postgresql',
        'driver': 'psycopg2',
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'hostname': 'my_postgres',
        'port': '5432',
        'database': os.environ.get('POSTGRES_DB')
    }
    postgres_engine = create_engine('{dialect}+{driver}://{user}:{password}@{hostname}:{port}/{database}'.format(**params))
    data = pd.DataFrame(data={'profession': data})
    data.to_sql(name='professions', con=postgres_engine, schema='public', if_exists='replace', index=False)


def main():
    html = get_html(url)
    professions = get_professions(html)
    save_to_database(professions)


if __name__ == '__main__':
    main()
