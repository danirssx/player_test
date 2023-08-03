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


def start(self):

    # Avoid blocking the page
    self.wait_time = 6

    options = Options()
    # Add arguments to the api
    options.add_argument('user-agent=Your_Custom_User_Agent')
    options.add_argument('--disable-images')
    options.add_argument('--incognito')
    
    # Set the path to the downloaded files:
    prefs = {'download.default_directory': 'c:\Users\user\Desktop\DATACAMP\player_test'}
    options.add_experimental_option('prefs', prefs)

    # Setting the driver
    service = Service(ChromeDriverManager().install())

    self.driver = webdriver.Chrome(options=options, service=service)



