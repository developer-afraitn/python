import re
from typing import List


class PersianLettersNumber:
    def __init__(self, number: int):
        self.words = [
            ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"],
            ["ده", "یازده", "دوازده", "سیزده", "چهارده", "پانزده", "شانزده", "هفده", "هجده", "نوزده", "بیست"],
            ["", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"],
            ["", "یکصد", "دویست", "سیصد", "چهارصد", "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد"],
            [
                "",
                " هزار",
                " میلیون",
                " میلیارد",
                " بیلیون",
                " بیلیارد",
                " تریلیون",
                " تریلیارد",
                " کوآدریلیون",
                " کادریلیارد",
                " کوینتیلیون",
                " کوانتینیارد",
                " سکستیلیون",
                " سکستیلیارد",
                " سپتیلیون",
                " سپتیلیارد",
                " اکتیلیون",
                " اکتیلیارد",
                " نانیلیون",
                " نانیلیارد",
                " دسیلیون",
            ],
        ]
        self.splitter = " و "
        self.number = number

    def persian_money(self) -> str:
        zero = "صفر"
        if self.number == 0:
            return zero

        num_str = str(self.number)
        if len(num_str) > 66:
            return "خارج از محدوده"

        # Split to sections of 3 digits
        splitted_number = self.prepare_number(num_str)

        result: List[str] = []
        split_length = len(splitted_number)

        for i in range(split_length):
            section_title = self.words[4][split_length - (i + 1)]
            converted = self.three_numbers_to_letter(splitted_number[i])
            if converted != "":
                result.append(converted + section_title)

        return self.splitter.join(result)

    def prepare_number(self, num) -> List[str]:
        # Keep behavior similar to PHP version: accept int/float/str
        if isinstance(num, (int, float)):
            num = str(num)

        length_mod = len(num) % 3
        if length_mod == 1:
            num = "00" + num
        elif length_mod == 2:
            num = "0" + num

        return [num[i:i + 3] for i in range(0, len(num), 3)]

    def three_numbers_to_letter(self, num) -> str:
        digits_only = re.sub(r"\D", "", str(num))
        if int(digits_only or "0") == 0:
            return ""

        parsed_int = int(digits_only)

        if parsed_int < 10:
            return self.words[0][parsed_int]

        if parsed_int <= 20:
            return self.words[1][parsed_int - 10]

        one = parsed_int % 10

        if parsed_int < 100:
            ten = (parsed_int - one) // 10
            if one > 0:
                return self.words[2][ten] + self.splitter + self.words[0][one]
            return self.words[2][ten]

        hundreds = (parsed_int - (parsed_int % 100)) // 100
        ten = (parsed_int - ((hundreds * 100) + one)) // 10

        out = [self.words[3][hundreds]]
        second_part = (ten * 10) + one

        if second_part > 0:
            if second_part < 10:
                out.append(self.words[0][second_part])
            elif second_part <= 20:
                out.append(self.words[1][second_part - 10])
            else:
                out.append(self.words[2][ten])
                if one > 0:
                    out.append(self.words[0][one])

        return self.splitter.join(out)


# نمونه استفاده:
# print(PersianLettersNumber(123456789).persian_money())
