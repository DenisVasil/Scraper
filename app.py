import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from io import BytesIO


def scrape_data():
    try:
        # Set up Chrome options for headless operation and to specify the path to Chrome binary
        options = Options()
        # Path to Chrome binary in the Docker container
        options.binary_location = "/usr/bin/google-chrome"
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Initialize WebDriver
        driver = webdriver.Chrome(service=Service(
            "/usr/local/bin/chromedriver"), options=options)

        # URL to scrape
        url = "https://cvvp.nva.gov.lv/#/pub/apmacibas/grupas"
        driver.get(url)
        time.sleep(5)  # Allow time for the page to load

        # Infinite scroll to load all data
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        scroll_pause_time = 2  # Adjust if needed

        while True:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()  # Close the driver

        # Extract table data
        table = soup.find("table", {"class": "table table-condensed"})

        # Extract headers and rows into lists
        data = []
        headers = [th.text.strip()
                   for th in table.find("thead").find_all("th")]

        for row in table.find("tbody").find_all("tr"):
            row_data = [td.text.strip() for td in row.find_all("td")]
            data.append(row_data)

        # Create a DataFrame from the data
        df = pd.DataFrame(data, columns=headers)

        return df

    except Exception as e:
        st.error(f"Error: {e}")
        return None


def save_file(df):
    # Save DataFrame to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


# Streamlit UI
st.title("Web Scraper")

# Add spinner while scraping data
if st.button("Scrape Data"):
    with st.spinner("Scraping data... Please wait."):
        df = scrape_data()

    if df is not None:
        st.write("Data scraped successfully:")
        st.dataframe(df)

        # Convert to Excel file and enable download
        excel_data = save_file(df)
        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name="scraped_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
