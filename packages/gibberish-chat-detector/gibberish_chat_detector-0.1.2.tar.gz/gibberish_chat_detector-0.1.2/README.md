
# gibberish-chat-detector

A simple Python package to detect gibberish or mischievous messages in chat logs using rule-based features.

## 🔍 What It Does

This package computes a set of linguistic and statistical features from a chat message and applies a customizable rule-based system to flag potentially gibberish messages.

## 🚀 Installation

```bash
pip install gibberish-chat-detector
```

## 🧠 How It Works

The detector extracts features such as repeated characters, punctuation patterns, token lengths, and entropy of characters and letters. These features are then checked against a list of boolean rules to determine if the message is gibberish.

## ✨ Features Used

The gibberish detector uses the following features:

- `repeat_letter_ratio`: Proportion of alphanumeric characters that are repeated consecutively (e.g., "aaa", "111").
- `repeat_group_ratio`: Proportion of repeated sequences of letters or digits (e.g., "abcabc", "1212").
- `repeat_punct`: Total count of repeated punctuation symbols (e.g., "!!!", "??!!??").
- `letter_token_ratio`: Fraction of characters that are alphabetic (useful for spotting symbol-heavy gibberish).
- `max_token_length`: Length of the longest token (word-like unit) in the message.
- `avg_token_length`: Average length of tokens in the message.
- `std_token_length`: Standard deviation of token lengths, indicating variation.
- `count_token`: Total number of tokens (words or fragments separated by whitespace).
- `count_total_character`: Total number of non-space characters.
- `count_unique_character`: Number of unique characters excluding spaces.
- `entropy_letter`: Entropy (diversity) of alphabetic characters, indicating randomness or repetitiveness.
- `entropy_character`: Entropy of all characters, including symbols, digits, and letters.

## 🧪 Example Usage

```python
from gibberish_detector import gibberish_detector

text = "aaaaa!!!??"
result = gibberish_detector(text)

print(result["gibberish"])  # 1 if gibberish, 0 otherwise
print(result)  # All feature values
```

## 🔧 Customizing Rules

You can pass your own rule string to override the default logic. The rule string should be a Python-style list of boolean expressions using the feature names listed above.

### Example:

```python
custom_rule = '''[
    (repeat_letter_ratio >= 0.5 and max_token_length >= 6),
    (repeat_punct >= 6 and count_token < 4 and max_token_length >= 10 and letter_token_ratio <= 0.1),
    (repeat_group_ratio >= 0.5 and max_token_length >= 6),
    (max_token_length >= 16),
    (letter_token_ratio == 0 and max_token_length > 10 and count_token != 1),
    (repeat_letter_ratio == 1 or repeat_group_ratio == 1)
]'''

result = gibberish_detector("aaa!!!", rule=custom_rule)
print(result["gibberish"])
```

⚠️ **Note**: The rule string is evaluated using `eval()` within the context of the feature dictionary, and should only be used in trusted environments.

## 📬 Output Format

The function returns a dictionary with the following fields:

```python
{
    "gibberish": 1,
    "repeat_letter_ratio": 0.8,
    "repeat_punct": 7,
    "repeat_group_ratio": 0.6,
    "max_token_length": 12,
    "avg_token_length": 6.0,
    "std_token_length": 2.3,
    "count_token": 4,
    "count_total_character": 20,
    "count_unique_character": 10,
    "letter_token_ratio": 0.3,
    "entropy_letter": 2.5,
    "entropy_character": 3.1
}
```

## 🛡️ License

MIT License

## 👤 Author

Developed by Jiangang Hao, June 2025
