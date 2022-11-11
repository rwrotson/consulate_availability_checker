from typing import Tuple, List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class element_has_css_value(object):
    def __init__(self, locator: Tuple[str], css_property: str, css_value: str) -> None:
        self.locator = locator
        self.css_property = css_property
        self.css_value = css_value


    def find_property(self, entries: List[str]) -> bool:
        is_property_found = False
        for entry in entries:
            css_property, css_value = self.extract_property_and_value(entry)
            if css_value is None:
                continue
            if css_property == self.css_property and css_value  == self.css_value:
                is_property_found = True
                break
        return is_property_found


    def extract_property_and_value(self, css_statement: str) -> Tuple[str]:
        items = css_statement.split(':')
        if len(items) == 2:
            key = items[0].strip()
            value = items[1].strip()
            return key, value
        return None, None


    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        styles = element.get_attribute('style')
        entries = styles.split(';')
        is_property_found = self.find_property(entries)

        if is_property_found:
            return element
        return False


def wait_until_window_mask_invisible(driver: WebDriver) -> None:
    wait = WebDriverWait(driver, 15)
    #wait.until(element_has_css_value((By.CLASS_NAME, 'window-mask'), 'display', 'block'))
    wait.until(element_has_css_value((By.CLASS_NAME, 'window-mask'), 'display', 'none'))


def wait_until_locator_is_visible(driver: WebDriver, locator: Tuple[str]) -> None:
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located(locator))


def wait_until_locator_is_clickable(driver: WebDriver, locator: Tuple[str]) -> None:
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable(locator))
