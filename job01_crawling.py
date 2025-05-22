from numpy.f2py.rules import defmod_rules
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

check_xpath = '//*[@id="contents"]/section/div[4]/div/div[2]/div/div[{}]/button'.format(4)

start_url = 'https://m.kinolights.com/discover/explore'
driver.get(start_url)
time.sleep(0.5)
button_movie = driver.find_element(By.XPATH, button_movie_xpath)
driver.execute_script("arguments[0].click();", button_movie)
time.sleep(3)
check_comedy = driver.find_element(By.XPATH, check_xpath)
driver.execute_script("arguments[0].click();", check_comedy)

for i in range(2):
    driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
    time.sleep(0.2)

hrefs = []
titles = []
for i in range(1, 5):
    href = driver.find_element(By.XPATH, '/html/body/div/div/div/main/div/div[2]/a[{}]'.format(i)).get_attribute('href')
    hrefs.append(href)
    title = driver.find_element(By.XPATH, '/html/body/div/div/div/main/div/div[2]/a[{}]/div/div[2]/span'.format(i)).text
    titles.append(title)
print(hrefs)
print(titles)
reviews = []
for idx, url in enumerate(hrefs):
    driver.get(url + '?tab=review')
    time.sleep(0.)

    for i in range(10):
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
        time.sleep(0.5)
    review = ''
    for i in range(1, 4):
        try:
            review = review + driver.find_element(By.XPATH, '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/a/h5'.format(i)).text
        except NoSuchElementException:
            review = review + driver.find_element(By.XPATH, '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/a[1]/h5'.format(i)).text
            driver.execute_script("arguments[0].click();", review_xpath)
            review = review + driver.find_element(By.XPATH, '//*[@id="contents"]/div[2]/div[1]/div/section[2]/div/div/div/p').text
            driver.back()
        except:
            review = review
    reviews.append(review)
print(reviews)

df = pd.DataFrame({'title': titles, 'reviews': reviews})
df.to_csv('./data/reviews.csv', index=False)