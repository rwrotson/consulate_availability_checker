import ssl
from smtplib import SMTPException, SMTPDataError, SMTP_SSL
from email.message import EmailMessage
from typing import Dict, List

from checker.utils import (
    get_sender_credentials,
    get_receivers_emails,
    get_email_port,
    convert_summary,
    run_function_until_executed,
    is_auto_application
)


def compose_message(summary: Dict, sender: str, receiver: str) -> EmailMessage:
    if is_auto_application():
        subject = 'APPLIED TO SERVICE'
        info_text = 'You have been applied for:'
    else:
        subject = 'VACANT SLOTS'
        info_text = 'There are vacant slots for:'

    message = EmailMessage()
    message['From'] = sender
    message['To'] = receiver    
    message['Subject'] = subject
    
    message.set_content(f"""
Hello, my dear waiting friend!

Good news! {info_text}:

{convert_summary(summary)}

Check it here:
https://q.midpass.ru/

Good luck!
""")

    return message


def send_info_emails(summary: Dict) -> None:
    sender_email, password = get_sender_credentials()
    receivers_emails = get_receivers_emails()

    context = ssl.create_default_context()
    with SMTP_SSL('smtp.yandex.ru', port=get_email_port(), context=context) as server:
        run_function_until_executed(
            server.login,
            sender_email, password,
            exc=SMTPException,
            executed_msg='SMTP server connected!\n'
        )
        try_to_send_emails(
            server, summary, sender_email, receivers_emails
        ) 


def try_to_send_emails(
    server: SMTP_SSL, summary: Dict, 
    sender_email: str, receivers_emails: List[str]
) -> None:

    is_sent = {}
    for receiver_email in receivers_emails:
        is_sent[receiver_email] = False
    NUMBER_OF_ROLLS = 2
    for _ in range(NUMBER_OF_ROLLS):
        for receiver_email, is_already_sent in is_sent.items():
            if not is_already_sent:
                message = compose_message(summary, sender_email, receiver_email)
                try:
                    server.sendmail(sender_email, receiver_email, message.as_string())
                    is_sent[receiver_email] = True
                    print(f'Email for {receiver_email} was send!')
                except (SMTPException, SMTPDataError):
                    pass

    not_sent = []
    for receiver_email, is_already_sent in is_sent.items():
        if not is_already_sent: not_sent.append(receiver_email)
    if len(not_sent) != 0:
        print('Emails was not sent to:\n  ', end='')
        print('\n  '.join(not_sent))
