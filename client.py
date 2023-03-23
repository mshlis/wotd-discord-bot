import discord
from nltk.corpus import wordnet
from deep_translator import GoogleTranslator
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
import os

class AidanClient(discord.Client):
    words = []
    langs = []
    hist = {}
    lang_map = GoogleTranslator().get_supported_languages(as_dict=True)
    wotd_id = "timed_wotd"
    alert_size = 2
    default_time = dict(
        day_of_week = "*",
        year = "*",
        month = "*",
        day = "*",
        hour = 9,
        minute = 0,
        second = 0,
        timezone = "est"
    )
    
    def __init__(self, channel_id, author_id, intents):
        self.channel_id = channel_id
        self.author_id = author_id
        self.load_state()
        super().__init__(intents=intents)
        
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        self.scheduler = AsyncIOScheduler()
        
        async def _print_word():
            channel = self.get_channel(self.channel_id)
            if len(self.words):
                self.hist[str(datetime.now().date())] = self.words[0]
            await channel.send(self.get_word())
            if len(self.words) <= self.alert_size:
                await self.dm(
                    self.author_id, 
                    f"there is only {len(self.words)} words in the queue. dont be a dongle and please add more asap"
                )
        
        self.scheduler.add_job(
            func=_print_word, 
            trigger=CronTrigger(**self.default_time), 
            id=self.wotd_id,
            replace_existing=True
        )
        self.scheduler.start()
        
    async def dm(self, user_id, msg):
        user = await self.fetch_user(user_id)
        await user.send(msg)
    
    def set_time(self, hours, minutes):
        trigger_args = self.default_time.copy()
        trigger_args.update(dict(hour=hours, minute=minutes))
        self.scheduler.reschedule_job(job_id=self.wotd_id, trigger=CronTrigger(**trigger_args))
    
    def translate(self, word, lang):
        abbr = self.lang_map[lang]
        return GoogleTranslator(source='en', target=abbr).translate(word)
    
    def remove_word(self, word):
        try:
            self.words.remove(word)
        except:
            pass
        
    @staticmethod
    def has_definitions(word):
        syns = wordnet.synsets(word)
        return len(syns) > 0
        
    def get_word_message(self, word):
        translations = [self.translate(word, lang) for lang in self.langs]
        syns = wordnet.synsets(word)
        msg = word
        msg += "\n" + "-"*30 + "\nDefinitions" + "\n" + "-"*30
        if len(syns):
            for i,syn in enumerate(syns):
                msg += f"\ndefinition {i+1}: " + syn.definition()
                examples = syn.examples()
                if len(examples):
                    msg += f"\n\t\tin a sentence: {examples[0]}"
        else:
            msg += "\nno definitions found"
        
        if len(translations):
            msg += "\n" + "-"*30 + "\nTranslations" + "\n" + "-"*30
            for lang, trans in zip(self.langs, translations):
                msg += f"\n{lang}: {trans}"
        return msg
    
    def get_word(self):
        if len(self.words):
            word = self.words.pop(0)
            return self.get_word_message(word)
        
        else:
            return "the bot is out of words :(... blame Aidan, im only Aidan-Bot"
        
    def validate_word_list(self, word_list):
        new_word_list = list()
        bad_word_list = list()
        for w in word_list:
            if w in self.words or not self.has_definitions(w):
                bad_word_list.append(w)
            else:
                new_word_list.append(w)
        return new_word_list, bad_word_list
    
    def validate_permissions(self, user_id, cmd):
        su = [self.author_id]
        permissions = {
            "!add": su,
            "!priority-add": su,
            "!get-word": su,
            "!wotd-time": su,
            "!list-words": su
        }
        return cmd not in permissions.keys() or user_id in permissions.get(cmd, [])
        
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        cmd = message.content.split(" ")[0]
        content = message.content[len(cmd)+1:].lower()
        if not self.validate_permissions(message.author.id, cmd):
            await message.channel.send(f"you do not have permissions to use the <{cmd}> command")
        
        if cmd == "!add":
            new_words, bad_words = self.validate_word_list(content.split())
            self.words.extend(new_words)
            if len(bad_words):
                await message.channel.send(f"the words in list [{', '.join(bad_words)}] are either already in the queue or have no definition")
        
        elif cmd == "!priority-add":
            new_words, bad_words = self.validate_word_list(content.split())
            self.words = new_words + self.words
            if len(bad_words):
                await message.channel.send(f"the words in list [{', '.join(bad_words)}] are either already in the queue or have no definition")
        
        elif cmd == "!get-word":
            await message.channel.send(self.get_word())
            
        elif cmd == "!add-lang":
            content = content.strip()
            if content in self.lang_map.keys():
                if content not in self.langs:
                    self.langs.append(content)
                else:
                    await message.channel.send(f"language <{content}> is already added!")
            else:
                await message.channel.send(f"language <{content}> does not appear to be supported")
        
        elif cmd == "!define":
            words = content.split()
            for word in words:
                await message.channel.send(self.get_word_message(word))
                
        elif cmd == "!remove":
            to_remove = content.split()
            for word in to_remove:
                self.remove_word(word)
                            
        elif cmd == "!wotd-time":
            try:
                h, m = content.split(":")
                self.set_time(h, m)
            except Exception as e:
                print("error:", e)
        
        elif cmd == "!history":
            msg = "history\n" + "-"*30
            for k,v in sorted(self.hist.items()):
                msg += f"\n{k}: {v}"
            await message.channel.send(msg)
            
        elif cmd == "!list-words":
            msg = "words\n" + "-"*30
            msg += "\n" + "\n".join(self.words)
            await message.channel.send(msg)
            
        elif cmd == "!count-words":
            await message.channel.send(f"there are {len(self.words)} in the queue")     
                
        elif cmd == "!help":
            await message.channel.send("existing commands are\n"
                                       "!add :: adds words to list (can delimit multiple via a space)\n"
                                       "!priority-add :: adds words to front of list (can delimit multiple via a space)\n"
                                       "!get-word :: returns top word\n"
                                       "!add-lang :: adds a language to translate the words into\n"
                                       "!remove :: removes list of given words\n"
                                       "!define :: defines list of given words\n"
                                       "!wotd-time :: changes default time to post word of the day, use military time\n"
                                       "!history :: lists history of all WOTDs\n"
                                       "!list-words :: lists all words in queue\n"
                                       "!count-words :: returns number of words in queue\n"
                                       "!add, !priority-add, !get-word, !wotd-time, !list-words require word-master")
    
    @property
    def state_dict(self):
        return dict(words=self.words, langs=self.langs, history=self.hist)
    
    def save_state(self, path="./client-state.json"):
        with open(path, "w") as f:
            json.dump(self.state_dict, f)
            
    def load_state(self, path="./client-state.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                state = json.load(f)
            self.words = state.get("words", list)
            self.langs = state.get("langs", list)
            self.hist = state.get("history", dict)
        else:
            print(f"No state exists at {path}")