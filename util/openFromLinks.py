from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep
import selenium


def runWeb(userpp="",browser_path=""):
    """
    opens an instance of browser\n
    optional: include user profile path to access extensions
    """

    b_path = browser_path
    options = webdriver.ChromeOptions()
    options.binary_location = b_path

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


def openNTab(driver, link="", i=0):
    """opens new tab in instanced driver"""
    if link != "":
        driver.execute_script(f"window.open('{link}','{link}')")
        driver.switch_to.window(f'{link}')
    else:
        driver.execute_script("window.open('about:blank','main')")
        driver.switch_to.window('main')
    # driver.execute_script(f"window.open('about:blank','{str(i)}')")
    # driver.switch_to.window(f"{str(i)}")


def openLinks(links=[], specAct="", userpp="",b_path=""):
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
        driver = runWeb(userpp,browser_path=b_path)
    else:
        driver = runWeb(browser_path=b_path)

    # if app is open (T/F): basically it will open twice if T -> F but once if T -> T
    tf = True
    i = 0
    iterLinks = iter(links)
    openNTab(driver=driver)
    while i < len(links):
        link = next(iterLinks)
        openNTab(driver=driver,i=i, link=link)
        #driver.get(next(iterLinks))
        if specAct != "":
            tf = __special(specAct, driver)
        i+=1


def __special(specAct, driver, i=0):
    match(specAct):
        case "internship":
            sleep(1)
            try:
                shadow_section = driver.execute_script(
                    '''return document.querySelector("simplifyjobs-popup").shadowRoot.querySelector("#fill-button")''')
                shadow_section.click()
                return True
            except selenium.common.exceptions.JavascriptException:
                # driver.close()
                # driver.switch_to.window('main')
                return False

        case _:
            return False
