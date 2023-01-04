import os
import pymorphy2
import pandas as pd
import datetime as dt
from random import randint
from aiogram import Bot, Dispatcher, executor


bot = Bot(os.environ.get('TOKEN'))
dp = Dispatcher(bot)


class MyBot:
    def __init__(self, database_path, cities_path, professions_path):
        self.db_path = database_path
        self.cities_path = cities_path
        self.professions_path = professions_path

    def create_database(self):
        database = pd.DataFrame(columns=['userid', 'info', 'ts'], index=[0])
        database.to_csv(self.db_path, index=False)

    def get_random_profession(self):
        with open(self.professions_path, 'r') as file:
            professions = file.read().split(sep='\n')
        return professions[randint(0, len(professions) - 1)]

    def get_random_city(self):
        with open(self.cities_path, 'r') as file:
            cities = file.read().split(sep='\n')
        return cities[randint(0, len(cities) - 1)]

    def get_random_user_info(self):
        profession = self.get_random_profession()
        city = self.get_random_city()

        morph = pymorphy2.MorphAnalyzer(lang='ru')
        city = morph.parse(city)[0].inflect({'loct'}).word.capitalize()

        info = profession + ' в ' + city
        return info

    def add_user_info(self, database: pd.DataFrame, userid: int, info: str, ts: dt.datetime):
        user_info = {
            'userid': userid,
            'info': info,
            'ts': ts
        }
        database = database.append(user_info, ignore_index=True)
        return database.to_csv(self.db_path, index=False)

    def get_user_info(self, userid):
        data = pd.read_csv(self.db_path)
        current_ts = dt.datetime.now().replace(microsecond=0)

        if userid in data.userid.values:
            if current_ts - pd.to_datetime(data.loc[data.userid == userid, 'ts'].values[0]) > dt.timedelta(minutes=1):
                info = self.get_random_user_info()

                data.loc[data.userid == userid, 'info'] = info
                data.loc[data.userid == userid, 'ts'] = current_ts

                data.to_csv(self.db_path, index=False)
            else:
                info = data.loc[data.userid == userid, 'info'].values[0]
        else:
            info = self.get_random_user_info()
            self.add_user_info(data, userid, info, current_ts)

        return info


@dp.message_handler(commands=['start'])
async def start(message):
    userid = message.from_user.id
    info = my_bot.get_user_info(userid)
    await message.reply(f'Сегодня ты - {info}')


if __name__ == '__main__':
    my_bot = MyBot('../data/database.csv', '../data/cities.txt', '../data/professions.txt')
    my_bot.create_database()
    executor.start_polling(dp)
