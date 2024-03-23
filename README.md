# Job Board Web Scrape & Analysis

The purpose of this project was to create a web scraper that could pull and parse data related to specific searches on a job board, store the extracted data in local database files, and conduct a high-level analysis on the overall data collected. The current use case involved pulling data from Indeed related to different roles within the data field and compare the results between them.

## Table of Contents

[Project Overview](#project-overview)

[Getting Started](#getting-started)

## Project Overview

### Goal
The goal of this project was to collect, analyze and compare data related to different roles within the data field to gauge the market interests of those specific roles. Rather than relying on trying to find the data from different sources and gauging which ones are current or accurate, the data was scraped and parsed directly from a large scale job board - Indeed. Although this project was comparing a subset of jobs within the data field, this program can be modified to search for any other subset of interest in future use cases.

### Detailed Description - Web Scraper
The web scraping aspect of the project accepts inputs from the user with the pertinent ones being a list of jobs to search the job board for and the number of pages to search. For each role provided, the program will navigate to the Indeed webpage and search for that role. The entire html content of the webpage is extracted into Python and the html containers holding the data related to each job is parsed out as a list. This allows for each jobs features to be extracted programmatically using a series of functions that look for each specific data field. Once extracted and modified into the correct format, the data is collected for the number of pages requested by the user and then appended back into the SQLite tables for storage. This process is repeated for each search term identified at the start.  

### Detailed Description - SQLite Storage
The data collected from the webscraper is held in 3 SQLite tables - Jobs, KeywordRef and Salaries. The jobs table has one row for each unique job with the unique features related to the job specifically. The KeywordRef table identifies which jobs were found with each keyword search term since it was possible for different search terms to load in the same job depending on the title and description of the role. Finally, the Salaries table holds more detailed salary information unique to each job but is separated out of the Jobs table to prevent cluttering of data. 

### Detailed Description - Data Analysis
The information from the SQLite tables was pulled into a Jupyter notebook to analyze overall trends and patterns in the data. Analysis included comparisons between variables including keywords, location, salary, job counts and more. 

The scraping and analysis was done using Python while the data extracted was stored in a local SQLite database file. The web scraper used Selenium with the Firefox browser to crawl through the pages and extract the raw data while Beautiful Soup was used to parse the extracted data. Pandas, numpy, sqlite3 and sqlalchemy were used to clean up the data and store it. Finally, seaborn and matplotlib were used to visualize the data in the data analysis section.


## Getting Started

The following libraries were used for this project.
