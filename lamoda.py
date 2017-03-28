# encoding=utf8
import sys
import time
import logging

from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display

from dispatch import dispatch_email_via_gmail

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
LOGGER = logging.getLogger("lamoda")

TIMEOUT = 5

JEANS_LINK = u"https://www.lamoda.by/c/513/clothes-muzhskie-d-insy/?sitelink=topmenuM&l=3&size_values=33%2C34"
JEANS_SIZES = ("33/36", "34/36")

def hover(wd, element):
    hov = ActionChains(wd).move_to_element(element)
    hov.perform()

def next_page_exists(next_page_btn):
    return unicode(next_page_btn.text).lower() == u"дальше"

def click_btn(btn):
    browser.execute_script("arguments[0].click();", btn)

def next_page_with_products_is_present(wd):
    next_page_btn = wait_element_location_and_get_list(wd, "paginator__next")[0]
    if next_page_exists(next_page_btn):
        click_btn(next_page_btn)
        return True
    return False

def wait_element_location_and_get_list(dw, class_name):
    element_present = EC.presence_of_element_located((By.CLASS_NAME, class_name))
    WebDriverWait(dw, TIMEOUT).until(element_present)
    return dw.find_elements_by_class_name(class_name)

def get_jeans_data(size, jeans_text, jeans_link):
    data = []
    data.append(u'\n'.join(jeans_text.split('\n')[1:-1])) # jeans brand and additional info
    data.append(u"Size: %s Price: %s", size, jeans_text.split('\n')[0])
    data.append(jeans_link)
    return ''.join(data)


def close_popup(wd):
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'popup__close'))
        WebDriverWait(wd, TIMEOUT).until(element_present)
        popup_close_btn = wd.find_element_by_class_name("popup__close")
        click_btn(popup_close_btn)
    except TimeoutException:
        LOGGER.debug("pop up did not appear")
    else:
        LOGGER.debug("closed popup")


def iterate_product_sizes(dw, jeans):
    hover(dw, jeans)
    sizes = wait_element_location_and_get_list(jeans, "products-list-item__size-item")
    jeans_link = jeans.find_element_by_class_name("products-list-item__link").get_attribute("href")
    jeans_text = jeans.text
    jeans_data = []
    for size in sizes:
        if size.text in JEANS_SIZES:
            jeans_data.append(get_jeans_data(size.text, jeans_text, jeans_link))
    return jeans_data


def iterate_products(browser):
    time.sleep(TIMEOUT)
    close_popup(browser)
    product_data = []
    products = wait_element_location_and_get_list(browser, "products-list-item")
    for product in products:
        product_data.extend(iterate_product_sizes(browser, product))
    return product_data

if __name__ == '__main__':
    display = None
    browser = None
    try:
        display = Display(visible=0, size=(1024, 768))
        display.start()
        browser = webdriver.Chrome()
        browser.get(JEANS_LINK)
        list_of_products = []
        list_of_products.extend(iterate_products(browser))
        LOGGER.debug("1st page done")
        while next_page_with_products_is_present(browser):
            LOGGER.debug("next page")
            list_of_products.extend(iterate_products(browser))
        LOGGER.info("Finished Search")
        LOGGER.info("Sending Email")
        dispatch_email_via_gmail('\n'.join(list_of_products))
        LOGGER.info("Email Sent")
    finally:
        if display is not None:
            display.stop()
        if browser is not None:
            browser.close()

