import os
import pymorphy2
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine
from aiogram import Bot, Dispatcher, executor


bot = Bot(os.environ.get('TOKEN'))
dp = Dispatcher(bot)

engine_params = {
    'dialect': 'postgresql',
    'driver': 'psycopg2',
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'hostname': 'my_postgres',
    'port': '5432',
    'database': os.environ.get('POSTGRES_DB')
}


def get_postgres_connection(params):
    postgres_engine = create_engine(
        '{dialect}+{driver}://{user}:{password}@{hostname}:{port}/{database}'.format(**params)
    )
    return postgres_engine


class MyBot:
    def __init__(self, postgres_engine):
        self.engine = postgres_engine

    def create_database(self) -> None:
        query = '''
            CREATE TABLE public.user_info (
                userid integer NOT NULL,
                info varchar,
                ts timestamp without time zone
            );
        '''
        self.engine.execute(query)

    def get_random_profession(self) -> str:
        query = f'''
            SELECT profession
            FROM public.professions
            ORDER BY random()
            LIMIT 1;
        '''
        profession = pd.read_sql(query, con=self.engine).values[0, 0]
        return str(profession)

    def get_random_city(self) -> str:
        query = f'''
            SELECT city
            FROM public.cities
            ORDER BY random()
            LIMIT 1;
        '''
        city = pd.read_sql(query, con=self.engine).values[0, 0]
        return str(city)

    def get_random_user_info(self) -> str:
        profession = self.get_random_profession()
        city = self.get_random_city()

        morph = pymorphy2.MorphAnalyzer(lang='ru')
        city = morph.parse(city)[0].inflect({'loct'}).word.capitalize()

        info = profession + ' в ' + city
        return info

    def add_user_info(self, userid: int, info: str, ts: dt.datetime) -> None:
        query = f'''
        INSERT INTO public.user_info (userid, info, ts) VALUES ({userid}, '{info}', '{ts}');
        '''
        self.engine.execute(query)

    def get_user_info(self, userid: int) -> str:
        query = '''
            SELECT userid, info, ts 
            FROM public.user_info;
        '''
        data = pd.read_sql(query, con=self.engine)
        current_ts = dt.datetime.now().replace(microsecond=0)

        if userid in data.userid.values:
            if current_ts - pd.to_datetime(data.loc[data.userid == userid, 'ts'].values[0]) > dt.timedelta(minutes=1):
                info = self.get_random_user_info()
                query = f'''
                    UPDATE public.user_info SET (info, ts) = ('{info}', '{current_ts}'); 
                '''
                self.engine.execute(query)
            else:
                info = data.loc[data.userid == userid, 'info'].values[0]
        else:
            info = self.get_random_user_info()
            query = f'''
                INSERT INTO public.user_info (userid, info, ts) VALUES ({userid}, '{info}', '{current_ts}') 
            '''
            self.engine.execute(query)

        return info


@dp.message_handler(commands=['start'])
async def start(message):
    userid = message.from_user.id
    info = my_bot.get_user_info(userid)
    await message.reply(f'Сегодня ты - {info}')


if __name__ == '__main__':
    engine = get_postgres_connection(engine_params)
    my_bot = MyBot(engine)
    my_bot.create_database()

    executor.start_polling(dp)
