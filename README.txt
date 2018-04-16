BRIE Readme file

This text file contains a general overview of BRIE's codebase denoting which parts of the codebase contains what functionalities

Folder src - Entire data collection and data loading
	Folder gcp_data_loading - Trials to load data into GCP
	Folder data_migration - Loading appropriate data into mysql and mongo


Folder data - All the cleaned and uncleaned data split into appropirate batches

Folder extra - Some mongo queries for reference

Folder Brie - The entire django web framework 
	Folder Brie - Some basic settings of the product
	Folder app - The required pages, templates and rendering of the product
		Folder templates - Actual html pages
		Folder static - The necessary static files such as images and stylesheets
		Folder migrations - Data loading into mysql supported by Django
		views.py - The View file of the MVC pattern. Can find all functionalities here.
