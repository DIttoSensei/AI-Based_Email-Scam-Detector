# Hybrid Fraud & Scam Detector (AI + Rule-Based Django App)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![Sqlite](https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)

An intelligent hybrid platform that detects potential digital threats across multiple communication channels — **Email** and **SMS** — using machine learning classification coupled with heuristic rule-based checkpoints. It extracts metadata, runs vectorization through channel-specific trained models, and yields a final classification: **Safe**, **Suspicious**, or **Fraudulent**.

---

## Features

- **Dual AI Core Engine** – Dynamically routes input to load channel-specific weights (`email_model.joblib` or `sms_model.joblib`) for accurate per-mode inference.
- **Rule-Based Heuristics Engine** – Flags suspicious elements like shortened URLs, phishing vocabulary, urgency hooks, and uppercase abuse across both channels.
- **Tabbed Interface Dashboard** – Supports drag-and-drop `.eml` file parsing for emails alongside a direct text input area for SMS content.
- **Unified Risk Matrix** – Both subsystems communicate through a strict `0.0` to `1.0` decimal scoring layer, feeding a single Hybrid Decision Engine.
- **Final Verdict Card** – Combines AI model probability with rule-based confidence scores into one clearly rendered risk classification.
- **Persistent Analytics Logging** – Every scan is saved asynchronously to an SQLite database via Django models for history and auditing.
- **User Guidance** – Offers safety recommendations based on the result returned.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone -b version_2 https://github.com/DIttoSensei/AI-Based_Email-Scam-Detector.git
cd AI-Based_Email-Scam-Detector
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate      # On Windows
source venv/bin/activate   # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

---

## Project Architecture & Code Layout

The core detection intelligence lives inside the application directory within a dedicated subsystem folder structure:

```text
├── datasets/                  # Storage folder containing the training raw CSV files
│   ├── email_dataset.csv
│   └── sms_dataset.csv
├── engine/                    # Core detection subsystem
│   ├── __init__.py
│   ├── classifier.py          # Dynamic weight loading and inference logic for both channels
│   ├── analyzer.py            # Combines ML output with heuristic string scanning rules
│   ├── legit_sources.py       # Verified domain whitelist lookups
│   ├── email_model.joblib     # Trained email vectorizer + classifier binary
│   └── sms_model.joblib       # Trained SMS vectorizer + classifier binary
```

---

## How the AI Works (In Simple Terms)

Think of this detector as a secure border checkpoint run by two different types of security guards working together: **The Veteran Inspector** (Rules-Based Engine) and **The Data Profiler** (Machine Learning Model). Both channels — Email and SMS — pass through the same checkpoint structure, but each carries its own trained model weights suited to the linguistic patterns of that channel.

```text
                     ┌─────────────────────────────────┐
                     │     User Input via Dashboard     │
                     └──────────────┬──────────────────┘
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
   ┌───────────────────────┐               ┌───────────────────────┐
   │       EMAIL MODE      │               │        SMS MODE       │
   │  Drag-and-drop .eml   │               │  Direct text paste    │
   │  Header + body parse  │               │  Raw payload capture  │
   └──────────┬────────────┘               └──────────┬────────────┘
              │                                       │
              ▼                                       ▼
   ┌───────────────────────┐               ┌───────────────────────┐
   │   email_model.joblib  │               │   sms_model.joblib    │
   │   (TF-IDF + LogReg)   │               │   (TF-IDF + LogReg)   │
   └──────────┬────────────┘               └──────────┬────────────┘
              │                                       │
              └───────────────────┬───────────────────┘
                                  ▼
                   ┌──────────────────────────────┐
                   │   Rule-Based Heuristics       │
                   ├──────────────────────────────┤
                   │ • Short / obfuscated links    │
                   │ • Urgency hook vocabulary     │
                   │ • Fake-safe reassurance text  │
                   │ • Aggressive caps abuse       │
                   └──────────────┬───────────────┘
                                  ▼
                   ┌──────────────────────────────┐
                   │     Hybrid Decision Engine   │
                   │  (Aggregates 0.0 – 1.0 score │
                   │   from ML + Rules layers)    │
                   └──────────────┬───────────────┘
                                  ▼
                        Final Risk Verdict Issued
                     Safe /  Suspicious /  Fraudulent
```

### The Veteran Inspector (Rule-Based Engine)
This part follows a strict, explicit checklist. It doesn't guess — it scans string characters directly for known red flags:
- It checks if the text contains high-pressure vocabulary (`"URGENT"`, `"WIRE TRANSFER NOW"`, `"ACCOUNT SUSPENDED"`).
- It looks for formatting irregularities, such as an excessive percentage of text typed in all CAPITAL LETTERS.
- It extracts and inspects links using `tldextract` to detect shortened URLs, obfuscated domains, and suspicious TLD patterns.
- It isolates fake-safe reassurance phrasing — language designed to lower the reader's guard before delivering the scam payload.

### The Data Profiler (Machine Learning)
Unlike the rule checklist, the ML model reads contextual language patterns. It analyzes how words are paired together, how sentences are structured, and what the overall underlying tone represents. Each channel has its own trained weights because email bodies are typically verbose and multipart while SMS messages are brief and link-heavy — requiring different token distributions to classify accurately.

The final verdict combines both insights. If the ML model finds a subtle pattern but the rules engine triggers multiple red flags, the application escalates the classification aggressively.

---

## How Input Processing Works

### Email Processing
When you drag and drop or upload an `.eml` file into the frontend, it undergoes an automated extraction process before it ever reaches the AI engine.

An `.eml` file is a structured block text document that looks like this behind the scenes:

```text
From: "Security Update" <spoofed-login@attacker-node.net>
Subject: Action Required: Account Compromise
Content-Type: multipart/alternative; boundary="boundary_marker"

--boundary_marker
Content-Type: text/plain; charset="UTF-8"

We detected an unauthorized access attempt on your profile. Update now.
--boundary_marker
```

The backend processes this through three steps:

1. **Header Stripping** – Targets strings appended to `From:` and `Subject:` keys to populate sender verification variables.
2. **Multipart Sifting** – Uses `msg.walk()` to loop through MIME parts, discarding HTML wrappers, scripts, and attachments, extracting only the clean `text/plain` content body.
3. **Encoding Standardization** – Converts complex character encodings into clean string data types before passing the payload downstream to the analyzer.

### SMS Processing
SMS input bypasses file handling entirely. The raw message text is captured directly from the POST request body via the text input field on the SMS tab. The backend strips leading and trailing whitespace, then passes the normalized string straight into the SMS classifier and rules engine. No multipart parsing or encoding conversion is required.

---

## How the Models Are Trained

The pre-compiled `.joblib` binary files were created through an optimization training pipeline using the text data stored inside the `datasets/` folder. Each channel has its own independently trained model.

```text
┌──────────────┐     ┌─────────────────┐     ┌────────────────┐     ┌───────────────────┐
│ Training CSV │ --> │ Text Tokenizer/ │ --> │ Classification │ --> │   Output Model    │
│   Dataset    │     │  TF-IDF Vectors │     │   Algorithm    │     │  (*.joblib file)  │
└──────────────┘     └─────────────────┘     └────────────────┘     └───────────────────┘
```

### 1. Data Aggregation
The process starts with labeled raw training data inside the `datasets/` directory — rows of historic messages categorized into explicit classes: `1` for documented phishing or fraud, and `0` for legitimate correspondence.

### 2. Feature Extraction (Turning Text into Numbers)
The pipeline tokenizes text by splitting it into distinct word units and passing them through a TF-IDF vectorizer. Common functional words like `"the"` or `"and"` are minimized, while diagnostic terms like `"invoice"`, `"bitcoin"`, `"verify"`, or `"claim your prize"` receive targeted weight values.

### 3. Algorithmic Optimization
The numeric arrays are fed into a Logistic Regression classifier. The model adjusts its internal weights iteratively:
- It evaluates a fraudulent message, predicts its class, and checks accuracy.
- If it misclassifies a phishing attempt, it recalibrates the mathematical weight of those specific token combinations.
- This repeats across thousands of records until prediction accuracy stabilizes.

### 4. Serialization (Joblib Export)
Once training finishes, the fitted vectorizer and model weights are serialized using the `joblib` library and saved as `email_model.joblib` and `sms_model.joblib` respectively. The application loads these binaries at inference time in `classifier.py` without re-running the training pipeline.