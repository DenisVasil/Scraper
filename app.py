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
        # Initialize WebDriver
        options = Options()
        options.add_argument('--headless')  # Run in headless mode if needed
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)

        url = "https://cvvp.nva.gov.lv/#/pub/apmacibas/grupas"
        driver.get(url)
        time.sleep(5)  # Allow page to load initially

        # Infinite scroll setup
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        scroll_pause_time = 2  # Adjust if needed

        while True:
            # Scroll to the bottom of the page
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with the last scroll height
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()  # Close the driver

        # Extract the table data
        table = soup.find("table", {"class": "table table-condensed"})

        # Create lists to store the extracted data
        data = []
        headers = []

        # Extract headers
        for th in table.find("thead").find_all("th"):
            headers.append(th.text.strip())

        # Extract rows
        for row in table.find("tbody").find_all("tr"):
            row_data = [td.text.strip() for td in row.find_all("td")]
            data.append(row_data)

        # Create DataFrame
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

if st.button("Scrape Data"):
    with st.spinner("Scraping data, please wait..."):
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
