import re
import tldextract
from .classifier import predict
from .legit_sources import LEGIT_DOMAINS 
from urllib.parse import urlparse

def check_legit_sender(sender):
    """Check if sender domain matches known legitimate sources."""
    domain = sender.split('@')[-1].lower()
    for legit in LEGIT_DOMAINS:
        if domain.endswith(legit):
            return True, legit
    return False, domain

def extract_urls(text):
    """Find URLs in text body."""
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern.findall(text)

def check_short_urls(urls):
    """Detect shortened or suspicious URLs."""
    shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
    flagged = []
    for u in urls:
        domain = tldextract.extract(u).domain
        if domain in shorteners:
            flagged.append(u)
    return flagged

def analyze(subject, body, sender):
    text = f"{subject} {body}"

    # --- AI Model ---
    ml_label, ml_prob = predict(text)

    # --- Rules & Keywords ---
    keywords = ["password", "account", "verify", "confirm", "urgent", "access", "click", "update"]
    triggered = [kw for kw in keywords if kw in text.lower()]

    # --- Sender Check ---
    LEGIT_DOMAINS = ["paypal.com", "facebook.com", "google.com", "amazon.com", "apple.com", "microsoft.com"]
    domain = sender.split('@')[-1].lower()
    is_legit = any(domain.endswith(d) for d in LEGIT_DOMAINS)

    # --- URL Checks ---
    url_pattern = re.compile(r'https?://\S+')
    urls = url_pattern.findall(body)
    shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
    short_urls = [u for u in urls if tldextract.extract(u).domain in shorteners]

    # --- Final Verdict only from AI ---
    final_label = "Fraudulent" if ml_label == 1 else "Safe"

    # --- Friendly explanation of scoring ---
    score_explanation = {
        "model_confidence": f"AI model thinks this email is {ml_label} with {ml_prob*100:.1f}% confidence",
        "rules_triggered": f"{len(triggered)} suspicious keyword(s) found: {', '.join(triggered) if triggered else 'None'}",
        "sender_check": "Sender is recognized as legitimate" if is_legit else f"Sender domain {domain} not recognized",
        "short_urls": f"{len(short_urls)} suspicious short URL(s) found" if short_urls else "No suspicious URLs found",
    }

    # --- User guidance ---
    user_guidance = "Even if the AI marks this email as Safe, always double-check links and sender addresses. "
    if final_label == "Fraudulent":
        user_guidance += "Do NOT click on any links. Contact official support if unsure."
    elif final_label == "Safe":
        user_guidance += "Looks safe, but remain cautious with links and attachments."

    return {
        "final_label": final_label,
        "ml_label": "Fraudulent" if ml_label == 1 else "Safe",
        "ml_prob": ml_prob*100,
        "score": ml_prob*100,  # simplified to AI confidence
        "rules": triggered,
        "details": score_explanation,
        "urls": urls,
        "short_urls": short_urls,
        "user_guidance": user_guidance,
    }
