import re

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
        return []

    start = int(match.group(1))
    end = int(match.group(3))

    return list(range(start, end + 1))


def extract_stars_and(text):
    """
    استخراج الگری زیر از متن کاربر
    3 و 4 و 5 ستاره
    """
    select_match = re.search(r'((?:\d+\s*و\s*)+\d+)\s*ستاره', text)
    print('select_match',select_match)
    if select_match:
        numbers = re.findall(r'\d+', select_match.group(1))
        return list(map(int, numbers))

    return []

def extract_single_star_patterns(text: str):
    # پیدا کردن همه موارد «عدد + ستاره»
    matches = re.findall(r'(\d+)\s*ستاره', text)

    if not matches:
        return []

    # فقط مواردی که با «و» به هم وصل شده‌اند یا تکی هستند
    return list(map(int, matches))


class StarExtractor:
    def __init__(self):
        pass

    @staticmethod
    def extract(message: str, old_selected:list|None):
        print('star Extractor',message,old_selected)
        extract=is_remove_star_filter(message)
        if extract:
            return None
        extract=extract_stars_to(message)
        print('extract_stars_to',extract)
        if extract:
            return extract

        extract=extract_stars_and(message)
        print('extract_stars_and',extract)
        if extract:
            return extract

        extract=extract_single_star_patterns(message)
        print('extract_single_star_patterns',extract)
        if extract:
            return extract

        print('old_selected',old_selected)
        return old_selected
    