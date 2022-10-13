from time import sleep
import util.openFromLinks as oL


def press(URL,userpp,b_path,buttonSelector):

    i = 0

    if userpp != "":
        driver = oL.runWeb(userpp,b_path)
    else:
        driver = oL.runWeb(b_path)

    oL.openNTab(driver=driver,index = i, link=URL)#main

    curWindow = driver.current_window_handle

    cont = input("Search on site...")
    print(cont)

    buttons = driver.find_elements(buttonSelector[0],buttonSelector[1])

    print(driver.window_handles)
    print(buttons)

    for button in buttons:

        button.click()
        sleep(0.1)
        driver.switch_to.window(curWindow)
        
        
