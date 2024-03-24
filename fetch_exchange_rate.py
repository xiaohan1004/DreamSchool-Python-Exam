""" 
[Usage] python ./fetch_exchange_rate.py 20211231 USD

[Warning]
    部分货币（包括但不限于下面几种）两个网页的货币中文名称不一致，如果需要查询可以手动保存映射关系（未实现）
            HKD-港币 JPY-日元 CAD-加元 THP-泰铢 KRW-韩元 ...
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sys

def write_to_file(data, filename="result.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(data + "\n")

# Get command line arguments
if len(sys.argv) != 3:
    print("Usage: python your_script.py [date] [currency_code]")
    sys.exit(1)

date, currency_code = sys.argv[1], sys.argv[2]

# Set up Selenium WebDriver
driver = webdriver.Chrome()

try:
    # Step 1: Query the currency name on 11meigui.com
    driver.get("https://www.11meigui.com/tools/currency")
    currency_name_selector = f"//td[normalize-space(.)='{currency_code}']/parent::tr"
    try:
        # Locate the row that contains the currency_code
        currency_row = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, currency_name_selector))
        )
        currency_row_data = currency_row.get_attribute('innerText')
        write_to_file(currency_row_data)

        # Extract the currency name from the row
        currency_name = currency_row.find_elements(By.TAG_NAME, "td")[1].get_attribute('innerText')

    except TimeoutException:
        print(f"Failed to find currency row for {currency_code}.")
        sys.exit(2)

    # Step 2: Query the exchange rate on the Bank of China
    driver.get("https://www.boc.cn/sourcedb/whpj/")
    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    try:
        # Enter the start and end dates
        driver.find_element(By.NAME, "erectDate").send_keys(formatted_date)
        driver.find_element(By.NAME, "nothing").send_keys(formatted_date)

        # Select the currency
        currency_dropdown = driver.find_element(By.ID, "pjname")
        currency_dropdown.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//select[@id='pjname']/option[contains(text(), '{currency_name}')]"))
        ).click()

        # Submit the search
        driver.find_element(By.XPATH, "//input[@class='search_btn' and @onclick='executeSearch()']").click()
        
        # Extract data from the results table
        results_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='BOC_main publish']/table"))
        )
        # Get all rows within the table and write the header and first row to the file
        rows = results_table.find_elements(By.TAG_NAME, "tr")
        if len(rows) > 1:
            header = rows[0].text
            first_row = rows[1].text
            write_to_file(header)
            write_to_file(first_row)

            # Extract "现汇卖出价" and publication time from the first data row
            first_row_tds = rows[1].find_elements(By.TAG_NAME, "td")
            exchange_rate_sell = first_row_tds[4].text
            publish_time = first_row_tds[-1].text
            print(f"[{publish_time}] {currency_name}({currency_code}) 现汇卖出价: {exchange_rate_sell}")
        else:
            print("No data rows found")

    except Exception as e:
        print(f"[ERROR] while querying the exchange rate: {e}")
        sys.exit(3)

except Exception as e:
    print(f"[ERROR] {e}")

finally:
    driver.quit()