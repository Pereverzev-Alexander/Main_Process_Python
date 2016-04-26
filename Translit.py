upper_letters = {
    u'А': u'A',
    u'Б': u'B',
    u'В': u'V',
    u'Г': u'G',
    u'Д': u'D',
    u'Е': u'E',
    u'Ё': u'E',
    u'Ж': u'Zh',
    u'З': u'Z',
    u'И': u'I',
    u'Й': u'Y',
    u'К': u'K',
    u'Л': u'L',
    u'М': u'M',
    u'Н': u'N',
    u'О': u'O',
    u'П': u'P',
    u'Р': u'R',
    u'С': u'S',
    u'Т': u'T',
    u'У': u'U',
    u'Ф': u'F',
    u'Х': u'H',
    u'Ц': u'Ts',
    u'Ч': u'Ch',
    u'Ш': u'Sh',
    u'Щ': u'Sch',
    u'Ъ': u'',
    u'Ы': u'Y',
    u'Ь': u'',
    u'Э': u'E',
    u'Ю': u'Yu',
    u'Я': u'Ya'}

lower_letters = {
    u'а': u'a',
    u'б': u'b',
    u'в': u'v',
    u'г': u'g',
    u'д': u'd',
    u'е': u'e',
    u'ё': u'e',
    u'ж': u'zh',
    u'з': u'z',
    u'и': u'i',
    u'й': u'y',
    u'к': u'k',
    u'л': u'l',
    u'м': u'm',
    u'н': u'n',
    u'о': u'o',
    u'п': u'p',
    u'р': u'r',
    u'с': u's',
    u'т': u't',
    u'у': u'u',
    u'ф': u'f',
    u'х': u'h',
    u'ц': u'ts',
    u'ч': u'ch',
    u'ш': u'sh',
    u'щ': u'sch',
    u'ъ': u'',
    u'ы': u'y',
    u'ь': u'',
    u'э': u'e',
    u'ю': u'yu',
    u'я': u'ya'}


def transliterate(rus_string):
    len_str = len(rus_string)
    translit_string = u""
    for index, char in enumerate(rus_string, 1):
        present_char = lower_letters.get(char)
        if present_char:
            translit_string += present_char
            continue
        present_char = upper_letters.get(char)
        if present_char:
            if len_str > index:
                if rus_string[index] not in lower_letters:
                    present_char = present_char.upper()
            else:
                present_char = present_char.upper()
        else:
            present_char = char
        translit_string += present_char
    return translit_string
