import re
import math
import numpy as np
from collections import Counter

def gibberish_detector(s: str) -> dict:
    """
    Purpose: Detect if a chat turn is gibberish using a set of rules based on some features. It return 1 if it is gibberish and 0 if not. 

    Created by: J.Hao, June 2025
    """

    # 1. repeat_letter_ratio
    repeats1 = sum(m.end() - m.start()
                   for m in re.finditer(r'([A-Za-z0-9])\1+', s))
    total_alnum = sum(c.isalnum() for c in s)
    repeat_letter_ratio = repeats1 / total_alnum if total_alnum else 0.0

    # 2. repeat_group_ratio
    repeats2 = sum(m.end() - m.start()
                   for m in re.finditer(r'([A-Za-z0-9]+?)\1+', s))
    repeat_group_ratio = repeats2 / total_alnum if total_alnum else 0.0

    # 3. repeat_punct
    repeat_punct = sum(m.end() - m.start()
                       for m in re.finditer(r'([^\w\s])\1+', s))

    # 4. letter_token_ratio (per-character)
    n_chars = len(s)
    letter_token_ratio = sum(c.isalpha() for c in s) / n_chars if n_chars else 0.0

    # 5. count_token, avg/std/max token length
    tokens = s.split()
    count_token = len(tokens)
    if count_token:
        lengths = [len(t) for t in tokens]
        avg_token_length = sum(lengths) / count_token
        std_token_length = float(np.array(lengths).std(ddof=0))
        max_token_length = max(lengths)
    else:
        avg_token_length = std_token_length = max_token_length = 0.0

    # 6. count_unique_character
    count_unique_character = len(set(s) - {' '})

    # 7. count_total_character
    count_total_character = len(s) - s.count(' ')

    # 8. entropy_letter
    letters_only = ''.join(c for c in s if c.isalpha())
    N_letters = len(letters_only)
    if N_letters:
        cnts = Counter(letters_only)
        entropy_letter = -sum((cnt/N_letters) * math.log2(cnt/N_letters)
                              for cnt in cnts.values())
    else:
        entropy_letter = 0.0

    # 9. entropy_character
    N_chars_all = len(s)
    if N_chars_all:
        cnts_all = Counter(s)
        entropy_character = -sum((cnt/N_chars_all) * math.log2(cnt/N_chars_all)
                                 for cnt in cnts_all.values())
    else:
        entropy_character = 0.0

    # ——— your six rules ———
    rules = [
        (repeat_letter_ratio  >= 0.5 and max_token_length   >= 6),
        (repeat_punct         >= 6   and count_token  < 4   and
         max_token_length     >= 10  and letter_token_ratio <= 0.1),
        (repeat_group_ratio   >= 0.5 and max_token_length   >= 6),
        (max_token_length     >= 16),
        (letter_token_ratio   == 0   and max_token_length > 10  and count_token != 1),
        (repeat_letter_ratio  == 1   or repeat_group_ratio   == 1)
    ]

    return {"gibberish":int(any(rules)),"repeated_letter_ratio":repeat_letter_ratio, "repeat_punct":repeat_punct, \
            "repeat_group_ratio":repeat_group_ratio,"max_token_length":max_token_length,"avg_token_length":avg_token_length, \
            "token_count":count_token,"std_token_length":std_token_length, "total_char_count":count_total_character,\
            "unique_char_count":count_unique_character, "letter_token_ratio":letter_token_ratio, \
            "entropy_letter":entropy_letter,"entropy_character":entropy_character}