import pathlib
import shutil
import yaml
import logging.config
import numpy as np
from datetime import date, datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By

from dateutil.parser import parse

# get config values
with open("config.yaml",'r') as f:
    loggerConfig = yaml.safe_load(f.read())
    logging.config.dictConfig(loggerConfig)

infoLogger = logging.getLogger('infoLogger')
errorLogger = logging.getLogger('errorLogger')

def get_last_available_date():
    '''get last available date in the website'''
    # webdriver
    driver = webdriver.Chrome()
    driver.get('https://www.sgx.com/research-education/derivatives')

    # delay
    driver.implicitly_wait(20)

    # xpath to the report date drop down
    date_dropdown_xpath = '//*[@id="page-container"]/template-base/div/div/section[1]/div/sgx-widgets-wrapper/widget-research-and-reports-download[1]/widget-reports-derivatives-tick-and-trade-cancellation/div/sgx-input-select[2]/label/span[2]/input'
    step1 = driver.find_element(By.XPATH, date_dropdown_xpath)

    # click date dropdown box
    driver.execute_script("arguments[0].click();", step1)
    report_date_xpath = '//*[@id="sgx-select-dialog"]/div[2]/sgx-select-picker/sgx-list/div/div/sgx-select-picker-option[1]/label'
    step2 = driver.find_element(By.XPATH, report_date_xpath)
    dateStr = step2.text  # 16 Feb 2023

    driver.quit()

    dateObj = datetime.strptime(dateStr, "%d %b %Y")
    date = dateObj.strftime("%Y%m%d")

    return date


def convert_date_to_index(datereq):
    '''
    Function to calculate the index correspond to the date needs getting data
    :param datereq:
    :return:
    '''
    base = 5356  # date: 20230215
    base_date = date(2023, 2, 15)

    diff = np.busday_count(base_date, datereq.date())

    # calculate index
    index = base + diff

    if index < 0:
        errorLogger.error("There was no report on SGX back then on this day")
        raise Exception

    return index


def create_download_dir(date):
    root_dir = pathlib.Path('downloads/')
    dir = root_dir / f'{date}'
    if dir.exists() and len(list(dir.iterdir()))==4:
        # dir exist and all files downloaded successfully
        errorLogger.error(f'Directory /{dir.as_posix()} already exists. Remove the file or download another file。')
        # raise Exception
        return False
    elif dir.exists() and len(list(dir.iterdir())) < 4:
        # if failed with download all files, delete dir, and re-download data
        shutil.rmtree(dir)

    dir.mkdir(exist_ok=True, parents=True)
    infoLogger.info(f'Directory /{dir.as_posix()} created.')
    return dir.as_posix()


def isValidDate(dateStr, last_available_date):
    # check date format
    try:
        dateObj = parse(dateStr, fuzzy=True).date()
    except Exception as e:
        errorLogger.error("Date format invalid.")

    # check if date is in future
    if dateObj > parse(last_available_date, fuzzy=True).date():
        errorLogger.error(f"There has not been report for this day yet. The last available date is {last_available_date}")
        raise Exception

    # check if date is in weekends
    weekno = dateObj.weekday() # Get Day Number from weekday
    if weekno == 5 or weekno == 6:
        # 5 Sat, 6 Sun
        errorLogger.error("There is no report on the weekends")
        raise Exception

def date_range(d1, d2):
    '''generate list of dates between 2 dates'''
    for n in range(int((d2-d1).days)+1):
        yield d1 + timedelta(n)

if __name__ == '__main__':
    print(get_last_available_date())