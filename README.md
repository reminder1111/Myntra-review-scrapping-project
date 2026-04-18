# Myntra Review Scraping Project

A Streamlit-based review intelligence tool for exploring product feedback from Myntra.

This project searches Myntra products, opens the review pages through Selenium, collects user comments, stores the results in MongoDB when available, and presents them in a simple analysis dashboard. The goal is practical: get review data quickly, compare products side by side, and surface the positive and negative signals without manually opening dozens of product pages.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/reminder1111/Myntra-review-scrapping-project)

## What this project does

- Search a product keyword from the Streamlit interface
- Scrape review data for multiple Myntra products
- Save the collected reviews into `data.csv`
- Store reviews in MongoDB for later access when a database is available
- Generate a quick visual analysis page with rating and price comparisons
- Highlight positive and negative reviews product by product

## Project flow

1. Enter a product name in the Streamlit app.
2. Choose how many products you want to inspect.
3. The scraper opens Myntra in Chrome through Selenium.
4. Product review data is collected and saved locally.
5. The data is optionally written to MongoDB.
6. The analysis page turns that raw review data into visual summaries.

## Tech stack

- Python
- Streamlit
- Selenium
- BeautifulSoup
- Pandas
- Plotly
- MongoDB / PyMongo

## Project structure

```text
.
|-- app.py
|-- pages/
|   `-- generate_analysis.py
|-- src/
|   |-- cloud_io/
|   |-- constants/
|   |-- data_report/
|   |-- scrapper/
|   |-- utils/
|   `-- exception.py
|-- static/
|-- templates/
|-- requirements.txt
|-- setup.py
`-- data.csv
```

## Local setup

### Prerequisites

- Python 3.10 or newer
- Google Chrome installed
- Internet connection for scraping Myntra pages
- Optional: MongoDB connection string if you want cloud storage

### Installation

```bash
git clone https://github.com/reminder1111/Myntra-review-scrapping-project.git
cd Myntra-review-scrapping-project
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app.py
```

Once the server starts, open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Deploy on Render

This repository is configured for Render using a Docker-based web service so Selenium can run with a headless browser in production.

### One-click deploy

Use the button near the top of this README, or open:

[Deploy to Render](https://render.com/deploy?repo=https://github.com/reminder1111/Myntra-review-scrapping-project)

### Why Docker is used here

The app depends on Selenium and a Chrome-compatible browser. Render's docs note that native runtimes only include a fixed set of tools, and Docker is the right choice when your service needs OS-level packages that are not included by default.

### Render service notes

- Runtime: `Docker`
- Health check path: `/`
- Public URL: Render will assign your service a unique `onrender.com` subdomain after deployment
- Optional env var: `MONGO_DB_URL` if you want to store reviews in your own MongoDB instance

### Live deployment link

```text
https://myntra-review-scraping-project.onrender.com
```

## MongoDB configuration

The app can run even if MongoDB is not reachable. If you want to store reviews in your own database, set the connection string before starting the app:

```bash
set MONGO_DB_URL=your_mongodb_connection_string
```

On PowerShell:

```powershell
$env:MONGO_DB_URL="your_mongodb_connection_string"
```

## Using the app

- Open the search page
- Enter a product keyword such as `shirts`, `sneakers`, or `kurtas`
- Select how many products you want to scrape
- Click `Scrape Reviews`
- Move to the analysis page to explore charts and grouped review summaries

## Notes

- Selenium requires Chrome to be available on the machine.
- Scraping depends on Myntra's current page structure, so selectors may need updates if the site layout changes.
- MongoDB storage is treated as optional so the project still works for local exploration.
- The generated `data.csv` gives you a direct export of the latest scrape.

## Why this project is useful

Review data is noisy when read one product page at a time. This project helps turn that noise into something more actionable. Instead of browsing manually, you get a repeatable way to collect reviews, compare products, and spot trends in pricing, ratings, and customer sentiment.

## Future improvements

- Better selector resilience for Myntra layout changes
- Headless browser mode for server deployments
- Cleaner sentiment analysis on review text
- Downloadable reports from the dashboard
- More robust session and error handling

## Author

- Neha Nishad
- Email: nehanishad200311@gmail.com
