import os
import re
import csv
from misaki import en

NEPALI_NUMS = {
    0: 'शून्य', 1: 'एक', 2: 'दुई', 3: 'तीन', 4: 'चार', 5: 'पाँच', 6: 'छ', 7: 'सात', 8: 'आठ', 9: 'नौ', 10: 'दश',
    11: 'एघार', 12: 'बाह्र', 13: 'तेह्र', 14: 'चौध', 15: 'पन्ध्र', 16: 'सोह्र', 17: 'सत्र', 18: 'अठार', 19: 'उन्नाइस', 20: 'बीस',
    21: 'एकाइस', 22: 'बाइस', 23: 'तेइस', 24: 'चौबिस', 25: 'पच्चिस', 26: 'छब्बिस', 27: 'सत्ताइस', 28: 'अठ्ठाइस', 29: 'उनान्तीस', 30: 'तीस',
    31: 'एकतीस', 32: 'बत्तीस', 33: 'तेत्तीस', 34: 'चौतीस', 35: 'पैँतीस', 36: 'छत्तीस', 37: 'सैँतीस', 38: 'अठ्तीस', 39: 'उनान्चालीस', 40: 'चालीस',
    41: 'एकचालीस', 42: 'बियालीस', 43: 'त्रिचालीस', 44: 'चउरालीस', 45: 'पैँतालीस', 46: 'छयालीस', 47: 'सत्तालीस', 48: 'अठचालीस', 49: 'उनान्पचास', 50: 'पचास',
    51: 'एकाउन', 52: 'बाउन', 53: 'त्रिपन्न', 54: 'चौपन्न', 55: 'पञ्चउन्न', 56: 'छपन्न', 57: 'सन्ताउन', 58: 'अठ्ठाउन', 59: 'उनान्सट्ठी', 60: 'साट्ठी',
    61: 'एकसट्ठी', 62: 'बियसट्ठी', 63: 'त्रियसट्ठी', 64: 'चौसट्ठी', 65: 'पैँसट्ठी', 66: 'छयसट्ठी', 67: 'सट्सट्ठी', 68: 'अठसट्ठी', 69: 'उनान्सत्तर', 70: 'सत्तर',
    71: 'एकहत्तर', 72: 'बहत्तर', 73: 'त्रिहत्तर', 74: 'चौहत्तर', 75: 'पचहत्तर', 76: 'छहत्तर', 77: 'सतहत्तर', 78: 'अठहत्तर', 79: 'उनान्असी', 80: 'असी',
    81: 'एकासी', 82: 'बियासी', 83: 'त्रियासी', 84: 'चौरासी', 85: 'पचासी', 86: 'छियासी', 87: 'सतासी', 88: 'अठासी', 89: 'उनान्नब्बे', 90: 'नब्बे',
    91: 'एकानब्बे', 92: 'बयानब्बे', 93: 'त्रियानब्बे', 94: 'चौरानब्बे', 95: 'पञ्चानब्बे', 96: 'छियानब्बे', 97: 'सन्तानब्बे', 98: 'अन्ठानब्बे', 99: 'उनान्सय'
}

NEPALI_DIGIT_MAP = {
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}

ENGLISH_NUMS = {
    0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
    11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nineteen',
    20: 'twenty', 30: 'thirty', 40: 'forty', 50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninety'
}

NEPALI_MONTHS = {
    '01': 'वैशाख', '1': 'वैशाख', '०१': 'वैशाख', '१': 'वैशाख',
    '02': 'जेठ', '2': 'जेठ', '०२': 'जेठ', '२': 'जेठ',
    '03': 'असार', '3': 'असार', '०३': 'असार', '३': 'असार',
    '04': 'साउन', '4': 'साउन', '०४': 'साउन', '४': 'साउन',
    '05': 'भदौ', '5': 'भदौ', '०५': 'भदौ', '५': 'भदौ',
    '06': 'असोज', '6': 'असोज', '०६': 'असोज', '६': 'असोज',
    '07': 'कात्तिक', '7': 'कात्तिक', '०७': 'कात्तिक', '७': 'कात्तिक',
    '08': 'मङ्सिर', '8': 'मङ्सिर', '०८': 'मङ्सिर', '८': 'मङ्सिर',
    '09': 'पुस', '9': 'पुस', '०९': 'पुस', '९': 'पुस',
    '10': 'माघ', '१०': 'माघ',
    '11': 'फागुन', '११': 'फागुन',
    '12': 'चैत', '१२': 'चैत'
}

ENGLISH_MONTHS = {
    '01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
    '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'
}

NEPALI_ORDINALS = {
    1: 'पहिलो', 2: 'दोस्रो', 3: 'तेस्रो', 4: 'चौथो', 5: 'पाँचौँ', 6: 'छैटौँ', 7: 'सातौँ', 8: 'आठौँ', 9: 'नवौँ', 10: 'दसौँ'
}

ENGLISH_ORDINALS = {
    1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'
}

ABBREV_PROTECT = {
    'Dr.': 'Dr__DOT__', 'Mr.': 'Mr__DOT__', 'Mrs.': 'Mrs__DOT__', 'Ms.': 'Ms__DOT__',
    'Prof.': 'Prof__DOT__', 'e.g.': 'e__DOT__g__DOT__', 'i.e.': 'i__DOT__e__DOT__',
    'etc.': 'etc__DOT__', 'vs.': 'vs__DOT__', 'Ltd.': 'Ltd__DOT__', 'Govt.': 'Govt__DOT__',
    'Co.': 'Co__DOT__', 'approx.': 'approx__DOT__', 'St.': 'St__DOT__', 'Ave.': 'Ave__DOT__',
    'Jr.': 'Jr__DOT__', 'Sr.': 'Sr__DOT__', 'a.m.': 'a__DOT__m__DOT__', 'p.m.': 'p__DOT__m__DOT__',
    'डा.': 'डा__DOT__', 'रु.': 'रु__DOT__', 'आ.व.': 'आ__DOT__व__DOT__', 'वि.सं.': 'वि__DOT__सं__DOT__',
    'ई.सं.': 'ई__DOT__सं__DOT__', 'प्रा.लि.': 'प्रा__DOT__लि__DOT__', 'लि.': 'लि__DOT__',
    'स.नं.': 'स__DOT__न__DOT__', 'जि.वि.स.': 'जि__DOT__वि__DOT__स__DOT__',
    'मा.वि.': 'मा__DOT__वि__DOT__', 'प्र.अ.': 'प्र__DOT__अ__DOT__'
}

def protect_abbreviations(text):
    for k in sorted(ABBREV_PROTECT.keys(), key=len, reverse=True):
        text = text.replace(k, ABBREV_PROTECT[k])
    return text

def restore_abbreviations(text):
    for k in sorted(ABBREV_PROTECT.keys(), key=len, reverse=True):
        text = text.replace(ABBREV_PROTECT[k], k)
    return text

def clean_delimiters(num_str):
    return num_str.replace(',', '').strip()

def devanagari_to_arabic(text):
    return "".join(NEPALI_DIGIT_MAP.get(c, c) for c in text)

def nepali_int_to_words(val):
    if val < 0:
        return "माइनस " + nepali_int_to_words(abs(val))
    if val < 100:
        return NEPALI_NUMS[val]
    if val < 1000:
        hundreds = val // 100
        rem = val % 100
        res = NEPALI_NUMS[hundreds] + " सय"
        if rem > 0:
            res += " " + nepali_int_to_words(rem)
        return res
    if val < 100000:
        thousands = val // 1000
        rem = val % 1000
        res = nepali_int_to_words(thousands) + " हजार"
        if rem > 0:
            res += " " + nepali_int_to_words(rem)
        return res
    if val < 10000000:
        lakhs = val // 100000
        rem = val % 100000
        res = nepali_int_to_words(lakhs) + " लाख"
        if rem > 0:
            res += " " + nepali_int_to_words(rem)
        return res
    crores = val // 10000000
    rem = val % 10000000
    res = nepali_int_to_words(crores) + " करोड"
    if rem > 0:
        res += " " + nepali_int_to_words(rem)
    return res

def english_int_to_words(val):
    if val < 0:
        return "negative " + english_int_to_words(abs(val))
    if val < 20:
        return ENGLISH_NUMS[val]
    if val < 100:
        tens = (val // 10) * 10
        rem = val % 10
        res = ENGLISH_NUMS[tens]
        if rem > 0:
            res += "-" + ENGLISH_NUMS[rem]
        return res
    if val < 1000:
        hundreds = val // 100
        rem = val % 100
        res = ENGLISH_NUMS[hundreds] + " hundred"
        if rem > 0:
            res += " and " + english_int_to_words(rem)
        return res
    if val < 1000000:
        thousands = val // 1000
        rem = val % 1000
        res = english_int_to_words(thousands) + " thousand"
        if rem > 0:
            res += " " + english_int_to_words(rem)
        return res
    if val < 1000000000:
        millions = val // 1000000
        rem = val % 1000000
        res = english_int_to_words(millions) + " million"
        if rem > 0:
            res += " " + english_int_to_words(rem)
        return res
    billions = val // 1000000000
    rem = val % 1000000000
    res = english_int_to_words(billions) + " billion"
    if rem > 0:
        res += " " + english_int_to_words(rem)
    return res

def convert_number_to_words(num_str, is_nepali=True):
    num_str = devanagari_to_arabic(num_str).replace(',', '')
    if '.' in num_str:
        parts = num_str.split('.')
        whole = int(parts[0]) if parts[0] else 0
        dec = parts[1]
        if is_nepali:
            whole_word = nepali_int_to_words(whole)
            if dec:
                dec_word = " ".join(NEPALI_NUMS[int(d)] for d in dec)
                return f"{whole_word} दशमलव {dec_word}"
            return whole_word
        else:
            whole_word = english_int_to_words(whole)
            if dec:
                dec_word = " ".join(ENGLISH_NUMS[int(d)] for d in dec)
                return f"{whole_word} point {dec_word}"
            return whole_word
    else:
        val = int(num_str)
        if is_nepali:
            return nepali_int_to_words(val)
        else:
            return english_int_to_words(val)

def normalize_dates(text, is_nep):
    if is_nep:
        def repl_nepali_date(m):
            year = convert_number_to_words(m.group(1), is_nepali=True)
            month_code = m.group(2)
            month = NEPALI_MONTHS.get(month_code, month_code)
            day = convert_number_to_words(m.group(3), is_nepali=True)
            return f"साल {year}, {month} महिनाको {day} गते"

        text = re.sub(r'\b([०-९0-9]{4})[/\-]([०-९0-9]{2})[/\-]([०-९0-9]{2})\b', repl_nepali_date, text)

        def repl_nepali_verbal_date(m):
            day = convert_number_to_words(m.group(1), is_nepali=True)
            month = m.group(2)
            year = convert_number_to_words(m.group(3), is_nepali=True)
            return f"{month} {day}, {year}"
        
        text = re.sub(r'\b([०-९0-9]{1,2})\s+(वैशाख|जेठ|असार|साउन|भदौ|असोज|कात्तिक|मङ्सिर|पुस|माघ|फागुन|चैत)\s+([०-९0-9]{4})\b', repl_nepali_verbal_date, text)
    else:
        def repl_english_date(m):
            day_val = int(devanagari_to_arabic(m.group(1)))
            month_code = devanagari_to_arabic(m.group(2))
            year_val = int(devanagari_to_arabic(m.group(3)))
            
            ones = day_val % 10
            tens = day_val // 10
            suffix = "th"
            if tens != 1:
                if ones == 1: suffix = "st"
                elif ones == 2: suffix = "nd"
                elif ones == 3: suffix = "rd"
            day_word = english_int_to_words(day_val) + suffix
            if day_val in [1, 2, 3, 21, 22, 23, 31]:
                day_word = ENGLISH_ORDINALS.get(day_val, day_word)
                
            month_word = ENGLISH_MONTHS.get(month_code, month_code)
            year_word = english_int_to_words(year_val)
            if 1100 <= year_val < 2000:
                year_word = f"{english_int_to_words(year_val // 100)} {english_int_to_words(year_val % 100)}"
            elif 2000 <= year_val < 2100:
                if year_val % 100 == 0:
                    year_word = "two thousand"
                else:
                    year_word = f"twenty {english_int_to_words(year_val % 100)}"

            return f"the {day_word} of {month_word}, {year_word}"

        text = re.sub(r'\b([0-9]{1,2})[/\-]([0-9]{2})[/\-]([0-9]{4})\b', repl_english_date, text)
    return text

def normalize_years(text, is_nep):
    if is_nep:
        text = re.sub(r'वि\.सं\.\s*([०-९0-9]{4})', lambda m: f"विक्रम संवत् {convert_number_to_words(m.group(1), is_nepali=True)}", text)
        text = re.sub(r'ई\.सं\.\s*([०-९0-9]{4})', lambda m: f"ईस्वी संवत् {convert_number_to_words(m.group(1), is_nepali=True)}", text)
        text = re.sub(r'([०-९0-9]{4})\s*साल', lambda m: f"{convert_number_to_words(m.group(1), is_nepali=True)} साल", text)
        text = re.sub(r'सन्\s*([०-९0-9]{4})', lambda m: f"सन् {convert_number_to_words(m.group(1), is_nepali=True)}", text)
    else:
        text = re.sub(r'\b([0-9]{4})\s*AD\b', lambda m: f"{english_int_to_words(int(m.group(1)))} AD", text)

    def repl_fiscal_year(m):
        y1 = m.group(1)
        y2 = m.group(2)
        full_y1 = devanagari_to_arabic(y1)
        prefix = full_y1[:2]
        full_y2 = prefix + devanagari_to_arabic(y2)
        
        w1 = convert_number_to_words(y1, is_nep)
        w2 = convert_number_to_words(full_y2, is_nep)
        
        slash = "स्ल्यास" if is_nep else "slash"
        return f"{w1} {slash} {w2}"

    text = re.sub(r'\b([०-९0-9]{4})/([०-९0-9]{2})\b', repl_fiscal_year, text)

    def repl_year_range(m):
        y1 = m.group(1)
        y2 = m.group(2)
        w1 = convert_number_to_words(y1, is_nep)
        w2 = convert_number_to_words(y2, is_nep)
        if is_nep:
            return f"{w1} देखि {w2} सम्म"
        else:
            return f"{w1} to {w2}"
            
    text = re.sub(r'\b([०-९0-9]{4})-(२०[०-९]{2}|२१[०-९]{2}|20[0-9]{2}|21[0-9]{2})\b', repl_year_range, text)
    return text

def normalize_currency(text, is_nep):
    def repl_npr(m):
        amt_str = m.group(1)
        if '.' in amt_str:
            parts = amt_str.split('.')
            whole = convert_number_to_words(parts[0], is_nepali=is_nep)
            dec = convert_number_to_words(parts[1], is_nepali=is_nep)
            return f"{whole} रुपैयाँ {dec} पैसा"
        amt_words = convert_number_to_words(amt_str, is_nepali=is_nep)
        return f"{amt_words} रुपैयाँ"

    text = re.sub(r'(?:रु\.\s*|रु\s+|NPR\s+)([०-९0-9,]+(?:\.[०-९0-9]+)?)', repl_npr, text)

    def repl_usd(m):
        amt_str = m.group(1)
        if '.' in amt_str:
            parts = amt_str.split('.')
            whole = convert_number_to_words(parts[0], is_nepali=is_nep)
            dec = convert_number_to_words(parts[1], is_nepali=is_nep)
            dollars = "dollars" if not is_nep else "डलर"
            cents = "cents" if not is_nep else "सेन्ट"
            and_word = "and" if not is_nep else "र"
            return f"{whole} {dollars} {and_word} {dec} {cents}"
        
        amt_words = convert_number_to_words(amt_str, is_nepali=is_nep)
        currency = "dollars" if not is_nep else "डलर"
        if "USD" in m.group(0) or "$" in m.group(0):
            currency = "US dollars" if not is_nep else "अमेरिकी डलर"
        return f"{amt_words} {currency}"

    text = re.sub(r'(?:\$\s*|USD\s+)([०-९0-9,]+(?:\.[०-९0-9]+)?)', repl_usd, text)

    def repl_inr(m):
        amt_str = m.group(1)
        amt_words = convert_number_to_words(amt_str, is_nepali=is_nep)
        currency = "Indian rupees" if not is_nep else "भारतीय रुपैयाँ"
        return f"{amt_words} {currency}"

    text = re.sub(r'(?:₹\s*|INR\s+)([०-९0-9,]+(?:\.[०-९0-9]+)?)', repl_inr, text)
    return text

def normalize_numbers(text, is_nep):
    text = re.sub(r'([०-९0-9,]+(?:\.[०-९0-9]+)?)\s*%', lambda m: f"{convert_number_to_words(m.group(1), is_nepali=is_nep)} प्रतिशत", text)

    def repl_ordinal(m):
        num = int(devanagari_to_arabic(m.group(1)))
        if is_nep:
            return NEPALI_ORDINALS.get(num, f"{nepali_int_to_words(num)} औँ")
        else:
            return ENGLISH_ORDINALS.get(num, f"{english_int_to_words(num)}th")

    text = re.sub(r'\b([०-९0-9]+)(?:st|nd|rd|th)\b', repl_ordinal, text)

    def repl_fraction(m):
        num = int(devanagari_to_arabic(m.group(1)))
        den = int(devanagari_to_arabic(m.group(2)))
        if is_nep:
            if num == 1 and den == 2: return "आधा"
            return f"एक भाग दुई"
        else:
            if num == 1 and den == 2: return "one half"
            return f"{english_int_to_words(num)} over {english_int_to_words(den)}"

    text = re.sub(r'\b([०-९0-9]+)/([०-९0-9]+)\b', repl_fraction, text)

    def repl_phone(m):
        digits = devanagari_to_arabic(m.group(0))
        words = []
        for d in digits:
            val = int(d)
            words.append(NEPALI_NUMS[val] if is_nep else ENGLISH_NUMS[val])
        return " ".join(words)
        
    text = re.sub(r'\b[०-९0-9]{7,15}\b', repl_phone, text)

    def repl_range(m):
        n1 = m.group(1)
        n2 = m.group(2)
        w1 = convert_number_to_words(n1, is_nep)
        w2 = convert_number_to_words(n2, is_nep)
        if is_nep:
            return f"{w1} देखि {w2} सम्म"
        else:
            return f"{w1} to {w2}"

    text = re.sub(r'\b([०-९0-9]+)-([०-९0-9]+)\b', repl_range, text)

    def repl_standard_num(m):
        num_str = m.group(0)
        return convert_number_to_words(num_str, is_nep)

    text = re.sub(r'\b[०-९0-9,]+(?:\.[०-९0-9]+)?\b', repl_standard_num, text)
    return text

def normalize_abbreviations(text, is_nep):
    if is_nep:
        ne_abbrevs = {
            'डा.': 'डाक्टर',
            'श्री': 'श्री',
            'आ.व.': 'आर्थिक वर्ष',
            'वि.सं.': 'विक्रम संवत्',
            'ई.सं.': 'ईस्वी संवत्',
            'प्रा.लि.': 'प्राइभेट लिमिटेड',
            'लि.': 'लिमिटेड',
            'स.नं.': 'सिलसिला नम्बर',
            'जि.वि.स.': 'जिल्ला विकास समिति',
            'मा.वि.': 'माध्यमिक विद्यालय',
            'प्र.अ.': 'प्रधान अध्यापक'
        }
        for ab in sorted(ne_abbrevs.keys(), key=len, reverse=True):
            exp = ne_abbrevs[ab]
            text = text.replace(ab, exp)
    else:
        en_abbrevs = {
            r'\bDr\.(?!\w)': 'Doctor',
            r'\bMr\.(?!\w)': 'Mister',
            r'\bMrs\.(?!\w)': 'Missus',
            r'\bMs\.(?!\w)': 'Miz',
            r'\bProf\.(?!\w)': 'Professor',
            r'\be\.g\.(?!\w)': 'for example',
            r'\bi\.e\.(?!\w)': 'that is',
            r'\betc\.(?!\w)': 'et cetera',
            r'\bvs\.(?!\w)': 'versus',
            r'\bLtd\.(?!\w)': 'Limited',
            r'\bGovt\.(?!\w)': 'Government',
            r'\bCo\.(?!\w)': 'Company',
            r'\bapprox\.(?!\w)': 'approximately',
            r'\bSt\.(?!\w)': 'Street',
            r'\bAve\.(?!\w)': 'Avenue',
            r'\bJr\.(?!\w)': 'Junior',
            r'\bSr\.(?!\w)': 'Senior',
            r'\ba\.m\.(?!\w)': 'ay em',
            r'\bp\.m\.(?!\w)': 'pee em',
        }
        for ab, exp in en_abbrevs.items():
            text = re.sub(ab, exp, text, flags=re.IGNORECASE)
        
    return text

def normalize_contractions(text, is_nep):
    if not is_nep:
        contractions = {
            r"\bI'm\b": "I am",
            r"\bI'd\b": "I would",
            r"\bI'll\b": "I will",
            r"\bI've\b": "I have",
            r"\bdon't\b": "do not",
            r"\bwon't\b": "will not",
            r"\bcan't\b": "cannot",
            r"\bshouldn't\b": "should not",
            r"\bit's\b": "it is",
            r"\bthat's\b": "that is",
            r"\bthere's\b": "there is",
            r"\blet's\b": "let us",
            r"\bwho's\b": "who is",
            r"\by'all\b": "you all",
        }
        for con, exp in contractions.items():
            text = re.sub(con, exp, text, flags=re.IGNORECASE)
    return text

def normalize_punctuation_misc(text, is_nep):
    if is_nep:
        text = text.replace('&', ' र ')
        text = text.replace('+', ' प्लस ')
        text = re.sub(r'-(?=[०-९0-9])', 'माइनस ', text)
        text = text.replace('=', ' बराबर ')
    else:
        text = text.replace('&', ' and ')
        text = text.replace('+', ' plus ')
        text = re.sub(r'-(?=[0-9])', 'minus ', text)
        text = text.replace('=', ' equals ')

    text = text.replace('@', ' at ')
    text = text.replace('-', ' ')
    return text

def normalize_sentence(sentence):
    is_nep = bool(re.search(r'[\u0900-\u097F]', sentence))
    sentence = normalize_dates(sentence, is_nep)
    sentence = normalize_years(sentence, is_nep)
    sentence = normalize_currency(sentence, is_nep)
    sentence = normalize_numbers(sentence, is_nep)
    sentence = normalize_abbreviations(sentence, is_nep)
    sentence = normalize_contractions(sentence, is_nep)
    sentence = normalize_punctuation_misc(sentence, is_nep)
    return sentence

def normalize_text(text):
    # 1. Protect abbreviations so their dots are not used as sentence splitters
    protected_text = protect_abbreviations(text)
    
    # 2. Split into sentences by । ? ! . \n preserving delimiters
    parts = re.split(r'([।?!.\n])', protected_text)
    
    normalized_parts = []
    for part in parts:
        if part in ['।', '?', '!', '.', '\n']:
            normalized_parts.append(part)
        else:
            # Restore abbreviation dots inside the sentence, then normalize
            restored_part = restore_abbreviations(part)
            normalized_parts.append(normalize_sentence(restored_part))
            
    res = "".join(normalized_parts)
    res = re.sub(r' +', ' ', res)
    return res.strip()


# ---------------------------------------------------------------------------
# Hybrid G2P: espeak-ng (Nepali) for Devanagari + misaki en.G2P for Latin
# ---------------------------------------------------------------------------

# Kokoro-supported IPA character set (derived from phoneme_vocab.json)
_ALLOWED_IPA = set(
    " !\"(),.:;?AIOQSTWYabcdefghijklmnopqrstuvwxyz"
    "æçðøŋœɐɑɒɔɕɖəɚɛɜɟɡɣɤɥɨɪɯɰɲɳɴɸɹɻɽɾʁʂʃʈʊʋʌʎʒʔʝʣʤʥʦʧʨ"
    "ʰʲˈˌː̃βθχᵊᵝᵻ\u2014\u201c\u201d\u2026\u2192\u2193\u2197\u2198\uab67"
)

_DEVA_RE = re.compile(r'[\u0900-\u0963\u0966-\u097F]+')
_LATIN_RE = re.compile(r'[a-zA-Z]+')


class NepaliHybridG2P:
    """
    Hybrid G2P for code-mixed Nepali/English text.

    Devanagari  ->  misaki.espeak.EspeakG2P('ne')
                    Produces proper stress markers (ˈ ˌ) and natural prosody
                    via espeak-ng's Nepali voice.

    Latin/ASCII ->  misaki.en.G2P()
                    Standard English phonemiser for English words.

    espeak-ng's English output inside Nepali context uses different phoneme
    conventions from what Kokoro was trained on, so Latin words are always
    routed through en.G2P() for cleaner, Kokoro-compatible English IPA.
    """

    def __init__(self):
        from misaki import espeak as _esp
        self.ne_g2p = _esp.EspeakG2P(language='ne')
        self.en_g2p = en.G2P()
        print("NepaliHybridG2P ready (espeak-ne + misaki-en).")

    def _clean(self, ipa: str) -> str:
        """Normalise and filter IPA to Kokoro-supported characters only."""
        ipa = ipa.replace('ɦ', 'h')   # espeak uses ɦ; Kokoro vocab has h
        ipa = ipa.replace('g', 'ɡ')   # normalise ASCII g -> IPA ɡ
        return "".join(c for c in ipa if c in _ALLOWED_IPA)

    def __call__(self, text: str):
        """
        Convert a normalised mixed Nepali/English string to Kokoro IPA.

        Tokenises text into Devanagari runs, Latin runs, and punctuation/
        whitespace. Each run is routed to the appropriate G2P backend.
        """
        tokens = re.findall(
            # Devanagari letters (U+0900-U+097F, excluding dandas U+0964/U+0965)
            r'[\u0900-\u0963\u0966-\u097F]+'
            r'|[a-zA-Z]+'                          # Latin words
            r'|[^\u0900-\u097F\sa-zA-Z]+'          # other non-whitespace (includes dandas)
            r'|[\u0964\u0965]'                      # dandas explicitly (pass through)
            r'|\s+',                                # whitespace
            text
        )

        parts = []
        prev_was_word = False

        for token in tokens:
            if _DEVA_RE.fullmatch(token):
                try:
                    raw, _ = self.ne_g2p(token)
                    ph = self._clean(raw)
                except Exception:
                    ph = ''
                if ph:
                    if prev_was_word:
                        parts.append(' ')
                    parts.append(ph)
                    prev_was_word = True

            elif _LATIN_RE.fullmatch(token):
                try:
                    raw, _ = self.en_g2p(token)
                    ph = self._clean(raw)
                except Exception:
                    ph = token
                if ph:
                    if prev_was_word:
                        parts.append(' ')
                    parts.append(ph)
                    prev_was_word = True

            else:
                # punctuation / whitespace — pass through as-is
                parts.append(token)
                prev_was_word = False

        return "".join(parts), None


if __name__ == "__main__":
    sample_input = "डा. शर्माले २०८१ साल असार १५ गते रु. १,२५,००० को सम्झौता ई.सं. २०२४ मा गरे। I'd say it's approx. $1,000."
    print("Input:", sample_input)
    print("Output:", normalize_text(sample_input))

    g2p = NepaliHybridG2P()
    test_ph, _ = g2p("यो दिनचर्या कस्तो हुन्छ भने, बिहान उठ्ने बित्तिकै mobile मा notifications चेक गर्नै पर्छ ।")
    print("Phonemes:", test_ph)
