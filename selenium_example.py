from selenium import webdriver
from selenium.webdriver.common.keys import Keys

if __name__ == "__main__":
    url = "https://habr.com/ru/"
    browser = webdriver.Firefox()
    browser.get(url)
    s_button = browser.find_element_by_xpath('//button[@id="search-form-btn"]')
    s_button.click()
    s_input = browser.find_element_by_xpath('//input[@id="search-form-field"]')
    s_input.send_keys("fjhgfgfjbf fjhgfjhfjfb fkfhkfhkfhkfj")
    print(1)
