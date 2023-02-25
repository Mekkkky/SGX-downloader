import yaml
import logging
import requests
from datetime import datetime

from utils import create_download_dir, convert_date_to_index, get_last_available_date


# get config values
with open("config.yaml",'r') as f:
    loggerConfig = yaml.safe_load(f.read())
    logging.config.dictConfig(loggerConfig)

infoLogger = logging.getLogger('infoLogger')
errorLogger = logging.getLogger('errorLogger')


def request_downloader(datestr):
    '''
    Function to download data for the given date
    :param datestr:
    :return:
    '''
    dateObj = datetime.strptime(datestr, "%Y%m%d")
    index = convert_date_to_index(dateObj)
    url = 'https://links.sgx.com/1.0.0/derivatives-historical/' + str(index) + '/'

    files = [f'WEBPXTICK_DT.zip', 'TickData_structure.dat', f'TC.txt', 'TC_structure.dat']

    # creating a directory for saving downloaded files
    dir = create_download_dir(datestr)
    infoLogger.info(f'Directory created: {dir}')

    try:
        if dir != False:
            infoLogger.info(f'Start: Downloading {dateObj.strftime("%Y-%m-%d")} data')

            for filename in files:
                trial = 1
                link = url + filename
                infoLogger.info(f'### Downloading {filename}: {link}')
                content = requests.get(link)
                while trial <= 3:
                #  Attempt to download 3 times if failed before going to other downloads
                    if content.ok != True:
                        errorLogger.error(f'Attempt to download again, trial number: {trial}')
                        trial += 1
                        if trial == 4:
                            errorLogger.error(f'### Failed: to download {filename}, {content.status_code}: {content.reason}')
                            return datestr

                    if filename[-3:]=='zip':
                        with open(str(dir)+"/"+filename, 'wb') as f:
                            for info in content.iter_content(chunk_size=128):
                                f.write(info)
                    else:
                        with open(str(dir)+"/"+filename, 'w', encoding='utf-8') as f:
                            f.write(content.text.replace("\r\n", "\n"))

                    infoLogger.info(f'### Success: {filename} downloaded!')
                    break
            infoLogger.info(f'End: {dateObj.strftime("%Y-%m-%d")} data dawnloaded!')
        else:
            pass
    except Exception as e:
        errorLogger.error(e)

if __name__ == '__main__':
    datestr = get_last_available_date()
    request_downloader(datestr)