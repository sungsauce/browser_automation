#!/usr/bin/env python

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pdb
import getpass

company = input("Company to set as the URL Manager: ")
brand_ids = input("Brand IDs: ")

def clean_brand_ids(brand_ids):
    if "," in brand_ids:
        if ", " in brand_ids:
            return brand_ids.split(", ")
        else:
            return brand_ids.split(",")
    else:
        return brand_ids.split()

brand_ids = clean_brand_ids(brand_ids)
urls = []

login_email = input("Login email: ")
login_password = getpass.getpass("Password: ")

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

def log_in():
    driver.get('https://accounts.COMPANYX.com/users/sign_in')
    driver.find_elements_by_class_name('sign-in-button')[1].click()
    email = wait.until(EC.element_to_be_clickable((By.ID, 'identifierId')))
    email.send_keys(login_email)
    driver.find_element_by_id('identifierNext').click()
    wait.until(EC.element_to_be_clickable((By.ID, 'password')))
    password = driver.find_element_by_name('password')
    password.send_keys(login_password)
    next_button = wait.until(EC.element_to_be_clickable((By.ID, 'passwordNext')))
    next_button.send_keys(Keys.RETURN)
    wait.until(EC.element_to_be_clickable((By.ID, 'submit_approve_access')))
    driver.find_element_by_id('submit_approve_access').click()
    wait.until(EC.title_is('ListenFirst Media - Accounts'))
    driver.get('https://admin.listenfirstmedia.com/')

log_in()

# Takes a URL and checks if the company is already set as the URL Manager
# if not, sets the company as the URL Manager
def apply_url_manager(url):
    url_array = url.split('/')
    brand_id = url_array[url_array.index('movies') + 1]
    channel = url_array[-1]

    if 'brand_twitter_engagement_handles' in url:
        apply_engagement_subscriber(url, brand_id)

    else:
        if 'instagram_accounts' in url:
            table_id = 'index_table_instagram_accounts'
            url_manager_col = 6
            edit_col = 7
            add_class = 'select'
            select_id = 'instagram_account_subscriber_group_id'
        else:
            table_id = 'titles'
            url_manager_col = 8
            edit_col = 11
            add_class = 'has_many_add'
            select_id = 'url_subscriber_group_url_junction_attributes_subscriber_group_id'

        driver.get(url)
        try:
            table = driver.find_element_by_id(table_id)
            rows = table.find_elements_by_tag_name('tr')
            if len(rows) == 1:
                print(f"{brand_id}: No URL exists for {company} on {channel}")
                return
            for index, _ in enumerate(rows):
                if index == 0:
                    continue
                tds = rows[index].find_elements_by_tag_name('td')
                url_manager = tds[url_manager_col].text

                if company not in url_manager:
                    tds[edit_col].find_element_by_link_text('Edit').click()
                    driver.find_element_by_class_name(add_class).click()
                    subscriber_group = Select(driver.find_element_by_id(select_id))
                    subscriber_group.select_by_visible_text(company)
                    driver.find_element_by_name('commit').click()
                    print(f"{brand_id}: Successfully applied URL Manager for {company} on {channel}")
                else:
                    print(f"{brand_id}: {company} already set as URL Manager on {channel}")
        except NoSuchElementException:
            print(f"{brand_id}: No URL exists for {company} on {channel}")

def set_engagement_subscriber(url, brand_id):
    try:    
        #If URL exists
        dropdown = Select(driver.find_element_by_id('brand_twitter_engagement_handle_url_id'))
        dropdown.select_by_index(0)
        driver.find_element_by_xpath('//select[@id="brand_twitter_engagement_handle_subscriber_id"]/option[text()="' + company + '"]').click()
        driver.find_element_by_id('brand_twitter_engagement_handle_submit_action').click()
        print(f"{brand_id}: Successfully applied Twitter Engagement subscriber for {company}")
    except NoSuchElementException:
        print(f"{brand_id}: No URL exists for {company} on Twitter Engagement and/or {company} not available as subscriber")

def apply_engagement_subscriber(url, brand_id):
    driver.get(url)
    try:    
        #If no Engagement Handles exist
        driver.find_element_by_link_text('Create one').click()
        set_engagement_subscriber(url, brand_id)

    except NoSuchElementException:  
        #If Engagement Handle exists
        table = driver.find_element_by_class_name("index_as_table")
        cells = table.find_elements_by_tag_name("td")
        found = False
        for cell in cells:
            if cell.text == company:
                found = True
                print(f"{brand_id}: {company} already set as Subscriber on Twitter Engagement")
                break
        if found != True:
            driver.find_element_by_link_text('New Brand Twitter Engagement Handle').click()
            set_engagement_subscriber(url, brand_id)
        return

# Creating urls for each channel based on brand_ids
for brand_id in brand_ids:
    ig_url = 'https://admin.COMPANYX.com/admin/movies/' + brand_id + '/instagram_accounts'
    tw_url = 'https://admin.COMPANYX.com/admin/movies/' + brand_id + '/urls/list?channel=twitter'
    tw_engagement_url = 'https://admin.COMPANYX.com/admin/movies/' + brand_id + '/brand_twitter_engagement_handles'
    fb_url = 'https://admin.COMPANYX.com/admin/movies/' + brand_id + '/urls/list?channel=facebook'

    urls.extend([fb_url, tw_url, tw_engagement_url, ig_url])

for url in urls:
    apply_url_manager(url)
