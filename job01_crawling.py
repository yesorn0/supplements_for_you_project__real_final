from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from setuptools.package_index import user_agent
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime

options = ChromeOptions()
user_agent = ''
options.add_argument('user-agent=' + user_agent)
options.add_argument('lang=en-KR')
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

button_movie_xpath = '//*[@id="contents"]/section/div[3]/div/section/div/div/div[2]/button'
button_drama_xpath = '//*[@id="contents"]/section/div[3]/div/section/div/div/div[3]'
button_anime_xpath = '//*[@id="contents"]/section/div[3]/div/section/div/div/div[4]'
# button_anime_xpath = ''
# button_anime_xpath = ''
# button_anime_xpath = ''

check_xpath = '//*[@id="contents"]/section/div[4]/div/div[2]/div/div[{}]/button'.format(4)
# checkxpath = '//*[@id="contents"]/section/div[4]/div/div[2]/div/div[5]'

start_url = 'https://m.kinolights.com/discover/explore'
driver.get(start_url)
time.sleep(0.5)
button_movie = driver.find_element(By.XPATH, button_movie_xpath)
driver.execute_script("arguments[0].click();", button_movie)
time.sleep(5)
check_comedy = driver.find_element(By.XPATH, check_xpath)
driver.execute_script("arguments[0].click();", check_comedy)

for i in range(3):
    driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
    time.sleep(0.5)
a_tag_xpath = '//*[@id="contentPosterCard-140612"]'
title_xpath = '//*[@id="contentPosterCard-140612"]/div/div[2]/span'

hrefs = []
titles = []

for i in range(1, 5):

