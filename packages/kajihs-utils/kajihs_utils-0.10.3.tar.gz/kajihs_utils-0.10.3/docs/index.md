<p align="center">
<a href="https://github.com/Kajiih/kajihs-utils">
    <img alt="Kajih's Utils" src="https://www.python.org/static/community_logos/python-logo-generic.svg"/>
</a>
</p>

<p align="center">
    <em>Totally typed, plausibly practical, and remarkably random utilities—for me, and maybe for you too.</em>
</p>

---

**Documentation**: <https://Kajiih.github.io/kajihs-utils/>

**Source Code**: <https://github.com/Kajiih/kajihs-utils>

---

# 🧰 Kajih's Utils <!-- You can add a punchline here -->

## ⬇️ Installation

We recommend you use [uv](https://docs.astral.sh/uv/) to install packages from PyPI:

```shell
uv add kajihs-utils
```

## 🧩 Example

```python
# Useful protocols for structural subtyping
from kajihs_utils.protocols import SupportsAllComparisons, SupportsDunderLT

x: SupportsAllComparisons[int]

# === Core Algorithm Features ===
from kajihs_utils import get_first, is_sorted

# Get first key existing in a dict
d = {"a": 1, "b": 2, "c": 3}
print(get_first(d, ["x", "a", "b"]))  # Output: 1

# Check if an iterable is sorted
print(is_sorted([1, 2, 2, 3]))  # Output: True
print(is_sorted("cba", reverse=True))  # Output: True
print(is_sorted([0, 1, 0]))  # Output: False

from kajihs_utils.core import bisect_predicate

# Find partition points in sorted data
numbers = [1, 3, 5, 7, 9]
first_big = bisect_predicate(numbers, lambda x: x < 6)
print(f"First number >= 6 is at index {first_big}")  # Output: First number >= 6 is at index 3

# Works with custom objects and complex predicates
records = [
    {"temp": 12, "rain": 0.1},
    {"temp": 15, "rain": 0.3},
    {"temp": 18, "rain": 0.0},  # First "nice" day: temp >15 AND rain <0.2
    {"temp": 20, "rain": 0.1},
]
nice_day_idx = bisect_predicate(records, lambda day: not (day["temp"] > 15 and day["rain"] < 0.2))
print(f"First nice day at index {nice_day_idx}")  # Output: First nice day at index 2

# === Loguru features ===
from kajihs_utils.loguru import prompt, setup_logging

# Better logged and formatted prompts
prompt("Enter a number")

# Simply setup well formatted logging in files and console
setup_logging(prefix="app", log_dir="logs")

# === Numpy features ===
import numpy as np

from kajihs_utils.numpy_utils import Vec2d, find_closest

x = np.array([[0, 0], [10, 10], [20, 20]])
print(find_closest(x, [[-1, 2], [15, 12]]))  # Output: [0 1]

# Vec2d class
v = Vec2d(3.0, 4.0)
print(v)  # Output: [3. 4.]
print(tuple(v))  # Output: (np.float64(3.0), np.float64(4.0))
print(v.x)  # Output: 3.0
print(v.y)  # Output: 4.0
print(v.magnitude())  # Output: 5.0
print(v.normalized())  # Output: [0.6 0.8]
print(v.angle())  # Output: 53.13010235415598
print(v.rotate(90, center=(1, 1)))  # Output: [-2.  3.]

# === Whenever features ===
from datetime import datetime

from kajihs_utils.whenever import AllDateTime, ExactDateTime, dt_to_system_datetime  # Useful types

print(dt_to_system_datetime(datetime.now()))  # Output: 2025-05-01T09:48:13.348903+00:00
```
