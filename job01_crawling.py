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

def scroll_page(scroll_target=None, wait_time=2):
    if scroll_target:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_target)
    else:
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
    time.sleep(wait_time)


def scroll_to_bottom(scroll_target_xpath=None, times=0, wait_time=2):
    if scroll_target_xpath:
        try:
            scroll_target = driver.find_element(By.XPATH, scroll_target_xpath)
        except NoSuchElementException as e:
            print(f"Could not find scroll : {e}")
            return
    else:
        scroll_target = None  # document.body 대상

    if times == 0:
        command = "return arguments[0].scrollHeight" if scroll_target else "return document.body.scrollHeight"
        last_height = driver.execute_script(command, scroll_target)
        while True:
            scroll_page(scroll_target, wait_time=wait_time)
            new_height = driver.execute_script(command, scroll_target)
            if new_height == last_height:
                break
            last_height = new_height
    else:
        for i in range(times):
            scroll_page(scroll_target, wait_time)

options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
options.add_argument('user-agent=' + user_agent)
options.add_argument('lang=ko_KR')
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

button_movie_xpath = '//*[@id="contents"]/section/div[3]/div/section/div/div/div[2]/button'
button_drama_xpath = '//*[@id="contents"]/section/div[3]/div/section/div/div/div[3]/button'
button_anime_xpath = '//*[@id="contents"]/section/div[3]/div/section/div/div/div[4]/button'

check_xpath = '//*[@id="contents"]/section/div[4]/div/div[2]/div/div[{}]/button'.format(4)

start_url = 'https://m.kinolights.com/discover/explore'
driver.get(start_url)
time.sleep(0.5)
button_movie = driver.find_element(By.XPATH, button_movie_xpath)
driver.execute_script('arguments[0].click()', button_movie)
time.sleep(0.5)
check_comedy = driver.find_element(By.XPATH, check_xpath)
driver.execute_script('arguments[0].click()', check_comedy)

scroll_to_bottom(times=10)

hrefs = []
titles = []
for i in range(1, 100):
    href = driver.find_element(By.XPATH,
            '/html/body/div/div/div/main/div/div[2]/a[{}]'.format(i)).get_attribute('href')
    hrefs.append(href)
    title = driver.find_element(By.XPATH,
            '/html/body/div/div/div/main/div/div[2]/a[{}]/div/div[2]/span'.format(i)).text
    titles.append(title)
print(hrefs)
print(titles)
reviews = []
for idx, url in enumerate(hrefs):
    driver.get(url + '?tab=review')
    time.sleep(0.5)

    scroll_to_bottom(scroll_target_xpath='//*[@id="content__body"]', times=5)

    review = ''
    for i in range(1, 10):
        try:
            review_xpath = '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/a[2]'.format(i)
            review_button = driver.find_element(By.XPATH, review_xpath)
            driver.execute_script('arguments[0].click();', review_button)
            time.sleep(0.5)
            try:
                review = review + driver.find_element(By.XPATH,
                      '//*[@id="contents"]/div[2]/div[1]/div/section[2]/div/div/div/p').text
            except:
                review = review + driver.find_element(By.XPATH,
            '//*[@id="contents"]/div[2]/div[1]/div/section[2]/div/div/h3').text
            driver.back()
            print(i, 'try')
        except:
            try:
                review = review + driver.find_element(By.XPATH,
                  '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/a/h5'.format(
                              i)).text
                print(review)
                print(i, 'NoSuchElementException')

            except:
                review = review
                print(i, 'except')

    reviews.append(review)
print(reviews)

df = pd.DataFrame({'titles':titles, 'reviews':reviews})
my_name = 'JKY'
df.to_csv('./data/reviews_{}.csv'.format(my_name), index=False)






print("")








