Book Recommendation and Intelligence Engine (B.R.I.E.) - README FILE

This text file contains a general overview of BRIE's codebase denoting which parts of the codebase contain what functionalities

Folder src - Entire data collection and data loading. Contains the source code for web scraping, data cleaning, recommendation component and more.
	Folder gcp_data_loading - Trials to load data into Google Cloud Platform 
	Folder data_migration - Loading appropriate data into MySQL and Mongo database


Folder data - All the cleaned and uncleaned data split into appropriate batches

Folder extra - Some MongoDB queries for reference

Folder Brie - The entire Django Web Framework
	Folder Brie - Some basic settings of the product
	Folder app - The required pages, templates and rendering of the product
		Folder templates - Actual HTML pages
		Folder static - The necessary static files such as images and stylesheets
		Folder migrations - Data loading into MySQL supported by Django
		views.py - The View file of the MVC pattern. One can find all functionalities here