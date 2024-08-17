
# Shopping Assistant Application

This is a Flask-based web application that serves as an Amazon shopping assistant, using Selenium for web scraping and a Large Language Model (LLM) client for natural language processing. The application can search for products on Amazon, provide product details, and assist in adding items to the cart based on user input.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Application Overview](#application-overview)
  - [Main Components](#main-components)
  - [Key Functions](#key-functions)
- [Environment Variables](#environment-variables)
- [Technologies Used](#technologies-used)
- [License](#license)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/shopping-assistant.git
   cd shopping-assistant
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory of the project and add the required environment variables as specified in the [Environment Variables](#environment-variables) section.

5. **Run the application:**
   ```bash
   python app.py
   ```

## Usage

- Navigate to `http://localhost:5000` in your web browser to access the application.
- The home page allows you to start a chat session with the shopping assistant.
- Input your product queries, and the assistant will help you find products and assist with adding them to your cart.

## Features

### 1. **Search for Products Like a Pro**
   - Imagine you’re looking for a toy on Amazon. You can just tell the shopping assistant what you want, and it will find the top 5 toys for you! It’s like having a magical helper that knows where to look.

### 2. **Pick the Best One**
   - The shopping assistant doesn’t just find things; it also helps you choose the best one! If you’re unsure which toy to pick, it will suggest the best one and even tell you why it’s the best. It's like having a friend who’s really good at shopping.

### 3. **Add to Cart for You**
   - Once you’ve decided which toy you want, the assistant can put it in your cart for you. No need to click around – it does the work for you! Just like having a robot that knows exactly what you want to buy.

### 4. **Chat with the Assistant**
   - You can talk to the shopping assistant like you talk to a person. Ask it questions, tell it what you’re looking for, and it will chat back with you to help you find what you need. It’s like having a friendly conversation while shopping.

## Application Overview

### Main Components

1. **Flask Application (`app.py`):**
   - Serves as the backend server.
   - Routes incoming requests to the appropriate handler functions.
   - Handles communication between the user and the shopping assistant logic.

2. **Selenium WebDriver:**
   - Used for scraping Amazon's website to retrieve product information.
   - Configured to run in headless mode to simulate user interactions without a visible browser window.

3. **Shopping Assistant (`ShoppingAssistant` class):**
   - Handles the core logic for product searching, selection, and adding items to the cart.
   - Interacts with the LLM client for processing user inputs and generating responses.

4. **LLM Client (Groq):**
   - A language model API client used for processing natural language queries and generating context-aware responses.

### Key Functions

- **`load_driver()`**: Initializes and configures the Selenium WebDriver with the necessary options and settings to bypass bot detection mechanisms on websites like Amazon.

- **`get_product_info(product_name)`**: Searches Amazon for the specified product and returns a list of the top 5 matching products along with their prices.

- **`get_ai_response(messages)`**: Interacts with the LLM to generate a response based on the given chat messages.

- **`is_product(message)`**: Determines if the user's message is related to browsing or purchasing a product.

- **`extract_search(message)`**: Extracts the search query from the user's message to search for products on Amazon.

- **`add_to_cart(index)`**: Adds the selected product to the Amazon cart based on the index provided.

- **`handle_message(message)`**: Main function to handle user messages and generate appropriate responses, either by querying the LLM or interacting with Amazon's website.

### Environment Variables

- **`GROQ_API_KEY`**: API key for accessing the Groq language model API.
- **`CHROMEDRIVER_PATH`**: (Optional) Path to the ChromeDriver executable, if not using `webdriver_manager` for automatic installation.

Create a `.env` file in the root directory with the following content:

```plaintext
GROQ_API_KEY=your_groq_api_key
```

### Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python.
- **Selenium**: A web automation tool used for scraping and interacting with websites.
- **Groq API**: An API for interacting with a large language model for natural language processing.
- **Python**: The programming language used to develop the application.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
