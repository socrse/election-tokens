# Election Tokens

This tool is used to generate secure tokens for voter verification in elections.

## Install

```bash
git clone https://github.com/socrse/election-tokens.git
cd election-tokens
poetry install
```

## Usage

First generate the membership list from WhiteFuse 'people' and 'subscriptions' exports:

```bash
poetry run election-tokens filter-whitefuse --people export-people-2021-09-07.csv --subscriptions export-subscriptions-2021-09-07.csv -o subs.csv
```

Then copy and fill in the example `settings.ini` file.
The missing values are the email address and name of the sender and an email password.
To generate an email password, see the Google documentation on [Using the Gmail SMTP server](https://support.google.com/a/answer/176600#zippy=%2Cuse-the-gmail-smtp-server).

```bash
cp example-settings.ini settings.ini
nano settings.ini
```

Finally generate and send tokens for each address in the membership list:

```bash
poetry run election-tokens generate -i subs.csv -o tokens.txt
```

## License

MIT © Society of Research Software Engineering
