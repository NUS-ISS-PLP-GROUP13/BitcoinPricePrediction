from selenium import webdriver
import csv
import os
import time
import random
import pandas as pd
import re

BasePath='https://bitcointalk.org/index.php?board='
TitlePath=['2021titles.csv']
ReviewPath='2021reviews.csv'
regRules=[r'<img.*>',r'href=.*>',r'<b>',r'</b>',r'<br>',r'</i>',r'"ul"',r'class',r'<a',r'a>',r'=']

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

def getDetails(path):
    driver = webdriver.Edge()
    #driver.minimize_window()
    while True:
        for p in path:
            try:
                if not driver:
                    driver = webdriver.Edge()
                    driver.minimize_window()
                infos = []
                time.sleep(random.random() * 3 + 1.2)
                driver.get(p[0])
                for i in range(1, 25):
                    info=[]
                    if not checkContent(driver,'/html/body/div[@id="bodyarea"]/form[@id="quickModForm"]/table[@class="bordercolor"]/tbody/tr['+str(i)+']//div[contains(@class,"post")]'):
                        continue
                    reviewer=getEle(driver,'/html/body/div[@id="bodyarea"]/form[@id="quickModForm"]/table[@class="bordercolor"]/tbody/tr['+str(i)+']//td[@valign="top"][1]/b')
                    postime=getEle(driver,'/html/body/div[@id="bodyarea"]/form[@id="quickModForm"]/table[@class="bordercolor"]/tbody/tr['+str(i)+']//div[contains(@class,"subject")]/../div[2]')
                    membership=getEle(driver,'/html/body/div[@id="bodyarea"]/form[@id="quickModForm"]/table[@class="bordercolor"]/tbody/tr['+str(i)+']//td[@valign="top"][1]/div[contains(@class,"small")]')
                    post=getMessage(driver,'/html/body/div[@id="bodyarea"]/form[@id="quickModForm"]/table[@class="bordercolor"]/tbody/tr['+str(i)+']//div[contains(@class,"post")]')
                    if post=="" or reviewer =="" or postime == "" or membership == "":
                        continue
                    info.append(p[0])
                    info.append(p[1])
                    info.append(p[2])
                    info.append(p[3])
                    info.append(p[4])
                    info.append(reviewer)
                    info.append(membership)
                    info.append(post)
                    info.append(postime)
                    infos.append(info)
                store2CSV(ReviewPath,infos)
            except:
                driver.close()
                driver.quit()
        driver.close()
        driver.quit()

def checkContent(dr,regax):
    try:
        name = dr.find_element_by_xpath(regax)
        if name:
            return True
        else:
            return False
    except:
        return False

def getEle(dr, regax):
    try:
        name = dr.find_element_by_xpath(regax)
        if name:
            clear=str(name.text)
            return clear.replace("\n"," ").strip()
        else:
            return ""
    except:
        return ""

def getMessage(dr, regax):
    try:
        name = dr.find_element_by_xpath(regax)
        l=name.get_attribute('innerHTML')
        if l:
            comments = l.split('<br></div>')
            comments = comments[-1].split('quote')
            comments = comments[-1].split('Quote')
            comments = comments[-1].replace("\n", " ").strip() + " "
            for r in regRules:
                comments = re.sub(r, "", comments)
            return comments
    except:
        return False

def getUrls(title):
    ls=[]
    fcsv=csv.reader(open(title,'r',encoding='utf-8'))
    for l in fcsv:
        if l:
            try:
                r=[]
                #[re.match(r'https://.*?\.0\b'.group(),str(l[1]))]+[re.match(r'"?.*(?=,https:/)'.group(),str(l[0])]+[str(l[2])]+str(l[3])+str(l[4])
                url=re.match(r'https://.*?\.0\b',str(l[1])).group()
                r.append(url)
                r.append(l[0])
                r.append(l[2])
                r.append(l[3])
                r.append(l[4])
                #print(str(r))
                ls.append(r)
            except:
                continue
    return ls

if __name__=="__main__":
    for l in TitlePath:
        urls = getUrls(l)
        getDetails(urls)



