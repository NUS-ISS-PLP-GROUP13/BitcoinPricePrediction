from selenium import webdriver
import csv
import os
import time
import random

BasePath='https://bitcointalk.org/index.php?board='
TitlePath='2021titles.csv'


def store2CSV(path, data):
    if os.path.isfile(path):
        with open(path, mode="a+", encoding="utf-8", newline="") as f:
            fcsv = csv.writer(f)
            for r in data:
                fcsv.writerow(r)
    else:
        with open(path, mode="w", encoding="utf-8", newline="") as f:
            fcsv = csv.writer(f)
            for r in data:
                fcsv.writerow(r)

def getUrls(path):
    url = "1.0"
    while True:
        try:
            driver = webdriver.Edge()
            driver.minimize_window()
            time.sleep(random.random() * 3 + 2)
            driver.get(path+url)
            url = makePageIndex(url)
            time.sleep(random.random()*3+2)
            #rows=driver.find_elements_by_xpath('//tbody//tr')
            infos=[]
            infos.append([path + url])
            for i in range(2,43):
                info=[]
                title=getEle(driver,'//div[@class="tborder"]/table/tbody/tr['+str(i)+']/td/span[contains(@id,"msg")]/a')
                link=getAtt(driver,'//div[@class="tborder"]/table/tbody/tr['+str(i)+']/td/span[contains(@id,"msg")]/a','href')
                author=getEle(driver,'//div[@class="tborder"]/table/tbody/tr['+str(i)+']/td/a[contains(@title,"View")]')
                replies=getEle(driver,'//div[@class="tborder"]/table/tbody/tr['+str(i)+']/td[@class="windowbg"][2]')
                reviews=getEle(driver,'//div[@class="tborder"]/table/tbody/tr['+str(i)+']/td[@class="windowbg"][3]')
                lastreview = getEle(driver,'//div[@class="tborder"]/table/tbody/tr[' + str(i) + ']/td[@class="windowbg2 lastpostcol"]')
                info.append(title)
                info.append(link)
                info.append(author)
                info.append(replies)
                info.append(reviews)
                info.append(lastreview)
                infos.append(info)
            store2CSV(TitlePath,infos)
        finally:
            driver.close()
            driver.quit()

def getEle(dr, regax):
    try:
        name = dr.find_element_by_xpath(regax)
        if name:
            clear=str(name.text)
            return clear.replace("\n"," ").strip()
        else:
            return "NA"
    except:
        return "NA"

def getAtt(dr, regax,att):
    try:
        name = dr.find_element_by_xpath(regax)
        if name:
            clear=name.get_attribute(att)
            return clear.replace("\n"," ").strip()
        else:
            return "NA"
    except:
        return "NA"

def makePageIndex(index:str):
    out=index[0:2]
    ind=index[2:]
    ind=int(ind)+40
    return out+str(ind)

if __name__=="__main__":
    getUrls(BasePath)