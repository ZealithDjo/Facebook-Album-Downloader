from tkinter import *
import requests
from selenium import webdriver
import time
import os
from selenium.webdriver.chrome.options import Options


# check if login was successful returns 1 if error was found, else 0
def check_errors_login(driver):
    currenturl = driver.current_url
    # failed login will redirect driver to another url
    if currenturl == "https://www.facebook.com/":
        return 0
    # any other url is likely an error in login process
    return 1


# check if URL is valid returns 1 if error was found, else 0
def check_errors_albumurl(albumurl):
    # album urls have "set=a." in them
    if "set=a." in albumurl:
        return 0
    # any other url is likely an error
    return 1


# clears all entries in GUI
def clear_entries():
    entry1.delete(0, END)
    entry2.delete(0, END)
    entry3.delete(0, END)
    entry4.delete(0, END)


# will take input parameters and start Selenium driver to get album
def click(e):
    userid = entry1.get()
    password = entry2.get()
    albumurl = entry3.get()
    foldername = entry4.get()
    loginerr = 1
    urlerr = 1
    PATH = "./chromedriver.exe"
    homepg = "https://www.facebook.com"

    print(foldername)
    print(albumurl)

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
    # check for login error
    loginerr = check_errors_login(driver)
    if loginerr:
        clear_entries()
        displayLabel.config(text="Error in login process. Please confirm login credentials.")
        print("login error")
        driver.close()
    else:
        # check for incorrect album url
        urlerr = check_errors_albumurl(albumurl)
        if urlerr:
            clear_entries()
            displayLabel.config(text="Error in album url.")
            print("Error with album URL. Please Try again.")
            driver.close()
        else:
            # jump to album URL after login
            driver.get(albumurl)
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
            foldername = entry4.get()
            # create folder to save images
            if not os.path.isdir(foldername):
                os.makedirs(foldername)
            print("Saving images from list...")
            # save images from links in imageLinks
            num = 1
            for e in imageLinks:
                response = requests.get(e)
                if response.status_code == 200:
                    with open(os.path.join(foldername, str(num) + ".jpg"), 'wb') as file:
                        file.write(response.content)
                num += 1

            print("Done! Folder saved as " + "'" + str(foldername) + "'")
            displayLabel.config(text="Done! Folder saved as " + "'" + str(foldername) + "'")
            driver.close()

    clear_entries()


if __name__ == '__main__':
    # make Tkinter window
    root = Tk()
    root.title('Facebook Album Downloader')
    root.geometry("700x400")

    # labels
    label1 = Label(root, text="YOUR Facebook User Login", font=("Helvetica", 14), fg="grey")
    label1.grid(row=1, column=0, columnspan=1, padx=10, pady=10)
    label2 = Label(root, text="YOUR Facebook User Password", font=("Helvetica", 14), fg="grey")
    label2.grid(row=2, column=0, columnspan=1, padx=10, pady=10)
    label3 = Label(root, text="URL to album", font=("Helvetica", 14), fg="grey")
    label3.grid(row=3, column=0, columnspan=1, padx=10, pady=10)
    label4 = Label(root, text="Save album folder as", font=("Helvetica", 14), fg="grey")
    label4.grid(row=4, column=0, columnspan=1, padx=10, pady=10)

    # entry bars
    entry1 = Entry(root, font=("Helvetica", 14), width=25)
    entry1.grid(row=1, column=1)
    entry2 = Entry(root, font=("Helvetica", 14), width=25)
    entry2.grid(row=2, column=1)
    entry3 = Entry(root, font=("Helvetica", 14), width=25)
    entry3.grid(row=3, column=1)
    entry4 = Entry(root, font=("Helvetica", 14), width=25)
    entry4.grid(row=4, column=1)

    # button
    button1 = Button(root, text="Download Album", command=lambda: click(ACTIVE), width=40)
    button1.grid(row=5, column=0, columnspan=2)

    # output messages
    displayLabel = Label(root, width=40, font=("Helvetica", 15))
    displayLabel.grid(row=6, column=0, columnspan=2)

    root.mainloop()

