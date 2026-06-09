import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import resample
from joblib import dump

# ==========================================
# 1. PATH CONFIGURATION
# ==========================================
# Absolute path to your downloaded Kaggle dataset file
DATASET_FILE = r"F:\user\Documents\final_year_project\datasets_sms\spam.csv"

# Destination path for your new, separate SMS machine learning model
MODEL_OUTPUT_PATH = r"F:\user\Documents\final_year_project\detector\engine\sms_model.joblib"


# ==========================================
# 2. DATA LOADING & EXTRACTION
# ==========================================
print("📂 Loading Kaggle SMS dataset...")
if not os.path.exists(DATASET_FILE):
    raise FileNotFoundError(f"❌ Could not find 'spam.csv' at: {DATASET_FILE}. Please check the path.")

try:
    # Public datasets often use ISO-8859-1 / latin-1 encoding structures
    df = pd.read_csv(DATASET_FILE, encoding="latin-1")
except Exception as e:
    df = pd.read_csv(DATASET_FILE, encoding="utf-8")

print(f"✅ Raw dataset loaded successfully. Total records: {len(df)}")


# ==========================================
# 3. CLEANING & STANDARDIZATION
# ==========================================
# Kaggle's SMS dataset outputs columns named: 'v1' (label) and 'v2' (text)
# We map these safely to your engine's expected target architecture.
if "v1" in df.columns and "v2" in df.columns:
    df = df[["v1", "v2"]].copy()
    df.columns = ["label", "text"]
else:
    raise KeyError("Dataset columns mismatch! Ensure your CSV file contains 'v1' and 'v2' headers.")

# Convert text column strings to remove missing value fields
df["text"] = df["text"].fillna("").astype(str)

# Map text string classifications ('spam' -> 1, 'ham' -> 0) to numerical integers
df["label"] = df["label"].apply(lambda x: 1 if str(x).strip().lower() == "spam" else 0)


# ==========================================
# 4. CLASS IMBALANCE CORRECTION (DOWNSAMPLING)
# ==========================================
legit_messages = df[df["label"] == 0]
scam_messages = df[df["label"] == 1]

print(f"📊 Original Distribution -> Legit (Ham): {len(legit_messages)} | Scam (Spam): {len(scam_messages)}")

# Match minority class size to balance weights perfectly
min_sample_size = min(len(legit_messages), len(scam_messages))

legit_downsampled = resample(legit_messages, replace=False, n_samples=min_sample_size, random_state=42)
scam_downsampled = resample(scam_messages, replace=False, n_samples=min_sample_size, random_state=42)

# Merge back into a single balanced dataset frame and shuffle
balanced_df = pd.concat([legit_downsampled, scam_downsampled]).sample(frac=1, random_state=42)
print(f"⚖️ Balanced Matrix: {len(balanced_df)} rows total ({min_sample_size} records per target class)")


# ==========================================
# 5. DATASET SPLITTING
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(
    balanced_df["text"], balanced_df["label"], test_size=0.2, random_state=42
)


# ==========================================
# 6. FEATURE VECTORIZATION (TEXT TO NUMBERS)
# ==========================================
# Lower max_features (10,000) prevents dimensional overfitting on thin SMS sentences
vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    stop_words="english"
)

print("🧮 Transforming text strings into numeric matrices...")
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)


# ==========================================
# 7. MODEL TRAINING
# ==========================================
print("🚀 Training Logistic Regression classifier on SMS data profiles...")
model = LogisticRegression(max_iter=200, n_jobs=-1, random_state=42)
model.fit(X_train_tfidf, y_train)


# ==========================================
# 8. PERFORMANCE EVALUATION METRICS
# ==========================================
print("\n📋 Model Training Evaluation Summary:")
y_pred = model.predict(X_test_tfidf)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Legit (0)", "Scam (1)"]))

print("Confusion Matrix Layout:")
print(confusion_matrix(y_test, y_pred))


# ==========================================
# 9. SERIALIZATION & EXPORT
# ==========================================
# Create directory paths automatically if they don't exist
os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)

# Export structural configurations as a single loadable tuple bundle
dump((vectorizer, model), MODEL_OUTPUT_PATH)
print(f"\n✅ Dedicated SMS Vector Model matrix compiled and saved successfully!")
print(f"📍 Location: {MODEL_OUTPUT_PATH}")