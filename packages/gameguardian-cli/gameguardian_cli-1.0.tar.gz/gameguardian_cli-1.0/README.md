# 🛡️ GameGuardian CLI (ggcli)

A Command Line Interface (CLI) version of the Game Guardian application, built in Python.

🎯 Designed for Linux, Termux, or Android NetHunter environments with root access.
🧠 Intended for users who need full control over memory processes directly from the terminal.

---

## ✨ Key Features

* 🔍 Search values in process memory (int, float, string)
* ✏️ Edit found values
* 📌 Freeze values (prevent them from changing)
* 🧠 Select active process by PID or name
* 🛠️ Interactive shell interface using `cmdloop()`

---

## 🧪 Example Usage

```bash
ggcli
```

Then use commands inside the shell:

```
> list
> select 1234
> search 100
> edit 0 999
> freeze 0
```

---

## 🚀 Installation

### From PyPI:

```bash
pip install gameguardian-cli
```

### From Source:

```bash
git clone https://github.com/username/gameguardian-cli
cd gameguardian-cli
pip install .
```

---

## 💻 Requirements

* Python 3.6+
* Root access (Linux/Android)
* `gdb`, `ptrace`, or other low-level memory utilities (depending on backend)

---

## 🔒 Disclaimer

This tool is for educational and research purposes only.
**The author is not responsible for any misuse.**

---

## 🙌 Credits

Created by [Dx4Grey](https://github.com/DX4GREY)
Inspired by Game Guardian and the world of Android/Linux reverse engineering.