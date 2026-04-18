import os
import re
import shutil
import sys
import time
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from src.exception import CustomException

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)


class ScrapeReviews:
    def __init__(self,
                 product_name:str,
                 no_of_products:int):
        options = Options()
        headless_browser = os.getenv("HEADLESS_BROWSER", "true").lower() not in {
            "0",
            "false",
            "no",
        }

        if headless_browser:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-http2")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            f"--user-agent={os.getenv('SCRAPER_USER_AGENT', DEFAULT_USER_AGENT)}"
        )

        chrome_binary = (
            os.getenv("GOOGLE_CHROME_BIN")
            or os.getenv("CHROME_BIN")
            or shutil.which("google-chrome")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
        )
        if chrome_binary:
            options.binary_location = chrome_binary

        chromedriver_path = os.getenv("CHROMEDRIVER_PATH") or shutil.which("chromedriver")
        service = Service(chromedriver_path) if chromedriver_path else None

        # Start a new Chrome browser session
        if service is not None:
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)

        self.product_name = product_name
        self.no_of_products = no_of_products
        self.http_headers = {
            "User-Agent": os.getenv("SCRAPER_USER_AGENT", DEFAULT_USER_AGENT),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _extract_product_urls_from_html(self, html: str):
        product_urls = []

        soup = bs(html, "html.parser")
        pclass = soup.findAll("ul", {"class": "results-base"})
        for item in pclass:
            href = item.find_all("a", href=True)
            for anchor in href:
                product_urls.append(anchor["href"])

        regex_matches = re.findall(
            r"https://www\.myntra\.com/[^\"']+/buy",
            html,
        )
        for match in regex_matches:
            product_urls.append(match.replace("https://www.myntra.com/", ""))

        return list(dict.fromkeys(product_urls))

    def scrape_product_urls(self, product_name):
        try:
            search_string = product_name.replace(" ","-")
            # no_of_products = int(self.request.form['prod_no'])

            encoded_query = quote(search_string)
            search_url = f"https://www.myntra.com/{search_string}?rawQuery={encoded_query}"

            product_urls = []
            try:
                response = requests.get(
                    search_url,
                    headers=self.http_headers,
                    timeout=30,
                )
                response.raise_for_status()
                product_urls = self._extract_product_urls_from_html(response.text)
            except Exception:
                product_urls = []

            if not product_urls:
                # Fall back to Selenium when the HTTP response does not expose enough data.
                self.driver.get(search_url)
                product_urls = self._extract_product_urls_from_html(self.driver.page_source)

            return product_urls

        except Exception as e:
            raise CustomException(e, sys)

    def extract_reviews(self, product_link):
        try:
            if product_link.startswith("http"):
                productLink = product_link
            else:
                productLink = "https://www.myntra.com/" + product_link

            self.driver.get(productLink)
            prodRes = self.driver.page_source
            prodRes_html = bs(prodRes, "html.parser")
            title_h = prodRes_html.findAll("title")

            self.product_title = title_h[0].text if title_h else product_link
            self.product_rating_value = "No overall rating available"
            self.product_price = "No price available"

            overallRating = prodRes_html.findAll(
                "div", {"class": "index-overallRating"}
            )
            for i in overallRating:
                self.product_rating_value = i.find("div").text

            if self.product_rating_value == "No overall rating available":
                rating_value = prodRes_html.find("div", {"class": "index-overallRating"})
                if rating_value is not None:
                    self.product_rating_value = rating_value.get_text(strip=True)

            price = prodRes_html.findAll("span", {"class": "pdp-price"})
            for i in price:
                self.product_price = i.text

            if prodRes_html.find(
                "div", {"class": "detailed-reviews-userReviewsContainer"}
            ):
                return productLink

            product_reviews = prodRes_html.find(
                "a", {"class": "detailed-reviews-allReviews"}
            )

            if not product_reviews:
                return None
            return "https://www.myntra.com" + product_reviews["href"]
        except Exception as e:
            raise CustomException(e, sys)
        
    def scroll_to_load_reviews(self):
        # Change the window size to load more data
        self.driver.set_window_size(1920, 1080)  # Example window size, adjust as needed

        # Get the initial height of the page
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # Scroll in smaller increments, waiting between scrolls
        while True:
            # Scroll down by a small amount
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(3)  # Adjust this delay if needed
            
            # Calculate the new height after scrolling
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Break the loop if no new content is loaded after scrolling
            if new_height == last_height:
                break
            
            # Update the last height for the next iteration
            last_height = new_height



    def extract_products(self, product_reviews: list):
        try:
            if isinstance(product_reviews, str):
                review_link = product_reviews
            else:
                t2 = product_reviews["href"]
                review_link = "https://www.myntra.com" + t2

            if self.driver.current_url != review_link:
                self.driver.get(review_link)
            
            self.scroll_to_load_reviews()
            
            review_page = self.driver.page_source

            review_html = bs(review_page, "html.parser")
            review = review_html.findAll(
                "div", {"class": "detailed-reviews-userReviewsContainer"}
            )

            user_rating = []
            user_comment = []
            user_name = []
            for i in review:
                user_rating = i.findAll(
                    "div", {"class": "user-review-main user-review-showRating"}
                )
                user_comment = i.findAll(
                    "div", {"class": "user-review-reviewTextWrapper"}
                )
                user_name = i.findAll("div", {"class": "user-review-left"})

            reviews = []
            for i in range(len(user_rating)):
                try:
                    rating = (
                        user_rating[i]
                        .find("span", class_="user-review-starRating")
                        .get_text()
                        .strip()
                    )
                except:
                    rating = "No rating Given"
                try:
                    comment = user_comment[i].text
                except:
                    comment = "No comment Given"
                try:
                    name = user_name[i].find("span").text
                except:
                    name = "No Name given"
                try:
                    date = user_name[i].find_all("span")[1].text
                except:
                    date = "No Date given"

                mydict = {
                    "Product Name": self.product_title,
                    "Over_All_Rating": self.product_rating_value,
                    "Price": self.product_price,
                    "Date": date,
                    "Rating": rating,
                    "Name": name,
                    "Comment": comment,
                }
                reviews.append(mydict)

            review_data = pd.DataFrame(
                reviews,
                columns=[
                    "Product Name",
                    "Over_All_Rating",
                    "Price",
                    "Date",
                    "Rating",
                    "Name",
                    "Comment",
                ],
            )

            return review_data

        except Exception as e:
            raise CustomException(e, sys)
        
    
    def skip_products(self, search_string, no_of_products, skip_index):
        product_urls: list = self.scrape_product_urls(search_string, no_of_products + 1)

        product_urls.pop(skip_index)

    def get_review_data(self) -> pd.DataFrame:
        try:
            # search_string = self.request.form["content"].replace(" ", "-")
            # no_of_products = int(self.request.form["prod_no"])

            product_urls = self.scrape_product_urls(product_name=self.product_name)

            if not product_urls:
                raise ValueError(
                    f"No products were found for '{self.product_name}'. "
                    "Myntra may be blocking automated requests right now."
                )

            

            product_details = []

            review_len = 0


            while review_len < self.no_of_products and review_len < len(product_urls):
                product_url = product_urls[review_len]
                review = self.extract_reviews(product_url)

                if review:
                    product_detail = self.extract_products(review)
                    if product_detail is not None and not product_detail.empty:
                        product_details.append(product_detail)

                    review_len += 1
                else:
                    product_urls.pop(review_len)

            if not product_details:
                raise ValueError(
                    f"Reviews were not available for '{self.product_name}'. "
                    "Try another keyword or try again later."
                )

            self.driver.quit()

            data = pd.concat(product_details, axis=0)
            
            data.to_csv("data.csv", index=False)
            
            return data
            
            
                
            # columns = data.columns

            # values = [[data.loc[i, col] for col in data.columns ] for i in range(len(data)) ]
            
            # return columns, values
        
    

        except Exception as e:
            raise CustomException(e, sys)
