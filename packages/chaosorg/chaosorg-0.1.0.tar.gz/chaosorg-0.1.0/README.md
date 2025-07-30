# ⚡ chaosorg — Organize your messy projects with one command

Ever opened your project folder and thought:

> "Why are there 47 files here and none of them are where they should be?"

**ChaosOrg** is a dead-simple Python CLI tool that organizes your project by sorting files into folders like `/data`, `/scripts`, `/notebooks`, etc. It even supports dry runs and undoing your changes — so you're never locked in.

---

## 🧰 What It Does

| File Type              | Goes to Folder |
| ---------------------- | -------------- |
| `.csv`, `.xlsx`        | `data/`        |
| `.ipynb`               | `notebooks/`   |
| `.py`                  | `scripts/`     |
| `.pkl`, `.joblib`, etc | `models/`      |
| `.png`, `.jpg`         | `outputs/`     |
| `.txt`, `.md`, `.pdf`  | `docs/`        |

And yes, there's an **undo** feature.

---

## 🚀 Installation

Make sure you're in your virtual environment:

```bash
pip install -e .
```

---

## 🧪 Usage

### ✅ Organize the current folder

```bash
chaosorg organize
```

### 🔍 Preview changes (Dry Run)

```bash
chaosorg dry-run
```

### ⏪ Undo the last organization

```bash
chaosorg undo
```

Behind the scenes, it saves a `.chaosorg_log.json` to reverse moves. Clean and simple.

---

## 🧠 Why This Exists

I built this because I was working on multiple ML projects and they all looked like digital garbage dumps. I wanted a tool that's:

* **Beginner-friendly**
* **Undo-able**
* **Easy to extend**
* **Kind of fun to use**

---

## 🛠️ Local Dev Setup

```bash
git clone https://github.com/yourusername/chaosorg.git
cd chaosorg
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 🌐 Coming Soon

* Custom folder mappings
* Exclude folders from being touched
* Integration with `.chaosconfig` file

---

## 📄 License

MIT — free to use, modify, and even break (but don’t blame me 😅)

---

## 💬 Say Hi!

Pull requests, suggestions, or memes welcome.
Let's bring **order** to the **chaos**.
