import pathlib

from decouple import config

from election_tokens.__main__ import TemplatedEmail


def test_smtp_auth():
    with TemplatedEmail(config('SERVER_ADDRESS'), config('SERVER_PORT'),
                        config('SENDER_ADDRESS'), config('PASSWORD'),
                        config('SENDER_NAME'),
                        pathlib.Path('tests', 'data', 'templates')) as sender:
        pass


def test_send_single():
    with TemplatedEmail(config('SERVER_ADDRESS'), config('SERVER_PORT'),
                        config('SENDER_ADDRESS'), config('PASSWORD'),
                        config('SENDER_NAME'),
                        pathlib.Path('templates')) as sender:
        context = {
            'name': 'James',
            'token': 'Test Token',
            'sender': config('SENDER_NAME'),
        }

        sender.send('test-template.j2', context, 'matt@milliams.com',
                    'Test election-tokens email')
