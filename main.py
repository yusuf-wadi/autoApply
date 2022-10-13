from ast import match_case
from tkinter import Button
import util.crawl_link as crawl_link
import util.openFromLinks as openFromLinks
import util.buttonPress as buttonPress

#chrome-extension://pbanhockgagggenencehbnadejlgchfc/oneclickapply.html
#change from example to suit your needs
URL = ""
key = "greenhouse"
file = "misc/links.html"
specAct = "b"
userpp = r"C:\Users\thewa\AppData\Local\BraveSoftware\Brave-Browser-Nightly\User Data"
browser_path = "C:/Program Files/BraveSoftware/Brave-Browser-Nightly/Application/brave.exe"
###

links = crawl_link.fromFile(file, key) #or fromLink

choice = input("Make selection:\nLinks(l)\nButton\n")

match(choice):
    case 'l':
        openFromLinks.openLinks(links,specAct,userpp,b_path = browser_path) 
    case 'b':
        buttonPress.press(URL,userpp,b_path = browser_path, buttonSelector=["xpath","//*[@class='w-full shadow-sm inline-flex items-center justify-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-sm text-white bg-primary-darkest hover:bg-primary-dark focus:outline-none transition ease-in-out duration-150']"])


