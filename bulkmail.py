import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from email.policy import EmailPolicy
from email.utils import formatdate, make_msgid

from dotenv import load_dotenv
import csv
from email import policy
from email.parser import BytesParser
import chardet

load_dotenv()

def email_parser():
    with open('Demarrer 2024 avec 11% de rendement garanti.eml', 'rb') as fp:
        msg = BytesParser(policy=policy.default).parse(fp)
        text = msg.get_body(preferencelist=('plain')).get_content()
        print(text)
        # Notice the iter_attachments() method
        for attachment in msg.iter_attachments():
            fnam = attachment.get_filename()
            print(fnam)
            # Remove this attachment
            attachment.clear()

    with open('updated.eml', 'wb') as wp:
        wp.write(msg.as_bytes())

def send_email(subject, html_filepath, receiver_filepath, text_msg='', sender=None, app_password=None):
    if not sender:
        sender = os.getenv('GMAIL_USER')
        app_password = os.getenv('GOOGLE_APP_PASSWORD')
    else:
        sender = sender
        app_password = app_password

    receiver = []
    with open(receiver_filepath, 'r', ) as file:
        reader = csv.reader(file)
        headers = next(reader)
        for item in reader:
            receiver.extend(item)

    with open(html_filepath, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(html_filepath, 'r', encoding=encoding) as file:
        msg_html = file.read()

    # Server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    # Attempts to log in to the user's Gmail account
    try:
        server.login(user=sender, password=app_password)
    except smtplib.SMTPAuthenticationError as error:
        print("\nError: Make sure the Gmail address that you inputted is the same as the Gmail account you have created an app password for.\nAlso, double-check your Gmail and app password.")
        print(f"{error}")
        input("Enter to exit...")
        quit()

    print("\nEmail-bomber has started...\n")


    for email_receiver in receiver:
        # Loops through emails to send emails to
        try:
            msg = MIMEMultipart('alternative', policy=EmailPolicy())
            msg['message-id'] = make_msgid(domain='mail.gmail.com')
            msg['to'] = email_receiver
            msg['from'] = os.getenv('GMAIL_USER')
            msg['subject'] = subject
            msg['date'] = formatdate()
            msg['reply-to'] = os.getenv('GMAIL_USER')
            msg.add_header('List-Unsubscribe', '<mailto:listname-unsubscribe-927349872392343@gmail.com>')
            msg_txt = text_msg
            msg.attach(MIMEText(msg_txt, 'plain'))
            msg.attach(MIMEText(msg_html, 'html'))

            print(f"Sending email to {email_receiver}...")
            server.sendmail(from_addr=sender, to_addrs=email_receiver, msg=msg.as_string())
            print("Email sent successfully!")
        except smtplib.SMTPException as error:
            print(f"Error: {error}")
            continue
    #
    input("\nEmail-bomber was successful...\nPress enter to exit...")
    server.close()

if __name__ == '__main__':
    receiver_filepath = 'receiver_email.csv'
    subject = 'Demarrer 2024 avec 11% de rendement garanti'
    html_filepath = 'html_message.html'
    text_msg = 'Investir en Éco-Parking'
    send_email(receiver_filepath=receiver_filepath, subject=subject, html_filepath=html_filepath, text_msg=text_msg)