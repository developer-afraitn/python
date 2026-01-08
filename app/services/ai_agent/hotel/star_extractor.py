import re

from app.utils.main_helper import mask_bracketed, unmask_bracketed, wrap_words


def is_remove_star_filter(text: str) -> bool:
    pattern = r'(حذف\s+فیلتر\s+ستاره|فیلتر\s+ستاره\s+(را|رو)?\s*حذف\s+کن)'
    return bool(re.search(pattern, text))

def extract_stars_to(text):
    """
    استخراج الگری زیر از متن کاربر
    3 تا 5 ستاره
    """
    match = re.search(r'(\d+)\s*(تا|الی)\s*(\d+)\s*ستاره', text)

    if not match:
        return text,[]

    start = int(match.group(1))
    end = int(match.group(3))

    processed_message = wrap_words(text, [match.group(0)], "star")

    return processed_message,list(range(start, end + 1))


def extract_stars_and(text):
    """
    استخراج الگری زیر از متن کاربر
    3 و 4 و 5 ستاره
    """
    select_match = re.search(r'((?:\d+\s*و\s*)+\d+)\s*ستاره', text)
    print('select_match',select_match)
    if select_match:
        processed_message = wrap_words(text, [select_match.group(0)], "star")
        numbers = re.findall(r'\d+', select_match.group(1))
        return processed_message,list(map(int, numbers))

    return text,[]

def extract_single_star_patterns(text: str):
    # پیدا کردن همه موارد «عدد + ستاره»
    matches = re.findall(r'(\d+)\s*ستاره', text)

    text = wrap_words(text, [f"{item} ستاره" for item in matches], "star")

    if not matches:
        return text,[]

    # فقط مواردی که با «و» به هم وصل شده‌اند یا تکی هستند
    return text,list(map(int, matches))


class StarExtractor:
    def __init__(self):
        pass

    @staticmethod
    def extract(message: str, old_selected:list|None):
        print('\n\n-----------------------------------------START STAR EXTRACTOR---------------------------------------------------\n\n')
        print('message',message)
        process_message,masked=mask_bracketed(message)

        extract=is_remove_star_filter(process_message)
        print('is_remove_star_filter',extract)
        if extract:
            processed_message=unmask_bracketed(process_message,masked)
            return processed_message,None

        process_message,extract=extract_stars_to(process_message)
        print('extract_stars_to',extract)
        if extract:
            processed_message=unmask_bracketed(process_message,masked)
            return processed_message,extract

        process_message,extract=extract_stars_and(process_message)
        print('extract_stars_and',extract)
        if extract:
            processed_message=unmask_bracketed(process_message,masked)
            return processed_message,extract

        process_message,extract=extract_single_star_patterns(process_message)
        print('extract_single_star_patterns',extract)
        processed_message=unmask_bracketed(process_message,masked)
        if extract:
            return processed_message,extract

        print('\n\n-----------------------------------------END STAR EXTRACTOR---------------------------------------------------\n\n')
        return processed_message,old_selected
    