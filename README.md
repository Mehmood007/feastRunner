# FeastRunner

## Description

**This Django project is a comprehensive solution designed to facilitate multiple restaurant vendors in managing their online presence and orders, while offering customers a seamless platform to explore various eateries and place orders effortlessly.**

## Features

- Multi-Restaurant Support
- Vendor Management System
- Search in restaurant
- Customer Sign-Up and Ordering
- Order Management
- Google Maps Integration
- PayPal integrated
- Authentication and User Profiles
- Payment Integration
- Responsive Design


### Technologies Used

| HTML | CSS | JavaScript | Python | Django | PostgreSQL | PayPal |
|------|-----|------------|--------|--------|------------|--------|
| <img src="https://upload.wikimedia.org/wikipedia/commons/6/61/HTML5_logo_and_wordmark.svg" width="50"> | <img src="https://upload.wikimedia.org/wikipedia/commons/d/d5/CSS3_logo_and_wordmark.svg" width="50"> | <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Unofficial_JavaScript_logo_2.svg" width="50"> | <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" width="50"> | <img src="https://upload.wikimedia.org/wikipedia/commons/7/75/Django_logo.svg" width="50"> | <img src="https://wiki.postgresql.org/images/3/30/PostgreSQL_logo.3colors.120x120.png" width="50"> | <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/PayPal_Logo_Icon_2014.svg/487px-PayPal_Logo_Icon_2014.svg.png" width="50"> |



## Setup Locally
- **First clone repo locally**  
  **Run below command in terminal**  
  `git clone https://github.com/Mehmood007/feastRunner.git`


- **Install Dependencies**  
  - First make sure virtual environment is activated  
  - Make sure you have postgres installed on system and running  
`pip install -r requirements.txt`

- **Setup .env**  
  - Create `.env` file inside project  
  - Look into `.env-sample` and fill `.env` accordingly  

- **Google Maps Setup**  
  - To use google maps make sure you have valid api key setup  
  - Change database configuration to postgis  
  - Also install postgis extension in valid database  
  `CREATE EXTENSION postgis;`

- **Run Migrations in app directory**  
  - Make sure you have created db in postgres  
  `python manage.py makemigrations`  
  `python manage.py migrate`


- **Run Server**  
  `python manage.py runserver`

