# Email Fraud & Scam Detector (AI + Rule-Based Django App)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![Sqlite](https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)

An intelligent hybrid system that detects potential email scams using both machine learning and rule-based heuristics.  
It analyzes sender authenticity, suspicious URLs, keywords, and tone to determine if an email is Safe, Suspicious, or Fraudulent.

---

## Features

- AI Analyzer (Joblib Model) – Trained on real email datasets to classify messages as Safe or Fraudulent.
- Rule-Based Engine – Flags suspicious elements like short URLs, phishing words, and uppercase abuse.
- Detailed Analysis View – Displays full breakdown of sender, URLs, and rule triggers.
- Final Verdict – Combines AI model prediction with rule-based confidence.
- User Guidance – Offers safety recommendations based on results.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/DIttoSensei/AI-Based_Email-Scam-Detector.git
cd AI-Based_Email-Scam-Detector
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On macOS/Linux
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
├── datasets/             # Storage folder containing the training raw CSV files
├── engine/               # Core detection subsystem
│   ├── __init__.py
│   ├── classifier.py     # Handles model verification, loading, and text predictions
│   ├── analyzer.py       # Combines ML output with heuristic string scanning rules
│   └── model.joblib      # The compiled, trained machine learning model binary
```

---

## How the AI Works (In Simple Terms)

Think of this detector as a secure border checkpoint run by two different types of security guards working together: The Veteran Inspector (Rules-Based Engine) and The Data Profiler (Machine Learning Model).

```text
                  ┌──────────────────────────────┐
                  │ Uploaded Email Message File  │
                  └──────────────┬───────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
      ┌─────────────────────────┐ ┌─────────────────────────┐
      │   Rule-Based Heuristics │ │    Machine Learning     │
      │   (The Veteran Inspector)│ │   (The Data Profiler)   │
      ├─────────────────────────┤ ├─────────────────────────┤
      │ • Aggressive caps abuse │ │ • Vectorizes message    │
      │ • Known phishing links  │ │ • Computes probability  │
      │ • High-risk keywords    │ │   matrix using weights  │
      └────────────┬────────────┘ └────────────┬────────────┘
                   │                           │
                   └─────────────┬─────────────┘
                                 ▼
                  ┌──────────────────────────────┐
                  │    Hybrid Decision Engine    │
                  │ (Aggregates Scores & Yields) │
                  └──────────────┬───────────────┘
                                 ▼
                     Final Risk Verdict Issued
```

### The Veteran Inspector (Rule-Based Engine)
This part follows a strict, explicit checklist. It doesn't guess; it scans the string characters directly for known red flags:
- It checks if the text contains high-pressure vocabulary ("URGENT", "WIRE TRANSFER NOW", "ACCOUNT SUSPENDED").
- It looks for formatting irregularities, such as an excessive percentage of text typed in all CAPITAL LETTERS.
- It extracts links to see if they are hidden behind link-shortening services or use domains that look strange.

### The Data Profiler (Machine Learning)
Unlike the rule checklist, the ML model looks at the contextual patterns of the language. It reads the email and analyzes how words are paired together, how sentences are structured, and what the overall underlying tone represents. It computes a math-based probability percentage indicating how closely this email's linguistic fingerprint mirrors past confirmed historical scams.

The final verdict combines both insights. If the ML model finds a subtle pattern but the rules engine triggers three major red flags, the application flags it aggressively.

---

## How File Input Processing Works

When you drag and drop or upload an `.eml` file into the frontend, it undergoes an automated extraction process before it ever reaches the AI engine. 

An `.eml` file is actually a structured block text document that looks like this behind the scenes:

```text
From: "Security Update" <spoofed-login@attacker-node.net>
Subject: Action Required: Account Compromise
Content-Type: multipart/alternative; boundary="boundary_marker"

--boundary_marker
Content-Type: text/plain; charset="UTF-8"

We detected an unauthorized access attempt on your profile. Update now.
--boundary_marker
```

Because your custom detection engine needs clean textual elements, the code unrolls this raw file automatically:

1. **Header Stripping**: It targets strings appended to `From:` and `Subject:` keys to populate your sender verification variables instantly.
2. **Multipart Sifting**: True exported email files often contain an HTML visual structure along with hidden data attachments. The backend uses an unrolling pipeline loop (`msg.walk()`) to discard code wrappers, scripts, and attachments, extracting only the unformatted `text/plain` content body string.
3. **Encoding Standardization**: It converts complex text encodings into clean, safe string data types, passing an organized dataset downstream to your analyzer functions.

---

## How the Model is Trained

The pre-compiled `model.joblib` binary file was created through an optimization training pipeline using the text data stored inside your `datasets/` folder.

```text
┌──────────────┐      ┌─────────────────┐      ┌────────────────┐      ┌──────────────┐
│ Training CSV │ ───> │ Text Tokenizer/ │ ───> │ Classification │ ───> │ Output Model │
│   Dataset    │      │  Vectorization  │      │   Algorithm    │      │ (model.joblib)│
└──────────────┘      └─────────────────┘      └────────────────┘      └──────────────┘
```

### 1. Data Aggregation
The process starts with labeled raw training data inside the `datasets/` directory. This data consists of rows of historic email exchanges categorized cleanly into explicit classes: `1` for documented phishing/fraud messages, and `0` (or `-1`) for normal, legitimate corporate or personal correspondence.

### 2. Feature Extraction (Turning Text into Numbers)
Computers cannot interpret raw text strings or semantics directly; they process mathematical matrices. The data pipeline tokenizes the text by splitting sentences into distinct word units and passing them through a vectorizer wrapper (such as TF-IDF or CountVectorizer). 

This tool assigns specific mathematical scores to words based on their frequencies. Common functional words like "the" or "and" get minimized, while diagnostic terms like "invoice", "bitcoin", "verify", or "inheritance" yield targeted weight values.

### 3. Algorithmic Optimization
The numeric arrays are fed into a classification algorithm (like a Naive Bayes or Logistic Regression framework). The model adjusts its internal weights repeatedly:
- It looks at a fraudulent email, predicts its category, and checks if it got it right.
- If it misses a sneaky phishing attempt, it recalibrates the mathematical importance of those specific word combinations.
- This repeats across thousands of records until prediction accuracy stabilizes.

### 4. Serialization (Joblib Export)
Once training finishes, the optimal network state, vocabulary weights, and array dimensions are packed up. Using the `joblib` library, Python dumps this operational memory matrix out of RAM and saves it into a permanent binary layout file: `model.joblib`. 

Your application can load this lightweight file instantly in `classifier.py` to make real-time predictions without needing to re-run the entire data training pipeline every time a user uploads an email.