import json
import os

translations = {}

def load_translations():
    locales_dir = os.path.join(os.path.dirname(__file__), '../locales')
    for filename in os.listdir(locales_dir):
        if filename.endswith('.json'):
            lang = filename.split('.')[0]
            with open(os.path.join(locales_dir, filename), 'r', encoding='utf-8') as f:
                translations[lang] = json.load(f)

def get_text(lang, key, **kwargs):
    if lang not in translations:
        lang = 'en'
    text = translations[lang].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text

load_translations()
