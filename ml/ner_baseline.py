import re

def extract_entities(text):
    money_pattern = re.compile(r'\$[\d,]+(?:\.\d{2})?')
    date_pattern = re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b')
    return {
        "money": money_pattern.findall(text),
        "dates": date_pattern.findall(text),
    }
