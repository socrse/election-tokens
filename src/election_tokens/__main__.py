import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import logging
import os
import pathlib
import random
import smtplib
import ssl
import time
import typing

import click
from decouple import config
import jinja2
import pandas as pd
from tqdm import tqdm

logger = logging.getLogger(__name__)


class TemplatedEmail:
    def __init__(self, server_address: str, port: int, sender_address: str, password: str,
                 sender_name: str, template_dir: pathlib.Path):
        self.server_address = server_address
        self.port = port
        self.sender_address = sender_address
        self.sender_name = sender_name
        self.password = password

        self.template_loader = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    def __enter__(self):
        ssl_context = ssl.create_default_context()
        self._connection = smtplib.SMTP_SSL(self.server_address, self.port, context=ssl_context)
        self._connection.login(self.sender_address, self.password)

        return self

    def send(self, template_name: str, context: typing.Mapping, address: str, subject: str):
        template = self.template_loader.get_template(template_name)
        content = template.render(context)

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = f'{self.sender_name} <{self.sender_address}>'
        message['To'] = address

        message.attach(MIMEText(content, 'html'))
        body = message.as_string()

        self._connection.sendmail(self.sender_address, address, body)

    def __exit__(self, *exc):
        self._connection.close()


@click.group()
def cli():
    logging.basicConfig(level=config('LOG_LEVEL', default='INFO'))


@cli.command()
@click.option('--people', 'people_file', type=click.Path(exists=True))
@click.option('--subscriptions', 'subs_file', type=click.Path(exists=True))
@click.option('-o', 'output_file', type=click.Path(exists=False))
def filter_whitefuse(people_file: pathlib.Path, subs_file: pathlib.Path,
                     output_file: pathlib.Path):
    """Filter WhiteFuse exports to build list of valid memberships."""
    # Get valid memberships from the 'people' export
    people = pd.read_csv(people_file)
    valid_statuses = {'Valid', 'Overdue'}
    members = people[people['Subscription 1: Status'].isin(valid_statuses)
                     | people['Subscription 2: Status'].isin(valid_statuses)].copy()

    # Get email addresses marked as primary
    # Yes this is inefficient, but it's quick enough
    people_emails = set()
    for _, row in members.iterrows():
        for i in range(1, 4):
            if row[f'Email {i}: Text'] and (row[f'Email {i}: Primary'] == 'Yes'):
                people_emails.add(row[f'Email {i}: Text'])
                break

        else:
            people_emails.add(row['Email 1: Text'])

    # Get valid memberships from the 'subscriptions' export
    subs = pd.read_csv(subs_file)
    valid_sub_statuses = {'valid', 'overdue'}
    valid_subs = subs[subs['Status'].isin(valid_sub_statuses)][['Name', 'Email']].copy()

    # Check that the two approaches match
    assert set(valid_subs['Email']) == people_emails

    logger.info('Subscriptions matched membership data')
    logger.info('Found %d valid subscriptions', len(valid_subs))
    valid_subs.to_csv(output_file, index=False)  # TODO don't overwrite


@cli.command()
@click.option('-i', 'email_file', type=click.Path(exists=True))
@click.option('-o', 'token_file', type=click.Path(exists=False))
@click.option('--salt', 'salt_hex')
def generate(email_file: pathlib.Path,
             token_file: pathlib.Path,
             salt_hex: typing.Optional[str] = None):
    """Generate and send voting tokens."""
    logger.info('Generating tokens')

    if salt_hex is not None:
        salt = bytes.fromhex(salt_hex)

    else:
        salt = os.urandom(16)

    logger.info('Salt: %s', salt.hex())

    sender = TemplatedEmail(config('SERVER_ADDRESS'), config('SERVER_PORT'),
                            config('SENDER_ADDRESS'), config('PASSWORD'),
                            config('SENDER_NAME'),
                            pathlib.Path('templates'))
    with sender, open(email_file, 'r') as f_in, open(token_file, 'a') as f_out:
        # Shuffle list so output tokens list can't be linked
        rows = list(csv.DictReader(f_in))
        random.shuffle(rows)
        try:
            with open('checkpoint.txt') as checkpoint:
                sent_addresses = {a.strip() for a in checkpoint.readlines()}
        except FileNotFoundError:
            sent_addresses = set()

        for row in tqdm(rows):
            address = row['Email']
            if address in sent_addresses:
                continue
            token = hashlib.pbkdf2_hmac('sha256',
                                        bytes(address, encoding='utf-8'),
                                        salt,
                                        100000,
                                        dklen=8)
            token = token.hex()

            context = {'name': row['Name'], 'token': token, 'sender': config('SENDER_NAME')}
            sender.send(config('EMAIL_TEMPLATE'), context, address, config('EMAIL_SUBJECT'))

            print(token, file=f_out)

            # Save list of sent addresses so we can resume in case of failure
            sent_addresses.add(address)
            with open('checkpoint.txt', 'w') as checkpoint:
                print('\n'.join(sent_addresses), file=checkpoint)

            time.sleep(2)


if __name__ == '__main__':
    cli()
