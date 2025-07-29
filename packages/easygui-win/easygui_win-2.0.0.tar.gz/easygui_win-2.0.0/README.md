# EasyGUI - The Easiest Windows GUI Library

A super simple Windows GUI library for Python — with **no external dependencies**!

---

## 🚀 Features

- ✅ **Super simple API**
- 🔥 **No external dependencies**
- 💨 **Pure Python**, powered by the Windows API
- 🎨 Customizable **colors and styling**
- 🧱 Supports **method chaining**
- ⚡ **Lightweight and fast**

---

## 📦 Installation

```bash
pip install easygui-win
```

---

## 🧪 Quick Start

### Basic Style

```python
import easygui as gui

app = gui.App("My App")
app.text("Hello World!")
app.button("Click me!", lambda: print("Clicked!"))
app.run()
```

### Decorator Style

```python
import easygui as gui

@gui.app("My App")
def my_app():
    gui.text("Welcome!")
    gui.button("OK", gui.close)
```

---

## 🖼️ Examples

Run the included demos:

```bash
easygui-demo
```

---

## 📋 Requirements

- Python **3.7+**
- Windows OS

---

## 📄 License

MIT License — see the `LICENSE` file for details.
