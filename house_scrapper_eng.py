# !pip install translate
import csv
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

print("Checking urls...")
all_appartment_urls = list()
download_urls = [
    # Sale
    'https://www.estate.am/en/apartments-for-sale-s406442?page=',
    # Monthly Rent
    'https://www.estate.am/en/apartments-rentals-s131146?page=',
    # Daily Rent
    'https://www.estate.am/en/daily-rental-apartments-s299123?page='
]
# Saving URLS
try:
    old_urls = pd.read_csv('urls_eng.csv')
    count = old_urls.row.values.tolist()[-1]
    for url in download_urls:
        for pages in range(1, 10000):
            URL = url + f'{pages}'
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
            house_element = soup.find_all("td", class_="last")
            if len(house_element) == 0:
                break
            for house_url in house_element:
                get_house_url = house_url.find("a", href=True)
                new_url = "https://www.estate.am/en" + get_house_url['href']
                if new_url not in old_urls.url.values.tolist():
                    count += 1
                    all_appartment_urls.append([count, new_url])
    print('Fetching new Urls... ')
    print('New Urls: ', len(all_appartment_urls), 'Existing Urls: ', old_urls.shape[0])
    if len(all_appartment_urls) != 0:
        with open('urls_eng.csv', 'a+', encoding="UTF-8", newline='') as f_object:
            writer_object = csv.writer(f_object)
            for row in all_appartment_urls:
                writer_object.writerow(row)
    urls = pd.read_csv('urls_eng.csv')
    print("Updated Urls DB: ", urls.shape[0])
except FileNotFoundError:
    print("File not found")
    print("Creating new file ...")
    count = 0
    for url in download_urls:
        for pages in range(1, 10000):
            URL = url + f'{pages}'
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
            house_element = soup.find_all("td", class_="last")
            if len(house_element) == 0:
                break
            for house_url in house_element:
                get_house_url = house_url.find("a", href=True)
                new_url = "https://www.estate.am/en" + get_house_url['href']
                count += 1
                all_appartment_urls.append([count, new_url])
    print("Updated Urls DB: ", len(all_appartment_urls))
    urls = pd.DataFrame(all_appartment_urls, columns=['row', 'url'])
    urls.to_csv('urls_eng.csv', index=False)

# Saving Apartments
appartments = list()
try:
    appartment_db = pd.read_csv('appartment_descriptions_eng.csv')
    count = old_urls.row.values.tolist()[-1] if 'old_urls' in dir() else 0
    print('Fetching new Appartments ...')
    for apartment in urls.url.values.tolist():
        if apartment not in old_urls.url.values.tolist():
            page = requests.get(apartment)
            soup = BeautifulSoup(page.content, "html.parser")
            time.sleep(1.5)

            appartments.append(
                [
                    soup.find("strong", class_='addr').text,
                    soup.find("span", class_='rooms').text,
                    soup.find("span", class_='ruler').text,
                    re.sub('\s+', ' ', soup.find("span", class_='floor').text),
                    re.sub('\s+', ' ', soup.find("div", class_='price-w').text),
                    re.sub('\s+', ' ', soup.find("p").text),
                    soup.find('div', id='yandex-map')['data-x'],
                    soup.find('div', id='yandex-map')['data-y']

                ]
            )

            count += 1
            print(count)
    print('New Appartments: ', len(appartments), 'Existing Appartments: ', appartment_db.shape[0])
    if len(appartments) != 0:
        with open('appartment_descriptions_eng.csv', 'a+', encoding="UTF-8", newline='') as f_object:
            writer_object = csv.writer(f_object)
            for row in appartments:
                writer_object.writerow(row)
    df_appartments = pd.read_csv('appartment_descriptions_eng.csv')
    print("Updated Appartment DB: ", df_appartments.shape[0])
except FileNotFoundError:
    print("Creating Appartment DB ...")
    count = 0
    for apartment in urls.url.values.tolist():
        page = requests.get(apartment)
        soup = BeautifulSoup(page.content, "html.parser")
        time.sleep(1.5)

        appartments.append(
            {
                'addr': soup.find("strong", class_='addr').text,
                'rooms': soup.find("span", class_='rooms').text,
                'ruler': soup.find("span", class_='ruler').text,
                'floor': re.sub('\s+', ' ', soup.find("span", class_='floor').text),
                'price': re.sub('\s+', ' ', soup.find("div", class_='price-w').text),
                'descr': re.sub('\s+', ' ', soup.find("p").text),
                'lat': soup.find('div', id='yandex-map')['data-x'],
                'lon': soup.find('div', id='yandex-map')['data-y']
            }
        )

        count += 1
        print(count)
    df_appartments = pd.DataFrame(appartments)
    print('Appartment DB: ', count)
    df_appartments.to_csv('appartment_descriptions_eng.csv', index=False)
