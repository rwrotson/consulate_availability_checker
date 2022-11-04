import os, sys, json
from time import sleep
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Optional, Callable, Union
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from checker.consts import JSON_FILE_PATH, JSON_SCHEMA_PATH


def validate_json() -> None:
    print('\nValidating your settings...')
    try:
        with open(JSON_SCHEMA_PATH, 'r', encoding='utf-8') as file:
            schema = json.load(file)
        validate(instance=load_json_settings(), schema=schema)
    except (ValidationError, FileNotFoundError):
        print('Your settings.json file in incorrect')
        sys.exit()

    print('settings.json are correct\n')


def get_countries_from_json_settings() -> Optional[List[str]]:
    data = load_json_settings()
    return [country.get('country') for country in data['countries']]
        

def get_places_for_country(country: str) -> Optional[List[str]]:
    data = load_json_settings()
    country_obj = list(filter(lambda x: (x['country'] == country), data['countries']))
    if country_obj is None: return None
    return [place.get('place') for place in country_obj[0]['places']]


def get_services_for_place(place: str) -> Optional[List[str]]:
    data = load_json_settings()
    for country in data['countries']:
        for plc in country['places']:
            if plc['place'] == place:
                return plc['services']


def load_json_settings() -> Dict:
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def load_env() -> Dict[str, str]:
    load_dotenv()
    return {
        'EMAIL': os.getenv('EMAIL_FOR_QMIDPASS'),
        'PASSWORD': os.getenv('PASSWORD_FOR_QMIDPASS'),
        'API_KEY': os.getenv('API_KEY_FOR_2CAPTCHA'),
        'SENDER_EMAIL': os.getenv('SENDER_EMAIL'),
        'SENDER_PASSWORD': os.getenv('SENDER_PASSWORD'),
        'PORT': os.getenv('PORT'),
        'RECEIVERS_EMAILS': os.getenv('RECEIVERS_EMAILS')
    }


def get_credentials() -> Tuple[str]:
    return load_env()['EMAIL'], load_env()['PASSWORD']


def get_api_key() -> str:
    return load_env()['API_KEY']


def get_sender_credentials() -> Tuple[str]:
    return load_env()['SENDER_EMAIL'], load_env()['SENDER_PASSWORD']


def get_email_port() -> int:
    return int(load_env()['PORT'])


def get_receivers_emails() -> List[str]:
    return load_env()['RECEIVERS_EMAILS'].split(',')


def print_configuration() -> None:
    data = load_json_settings()
    for country in data['countries']:
        print(country['country'].upper() + ':')
        for place in country['places']:
            place_title = place['place']
            print(f'  {place_title}')
            for service in place['services']:
                print(f'    -- {service}')
    print()


def convert_summary(summary: Dict) -> str:
    str_of_available = ''
    for country, places in summary.items():
        for place, services in places.items():
            for service, available in services.items():
                if available:
                    str_of_available += f'{country.upper()} -- {place} -- {service}\n'
    return str_of_available


def is_there_available_slots(summary: Dict) -> bool:
    for places in summary.values():
        for services in places.values():
            for available in services.values():
                if available: return True
    return False


def run_function_until_executed(
    func: Callable, *args, executed_msg: str = '', exc: Union[object, Tuple]
) -> Optional[object]:
    is_executed = False
    while not is_executed:
        try:
            value_to_return = func(*args)
            is_executed = True
            print(executed_msg, end='')
        except exc:
            print(' ' * 8 + 'Process interrupted! Trying again...')
            sleep(5)
    return value_to_return
