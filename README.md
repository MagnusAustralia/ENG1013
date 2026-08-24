# ENG1013

The repository is split into the two milestone code submissions required for the project.

---

## 📦 Getting Started

### Prerequisites

Ensure that you have previously flashed **FirmataExpress** to the Arduino Uno.

You can either use your global Python environment, as you may have done previously, or use a Python environment manager such as `uv`.

### Installing uv

#### Windows

````powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"


#### macOS

```bash
brew install uv
````

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/MagnusAustralia/ENG1013.git
   cd ENG1013
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

### Running Python files

To run a python file:

```bash
uv run python main.py
```

---

## 🤝 How to add

1. Switch to test branch (`git switch test`)
2. Get latest changes (`git pull`)
3. Make your changes
   Run Ruff: (`uv run ruff check .`)
   Check ENG1013 Standards: (`uv run python check_eng1013.py`)
   Check formating (`uv run ruff format --check`)
4. Stage your Changes (`git add .`)
5. Commit your Changes (`git commit -m 'Explain what you have done'`)
6. Push to the Branch (`git push origin test`)
