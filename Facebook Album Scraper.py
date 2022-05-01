from tkinter import *
import requests
from selenium import webdriver
import time
import os
from selenium.webdriver.chrome.options import Options


if __name__ == '__main__':


    # ---------------SETTINGS - CHANGE IF NEEDED----------------------------------
    # File path to chromedriver.exe
    PATH = "./chromedriver.exe"
    # Username - Your FB username
    userid = "FACEBOOK USERID"
    # password - Your FB password
    password = "FACEBOOK PASSWORD"
    # photo album url - URL of the album you want
    album_URL = "URL TO DESIRED ALMUB"
    # folder where images are saved - Name of output folder
    folder_name = "Facebook Album Folder"
    # -----------------------------------------------------------------------------


    # website home page - DO NOT CHANGE
    homepg = "https://www.facebook.com"
    # driver options
    options = Options()
    prefs = {"profile.default_content_setting_values.notifications": 1}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument('--no-sandbox')
    options.add_experimental_option("prefs", prefs)
    # create driver
    driver = webdriver.Chrome(PATH, options=options)

    print("Created driver. Performing login...")
    driver.get(homepg)
    driver.implicitly_wait(6)
    driver.find_element_by_xpath("""//*[@id="email"]""").send_keys(userid)
    driver.find_element_by_xpath("""//*[@id="pass"]""").send_keys(password)
    driver.find_element_by_name("login").click()
    time.sleep(2)
    # jump to album URL after login
    driver.get(album_URL)
    time.sleep(2)

    print("Scrolling to bottom of album page to load images...")
    # scroll to bottom of page to load all images
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    time.sleep(2)

    print("Making a list of all images...")
    # make list of image links
    links = driver.find_elements_by_xpath("//a//img")
    imageLinks = []
    for element in links:
        imageLinks.append(element.get_attribute("src"))

    imageLinks.pop(0)

    # create folder to save images
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)

    print("Saving images from list...")
    # save images from links in imageLinks
    num = 1
    for e in imageLinks:
        response = requests.get(e)
        if response.status_code == 200:
            with open(os.path.join(folder_name, str(num) + ".jpg"), 'wb') as file:
                file.write(response.content)
        num += 1

    print("Done! Folder saved as " + "'" + str(folder_name) + "'")
    driver.close()
