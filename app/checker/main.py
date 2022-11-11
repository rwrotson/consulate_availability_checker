from selenium.common.exceptions import (
    ElementClickInterceptedException, TimeoutException
)

from checker.parser.start import initialize_driver
from checker.parser.check import check_place, login, logout
from checker.mail import send_info_emails
from checker.utils import (
    get_countries_from_json_settings, get_credentials,
    get_places_for_country, get_services_for_place,
    validate_json, print_configuration,
    run_function_until_executed, is_there_available_slots
)



def main() -> None:

    validate_json()
    driver = initialize_driver()

    email, password = get_credentials()

    summary = dict()
    countries = get_countries_from_json_settings()
    for country in countries:
        places = get_places_for_country(country)
        print('Starting a script for a given configuration:\n ')
        print_configuration()

        summary[country] = dict()
        print('Starting parsing...')
        print(country.upper() + ':')

        for place in places:
            print(f'  {place}')

            # Login with given credentials
            run_function_until_executed(
                login,
                driver, country, place, email, password,
                exc=(ElementClickInterceptedException, TimeoutException),
                executed_msg='Login successful!\n'
            )
            
            # Check if there are available slots in place
            availability = run_function_until_executed(
                check_place,
                driver, get_services_for_place(place),
                exc=(ElementClickInterceptedException, TimeoutException)
            )
            summary[country][place] = availability

            # Logout
            run_function_until_executed(
                logout, driver,
                exc=(ElementClickInterceptedException, TimeoutException)
            )
    driver.quit()

    # Send email if there are available slots
    if is_there_available_slots(summary):
        send_info_emails(summary)

if __name__ == '__main__':
    main()
