# script to scrape with selenium and beautifulsoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re

url = "https://apps.sfc.hk/publicregWeb/searchByRa"
chrome_driver_path = "/home/frontier/01_Programs/03_Playground/scraper/chrome-linux64"

options = Options()
service = Service()
driver = webdriver.Chrome(service=service, options=options)
# headless means no browser window will open
# options.add_argument("--headless")
driver.get(url)
# do some manipulation of the page
# need to wait a bit
# get list of radio buttons
# radio_button = driver.find_elements(By.CLASS_NAME, "x-form-radio-group")
# radio_button.click()

corporate_radio_button = driver.find_element(By.ID, "roleTypeCorporation-inputEl")
corporate_radio_button.click()
wait_time = 1
driver.implicitly_wait(wait_time+10)

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

dropdown = driver.find_element(By.ID, "ext-gen1091")
dropdown.click()
options = driver.find_elements(By.CLASS_NAME, "x-boundlist-item")
for i, option in enumerate(options[:26]):
    if i!=0:
        dropdown.click()
    option.click()
    for radio_id in radio_button_ids:
        radio_button = driver.find_element(By.ID, radio_id)
        radio_button.click()
        search_button = driver.find_element(By.ID, "button-1012-btnEl")
        label = driver.find_element(By.ID, radio_id[:-7]+"boxLabelEl")
        search_button.click()
        page_source = driver.page_source
        element = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "button-1065-btnEl"))
        )
        try:
            element2 = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "x-grid-row"))
            )
        except:
            continue
        while element.is_enabled():
            rows = driver.find_elements(By.CLASS_NAME, "x-grid-row")
            for row in rows:
                try:
                    results = row.text.split('\n')[:4]
                    if not re.findall(r'[\u4e00-\u9fff]+', row.text):
                        # no chinese chars
                        results[3] = results[2]
                        results[2] = ""
                    if len(results) < 2:
                        continue
                    results.append(label.text)
                    results.extend(list(dict.fromkeys([x.strip() for x in results[3].split(',') if x != ""][::-1]))) # split the address into street and citys
                    # clean results

                    data.append(results)
                except:
                    print("could not find the row")
                # ce.append(results[0])
                # names.append(results[1])
                # chinese_names.append(results[2])
                # adresses.append(results[3])
            next_button = driver.find_element(By.ID, "button-1065-btnEl")
            if next_button.is_enabled():
                try:
                    next_button.click()
                except:
                    print("could not click next button")
                    break
            # if driver.find_element(By.ID, "displayfield-1041-inputEl"):
            #     break
            element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "button-1065-btnEl"))
            )

columns = ['ce', 'names', 'nameCN', 'full Address', "SFO License"]
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

# extract information with bs

# print(soup)
# # Find an element by tag name
# element = soup.find("tag_name")

# # Find an element by CSS class
# element = soup.find(class_="class_name")

# # Find an element by ID
# element = soup.find(id="element_id")

# # Extract the text content of an element
# text_content = element.text

# # Extract attribute values from an element
# attribute_value = element["attribute_name"]