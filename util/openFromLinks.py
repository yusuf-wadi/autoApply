from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep
import selenium


def runWeb(userpp=""):
    """
    opens an instance of browser\n
    optional: include user profile path to access extensions
    """

    brave_path = "C:/Program Files/BraveSoftware/Brave-Browser-Nightly/Application/brave.exe"
    options = webdriver.ChromeOptions()
    options.binary_location = brave_path

    # set dl options
    #prefs = {"download.default_directory": "C:/Users/thewa/Desktop/"}
    # e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
    userD = f"--user-data-dir={userpp}"
    options.add_argument(userD)
    options.add_argument(r'--profile-directory=Default')  # e.g. Profile 3
    #options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    return driver


def openNTab(driver, i):
    """opens new tab in instanced driver"""
    body = driver.find_element("tag name", "body")
    body.send_keys(Keys.CONTROL + 't')
    driver.execute_script(f"window.open('about:blank','{i}')")
    driver.switch_to.window(f"{i}")


def openLinks(links=[], specAct="",userpp=""):
    """
    ## opens links in multiple tabs\n
    #### optional:\n
    - include user profile path ```userpp``` to access extensions

    ### current specAct poss. values:
    - "internship"
    - ""
    """

    if(links == []):
        print("Links array must be populated.")
        exit(0)

    if userpp != "":
        driver = runWeb(userpp)
    else:
        driver = runWeb()

    for i, link in enumerate(links):
        openNTab(driver, i)
        driver.get(link)
        if specAct != "":
            __special(specAct, driver)


def __special(specAct, driver):
    match(specAct):
        case "internship":
            sleep(1)
            try:
                shadow_section = driver.execute_script('''return document.querySelector("simplifyjobs-popup").shadowRoot.querySelector("#fill-button")''')
                shadow_section.click()
            except selenium.common.exceptions.JavascriptException:
                print("next")
        case _:
            return False
