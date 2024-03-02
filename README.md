# Hobby Horse Gallery

#### Video Demo: placeholder
Online Web Gallery made for CS50's final project.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Description](#description)
- [Credits](#credits)

## Installation

Project runs on flask, dependencies in requirements.txt.
Made in HTML, CSS, Javascript and Python.

## Usage

Run app.py in python.

## Description

A project made for CS50's final project. 
It's a web gallery that lets users upload images, comment and like images.
The login system uses an username and a hashed password thanks to werkzeug.security.
The layout gets updated depending on whether the user is logged in using a context_processor.
If the user is logged in they can press the logout button to clear all cookies from this page.
Checking if user is logged in is done by using Session from Flask.
Registering requires a password of 8 or more characters.

The gallery system dynamically displays images uploaded by users. It allows for commenting on the image and also liking a image.
If the user is an admin they can delete comments, images and ban users. If a user is banned they're forcibly redirected thanks to before_request and their comments and images are no longer being shown.
The user can sort the images by newest, oldest, most upvoted or in random order using dropdown options.
The user can also search for the image's title, the author's username or both by inputting their desired search in a search bar.
The Javascript in gallery allows for upvoting the image by pressing a button near the image you want to upvote.

The upload system uses upload.html and allows logged in users for submitting their image. Javascript allows for an image to be visible after uploading it.
Users must submit name, description and gender in the form. All of it is being double-checked in python to make sure the data is correct and exists. The magic library is being used to check if the file the users submit is an image.

The project uses SQL databases to store all of it's data except images.
gallery.db has multiple tables including: users, images, reviews, upvotes.
The images are stored in /static/ with a dynamically generated filename thanks to uuid.
In SQL to access the images the project is storing their filename and accesses it later.

The navbar is contained in layout.html.
layout.html is extended to every other file in /templates/.
The title and body is filled by other .html files.

helpers.py contains functions that help with checking the image type and getting image rating.
The type of the file is confirmed using magic library.

Buttons and inputs are styled using CSS in styles.css.

The first registered account has admin privileges that allow for banning users and deleting images.

favicon.png is used for visual reasons.

## Credits

ChatGPT 3.5
Venomkajo, kajres
