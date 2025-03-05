# AGRHYMET Django Web Application

This Django web application enables the visualization of meteorological data, focusing on West Africa.  

## Features

- 🌍 **Interactive Map**: Centered on West Africa.
- 🗺️ **Customizable Divisions**: View data by country or administrative regions.
- 📊 **Parameter Selection**: Choose from indicators like:
  - Consecutive Dry Days
  - Total Rainy Days
- 📍 **Hover Information**: Displays latitude, longitude, and values based on the selected parameter.
- 🔍 **Statistical Graphs**: Click on a country or region to visualize statistical insights.

---

## 📌 Installation Guide

Follow the steps below to install and run the project on your local machine.

### 🔧 Prerequisites

Ensure you have the following installed:

- [Python 3.12](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)

### 🛠️ Clone the Repository

```bash
git clone https://github.com/Djifack-ulrich/AGRHYMET-Django-web-app.git
cd AGRHYMET-Django-web-app
```

# 📂 Configure the Data Directory  
You need to add the `SubX/data` directory from the AGRHYMET HPC to the `src` folder.  

To access the AGRHYMET HPC, use:  

```bash
ssh ulrich.djifack@154.127.90.199
```
# 🔑 Password: cra24
Copy the SubX/data directory to your local machine and place it inside the src folder.

## 🏗️ Create a Virtual Environment and Install Dependencies  
On Linux, run:  

```bash
python3.12 -m venv .env3.12
source .env3.12/bin/activate
pip install -r requirements.txt
```

## 🔄 Apply Database Migrations  
Move to the Django project directory:  

```bash
cd src/ClamateAGRHYMET
python manage.py makemigrations
python manage.py migrate
```

## 🚀 Run the Development Server  
Start the Django development server:  

```bash
python manage.py runserver
```

## 📁 Project Structure  

AGRHYMET-Django-web-app/
├── src/
│   ├── ClamateAGRHYMET/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── ...
│   ├── data/
│   │   └── ...
│   └── manage.py
├── requirements.txt
└── README.md





