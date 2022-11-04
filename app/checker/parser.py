from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


from checker.captcha import solve_captcha
from checker.consts import (
    LOGIN_PAGE, LOGOUT_LINK, LOGIN_INPUTS,
    CAPTCHA_IMAGE_FILE, CAPTCHA_INPUT
)


def initialize_driver() -> WebDriver:
    exec_path = ChromeDriverManager().install()
    service = ChromeService(executable_path=exec_path)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}

    driver = webdriver.Chrome(service=service, options=chrome_options)

    print('Selenium Chrome driver initialized!')
    return driver


def load_login_page(driver: WebDriver) -> None:
    driver.get(LOGIN_PAGE)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'imgCaptcha'))
    )

def fill_inputs(
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


def try_to_login(
    driver: WebDriver, country: str, place: str,
    email: str, password: str
) -> None:
    
    load_login_page(driver)
    fill_inputs(driver, country, place, email, password)
    fill_captcha_input(driver)
    
    form_element = driver.find_element(By.ID, 'FormLogOn')
    buttons = form_element.find_elements(By.TAG_NAME, 'button')
    submit_button = list(filter(
        lambda button: button.text == 'Войти',
        buttons
    ))[0]
    submit_button.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'service-item'))
    )


def is_login_failed(driver: WebDriver) -> bool:
    return bool(driver.find_elements(By.ID, 'captchaError'))


def login(
    driver: WebDriver, country: str, place: str,
    email: str, password: str
) -> None:
    try_to_login(driver, country, place, email, password)
    while is_login_failed(driver):
        print('Captcha solved incorrectly!')
        login(driver, country, place, email, password)


def find_service_and_go_to_it(driver: WebDriver, service: str) -> bool:
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

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'availableSlotsCount'))
    )
    return True


def check_service(driver: WebDriver, service: str) -> bool:
    available_quantity = int(driver.find_element(By.ID, 'availableSlotsCount').text)
    if available_quantity > 0:
        print(f'    -- {service}: 🟢')
        return True
    print(f'    -- {service}: 🔴')
    return False


def go_back_to_services(driver: WebDriver) -> None:
    back_td = driver.find_element(By.CLASS_NAME, 'backStep')
    back_a = back_td.find_element(By.TAG_NAME, 'a')
    back_a.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'service-item'))
    )


def check_place(driver: WebDriver, services: List[str]) -> List[Optional[bool]]:
    availability = dict()
    for service in services:
        is_service_found = find_service_and_go_to_it(driver, service)
        if is_service_found:
            is_available = check_service(driver, service)
            availability[service] = is_available
            go_back_to_services(driver)
        else:
            availability[service] = None
    print()
    return availability
        

def logout(driver: WebDriver) -> None:
    driver.get(LOGOUT_LINK)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'imgCaptcha'))
    )
