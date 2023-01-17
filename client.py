import discord
from nltk.corpus import wordnet
from deep_translator import GoogleTranslator
import json
import os

class AidanClient(discord.Client):
    words = []
    langs = []
    lang_map = GoogleTranslator().get_supported_languages(as_dict=True)
    
    def __init__(self, *args, **kwargs):
        self.load_state()    
        super().__init__(*args, **kwargs)
    
    def translate(self, word, lang):
        abbr = self.lang_map[lang]
        return GoogleTranslator(source='en', target=abbr).translate(word)
    
    def get_word(self):
        if len(self.words):
            word = self.words.pop(0)
            translations = [self.translate(word, lang) for lang in self.langs]
            syns = wordnet.synsets(word)
            word += "\n" + "-"*30 + "\nDefinitions" + "\n" + "-"*30
            if len(syns):
                for i,syn in enumerate(syns):
                    word += f"\ndefinition {i+1}: " + syn.definition()
                    examples = syn.examples()
                    if len(examples):
                        word += f"\n\t\tin a sentence: {examples[0]}"
            else:
                word += "\nno definitions found"
            
            if len(translations):
                word += "\n" + "-"*30 + "\nTranslations" + "\n" + "-"*30
                for lang, trans in zip(self.langs, translations):
                    word += f"\n{lang}: {trans}"
            return word
        else:
            return "the bot is out of words :(... blame Aidan, im only Aidan-Bot"

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        cmd = message.content.split(" ")[0]
        content = message.content[len(cmd)+1:]
        if cmd == "!add":
            self.words.extend(content.split())
        
        elif cmd == "!priority-add":
            self.words = content.split() + self.words
        
        elif cmd == "!get-word":
            await message.channel.send(self.get_word())
            
        elif cmd == "!add-lang":
            content = content.lower().strip()
            if content in self.lang_map.keys():
                self.langs.append(content)
            else:
                await message.channel.send(f"language <{content}> does not appear to be supported")
                
        elif cmd == "!help":
            await message.channel.send("existing commands are\n"
                                       "!add := adds words to list (can delimit multiple via a space)\n"
                                       "!priority-add := adds words to front of list (can delimit multiple via a space)\n"
                                       "!get-word := returns top word\n"
                                       "!add-lang := adds a language to translate the words into")
    
    @property
    def state_dict(self):
        return dict(words=self.words, langs=self.langs)
        
    
    def save_state(self, path="./client-state.json"):
        with open(path, "w") as f:
            json.dump(self.state_dict, f)
            
    def load_state(self, path="./client-state.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                state = json.load(f)
            self.words = state.get("words", list)
            self.langs = state.get("langs", list)
        else:
            print(f"No state exists at {path}")     