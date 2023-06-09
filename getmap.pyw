from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import time
import pandas as pd
import drawmap as dm
from subprocess import CREATE_NO_WINDOW
# Script will automate gps visualization by using selenium to access OpenStreetMaps.org to get portion of map

def get_map(csv_path, chromedriver_excecutable, map_path):
    # Retrieves the min and max lon and lat cooridnates for bounding box of section of map to get
    df = pd.read_csv(rf'{csv_path}', names=['lat', 'lon'])  # Remove all columns except for lat, lon and flags which are needed

    # File paths need forward slash for default_directory on Windows OS
    path_split = map_path.split('.')[0].split('/')[:-1]
    new_path = r'/'.join(path_split)
    temp_dir = new_path.replace('/', r'\\'[0])
    temp_map_path = f"{temp_dir}/map.png"

    # Get minimum and maximum latitiude and longitude from the cvs. Also add/subtract constant for padding around the image
    min_lat = df['lat'].min() - 0.001
    min_lon = df['lon'].min() - 0.001
    max_lat = df['lat'].max() + 0.001
    max_lon = df['lon'].max() + 0.001

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_experimental_option("prefs", {
        "download.default_directory": temp_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    chrome_service = ChromeService('chromedriver')
    chrome_service.creation_flags = CREATE_NO_WINDOW

    # Modifying elements of html to use input csv's coordinates to capture section of map
    driver = webdriver.Chrome(executable_path=chromedriver_excecutable, options=options, service=chrome_service)
    driver.get(r'https://www.openstreetmap.org/export#map=13/41.0219/-73.7599')

    element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div[4]/form/input[1]')
    driver.execute_script(f"arguments[0].setAttribute('value', '{min_lon}')", element)

    element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div[4]/form/input[2]')
    driver.execute_script(f"arguments[0].setAttribute('value', '{min_lat}')", element)

    element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div[4]/form/input[3]')
    driver.execute_script(f"arguments[0].setAttribute('value', '{max_lon}')", element)

    element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div[4]/form/input[4]')
    driver.execute_script(f"arguments[0].setAttribute('value', '{max_lat}')", element)

    element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div[4]/form/input[7]')
    driver.execute_script(f"arguments[0].click()", element)

    time.sleep(5)
    driver.quit()

    # Start modifying selected map
    dm.create_map(temp_map_path, csv_path, map_path, [min_lat, max_lat, min_lon, max_lon])
