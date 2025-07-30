# gibberish-chat-detector

`gibberish-chat-detector` is a lightweight Python package that detects gibberish or mischievous chat messages using a set of interpretable, rule-based heuristics. Machine learning approach generally won't work well given there are often special definition of what is considered gibberish in specific application. This detector give you full flexibility and transparence about what to detect. It is particularly useful for filtering low-quality user input in chat systems, collaborative platforms, or educational environments.

---

## 🔍 How It Works

The core detection logic is based on a suite of **handcrafted textual features** and a set of **six transparent rules**. If any rule triggers, the message is flagged as **gibberish**.

The detection is deterministic, fast, and doesn't rely on machine learning — making it interpretable and easily customizable.

---

## 📥 Input and 📤 Output

### Input

The main function accepts a single string:

```python
detect_gibberish_chat(s: str)
```

- `s` — A chat message or short text (e.g., `"hellooooooo!!!!"`)

### Output

The function returns a dictionary containing:
- A top-level `gibberish` flag: `1` (True) or `0` (False)
- A collection of interpretable features

Example:
```python
{
  'gibberish': 1,
  'repeated_letter_ratio': 0.73,
  'repeat_punct': 8,
  'repeat_group_ratio': 0.0,
  'max_token_length': 12,
  'avg_token_length': 5.2,
  'token_count': 3,
  'std_token_length': 2.3,
  'total_char_count': 19,
  'unique_char_count': 8,
  'letter_token_ratio': 0.12,
  'entropy_letter': 1.44,
  'entropy_character': 2.10
}
```

---

## ✨ Features Used

The detector computes the following per-message features:

| Feature Name               | Description |
|---------------------------|-------------|
| `repeated_letter_ratio`   | Ratio of repeated single characters (e.g., `aaa`, `111`) to total alphanumeric characters |
| `repeat_group_ratio`      | Ratio of repeated character groups (e.g., `abcabcabc`) |
| `repeat_punct`            | Count of repeated non-alphanumeric symbols (e.g., `!!!` or `???`) |
| `letter_token_ratio`      | Ratio of alphabetic characters to all characters |
| `token_count`             | Number of tokens (split by whitespace) |
| `avg_token_length`        | Average length of tokens |
| `std_token_length`        | Standard deviation of token lengths |
| `max_token_length`        | Length of the longest token |
| `unique_char_count`       | Count of unique non-space characters |
| `total_char_count`        | Count of all non-space characters |
| `entropy_letter`          | Entropy of alphabetic characters |
| `entropy_character`       | Entropy of all characters |

---

## ✅ Example Usage

```python
from gibberish_chat_detector import detect_gibberish_chat

text = "l;kjasdf;lkjasdf;lkj!!!!"
result = detect_gibberish_chat(text)

print(result['gibberish'])

```

---

## 🛠 Customizing the Rules

By default, the detector uses six interpretable rules based on the above features. For example:

```python
(repeated_letter_ratio >= 0.5 and max_token_length >= 6)
```

You can customize the rules by modifying the rule section in `detector.py`, or refactor it to load thresholds dynamically from a config file or function argument.

---

## 📦 Installation

```bash
pip install gibberish-chat-detector
```

Requires Python 3.7+.

---

## 🔓 License

MIT License

---

## 👨‍💻 Author

Developed by Jiangang Hao

---

## 💡 Contributing

Got ideas for new features or more precise rules? Contributions are welcome — open a PR or issue!
