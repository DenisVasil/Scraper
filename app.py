from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import time
from io import BytesIO


def scrape_data():
    try:
        # Set Chrome options
        options = Options()
        options.binary_location = "/usr/bin/google-chrome"
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Initialize WebDriver
        driver = webdriver.Chrome(service=Service(
            "/usr/local/bin/chromedriver"), options=options)

        # Web scraping process
        url = "https://cvvp.nva.gov.lv/#/pub/apmacibas/grupas"
        driver.get(url)
        time.sleep(5)

        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        while True:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        table = soup.find("table", {"class": "table table-condensed"})
        headers = [th.text.strip()
                   for th in table.find("thead").find_all("th")]
        data = [[td.text.strip() for td in row.find_all("td")]
                for row in table.find("tbody").find_all("tr")]

        df = pd.DataFrame(data, columns=headers)
        return df

    except Exception as e:
        st.error(f"Error: {e}")
        return None


def save_file(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


st.title("Web Scraper")

if st.button("Scrape Data"):
    with st.spinner("Scraping data..."):
        df = scrape_data()

    if df is not None:
        st.write("Data scraped successfully:")
        st.dataframe(df)
        excel_data = save_file(df)
        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name="scraped_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
