# 📧 Email Fraud & Scam Detector (AI + Rule-Based Django App)

An intelligent hybrid system that detects potential email scams using both **machine learning** and **rule-based heuristics**.  
It analyzes sender authenticity, suspicious URLs, keywords, and tone to determine if an email is **Safe**, **Suspicious**, or **Fraudulent**.

---

## 🚀 Features

- 🧠 **AI Analyzer (Joblib Model)** – Trained on real email datasets to classify messages as Safe or Fraudulent.
- 🧾 **Rule-Based Engine** – Flags suspicious elements like short URLs, phishing words, and uppercase abuse.
- 🔍 **Detailed Analysis View** – Displays full breakdown of sender, URLs, and rule triggers.
- 🎯 **Final Verdict** – Combines AI model prediction with rule-based confidence.
- 💡 **User Guidance** – Offers safety recommendations based on results.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/DIttoSensei/AI-Based_Email-Scam-Detector.git
cd AI-Based_Email-Scam-Detector
```

## Create and Activate a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On macOS/Linux
```

## Install Dependencies
```bash
pip install -r requirements.txt
```

## Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Run the Development Server
```bash
python manage.py runserver
```


