# Framer

A lightweight Python-based 2D graphics library.

> **Note:** This library is Windows-specific as it uses `msvcrt` and the `mode con` command to control the console.

---

## ✨ Features

- Dynamic console window resizing and color setting
- ASCII-based frame rendering engine
- Object placement by coordinates
- Frame-rate control using `fps`
- Minimal keyboard input capture (`msvcrt.getch()`)

---

## 📦 Installation

Use pip to install:
`pip install framer43`

---

## 🧠 How It Works

Framer renders frames using a list of `[x, y, char]` objects and manually calculates spacing between characters to simulate positions in the terminal. It flushes each frame to the standard output with optional FPS delay.

---

## 📘 Usage

### Example

```python
from framer import Framer

f = Framer()
f.initwin(ar="16:9", scale=5, color="0A", fps=10)  # Sets resolution and color

# Animate a simple horizontal line moving across
for i in range(10, f.cols - 10):
    f.addObj(i, f.lines // 2, "*")  # Middle row
    if f.renderFrame() == 'q':
        break
