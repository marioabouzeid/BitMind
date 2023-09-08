# BitMind: Cryptocurrency Portfolio API


[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/release/python-38/)
[![Django Version](https://img.shields.io/badge/Django-3.2%2B-green.svg)](https://docs.djangoproject.com/en/3.2/)
[![Django Rest Framework](https://img.shields.io/badge/Django%20Rest%20Framework-3.12%2B-orange.svg)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10%2B-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue.svg)](https://www.postgresql.org/)
[![DRF Spectacular](https://img.shields.io/badge/DRF%20Spectacular-0.14%2B-blue.svg)](https://drf-spectacular.readthedocs.io/)


**Project Description**:

Welcome to BitMind, a cutting-edge platform designed to redefine cryptocurrency management. BitMind is your gateway to seamless cryptocurrency portfolio tracking, transaction management, and data-driven insights. Leveraging the power of PostgreSQL for scalability and security, BitMind offers an unparalleled experience for both cryptocurrency enthusiasts and professionals.

**Key Features**:

- **Scalable PostgreSQL Database**: BitMind's foundation is built on PostgreSQL, ensuring your cryptocurrency data is securely stored and readily scalable as your portfolio grows.
- **User Authentication**: Prioritizing security, BitMind offers robust user authentication with token-based mechanisms, safeguarding your sensitive financial information.
- **Comprehensive Cryptocurrency Management**: Effortlessly access, add, and update an extensive range of cryptocurrencies through an intuitive and user-friendly interface. Real-time data feeds keep your information accurate and up-to-date.
- **Portfolio Tracking**: Keep your finger on the pulse of your cryptocurrency holdings with BitMind's portfolio management tools. Easily create and manage portfolios to track your assets and monitor their performance.
- **Transaction Handling**: BitMind supports a variety of cryptocurrency transaction types, including buys and sells. Create, update, and delete transactions with confidence, knowing that the system ensures precise calculations and data integrity.
- **API Documentation**: Seamlessly integrate BitMind into your projects with comprehensive API documentation, powered by DRF Spectacular. Developers will find it easy to extend and customize BitMind to their specific needs.
- **Effortless Deployment**: BitMind simplifies deployment with Docker and Docker Compose. Included Dockerfiles and Compose configurations make setting up the platform a straightforward process.


**Next Steps:**
To begin your journey with BitMind, follow the installation instructions provided in the project documentation. Prepare to experience a new level of efficiency and control in managing your cryptocurrency portfolio with BitMind.


## Table of Contents

- [BitMind API](#bitmind)
  - [Table of Contents](#table-of-contents)
  - [Technologies Used](#technologies-used)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
  - [Docker and Docker Compose](#docker-and-docker-compose)
  - [API Documentation](#api-documentation)
  - [Custom Permissions](#custom-permissions)

## Technologies Used

Backend Development:

    Python 3.8+
    Django 3.2+
    Django Rest Framework (DRF) 3.12+
    DRF Spectacular 0.14+
    PostgreSQL 13+

Deployment and Containerization:

    Docker 20.10+

## Getting Started

## Prerequisites

Before you start, ensure you have Docker installed on your system. You can download and install Docker from the [official Docker website](https://www.docker.com/get-started).

The project's Docker setup includes all the necessary dependencies, frameworks, and libraries, so you don't need to manually install Python, Django, Django Rest Framework, PostgreSQL, or DRF Spectacular on your local machine.

### Step 1: Clone the Repository

Clone this Git repository to your local machine:

```bash
git clone https://github.com/marioabouzeid/bitmind.git
cd bitmind
```

### Step 2: Create an Environment File

Create a .env file in the project directory to store environment variables. Replace the placeholders with your values:

env

    DB_NAME=your_database_name
    DB_USER=your_database_user
    DB_PASS=your_database_password
    DJANGO_SECRET_KEY=your_django_secret_key

    # If testing you can set it to 0.0.0.0 to run on local mashine
    DJANGO_ALLOWED_HOSTS=your_allowed_hosts
    DEBUG=0_or_1

### Step 3: Build the Docker Image

Build the Docker image for the project:

```bash
docker build -t your-project-name .
```

### Step 4: Run Docker Compose

Run Docker Compose to start the containers for the web application and the PostgreSQL database:

```bash
docker-compose up
```

### Step 5: Check Migrations

Open a new terminal window and enter the web container:

```bash
docker exec -it your-project-name_web /bin/bash
```

Inside the web container, check migrations:

```bash
python manage.py checkmigrations
```

All migrations should be done automatically at container startup

### Step 6: Create a superuser

While still inside the web container, you can create a superuser using the following Django command:

```bash
python manage.py createsuperuser
```

### Step 7: Import Cryptocurrencies

To import default cryptocurrencies into the database, execute the following custom create command inside the web container:

```bash
python manage.py import_cryptocurrencies cryptocurrencies.json
```

Replace cryptocurrencies.json  with the (path /app/file.json) to your JSON file if you changed the file.

### Step 8: Access the Application

You can access the web application at http://0.0.0.0:8000 in your web browser (or your allowed hosts).

That's it! You've successfully set up and run the project using Docker.

## API Documentation

The API documentation is generated with DRF Spectacular and is available at `/api/docs`.

## License

This project is licensed under the MIT License.
