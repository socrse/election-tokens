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
import typing

import click
from decouple import config
import jinja2

logger = logging.getLogger(__name__)


class TemplatedEmail:
    def __init__(self, server_address: str, port: int, sender_address: str,
                 password: str, template_dir: pathlib.Path):
        self.server_address = server_address
        self.port = port
        self.sender_address = sender_address
        self.password = password

        self.template_loader = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir))

    def __enter__(self):
        ssl_context = ssl.create_default_context()
        self._connection = smtplib.SMTP_SSL(self.server_address,
                                            self.port,
                                            context=ssl_context)
        self._connection.login(self.sender_address, self.password)

        return self

    def send(self, template_name: str, context: typing.Mapping, address: str,
             subject: str):
        template = self.template_loader.get_template(template_name)
        content = template.render(context)

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = self.sender_address
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
@click.option('-i', 'email_file', type=click.Path(exists=True))
@click.option('-o', 'token_file', type=click.Path(exists=False))
@click.option('--salt', 'salt_hex')
def generate(email_file: pathlib.Path, token_file: pathlib.Path, salt_hex: typing.Optional[str] = None):
    logger.info('Generating tokens')

    if salt_hex is not None:
        salt = bytes.fromhex(salt_hex)
    
    else:
        salt = os.urandom(16)

    logger.info('Salt: %s', salt.hex())

    sender = TemplatedEmail(config('SERVER_ADDRESS'), config('SERVER_PORT'),
                            config('SENDER_ADDRESS'), config('PASSWORD'),
                            pathlib.Path('templates'))
    with sender, open(email_file, 'r') as f_in, open(token_file, 'w') as f_out:
        # Shuffle list so output tokens list can't be linked
        rows = list(csv.DictReader(f_in))
        random.shuffle(rows)

        for row in rows:
            address = row['email']
            token = hashlib.pbkdf2_hmac('sha256',
                                        bytes(address, encoding='utf-8'),
                                        salt,
                                        100000,
                                        dklen=8)
            token = token.hex()

            context = {
                'name': row['name'],
                'token': token,
                'sender': config('SENDER_NAME')
            }
            sender.send(config('EMAIL_TEMPLATE'), context, address,
                        config('EMAIL_SUBJECT'))

            print(token, file=f_out)


if __name__ == '__main__':
    cli()
