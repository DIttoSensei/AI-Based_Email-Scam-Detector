# train_small_model.py
import random
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from joblib import dump
from detector.engine.classifier import save_model

# Create small synthetic dataset (you should replace/add real examples later)
fraud_samples = [
    "URGENT: Verify your account now to avoid suspension. Click here: http://bit.ly/fake",
    "Congratulations! You have won a lottery. Claim your prize by sending bank details.",
    "Your account has been suspended. Login to verify: http://malicious.example.com",
    "We noted unusual activity, verify your password now",
    "Immediate action required: confirm your banking details to avoid penalty"
]
ham_samples = [
    "Meeting rescheduled to Monday afternoon. Please confirm attendance.",
    "Monthly report attached. Kindly review and send feedback.",
    "Dinner plans for Saturday? Let me know your availability.",
    "Your order has been shipped. Tracking number: 123456",
    "Invitation: Join our webinar on AI on Friday at 3pm."
]

# augment to reach ~200 items (small)
X = []
y = []
for i in range(40):
    X.append(random.choice(fraud_samples) + " " + str(i))
    y.append("fraud")
for i in range(160):
    X.append(random.choice(ham_samples) + " " + str(i))
    y.append("ham")

# shuffle
combined = list(zip(X,y))
random.shuffle(combined)
X, y = zip(*combined)

# vectorize with small features to save memory
vec = TfidfVectorizer(max_features=2000, stop_words='english')
Xv = vec.fit_transform(X)

clf = MultinomialNB()
clf.fit(Xv, y)

# save model using the helper
save_model(vec, clf)
print("Trained tiny model and saved.")
