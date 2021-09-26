# Election Tokens

This tool is used to generate secure tokens for voter verification in elections.

## Install

```bash
git clone https://github.com/socrse/election-tokens.git
cd election-tokens
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Usage

```bash
election-tokens generate -i tests/data/example-voters.csv -o tokens.txt
```

## License

MIT © Society of Research Software Engineering
