import util.crawl_link as crawl_link
import util.openFromLinks as openFromLinks

#chrome-extension://pbanhockgagggenencehbnadejlgchfc/oneclickapply.html
#change from example to suit your needs
URL = "https://github.com/pittcsc/Summer2023-Internships"
key = "greenhouse"
file = "misc/links.html"
specAct = "internship"
userpp = r"C:\Users\thewa\AppData\Local\BraveSoftware\Brave-Browser-Nightly\User Data"
browser_path = "C:/Program Files/BraveSoftware/Brave-Browser-Nightly/Application/brave.exe"
###

links = crawl_link.fromFile(file, key) #or fromLink

openFromLinks.openLinks(links,specAct,userpp,b_path = browser_path)  


