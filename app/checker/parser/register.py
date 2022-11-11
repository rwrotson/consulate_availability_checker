from typing import List, Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


from checker.parser.waits import (
    wait_until_locator_is_visible, wait_until_window_mask_invisible,
    wait_until_locator_is_clickable
)
from checker.utils import load_credentials_for_application


def enroll_for_service(driver: WebDriver, service: str) -> bool:
    # checking first month: there can be no working days in first month, 
    # but they might be in the second one        
    working_dates = find_all_working_dates_in_month(driver)
    if working_dates:
        available_date = find_available_date_or_none(working_dates)
        if available_date is not None:
            go_to_time_select(driver, available_date)
            is_time_slot_available = choose_time(driver)
            if is_time_slot_available == False:
                return False
            submit_form_for_application(driver)
            print(f'Successfully enrolled for a {service}!')
            return True

    # checking other months: the last month will not have working days
    go_to_the_next_month(driver)
    working_dates = find_all_working_dates_in_month(driver)
    while working_dates:
        available_date = find_available_date_or_none(working_dates)
        if available_date is not None:
            go_to_time_select(driver, available_date)
            is_time_slot_available = choose_time(driver)
            if is_time_slot_available == False:
                return False
            submit_form_for_application(driver)
            print(f'Successfully enrolled for a {service}!')
            return True
        go_to_the_next_month(driver)
        working_dates = find_all_working_dates_in_month(driver)

    # in case the available appointment was booked before us 
    return False


def find_all_working_dates_in_month(driver: WebDriver) -> List[WebElement]:
    all_dates = driver.find_elements(By.CLASS_NAME, 'DateBox')
    working_dates = list(filter(
        lambda date: date.text.split('\n')[1] != 'Нет записи', 
        all_dates
    ))
    return working_dates


def find_available_date_or_none(working_dates: List[WebElement]) -> Optional[WebElement]:
    available_dates = list(filter(
        lambda date: date.find_element(By.TAG_NAME, 'span').text.split('/')[0] != 0,
        working_dates
    ))
    if not available_dates:
        return None
    return available_dates[0]


def go_to_the_next_month(driver: WebDriver) -> None:
    # test this function
    next_month_button = driver.find_element(By.CLASS_NAME, 'link-next')
    next_month_button.click()
    wait_until_locator_is_visible(driver, (By.CLASS_NAME, 'DateBox'))


def go_to_time_select(driver: WebDriver, available_date: WebElement) -> None:
    available_date.click()
    wait_until_locator_is_visible(driver, (By.ID, 'selectable'))


def choose_time(driver: WebDriver) -> bool:
    wait_until_window_mask_invisible(driver)

    time_table = driver.find_element(By.ID, 'selectable')
    available_time = time_table.find_elements(By.CLASS_NAME, 'available')
    if not available_time:
        return False
    available_time[0].click()
    wait_until_window_mask_invisible(driver)
    wait_until_locator_is_clickable(driver, (By.ID, 'confirm'))
    next_button = driver.find_element(By.ID, 'confirm')
    next_button.click()

    return True


def submit_form_for_application(driver: WebDriver) -> None:
    wait_until_locator_is_visible(driver, (By.CLASS_NAME, 'saveButton'))

    inputs = {
        'SURNAME': driver.find_element(By.CLASS_NAME, 'surname'),
        'NAME': driver.find_element(By.CLASS_NAME, '_name'),
        'PATRONYMIC': driver.find_element(By.CLASS_NAME, 'patronymic'),
        'BIRTH_DATE': driver.find_element(By.CLASS_NAME, 'birth-date'),
        'PHONE_NUMBER': driver.find_element(By.CLASS_NAME, 'phone-number'),
        'ADDRESS': driver.find_element(
            By.ID, 'payload_fields'
        ).find_element(By.TAG_NAME, 'input'),
    }
    for key, element in inputs.items():
        element.send_keys(load_credentials_for_application()[key])

    warning_checkbox = driver.find_element(By.ID, 'warningChecbox')
    warning_checkbox.click()

    save_button = driver.find_element(By.CLASS_NAME, 'saveButton')
    save_button.click()

    print('Congratulation! Your application is registered')
