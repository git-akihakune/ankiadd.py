#!/usr/bin/env python3
from typing import Dict


def parser():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--deck", help="Anki deck name")
    parser.add_argument("-w", "--word", nargs="+", help="List of words to add")
    parser.add_argument(
        "-t", "--type", default="Basic (and reversed card)", help="Type of adding cards"
    )
    parser.add_argument(
        "-n", "--nogui", action="store_true", help="Run in headless mode"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Set verbosity")
    parser.add_argument("-V", "--version", action="version", version="1.0.0")
    return parser


class Card:
    def __init__(
        self, deck: str, word: str, card_type: str, nogui: bool = False
    ) -> None:
        self.deck = deck
        self.word = word
        self.card_type = card_type
        self.action = "addNote" if nogui else "guiAddCards"

        self.dictionary_data = self._search_dictionary(word)

    @staticmethod
    def _search_dictionary(word: str) -> Dict[str, str]:
        import requests

        endpoint = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        json_data = requests.get(endpoint).json()[0]

        return json_data

    @staticmethod
    def _search_image(word: str) -> str:
        import requests
        from bs4 import BeautifulSoup

        url = ""
        endpoint = f"https://www.google.com/search?q={word}&client=firefox&hs=cTQ&source=lnms&tbm=isch&sa=X&ved=0ahUKEwig3LOx4PzKAhWGFywKHZyZAAgQ_AUIBygB&biw=1920&bih=982"
        page = requests.get(endpoint).text
        soup = BeautifulSoup(page, "html.parser")
        for image in soup.find_all("img"):
            link = image.get("src")
            if link and "gstatic" in link:
                url = link
                break

        return url

    def contruct(self):
        import re

        meanings = list(
            filter(
                lambda phonetic: phonetic.get("partOfSpeech")
                and phonetic.get("definitions"),
                self.dictionary_data.get("meanings"),
            )
        )

        try:
            example = [
                meaning.get("definitions")[0].get("example")
                for meaning in meanings
                if meaning.get("definitions")[0].get("example")
            ][0]
            # Get indentation on the word in example
            italic_word = re.compile(self.word, re.IGNORECASE)
            example = italic_word.sub(f"<b><i>{self.word}</b></i>", example)
        except IndexError:
            example = f"<b><i>{self.word}</i></b>"

        word_type = " ".join(
            [
                f"({meaning.get('partOfSpeech')})"
                for meaning in meanings
                if meaning.get("partOfSpeech")
            ]
        )

        definitions = min(
            [
                meaning.get("definitions")[0].get("definition")
                for meaning in meanings
                if meaning.get("definitions")[0].get("definition")
            ],
            key=len,
        )

        try:
            phonetics = list(
                filter(
                    lambda phonetic: phonetic.get("text") and phonetic.get("audio"),
                    self.dictionary_data.get("phonetics"),
                )
            )[0]
            phonetic = phonetics.get("text")
            audio_url = phonetics.get("audio")
        except IndexError:
            if input("[!] No phonetic data found. Manually add? [y/n] ") == "y":
                phonetic = input("[?] How's it pronounced? ")
                audio_url = input("[?] Enter pronunciating audio URL: ")
            else:
                phonetic = audio_url = ""

        image_url = self._search_image(self.word)

        self.content = {
            "action": self.action,
            "version": 6,
            "params": {
                "note": {
                    "deckName": self.deck,
                    "modelName": self.card_type,
                    "fields": {
                        "Front": f"{example} {phonetic}\n\n\n",
                        "Back": f"{word_type} {definitions}\n\n\n",
                    },
                    "options": {"closeAfterAdding": True},
                    "tags": ["AutoAdded"],
                }
            },
        }

        if image_url != "":
            self.content["params"]["note"]["picture"] = [
                {
                    "url": image_url,
                    "filename": f"{self.word}.png",
                    "fields": ["Back"],
                }
            ]

        if audio_url != "":
            self.content["params"]["note"]["audio"] = [
                {
                    "url": audio_url,
                    "filename": f"{self.word}.mp3",
                    "fields": ["Front"],
                }
            ]

    def add(self):
        import json
        import urllib.request

        endpoint = "http://localhost:8765"

        requestJson = json.dumps(self.content).encode("utf-8")
        response = json.load(
            urllib.request.urlopen(urllib.request.Request(endpoint, requestJson))
        )

        if len(response) != 2:
            raise Exception("Response has an unexpected number of fields")
        if "error" not in response:
            raise Exception("response is missing required error field")
        if "result" not in response:
            raise Exception("response is missing required result field")
        if response["error"] is not None:
            raise Exception(response["error"])
        return response["result"]


def main():
    args = parser().parse_args()

    import logging

    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.INFO if args.verbose else logging.ERROR,
    )

    if not args.word or not args.deck:
        if input("[*] No parameter set. Interactively set? [y/n] ") == "y":
            args.deck = input("[?] Which deck do you want to add to? ")
            args.word = input("[?] Words you want to add: ").split()
        else:
            print("[#] Understandable, have a nice day!")
            exit()

    for word in args.word:
        logging.info(f"Searching for word: {word}")
        card = Card(
            deck=args.deck,
            word=word,
            card_type=args.type,
            nogui=True if args.nogui else False,
        )

        logging.info("Creating card...")
        card.contruct()

        logging.info("Adding card...")
        card.add()

        logging.info(f"'{word}' added succesfully")


if __name__ == "__main__":
    main()
