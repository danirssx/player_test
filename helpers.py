import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time
import re

# class where I will save all the data


class Scrapper:
    # Starting point
    def start(self):

        # Avoid blocking the page
        self.wait_time = 6

        options = Options()
        # Add arguments to the api
        options.add_argument('user-agent=Your_Custom_User_Agent')
        options.add_argument('--disable-images')
        options.add_argument('--incognito')

        # Set the path to the downloaded files:
        prefs = {
            'download.default_directory': 'c:/Users/user/Desktop/DATACAMP/player_test'}
        options.add_experimental_option('prefs', prefs)

        # Setting the driver
        service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(options=options, service=service)

#####################################################################

    # Close the page
    def close(self):
        # Close selenium WebDriver
        self.driver.close()
        self.driver.quit()

#################################################################

    # Get the url
    def get(self, url):
        # Custom function to get the module
        self.driver.get(url)
        time.sleep(self.wait_time)

#############################################################

    def requests_get(self, url):
        # Start header
        self.start()
        # To retrieve an error if there's something wrong
        bool_link = False
        while not bool_link:
            response = requests.get(url)
            time.sleep(5)

            if (response.status_code) == 200:
                bool_link = True

        return response

    def get_match(self, url):
        # Get data url
        response = self.requests_get(url)

        # Parsing data
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup


data = Scrapper()
match = data.get_match(
    'https://fbref.com/en/matches/abf3df21/South-Africa-Italy-August-2-2023-FIFA-Womens-World-Cup')

print(match)
