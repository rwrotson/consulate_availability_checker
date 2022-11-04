LOGIN_PAGE = 'https://q.midpass.ru/'
LOGOUT_LINK = 'https://q.midpass.ru/ru/Account/LogOff'

JSON_FILE_PATH = 'settings.json'
JSON_SCHEMA_PATH = 'settings_schema.json'
CAPTCHA_IMAGE_FILE = 'captcha.png'

LOGIN_INPUTS = {
    'country': '//*[@id="FormLogOn"]/div/div[2]/div[2]/div[2]/select',
    'place': '//*[@id="FormLogOn"]/div/div[2]/div[3]/div[2]/select',
    'email': '//*[@id="Email"]',
    'password': '//*[@id="Password"]'
}

CAPTCHA_INPUT = '//*[@id="Captcha"]'




