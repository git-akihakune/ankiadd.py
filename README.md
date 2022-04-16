# ankiadd.py
Automatically look up for English words meaning and add to Anki

## Purpose
In the process of learning English, I find myself repetitively adding cards to [Anki](https://apps.ankiweb.net/) in a predefined format, with audio, images, word type, example, and definition several times. For that reason, I decided to automate it.

## Installation
You only need the ***ankiadd.py*** file, nothing more.

The script itself does not rely on any third party module, and therefore, should be cross-platform.

However, [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on is required to be installed first.

## Usage
All the options can be found by `--help` option.
```bash
$ ./ankiadd.py --help
usage: ankiadd.py [-h] [-d DECK] [-w WORD [WORD ...]] [-t TYPE] [-n] [-v] [-V]

optional arguments:
  -h, --help            show this help message and exit
  -d DECK, --deck DECK  Anki deck name
  -w WORD [WORD ...], --word WORD [WORD ...]
                        List of words to add
  -t TYPE, --type TYPE  Type of adding cards
  -n, --nogui           Run in headless mode
  -v, --verbose         Set verbosity
  -V, --version         show program's version number and exit
```

There're not much options, so it should be self-explanatory enough. For example, if you want to add the word `test` to `testdeck`:
```bash
./ankiadd.py -d testdeck -w test -t Basic
```

## Development
This is also one of on-a-whim scripts that I thought would be useful, so any contribution will be appreciated.