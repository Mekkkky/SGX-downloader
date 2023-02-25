# SGX Downloader
## Description

SGX publishes derivative data daily at the website: https://www.sgx.com/research-education/derivatives

Design a job to download the following files daily from the above website.
1. WEBPXTICK_DT-*.zip
2. TickData_structure.dat
3. TC_*.txt
4. TC_structure.dat

The website is only provided data for the past 5 market days. The older data can only by sending GET request with specific index for the older date.

In this project, a request_downloader() function has been designed to obtain data, some helper functions are included in the utils.py.

## Quick start
### Requirements
```shell
pip install -r requirements.txt
```
### Run
By running the following code, you can download the latest available date data.
```shell
python main.py
```
By specifying a date to get the historcial data on this day.
```shell
python main.py --date 20230214 
```
By giving a date and set automate to 1, to get all data up to the last available date by given date.
```shell
python main.py --date 20230214 --automate 1
```

## Some concerns
1. No clear definite market days. Applying index to get data may not be 100% accurate.
3. If there is a problem with the function get_last_available_date(), manual intervention is required to run it again.