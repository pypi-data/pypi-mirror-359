# streamlit_autocomplete

A simple Python package for adding **autocomplete** functionality to a Streamlit app’s `st.text_area`, using [`streamlit-textcomplete`](https://pypi.org/project/streamlit-textcomplete/).

## Features

- Fast, case‑insensitive autocomplete as you type
- Works with any list of strings (cities, stock names, etc.)
- Clean, minimal API for Streamlit

---

## Installation

```bash
pip install streamlit-autocomplete
```

> **Note:** `streamlit` and `streamlit-textcomplete` are installed automatically as dependencies.

---

## Usage

```python
import streamlit as st
from streamlit_autocomplete import st_textcomplete_autocomplete

# Autocomplete options
city_names = [
    "New York", "London", "Paris", "Berlin", "Tokyo", "Mumbai",
    # ...more
]

query = st_textcomplete_autocomplete(
    label="Enter city or metric",
    options=city_names,
    key="city_autocomplete",
    help="Start typing a city name"
)

st.write("You typed:", query)
```

---

## API

| Parameter             | Type | Description                                            |
| --------------------- | ---- | ------------------------------------------------------ |
| **label**       | str  | Label for the text area                                |
| **options**     | list | List of strings for autocomplete                       |
| **key**         | str  | Streamlit key (use different keys for multiple fields) |
| **placeholder** | str  | Placeholder text (optional)                            |
| **height**      | int  | Text area height (optional, default `120`)           |
| **help**        | str  | Help tooltip (optional)                                |
| **max_count**   | int  | Maximum suggestions to display (default `10`)        |

**Returns:** `str` – the current typed/autocompleted string.

---

## License

MIT License

---

## Credits

- [streamlit-textcomplete](https://github.com/huseinzol05/streamlit-textcomplete)
