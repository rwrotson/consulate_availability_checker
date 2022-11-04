
from time import sleep
from twocaptcha import TwoCaptcha

from checker.utils import get_api_key

def solve_captcha(image_path: str) -> str:
    solver = TwoCaptcha(get_api_key())
    params = {
        'caseSensitive': 1,
        'numeric': 4,
        'minLength': 6,
        'maxLength': 6,
        'lang': 'en',
        }
    try:
        result = solver.normal(image_path, params=params)['code']
    except Exception as e:
        print(e)
        sleep(10)
        result = solve_captcha(image_path)
    print(f'  Captcha solved: {result}...', end=' ')
    return result
    