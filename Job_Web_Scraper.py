from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as ex

import time
from datetime import datetime

from bs4 import BeautifulSoup

import numpy as np
import pandas as pd

import sqlite3
import sqlalchemy


def create_initial_empty_df(df_type):
    '''Create empty dataframes to append new jobs and keywords data to.'''

    if df_type == 'job':
        return pd.DataFrame(columns=['id', 'job_title', 'company', 'location', 'rating_provided', 'rating', 'salary_provided', 'salary_text', 'weblink', 'date_recorded']).set_index('id')
    if df_type == 'keyword':
        return pd.DataFrame(columns=['id', 'keyword']).set_index('id')

def get_searchable_dict(dict_type, search_term = None):
    '''Create a dictionary with the existing values from SQL as the keys. Used to do hash lookups to ensure only unique values are inserted back into the database.'''
    engine = sqlalchemy.create_engine('sqlite:///JobData.db')
    if dict_type == 'job':
        return pd.read_sql('SELECT id, row_number() OVER () AS row_num FROM Jobs', engine, index_col= 'id')['row_num'].to_dict()
    if dict_type == 'keyword':
        return pd.read_sql(f"SELECT id, row_number() OVER () AS row_num FROM KeywordRef WHERE keyword = '{search_term}'", engine, index_col= 'id')['row_num'].to_dict()


def create_firefox_driver(headless = False):
    '''Open Firefox webpage usable by program to navigate to webpages.'''
    options = Options()
    options.headless = headless
    driver = webdriver.Firefox(options = options)
    return driver

def click_to_next_page(driver):
    '''Click the next page button, moving to the next page of jobs.'''
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #Scroll to bottom required to load next page button on webpage
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@data-testid="pagination-page-next"]'))).click()
        return True
    except (ex.TimeoutException, ex.ElementClickInterceptedException):
        return False

def close_email_popup(driver):
    '''Clears email popup if prompted on indeed during web scrape.'''
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="DesktopJobAlertPopup-heading"]'))).click()
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="css-yi9ndv e8ju0x51"]'))).click()
        return True
    except ex.TimeoutException:
        print('failed clicking next button')
        return False

def bypass_cloudflare_check(driver):
    '''In rare instances, a cloudflare check comes up on Indeed. This will bypass the cloudflare check if it comes up.'''
    try:
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@title='Widget containing a Cloudflare security challenge']")))
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//label[@class='ctp-checkbox-label']"))).click()
        time.sleep(10)
        return True
    except ex.TimeoutException:
        return False

def parse_webpage_html(driver):
    '''
    Parse the page to extract the html code blocks related to the listings on the left side of the webpage. 
    Creates a list with each element in the list containing the information for each listing.
    '''
    source = driver.page_source
    soup = BeautifulSoup(source, 'lxml')
    job_list = soup.find_all('li', class_ = 'css-5lfssm eu4oa1w0')
    return job_list


def job_is_ad(job):
    '''Ensure element extracted is a job rather than an ad by looking for a class unique to jobs only.'''
    ad_container = job.find('div', class_ = 'mosaic-zone nonJobContent-desktop')
    return ad_container

def get_job_uid(job, id_dict):
    '''Parse out job uid from html string. If job id is not found or it already exists in database then None is retured to tell the program to ignore that job element.'''
    job_uid = job.find('span')['id'].split('-')[1]
    if job_uid is None:
        return None
    if job_uid in id_dict:
        return None
    return job_uid

def get_job_title(job):
    '''Parse out job title from html string'''
    return job.find('h2').text

def get_job_company(job):
    '''Parse out job company from html string'''
    return job.find('span', {'data-testid': 'company-name'}).text

def get_job_location(job):
    '''Parse out job location from html string'''
    return job.find('div', {'data-testid' : 'text-location'}).text

def get_company_rating(job):
    '''Parse out company rating of job from html string. Most companies have no rating, so a y/n field is also passed back to differentiate.'''
    rating_container = job.find('span', {'data-testid': 'holistic-rating'})
    if rating_container:
        return 'y', rating_container.text
    else:
        return 'n', None

def get_job_salary(job):
    '''Parse out job salary from html string. Many jobs have no salary, so a y/n field is also passed back to differentiate'''
    salary_container = job.find('div', class_='metadata salary-snippet-container')
    if salary_container:
        salary_element = salary_container.find('div', {'data-testid': 'attribute_snippet_testid'})
        if salary_element:
            return 'y', salary_element.text
        else: return 'n', None
    else:
        return 'n', None

def get_job_url(job_uid):
    '''Parse out job webpage url from html string'''
    return f'https://ca.indeed.com/viewjob?jk={job_uid}'

def get_current_str_date():
    return datetime.today().strftime('%Y-%m-%d')

def get_job_attrs(job, job_id_dict):
    '''
    Accept html section of code relating to a single job and a reference dictionary of job id's from the Jobs database. 
    Ensures job found has a unique job id and, if so, parses out necessary elements of the job and populates into a pandas dataframe row. This is the main return value.
    If element does not have a job id or it's a duplicate of an existing one, a Null value is returned which will skip that element.
    '''
    if job_is_ad(job):
        return None

    job_uid = get_job_uid(job, job_id_dict)
    if job_uid is None:
        return None
        
    job_title = get_job_title(job) 
    company = get_job_company(job)
    location = get_job_location(job)
    rating_provided, rating = get_company_rating(job)
    salary_provided, salary = get_job_salary(job)
    job_url = get_job_url(job_uid)
    date_recorded = get_current_str_date()

    new_row = {'id': job_uid, 'job_title': job_title, 'company': company, 'location': location, 'rating_provided': rating_provided, 'rating': rating,
    'salary_provided': salary_provided, 'salary_text': salary, 'weblink': job_url, 'date_recorded': date_recorded}
    row_to_add = pd.DataFrame(new_row, index = [0]).set_index('id')

    return row_to_add

def get_keyword_attrs(job, keyword_id_dict, search_term):
    '''
    Accept html section of code relating to a single job, a reference dictionary of job id's and keyword in the keyword database, and the search term used for the current job found.
    Ensures job and keyword combination found is unique and, if so, populates the job id and keyword into a pandas dataframe row. This is the return value. 
    If element does not have a job id or it's a duplicate of an existing one, a Null value is returned which will skip that element. 
    ''' 
    if job_is_ad(job):
        return None

    job_uid = get_job_uid(job, keyword_id_dict)
    if job_uid is None:
        return None

    new_row = {'id': job_uid, 'keyword': search_term}
    row_to_add = pd.DataFrame(new_row, index = [0]).set_index('id')

    return row_to_add

def append_single_webpage_of_job_info_to_dfs(job_list, job_df, job_id_dict, keyword_df, keyword_id_dict, search_term):
    '''
    Loops through each listing in list provided. For each listing, calls functions to ensure listing is a job and if so, extract the relevant features provided for the job. 
    Returns this information as a pandas dataframe. Returns information for both job and keyword dataframes. 
    '''    
    for job in job_list:
        new_job = get_job_attrs(job, job_id_dict)
        new_keyword = get_keyword_attrs(job, keyword_id_dict, search_term)

        try:
            if new_job is not None:
                job_df = pd.concat([job_df, new_job], verify_integrity = True)
        except ValueError:
            pass
        
        try:
            if new_keyword is not None:    
                keyword_df = pd.concat([keyword_df ,new_keyword], verify_integrity = True)
        except ValueError:
            pass

    return job_df, keyword_df

def crawl_webpages_to_append_job_data_to_dfs(search_term, search_location, page_limit = 100):
    '''
    Web scraper function to navigate to indeed, search for requested job title keywork (search_term), and loop through pages up to specified limit (page_limit).
    The job data is extracted from the webpages and sent to necessary functions to parse. New jobs found are appended to the relevant pandas dataframes. 
    '''
    job_df = create_initial_empty_df('job') 
    job_id_dict = get_searchable_dict('job') 

    keyword_df = create_initial_empty_df('keyword')
    keyword_id_dict = get_searchable_dict('keyword', search_term)

    driver = create_firefox_driver()
    driver.get(f'https://ca.indeed.com/jobs?q={search_term}&l={search_location}&lang=en')
    
    for page in range(1,page_limit+1):    
        if page > 1:
            if not click_to_next_page(driver):
                if not close_email_popup(driver):
                    if not bypass_cloudflare_check(driver):
                        print(f'reached last page of jobs at page: {page}, page requested: {page_limit}')
                        driver.close()
                        return job_df, keyword_df

        job_list = parse_webpage_html(driver)
        
        job_df, keyword_df = append_single_webpage_of_job_info_to_dfs(job_list, job_df, job_id_dict, keyword_df, keyword_id_dict, search_term)

    print(f'page reached: {page}, page requested: {page_limit}')
    driver.close()    
    return job_df, keyword_df


def assign_salary_period(df):
    '''
    Determine the salary period used for the jobs and populate within dataframe. 
    Periods are typically yearly or hourly salaries; but monthly, weekly and daily periods also exist.
    '''
    df['salary_period'] = np.where(df['salary_text'].str.contains('year'), 'yearly',
    np.where(df['salary_text'].str.contains('hour'), 'hourly',
    np.where(df['salary_text'].str.contains('month'), 'monthly',
    np.where(df['salary_text'].str.contains('day'), 'daily',
    np.where(df['salary_text'].str.contains('week'), 'weekly',
    np.NaN
    )))))

    return df

def assign_salary_type(df):
    '''
    Determine the type of salary for the jobs and populte within dataframe. In this case, type is defined as either range, floor, ceiling or expected. 
    Most of the time, the salary is a range between 2 values (range) or a single value (expected). 
    Sometimes, the top (ceiling) or bottom (floor) of the salary is provided instead (ie. "From $x" or "To $x" respectively).
    '''
    df['salary_type'] = np.where(df['salary_text'].str.contains('–'), 'range',
    np.where(df['salary_text'].str.contains('From'), 'floor',
    np.where(df['salary_text'].str.contains('Up'), 'ceiling',
    np.where(df['salary_text'].str.startswith('$'), 'expected',
    np.NaN
    ))))

    return df

def convert_salary_str_to_float(salary_str, salary_type = None, column = None):
    '''Convert a salary string to a floating point number.'''
    if salary_type == 'range':
        if column == 'min':
            return float(salary_str.split('–')[0].replace('$','').replace(',',''))
        if column == 'max':
            return float(salary_str.split('–')[1].split()[0].replace('$','').replace(',',''))

    return float(salary_str.split('$')[1].split()[0].replace(',',''))

def get_actual_salary_values(row):
    '''
    Defines and populates 3 salary columns. "Floor" represents the minimum salary, "Ceiling" represents the maximum salary, and "Expected" represents the expected salary. 
    The "Range" salary type has a floor and ceiling value with the a calculated expected being linearlly interpolated between the two. The rest only have one salary value corresponding to their respective type. 
    '''
    if row['salary_type'] == 'range':
        row['floor'] = convert_salary_str_to_float(row['salary_text'], 'range', 'min')
        row['ceiling'] = convert_salary_str_to_float(row['salary_text'], 'range', 'max')
        row['expected'] = round((row['ceiling'] + row['floor'])/2.0,2)
        return row
    if row['salary_type'] == 'expected':
        row['expected'] = convert_salary_str_to_float(row['salary_text'])
        return row
    if row['salary_type'] == 'ceiling':
        row['ceiling'] = convert_salary_str_to_float(row['salary_text'])
        return row
    if row['salary_type'] == 'floor':
        row['floor'] = convert_salary_str_to_float(row['salary_text'])
        return row
        
def create_salary_df(job_df):
    '''Use jobs with salaries provided to create a dataframe with salary numbers for those jobs.'''
    salary_df = job_df[job_df['salary_provided'] == 'y'][['salary_text']]

    salary_df = (
        salary_df.pipe(assign_salary_period).pipe(assign_salary_type).apply(get_actual_salary_values, axis=1)
    )
    return salary_df


def assign_job_location_type(job_df):
    '''
    Defines a location "type" based on presence or absence of "in" or "," in the location string. The location fields that can be parsed from the string will depend on the location type determined.
    The typical format for a location string is: "[Location Model] in [city], [jurisdiction]. Where location model is "Remote", "Hybrid Remote", etc. 
    However, all three fields there are optional so the parsing has to be able to account for this. 
    '''
    job_df['location_type'] = np.where(~job_df['location'].str.contains(' in |,', regex = True), 'neither',
    np.where(~job_df['location'].str.contains(' in ') & job_df['location'].str.contains(','), 'comma',
    np.where(job_df['location'].str.contains(' in ') & ~job_df['location'].str.contains(','), 'in',
    np.where(job_df['location'].str.contains(' in ') & job_df['location'].str.contains(','), 'both',
    np.NaN))))

    return job_df

def get_job_location_model(row):
    '''Parse out location model based on location string and location type. This is done on a row basis.'''
    if row['location_type'] == 'neither':
        if row['location'] in ['Remote', 'Remote Hybrid']:
            row['location_model'] = row['location']
            return row

    elif row['location_type'] == 'comma':
        row['location_model'] = 'Not Specified'
        return row

    elif row['location_type'] == 'in' or row['location_type'] == 'both':
        row['location_model'] = row['location'].split(' in ')[0]
        return row
    
    row['location_model'] = 'Not Specified'
    return row

def check_if_jurisdiction(location_str):
    '''Checks to see if location string contains a reference to a Canadian jurisdiction (province/territory)'''
    
    canada_jurisdictions = {'Alberta' : 'AB', 'British Columbia': 'BC', 'Manitoba': 'MB', 'New Brunswick': 'NB', 'Newfoundland and Labrador': 'NL', 'Nova Scotia': 'NS', 'Ontario': 'ON', 
    'Prince Edward Island': 'PE', 'Quebec': 'QC', 'Saskatchewan': 'SK', 'Northwest Territories': 'NT', 'Nunavut': 'NU', 'Yukon': 'YT'}

    if location_str in canada_jurisdictions:
        return True
    return False

def check_if_country(location_str):
    '''At times, the location string provides just the country and no other information - this is a check for that.'''
    if location_str in ['Canada']:
        return True
    return False

def get_abbreviated_jurisdiction(jurisdiction_str):
    '''Returns an abbreviated form of the canadian jurisdiction based on the full name string provided.'''

    canada_jurisdictions = {'Alberta' : 'AB', 'British Columbia': 'BC', 'Manitoba': 'MB', 'New Brunswick': 'NB', 'Newfoundland and Labrador': 'NL', 'Nova Scotia': 'NS', 'Ontario': 'ON', 
    'Prince Edward Island': 'PE', 'Quebec': 'QC', 'Saskatchewan': 'SK', 'Northwest Territories': 'NT', 'Nunavut': 'NU', 'Yukon': 'YT'}

    return canada_jurisdictions.get(jurisdiction_str, 'Not Found')

def get_job_city(row):
    '''Parse out city based on location string and location type. This is done on a row basis.'''
    if row['location_type'] == 'neither':
        if not check_if_jurisdiction(row['location']) and not check_if_country(row['location']):
            row['city'] = row['location']
            return row

    elif row['location_type'] == 'comma':
        row['city'] = row['location'].split(',')[0]
        return row

    elif row['location_type'] == 'in':
        row['city'] = 'Not Specified'
    
    elif row['location_type'] == 'both':
        row['city'] = row['location'].split(',')[0].split(' in ')[1]
        return row
    
    row['city'] = 'Not Specified'
    return row

def get_job_jurisdiction(row):
    '''Parse out juristiction based on location string and location type. This is done on a row basis.'''
    if row['location_type'] == 'neither':
        if check_if_jurisdiction(row['location']):
            row['jurisdiction'] = get_abbreviated_jurisdiction(row['location'])
            return row

    elif row['location_type'] == 'comma':
        row['jurisdiction'] = row['location'].split(', ')[1]
        return row

    elif row['location_type'] == 'in':
        location_to_check = row['location'].split(' in ')[1]
        if check_if_jurisdiction(location_to_check):
            row['jurisdiction'] = get_abbreviated_jurisdiction(location_to_check)
            return row
    
    elif row['location_type'] == 'both':
        row['jurisdiction'] = row['location'].split(', ')[1]
        return row
    
    row['jurisdiction'] = 'Not Specified'
    return row

def get_job_country(df, country):
    '''Parse out country based on location string.'''
    df['country'] = country
    return df

def get_job_location_attrs(job_df, country):
    '''Pass dataframe into various functions that parse out location attributes from the location string using method chaining. Parsed attributes are populated into the database and returned.'''
    job_df_with_location_data = (
        job_df.pipe(assign_job_location_type).apply(get_job_location_model, axis=1).apply(get_job_city, axis=1).apply(get_job_jurisdiction, axis=1).pipe(get_job_country, country)
    )

    return job_df_with_location_data[['job_title','company','location','rating_provided','rating','salary_provided','weblink','date_recorded','location_model','country', 'jurisdiction','city']]


def append_pandas_to_sql(df, df_type):
    '''Take dataframes created and populated by program with new jobs found and append them to the existing SQL tables.'''

    engine = sqlalchemy.create_engine('sqlite:///JobData.db')

    if df_type == 'job':
        try:
            df.to_sql('Jobs', engine, if_exists='append')
            return True
        except Exception as e:
            print(f'Cannot add to job table. Error raised: {e}')
    if df_type == 'keyword':
        try:
            df.to_sql('KeywordRef', engine, if_exists='append')
            return True
        except Exception as e:
            print(f'Cannot add to keyword table. Error raised: {e}')
    if df_type == 'salary':
        try:
            df.to_sql('Salaries', engine, if_exists = 'append')
            return True
        except Exception as e:
            print(f'Cannot add to salary table. Error raised: {e}')

def get_indeed_job_data(search_terms, country = 'Canada', page_limit = 15):
    for keyword in search_terms:
        job_df, keyword_df = crawl_webpages_to_append_job_data_to_dfs(keyword, country, page_limit)

        salary_df = create_salary_df(job_df)

        job_df_with_location_data = get_job_location_attrs(job_df, country)

        print(f'New {keyword} jobs found to be added: {len(job_df_with_location_data.index)}')

        append_pandas_to_sql(job_df_with_location_data, 'job')
        append_pandas_to_sql(keyword_df, 'keyword')
        append_pandas_to_sql(salary_df, 'salary')

        
get_indeed_job_data(['data analyst', 'data scientist', 'business intelligence', 'database administrator'], 'Canada', 5)