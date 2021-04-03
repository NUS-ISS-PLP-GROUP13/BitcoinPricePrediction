import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from csv import reader, writer
import numpy as np
import pandas as pd
import re
import time

###########################################################################################
# Script to get both the post url and the post date and writes it to csv

file1 = open('post_urls.csv', 'a', newline='', encoding="utf-8")
writer = csv.writer(file1)

# 1 Jan 2017: 14832000 + 00
# 25 Jan 2021: 16115040 + 00
# 31 March 2021: 1617198872
# Intervals of 7 days: 864 * 7 

for i in range(14832000, 16171989, 864*7):
    url = f"https://redditsearch.io/?term=&dataviz=false&aggs=false&subreddits=bitcoinmarkets&searchtype=posts&search=true&start=\
{i}00&end={i+(864*7)}00&size=1000"

    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    driver.implicitly_wait(5)
    data = driver.page_source
    soup = BeautifulSoup(data, "html.parser")  
    posts = soup.find_all('div', attrs={"class":"content"})

    for post in posts:
        post_url = post.find('div', attrs={"class":"title"}).get('data-url')
        # print("url:", post_url) 
        post_date = post.find('div', attrs={"class":"description"}).find('time', {"class":"date"}).get('title')
        post_date = post_date[:10]
        print(post_date)
        # print("date:", post_date)
        # Write row to file  
        writer.writerow([post_date, post_url])  

    time.sleep(2)
    driver.close()
file1.close()
print('done')

######################################################################
# Script to open each link and crawl all the text inside it

# Unit test for single page

url = "https://www.reddit.com/r/BitcoinMarkets/comments/az6spx/bitcoin_and_ethereum_preparing_for_pump_march/?sort=confidence"

driver = webdriver.Chrome()
driver.get(url)
time.sleep(1)
driver.implicitly_wait(2)

# If there is a button 'View Entire Discussion', click it
try:
    button = driver.find_element_by_xpath("//button[contains(text()='View Entire Discussion')]")
    button.click()
    time.sleep(3)
except:
    pass
data = driver.page_source
soup = BeautifulSoup(data, "html.parser")  

nocomments = soup.find('p', text='no comments yet')
if nocomments is not None:
    print('no comments found')

# Find all divs with data-test-id='comment'
comments = soup.find_all('div', attrs={"data-test-id":"comment"})

for comment in comments:
    # Get username of poster with a tag
    try:
        username = comment.find_previous_sibling('div').find('a', href=re.compile('^/user/.+'))
        print("username: ", username.text) 
    except:
        username = "[deleted]"
        print("[deleted]")
    
    # Find the text of each comment with p tag
    paras = comment.findChildren('p')
    paras = ' '.join(para.text for para in paras) # Join all paras in one comment
    print("comment: ", paras)
driver.close()

###############################################################################
# Iterating over all rows in post_urls.csv

post_urls = open('post_urls_updated.csv', 'r', encoding="utf-8")
postreader = csv.reader(post_urls)
post_texts = open('reddit_post_texts-part4.csv', 'a', newline='', encoding="utf-8")
postwriter = csv.writer(post_texts)

# Write headers
postwriter.writerow(['date', 'url', 'username','text','header'])
options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(options=options)

# Read line by line
j = 0
k = 0

for row in postreader: # list(postreader)[:5]:
    post_date = row[0]
    post_url = row[1]+"?sort=confidence" # sort comments according to most upvoted
    print('date:', post_date)
    print('url:', post_url)
    
    try:
        driver.get(post_url)
    except:
        print("page not found")
        j += 1
        continue
    
    print("at post")

    time.sleep(1)
    driver.implicitly_wait(2)
    # If there is a button 'View Entire Discussion', click it to reveal all comments
    try:
        button = driver.find_element_by_xpath("//button[contains(text()='View Entire Discussion')]")
        button.click()
        time.sleep(1)
    except:
        pass
    
    # Scroll down twice
    for i in range(2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
    print("scrolled down")
    soup = BeautifulSoup(driver.page_source, "html.parser")  

    nocomments = soup.find('p', text='no comments yet')
    if nocomments is not None:
        j += 1
        k += 1
        print(f'no comments found, total {k}\n')
        continue

    try: # Get original post header
        post_header = soup.find('h1').text 
        print(post_header)
    except:
        post_header = ""
        pass
    
    try: # Get original poster's username
        op_postername = soup.find('span', text="Posted by").find_next_sibling().find('a', href=re.compile('^/user/.+')).text
    except:
        op_postername = '[deleted]'
    
    # Get original post text with data-click-id='text'
    try:
        posttext = soup.find('div', attrs={'data-click-id':'text'}).findChildren('p')
        posttext = post_header + " " + " ".join(para.text for para in posttext)
    except:
        posttext = ""
    # Write post header and text to file
    postwriter.writerow([post_date, post_url, op_postername, posttext, 1])

    # Find all comments: divs with data-test-id='comment'
    comments = soup.find_all('div', attrs={"data-test-id":"comment"})
    for comment in comments:
        # Get username of poster with a tag
        try:
            username = comment.find_previous_sibling('div').find('a', href=re.compile('^/user/.+')).text
        except:
            username = "[deleted]"
        # Find the text of each comment with p tag
        paras = comment.findChildren('p')
        paras = ' '.join(para.text for para in paras) # Join text from all p tags together
        # Write post comment to file
        postwriter.writerow([post_date, post_url, username, paras, 0])
    j += 1
    print(f"written {j} out of the pages\n")

driver.close()
post_texts.close()
post_urls.close()  
print("done") 