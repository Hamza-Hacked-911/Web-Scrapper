import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import logging

# Configure logging
logging.basicConfig(filename='../logs/scrape.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def get_cars_from_pakwheels():
    base_url = 'https://www.pakwheels.com'
    search_url = f'{base_url}/used-cars/search/-/mk_toyota/md_corolla/yr_2018/ct_karachi/?page='
    cars = []

    for page in range(1, 6):  # Adjust the range based on the number of pages to scrape
        response = requests.get(search_url + str(page))
        soup = BeautifulSoup(response.text, 'lxml')

        car_listings = soup.find_all('div', class_='search-title')

        for car in car_listings:
            car_url = base_url + car.find('a')['href']
            car_name = car.find('a').text.strip()
            
            price_box = car.find_next_sibling('div', class_='price-box')
            car_price = price_box.text.strip() if price_box else 'N/A'
            
            details_box = car.find_next_sibling('div', class_='generic-grey')
            car_details = details_box.text.strip() if details_box else 'N/A'

            cars.append({
                'Name': car_name,
                'Price': car_price,
                'Details': car_details,
                'URL': car_url
            })

    return pd.DataFrame(cars)

def get_cars_from_olx():
    url = 'https://www.olx.com.pk/cars_c84/q-toyota-corolla-2018'
    service = Service('../chromedriver/chromedriver')  # Ensure you have the correct WebDriver for your browser
    driver = webdriver.Chrome(service=service)
    driver.get(url)

    cars = []

    for page in range(1, 6):  # Adjust the range based on the number of pages to scrape
        driver.get(f'{url}?page={page}')
        time.sleep(3)  # Wait for the page to load
        soup = BeautifulSoup(driver.page_source, 'lxml')

        car_listings = soup.find_all('div', class_='_2kHMtA')

        for car in car_listings:
            car_name = car.find('span', class_='_2B_pmu').text.strip()
            car_price = car.find('span', class_='_89yzn').text.strip()
            car_location = car.find('span', class_='_2FRXm9').text.strip()
            car_details_url = car.find('a', class_='core').get('href')
            car_url = f'https://www.olx.com.pk{car_details_url}'

            cars.append({
                'Name': car_name,
                'Price': car_price,
                'Location': car_location,
                'URL': car_url
            })

    driver.quit()
    return pd.DataFrame(cars)

def save_to_csv(dataframe, filename):
    dataframe.to_csv(filename, index=False)

if __name__ == '__main__':
    logging.info('Starting PakWheels scraper')
    pakwheels_cars_df = get_cars_from_pakwheels()
    save_to_csv(pakwheels_cars_df, '../data/pakwheels_cars_2018.csv')
    logging.info('PakWheels data saved to ../data/pakwheels_cars_2018.csv')

    logging.info('Starting OLX scraper')
    olx_cars_df = get_cars_from_olx()
    save_to_csv(olx_cars_df, '../data/olx_cars_2018.csv')
    logging.info('OLX data saved to ../data/olx_cars_2018.csv')

    print("Scraping completed and data saved.")
