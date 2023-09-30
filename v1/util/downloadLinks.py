import util.openFromLinks as oL

def downloadLinks(URL,userpp,b_path):
    """click all download links on page at URL"""

    #open browser with main profile or empty
    if userpp != "":
        driver = oL.runWeb(userpp,b_path)
    else:
        driver = oL.runWeb(b_path)

    driver.get(URL)
    curWindow = driver.current_window_handle

    
    