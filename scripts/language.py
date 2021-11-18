import json

class Language:
    def __init__(self):
        self.language_dic = {}

        self.channel_language = {}


    def load_all_language(self):
        activate_languages = ['ko-KR', 'en-US', 'zh-CN', 'ja-JP']

        for language in activate_languages:
            path = "language_data/{}.json".format(language)

            with open(path, 'rt', encoding = 'UTF-8') as f:
                self.language_dic[language] = json.load(f)

    def save_server_language(self):
       with open("language_data/server_language.json", 'w', encoding='UTF-8') as f:
           json.dump(self.channel_language, f)

    def load_server_language(self):
       with open("language_data/server_language.json", 'r', encoding='UTF-8') as f:
           self.channel_language = dict(json.load(f))

    def tl(self, key, server_id): # translate
        if not server_id in self.channel_language:
            self.channel_language[server_id] = 'en-US'
            self.save_server_language()
        
        return self.language_dic[self.channel_language[server_id]][key]