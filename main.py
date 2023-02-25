import logging
import yaml
import argparse

from dateutil.parser import parse
import time
from datetime import date

from downloader import request_downloader
from utils import get_last_available_date, isValidDate, date_range

# get last available date
last_available_date = get_last_available_date()

parser = argparse.ArgumentParser()
parser.add_argument("--date", type=str, default=last_available_date, help='Date of the request document (yymmdd)')
parser.add_argument('--automate', type=int, default=0, help='Run automatically download all files from the specified date until interupted. Default set to 0, set to 1 or other number to run automatically')

args = parser.parse_args()

with open("config.yaml",'r') as f:
    loggerConfig = yaml.safe_load(f.read())
    logging.config.dictConfig(loggerConfig)

infoLogger = logging.getLogger('infoLogger')
errorLogger = logging.getLogger('errorLogger')

infoLogger.info(f"User input: \ndate: {args.date} \nautomate: {args.automate}")

if args.automate == 0: # single download

    infoLogger.info('Check date validity...')
    isValidDate(args.date, last_available_date)
    infoLogger.info('Valid date!')

    request_downloader(args.date)

else: # automaic download
    failed = set() # record failed dates

    # download data up to the last available date
    try:
        infoLogger.info('Check date validity...')
        isValidDate(args.date, last_available_date)
        infoLogger.info('Valid date!')

        d1 = parse(args.date, fuzzy=True).date()
        d2 = parse(last_available_date, fuzzy=True).date()

        for date in date_range(d1, d2):
            dateStr = date.strftime("%Y%m%d")

            infoLogger.info(f'Check date validity...')
            isValidDate(dateStr, last_available_date)
            infoLogger.info('Valid date!')

            failed.add(request_downloader(dateStr))
            failed.discard(None)

        infoLogger.info("Going to sleep and wait until the next day")
        # 24 hours
        time.sleep(86400)
    except Exception as e:
        errorLogger.error(e)

    while True: # download data daily
        last_available_date = get_last_available_date() # update last available date
        today = date.today().strftime("%Y%m%d")

        try:
            infoLogger.info('Check date validity...')
            isValidDate(today, last_available_date)
            infoLogger.info('Valid date!')

            failed.add(request_downloader(today))
            failed.discard(None)
        except Exception as e:
            errorLogger.error(e)

        # Retry getting failed download files everyday
        while len(failed) != 0:
            re_download = failed.pop()
            infoLogger.info(f"Re-download data for the date {re_download}")
            failed.add(request_downloader(re_download))
            failed.discard(None)

        infoLogger.info("Going to sleep and wait until the next day")
        time.sleep(86400)