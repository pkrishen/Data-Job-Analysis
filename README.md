# Job Board Web Scrape & Analysis

The purpose of this project was to create a web scraper that could pull and parse data related to specific searches on a job board, store the extracted data in local database files, and conduct a high-level analysis on the overall data collected. The current use case involved pulling data from Indeed related to different roles within the data field and compare the results between them.

## Table of Contents

[Project Details](#project-details)

[Getting Started](#getting-started)

## Project Details

### Goal
The goal of this project was to collect, analyze and compare data related to different roles within the data field to gauge the market interests of those specific roles. Rather than relying on trying to find the data from different sources and gauging which ones are current or accurate, the data was scraped and parsed directly from a large scale job board - Indeed. Although this project was comparing a subset of jobs within the data field, this program can be modified to search for any other subset of interest in future use cases.

### Detailed Description - Web Scraper
The web scraping aspect of the project accepts inputs from the user with the pertinent ones being a list of jobs to search the job board for and the number of pages to search. For each role provided, the program will navigate to the Indeed webpage and search for that role. The entire html content of the webpage is extracted into Python and the html containers holding the data related to each job is parsed out as a list. This allows for each jobs features to be extracted programmatically using a series of functions that look for each specific data field. Once extracted and modified into the correct format, the data is collected for the number of pages requested by the user and then appended back into the SQLite tables for storage. This process is repeated for each search term identified at the start.  

### Detailed Description - SQLite Storage
The data collected from the webscraper is held in 3 SQLite tables - Jobs, KeywordRef and Salaries. The jobs table has one row for each unique job with the unique features related to the job specifically. The KeywordRef table identifies which jobs were found with each keyword search term since it was possible for different search terms to load in the same job depending on the title and description of the role. Finally, the Salaries table holds more detailed salary information unique to each job but is separated out of the Jobs table to prevent cluttering of data. 

### Detailed Description - Data Analysis
The information from the SQLite tables was pulled into a Jupyter notebook to analyze overall trends and patterns in the data. Analysis included comparisons between different job features including keywords, location, salary, job counts and more. Overall, the analysis provides a good view of how the market is for the different roles and their related features. If a more current view of market conditions is required, the webscraper can collect the most current data and the analysis can be filtered to the more current datetime range required. 

## Getting Started
The primary objective of this project was to demonstrate the capability of a webscraper to pull sufficient data to get a job market analysis of various roles through data analysis. It wasn't designed specifically for others to be able to pull their own datasets in current state. Having said that, it is still possible to do and, if desired, the steps to do so are outlined below.

### Installation
Download or clone the repository: git clone https://github.com/pkrishen/Data-Job-Analysis.git

If you only require to view the data analysis itself, open the Job_Data_Analysis.ipynb file. It will open in a local web browser and you will be able to scroll through the results and commentary.

Steps to run the webscrape to collect more data and modify the analysis are provided below:

A conda environment was used to build the project. Conversion to pip install created many issues so better to use conda environment to run scripts. 
To create a conda environment, install Miniconda (no pre-packages installed) or Anaconda (full version). 
Links to install Miniconda (https://docs.anaconda.com/free/miniconda/index.html) or Anaconda (https://www.anaconda.com/download).

In Anaconda prompt, install and activate the conda environment with the provided .yml file. Add path locations as necessary: 
conda env create -f webscrape_analysis_project.yml
conda activate webscrape_analysis_project

The webscraper uses Firefox for the webcrawling. You will need to install the Firefox driver for this to work. This project uses version 0.34.0. Installation found here: https://github.com/mozilla/geckodriver/releases

###Usage
To use the webscraper to pull more data, run the Job_Web_Scraper.py file from the terminal or an IDE. To search for different keywords than the default, open the .py file and update the list parameter in the last line as required. The defaults are ['data analyst', 'data scientist', 'business intelligence', 'database administrator']. Save changes then run.

If a clean copy of the data is preferred, delete the JobData.db file and run the Initialize_SQLite_Database.py file to generate empty tables. 

To modify or review data analysis, use the Job_Data_Analysis.ipynb file. Ensure the kernel selected is the same as the conda enviornment created earlier. 
