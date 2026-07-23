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

Generating the election tokens is a two-step process. The following steps have been tested
on Windows.

### Step 1: Preparing the Membership Data

First, export the membership list from WildApricot. 

- Go to `Members -> Summary -> Export All`.
- Make sure the First Name, Last Name, Email and Membership status fields are selected.
- Click Export

This will generate and download an XLS file with all the members' details in it.

- Open the XLS file in Excel and save it as a CSV file.
  - **Make sure to export it as `CSV UTF-8 (Comma delimited)` format.**
- Copy the CSV file into the `data` folder.
- Rename it to something like `members.csv` for simplicity 

Next, run the following command to filter the results:

```bash
poetry run election-tokens filter-wildapricot --people data/members.csv -o data/subs.csv
```

This will output a CSV file into data/subs.csv containing the list of full names and email addresses 
for all valid members who are eligible to vote. This data is then used by the next step to generate
tokens and send out the emails.

### Step 2: Generate Tokens and Send Emails

Then copy and fill in the example `settings.ini` file.
The missing values are the email address and name of the sender, and an email password.
To generate an email password, see the Google documentation on
[Using the Gmail SMTP server](https://support.google.com/a/answer/176600#zippy=%2Cuse-the-gmail-smtp-server).

```bash
cp example-settings.ini settings.ini
nano settings.ini
```

#### Testing

#### Sending the Emails

Finally, when you've tested everything and are ready to hit go, use the following command to
generate and send tokens for each address in the membership list:

```bash
poetry run election-tokens generate -i data/subs.csv -o data/tokens.txt
```

#### The Tokens

All of the tokens generated during this process are saved in `data/tokens.txt`. Keep this file,
as you will need to send it to the scrutineers to verify the votes.

## Notes: Checkpoints

A `checkpoint.txt` file will be created to track progress.

- The process will probably fail at some point, but `checkpoint.txt` will track progress.
Run the `generate` command again, and it will continue from where it left off.  

- If you send out a test email and want to test again, but nothing happens, remember to
delete `checkpoint.txt` and try again.

## License

MIT © Society of Research Software Engineering
