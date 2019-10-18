import logging, csv, time, random, datetime, re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Настраиваем логирование (не обязательно, но при множестве запросов помогает отследить "отлупы")
logging.basicConfig(filename='log.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# Задаём свой формат разделителей (столбцы пилим через |, а новые строки по переносу)
csv.register_dialect('csvCommaDialect', delimiter='|', lineterminator='\n')


# Обернул модуль requests в функцию для удобства
# + добавил слабую защиту от внезапного разрыва соединения и рандомный таймаут
def download_page(url):
    response = ''
    try:
        random.seed()
        time.sleep(random.randrange(1, 3))
        headers = {'User-agent': 'YaBrowser/16.10.0.2564'}
        s = requests.session()
        response = s.get(url, headers=headers)
    except requests.HTTPError:
        logging.error(url)
    except ConnectionError:
        time.sleep(10)
        download_page(url)
    finally:
        return response.text


# Объявляем урл, к которому будем обращаться
url = 'http://fssprus.ru/gosreestr_jurlic/'
# (ОГРН)\s*[0-9]{13,15}|(ИНН)\s*[0-9]{10,12}
# В BS ищем значения по паттерну
dataBS = BeautifulSoup(download_page(url), 'lxml').find_all(text=re.compile('(ИНН)\s*[0-9]{10,12}'))
# Использовал "включения" списков
# По сути цикл в цикле (для каждого row я получаю e и формирую из него список словарей)
rows = [{'inn': e.replace('ИНН', '')} for row in dataBS for e in row.replace('ИНН ', 'ИНН').replace(',', ' ').split(' ')
        if 'ИНН' in e]
df = pd.DataFrame(data=rows)
# С помощью модуля csv пишем данные
with open('fssp.csv', 'wt', encoding='cp1251', errors='ignore') as file:
    writer = csv.DictWriter(file, ['inn'], dialect='csvCommaDialect')
    writer.writerows(rows)
