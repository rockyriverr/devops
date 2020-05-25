import os
import logging
import time
import unicodedata
import graphyte


from selenium import webdriver
from bs4 import BeautifulSoup

logging.getLogger().setLevel(logging.INFO)

BASE_URL = 'https://yandex.ru/pogoda/kaluga'

def parse_yandex_page(page):
    temp = page.findAll('span', {'class': 'temp__value'})[1].text
    wind = page.find('span', {'class': 'wind-speed'}).text
    humidity_press = page.findAll('div', {'class': 'term__value'})
    humidity = humidity_press[3].text
    pressure = humidity_press[4].text


    metrics = []
    metrics.append(('temperature', int(temp)))
    metrics.append(('wind_speed', float(wind.replace(',', '.'))))
    metrics.append(('humidity', int(humidity.replace('%', ''))))
    metrics.append(('pressure', int(pressure.split()[0])))
    return metrics


GRAPHITE_HOST = 'graphite'

def send_metrics(metrics):
    sender = graphyte.Sender(GRAPHITE_HOST, prefix='weather')
    for metric in metrics:
        sender.send(metric[0], metric[1])

def main():

    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        desired_capabilities={'browserName': 'chrome', 'javascriptEnabled': True}
    )

    driver.get('https://yandex.ru/pogoda/kaluga')
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    metric = parse_yandex_page(soup)
    send_metrics(metric)

    driver.quit()

    logging.info('Accessed %s ..', BASE_URL)
    logging.info('Metrics: %s', metric)

if __name__ == '__main__':
    main()
