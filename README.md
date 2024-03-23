# Job Board Web Scrape & Analysis

The purpose of this project was to create a web scraper that could pull and parse data related to specific searches on a job board, store the extracted data in local database files, and conduct a high-level analysis on the overall data collected. The current use case involved pulling data from Indeed related to different roles within the data field and compare the results between them.

## Table of Contents

[Project Overview](#project-overview)

[Getting Started](#getting-started)

## Project Overview

The goal of this project was to collect, analyze and compare data related to different roles within the data field to gauge the market interests of those specific roles. Rather than relying on trying to find the data from different sources and gauging which ones are current or accurate, the data was scraped and parsed directly from a large scale job board - Indeed. Although this project was comparing a subset of jobs within the data field, this program can be modified to search for any other subset of interest in future use cases. 

The scraping and analysis was done using Python while the data extracted was stored in a local SQLite database file. The web scraper used Selenium with the Firefox browser to crawl through the pages and extract the raw data while Beautiful Soup was used to parse the extracted data. Pandas, numpy, sqlite3 and sqlalchemy were used to clean up the data and store it. Finally, seaborn and matplotlib were used to visualize the data in the data analysis section. 

## Getting Started

The following libraries were used for this project.
