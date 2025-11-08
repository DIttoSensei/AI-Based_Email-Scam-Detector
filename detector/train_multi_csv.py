import os
import glob
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import resample
from joblib import dump

# === CONFIG ===
DATA_PATH = r"C:\Users\Owner\Documents\Project\Main\final_year_project\datasets"  # <-- folder where your CSVs are
MODEL_PATH = r"C:\Users\Owner\Documents\Project\Main\final_year_project\detector\engine\email_model.joblib"

print("📂 Loading datasets...")
csv_files = glob.glob(os.path.join(DATA_PATH, "*.csv"))
frames = []
for file in tqdm(csv_files):
    try:
        df = pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="latin-1")
    frames.append(df)

data = pd.concat(frames, ignore_index=True)
print(f"✅ Loaded {len(data)} total emails")

# === CLEANING ===
data = data.fillna("")

# merge key text columns
merge_cols = [col for col in ["sender", "subject", "body", "urls"] if col in data.columns]
data["text"] = data[merge_cols].apply(lambda x: " ".join(x.astype(str)), axis=1)

# ensure label column exists and is numeric
if "label" not in data.columns:
    raise ValueError("Dataset must have a 'label' column (0 = legit, 1 = scam)")

data["label"] = data["label"].astype(int)

# === BALANCING ===
legit = data[data["label"] == 0]
scam = data[data["label"] == 1]

min_len = min(len(legit), len(scam))
legit_down = resample(legit, replace=False, n_samples=min_len, random_state=42)
scam_down = resample(scam, replace=False, n_samples=min_len, random_state=42)

data_balanced = pd.concat([legit_down, scam_down]).sample(frac=1, random_state=42)
print(f"📊 Balanced dataset: {len(data_balanced)} emails (each class = {min_len})")

# === SPLIT ===
X_train, X_test, y_train, y_test = train_test_split(
    data_balanced["text"], data_balanced["label"], test_size=0.2, random_state=42
)

# === TF-IDF Vectorizer ===
vectorizer = TfidfVectorizer(
    max_features=20000,
    ngram_range=(1, 2),
    stop_words="english"
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# === MODEL ===
print("\n🚀 Training model (Logistic Regression)...")
model = LogisticRegression(max_iter=200, n_jobs=-1)
model.fit(X_train_tfidf, y_train)

# === EVALUATION ===
print("\n📊 Evaluating...")
y_pred = model.predict(X_test_tfidf)
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# === SAVE MODEL ===
dump((vectorizer, model), MODEL_PATH)
print(f"\n✅ Model saved at: {MODEL_PATH}")
