import base64
import csv
import hashlib
import logging
import os

import click
from decouple import config

logger = logging.getLogger(__name__)

@click.group()
def cli():
    logging.basicConfig(level=config('LOG_LEVEL', default='INFO'))

@cli.command()
@click.option('-f', '--file', 'email_file', type=click.Path(exists=True))
def generate(email_file: click.Path(exists=True)):
    logger.info('Generating tokens')

    salt = os.urandom(16)
    logger.info('Salt: %s', base64.b16encode(salt))

    with open(email_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            logger.info('Email: %s', row['email'])
            token = hashlib.pbkdf2_hmac('sha256', bytes(row['email'], encoding='utf-8'), salt, 100000, dklen=8)
            logger.info('Token: %s', base64.b16encode(token))
