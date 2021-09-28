import pathlib

from decouple import config

from election_tokens.__main__ import TemplatedEmail


def test_smtp_auth():
    with TemplatedEmail(config('SERVER_ADDRESS'), config('SERVER_PORT'),
                        config('SENDER_ADDRESS'), config('PASSWORD'),
                        pathlib.Path('tests', 'data', 'templates')) as sender:
        pass


def test_send_single():
    with TemplatedEmail(config('SERVER_ADDRESS'), config('SERVER_PORT'),
                        config('SENDER_ADDRESS'), config('PASSWORD'),
                        pathlib.Path('templates')) as sender:
        context = {
            'name': 'James',
            'token': 'Test Token',
            'sender': 'James',
        }

        sender.send('example-template.j2', context, 'j.graham@software.ac.uk',
                    'Test election-tokens email')
