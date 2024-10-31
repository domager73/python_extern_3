import re


class UtilFunctions:
    @classmethod
    def getLanguage(cls, city):
        if re.search(r'[а-яА-Я]', city):
            return 'ru'
        else:
            return 'en'