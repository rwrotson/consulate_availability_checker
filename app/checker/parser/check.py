from typing import List, Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from checker.parser.register import enroll_for_service
from checker.parser.waits import (
    wait_until_window_mask_invisible, wait_until_locator_is_visible,
)
from checker.captcha import solve_captcha
from checker.utils import is_auto_application
from checker.consts import (
    LOGIN_PAGE, LOGOUT_LINK, LOGIN_INPUTS,
    CAPTCHA_IMAGE_FILE, CAPTCHA_INPUT
)


def login(
    driver: WebDriver, country: str, place: str,
    email: str, password: str
) -> None:
    try_to_login(driver, country, place, email, password)
    while is_login_failed(driver):
        print('Captcha solved incorrectly!')
        login(driver, country, place, email, password)


def is_login_failed(driver: WebDriver) -> bool:
    return bool(driver.find_elements(By.ID, 'captchaError'))


def try_to_login(
    driver: WebDriver, country: str, place: str,
    email: str, password: str
) -> None:
    
    load_first_page(driver)
    fill_login_inputs(driver, country, place, email, password)
    fill_captcha_input(driver)
    
    form_element = driver.find_element(By.ID, 'FormLogOn')
    buttons = form_element.find_elements(By.TAG_NAME, 'button')
    submit_button = list(filter(
        lambda button: button.text == 'Войти',
        buttons
    ))[0]
    submit_button.click()


def load_first_page(driver: WebDriver, is_logined: bool = False) -> None:
    driver.get(LOGIN_PAGE)
    wait_until_window_mask_invisible(driver)
    if is_logined == False:
        wait_until_locator_is_visible(driver, (By.ID, 'imgCaptcha'))
    else:
        wait_until_locator_is_visible(driver, (By.CLASS_NAME, 'servicebutton'))


def fill_login_inputs(
    driver: WebDriver, country: str, place: str,
    email: str, password: str
) -> None:
    data = {
        'country': country, 'place': place,
        'email': email, 'password': password
    }
    for key, value in LOGIN_INPUTS.items():
        input_element = driver.find_element(By.XPATH, value)
        input_element.send_keys(data[key])


def fill_captcha_input(driver: WebDriver) -> None:
    captcha_img_element = driver.find_element(By.ID, 'imgCaptcha')
    with open(CAPTCHA_IMAGE_FILE, 'wb') as file:
        file.write(captcha_img_element.screenshot_as_png)

    solved_captcha = solve_captcha(CAPTCHA_IMAGE_FILE)
    
    captcha_input = driver.find_element(By.XPATH, CAPTCHA_INPUT)
    captcha_input.send_keys(solved_captcha)


def check_place(driver: WebDriver, services: List[str]) -> List[Optional[bool]]:
    load_first_page(driver, is_logined=True)
    availability = dict()
    for service in services:
        is_service_found = find_service_and_go_to_it(driver, service)
        if is_service_found:
            is_available = check_service(driver, service)
            availability[service] = is_available
            go_back_to_services_selection(driver)
        else:
            availability[service] = None
    print()
    return availability


def find_service_and_go_to_it(driver: WebDriver, service: str) -> bool:
    wait_until_locator_is_visible(driver, (By.CLASS_NAME, 'service-item'))
    all_services_buttons = driver.find_elements(By.CLASS_NAME, 'service-item')
    service_link_list = list(filter(
        lambda btn: btn.find_element(By.TAG_NAME, 'span').text == service,
        all_services_buttons
    ))
    if not service_link_list:
        print(f'The service "{service}" not found')
        return False

    service_link = service_link_list[0]
    service_link.click()

    return True


def check_service(driver: WebDriver, service: str) -> bool:
    wait_until_window_mask_invisible(driver)
    wait_until_locator_is_visible(driver, (By.ID, 'availableSlotsCount'))
    # check if the page loaded correctly
    overall_quantity = int(driver.find_element(By.ID, 'totalSlotsCount').text)
    while overall_quantity == 0:
        driver.refresh()
        wait_until_window_mask_invisible(driver)
        wait_until_locator_is_visible(driver, (By.ID, 'availableSlotsCount'))
        overall_quantity = int(driver.find_element(By.ID, 'totalSlotsCount').text)
        print('The page loaded incorrectly. Refreshing...')

    # get is there available slots
    available_quantity = int(driver.find_element(By.ID, 'availableSlotsCount').text)
    if available_quantity > 0:
        print(f'    -- {service}: 🟢')
        if is_auto_application():
            enroll_for_service(driver, service)
            return True
        return True
    print(f'    -- {service}: 🔴')
    return False


def go_back_to_services_selection(driver: WebDriver) -> None:
    back_td = driver.find_element(By.CLASS_NAME, 'backStep')
    back_a = back_td.find_element(By.TAG_NAME, 'a')
    back_a.click()
    wait_until_window_mask_invisible(driver)
    wait_until_locator_is_visible(driver, (By.CLASS_NAME, 'service-item'))
        

def logout(driver: WebDriver) -> None:
    driver.get(LOGOUT_LINK)
    wait_until_window_mask_invisible(driver)
    wait_until_locator_is_visible(driver, (By.ID, 'imgCaptcha'))
