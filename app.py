from flask import Flask, request, jsonify, render_template, session, make_response
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from groq import Groq
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import traceback
import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from groq import Groq
import time
from webdriver_manager.chrome import ChromeDriverManager
import traceback
from selenium_stealth import stealth
import argparse
import os
import time
from threading import Thread, Lock
from queue import Queue
from dotenv import load_dotenv
from tqdm import tqdm
import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bson import ObjectId
from datetime import datetime
from langdetect import detect
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import signal
import psutil
import concurrent.futures
from selenium.common.exceptions import NoSuchElementException
from dateutil.parser import parse
import traceback
from selenium.common.exceptions import TimeoutException

app = Flask(__name__)
session = []

def load_driver():
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108 Safari/537.3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    try:
        service = Service(ChromeDriverManager().install())  
        driver = webdriver.Chrome(service=service, options=chrome_options)
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
        return driver
    except Exception as e:
        traceback.print_exc()
        raise

class ShoppingAssistant:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.driver = load_driver()
        self.lock = threading.Lock()

    def get_product_info(self, product_name):
        url = "https://www.amazon.in/s?k=" + product_name
        #print(url)

        self.driver.get(url)
        time.sleep(5)

        products = self.driver.find_elements(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal")
        prices = self.driver.find_elements(By.CSS_SELECTOR, "span.a-price-whole")

        product_titles = [product.text for product in products[:5]]
        product_prices = [price.text for price in prices[:5]]
        products_with_prices = list(zip(product_titles, product_prices))

        products_with_prices = [f"{product.text} - {price.text}" for product, price in zip(products[:5], prices[:5])]
        return products_with_prices

    def get_ai_response(self, messages):
        #print(messages)
        completion = self.llm_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        return response.strip()
    
    def is_product(self, message):
        classification_messages = [
            {"role": "system", "content": "Answer in True or False. You are an amazon product assistant. Based on the most recent prompt, is it related to buying or browsing any product? Answer only True or False"},
            {"role": "user", "content": message}
        ]
        classification_response = self.get_ai_response(classification_messages)
        return classification_response

    def is_searchable(self, message):
        classification_messages = [
            {"role": "system", "content": "Given that you are a search tool in a shopping website, does the below prompt contain any information that can guide you to search on the website searchbar? Answer only in True or False"},
            {"role": "user", "content": message}
        ]
        classification_response = self.get_ai_response(classification_messages)
        return classification_response

    def extract_search(self, message):
        classification_messages = [
            {"role": "system", "content": "Given that you are a search tool in a shopping website, does the below prompt contain any information that can guide you to search on the website searchbar? Answer only what you will search in the searchbar"},
            {"role": "user", "content": message}
        ]
        product_name = self.get_ai_response(classification_messages)
        product_name = ''.join([char for char in product_name if char.isalpha() or char == '+'])
        return product_name
    
    def add_to_cart(self, index):
        #span.a-price-whole
        
        elements = self.driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")[index-1]
        href = elements.get_attribute("href")
        
        self.driver.get(href)
        time.sleep(5)
        add_to_cart_button = self.driver.find_elements(By.CSS_SELECTOR, "#submit\.add-to-cart > span")[-1]
        add_to_cart_button.click()


    
        

    def proceed_product(self):
        global session 
        #print(session[-1]["content"])
        classification_messages = [
            {"role": "system", "content": "based on the below prompts, you will output the index of the selected product from the list of 5 products (index starting from 1, not 0). You will only output the index"},
            {"role": "user", "content": session[-2]["content"] + "\n\n" + session[-1]["content"]}
        ]
        index = self.get_ai_response(classification_messages)
        self.add_to_cart(int(index))
        return "Item has been added to cart"

    def determine_yes(self):
        global session 
        #print(session[-1]["content"])
        classification_messages = [
            {"role": "system", "content": "Based on the prompt, you will decide whether the product is selected or yet to be selected. Your response will be 0 if product is selected. 1 if product is yet to be selected."},
            {"role": "user", "content": session[-1]["content"]}
        ]
        determined = self.get_ai_response(classification_messages)
        if determined == '1':
            response = self.select_best()
        elif determined == '0':
            response = self.proceed_product()
        return response
    
    def select_best(self):
        global session 
        #print(session[-1]["content"])
        classification_messages = [
            {"role": "system", "content": "Based on the following products, you are to select the best of these. You will also provide the reasoning for your selection, on why it is better than others in a sentence or two."},
            {"role": "user", "content": session[-1]["content"]}
        ]
        classification_messages = self.get_ai_response(classification_messages)
        session.append({"role": "user", "content": "yes"})
        session.append({"role": "assistant", "content": classification_messages})
        classification_messages += "<br><br>Do you want to proceed with my selection?"
        return classification_messages

    def handle_message(self, message):
        global session  
        session.append({"role": "user", "content": message})
        #prices = self.is_pricerange(message)
        #print("is product",self.is_product(message))
        if self.is_product(message) == 'True':
            if self.is_searchable(message) == 'True':
                product_name = self.extract_search(message)
                matching_products = self.get_product_info(product_name)

                if matching_products:
                    response_content = f"Top 5 matching product titles:<br><br>" + "<br><br>".join(matching_products)
                    response_content += "<br><br>Do you want me to select for you?"
                    session.append({"role": "assistant", "content": response_content})
                    
                else:
                    response_content = "Sorry, I couldn't find any matching products on Amazon."
            else:
                response_content = "Please provide more information on the product you want to purchase."

        else:
            ai_response = self.get_ai_response(session)
            session.append({"role": "assistant", "content": ai_response})
            response_content = ai_response

        #session['conversation'].append({"role": "assistant", "content": response_content})
        session = session[-15:]
        return response_content


    def __del__(self):
        self.driver.quit()


llm_client = Groq(api_key="")
assistant = ShoppingAssistant(llm_client)

session = []

@app.before_request
def clear_cookie_on_refresh():
    global session  
    if request.endpoint == 'index':  
        session = []

@app.route('/')
def index():
    global session  
    session = []
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    global session  
    data = request.json
    user_message = data.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    elif "yes" in user_message:
        response = assistant.determine_yes()
    else:
        response = assistant.handle_message(user_message)
    #print(session)
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
