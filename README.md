# Election Tokens

This tool is used to generate secure tokens for voter verification in elections.

## Prerequisites

The tool requires `python` and uses the [Poetry](https://python-poetry.org/docs/#installation) package manager.

## Install

```bash
git clone https://github.com/socrse/election-tokens.git
cd election-tokens
poetry install
```

## Usage

First, export the membership list from WildApricot and then run the following command to filter the results:

```bash
poetry run election-tokens filter-wildapricot --people [members.csv] -o subs.csv
```

Then copy and fill in the example `settings.ini` file.
The missing values are the email address and name of the sender, and an email password.
To generate an email password, see the Google documentation on [Using the Gmail SMTP server](https://support.google.com/a/answer/176600#zippy=%2Cuse-the-gmail-smtp-server).

```bash
cp example-settings.ini settings.ini
nano settings.ini
```

Finally, generate and send tokens for each address in the membership list:

```bash
poetry run election-tokens generate -i subs.csv -o tokens.txt
```

## Notes

The process will probably fail at some point, but a `checkpoint.txt` file will be created to track progress. Run the generate command again, and it will continue
from where it left off.  

If you send out a test email and want to test again, but nothing happens, delete `checkpoint.txt` and try again.

## License

MIT © Society of Research Software Engineering
