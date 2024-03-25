# script to scrape with selenium and beautifulsoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import re

wait_time = 1

# headless means no browser window will open
# options.add_argument("--headless")
# do some manipulation of the page
# need to wait a bit
# get list of radio buttons
# radio_button = driver.find_elements(By.CLASS_NAME, "x-form-radio-group")
# radio_button.click()
url = "https://apps.sfc.hk/publicregWeb/searchByRa"
options = Options()
service = Service()
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)
corporate_radio_button = driver.find_element(By.ID, "roleTypeCorporation-inputEl")
corporate_radio_button.click()
driver.implicitly_wait(wait_time+10)
dropdown = driver.find_element(By.ID, "ext-gen1091")
dropdown.click()
options = driver.find_elements(By.CLASS_NAME, "x-boundlist-item")
# get the drop down 
# drop_down = driver.find_element(By.ID, "boundlist-1074")
# drop_down = driver.find_element(By.CLASS_NAME, "x-boundlist")
ce = []
names = []
chinese_names = []
adresses = []
data = []

radio_button_ids = ["radiofield-1022-inputEl", "radiofield-1023-inputEl", "radiofield-1024-inputEl", 
                    "radiofield-1025-inputEl", "radiofield-1026-inputEl", "radiofield-1027-inputEl",
                    "radiofield-1028-inputEl", "radiofield-1029-inputEl", "radiofield-1030-inputEl",
                    "radiofield-1031-inputEl", "radiofield-1032-inputEl"]


for i, option in enumerate(options[:1]):
    if i!=0:
        dropdown.click()
    option.click()
    for radio_id in radio_button_ids:
        radio_button = driver.find_element(By.ID, radio_id)
        radio_button.click()
        search_button = driver.find_element(By.ID, "button-1012-btnEl")
        label = driver.find_element(By.ID, radio_id[:-7]+"boxLabelEl")
        search_button.click()
        try:
            element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "x-grid-row"))
            )
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            no_results_txt = "Sorry, there is no Name matched with your chosen criteria. Please try again."
            # how many pages are there
            pages = int(soup.find(attrs={"id": "tbtext-1063"}).text.split(' ')[-1])
            for page in range(pages):
                for row in soup.find_all(attrs={"class": "x-grid-row"}):
                    cells = row.find_all(attrs={"class": "x-grid-cell"})
                    results = []
                    name = cells[1].text
                    cn_name = cells[2].text
                    address = cells[5].text
                    results.append(name)
                    results.append(cn_name)
                    results.append(address)
                    data.append(results)
                # check if there is next button
                next_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.ID, "button-1065-btnWrap"))
                )
                next_button.click()
        except TimeoutException:
            print( "Could not find any companies for the selection in time")

columns = ['names', 'nameCN', 'full Address']
max_l = 0
for d in data:
    if len(d) > max_l:
        max_l = len(d)
for i in range(max_l-5):
    columns.append(f"Address Part{i+1}")
# "Address Part1", "Address Part2", "Address Part3", "Address Part4", "Address Part5", "Address Part6", "Address Part7", "Address Part8"
df = pd.DataFrame(data, columns=columns)
df.to_csv("results.csv")
driver.quit()