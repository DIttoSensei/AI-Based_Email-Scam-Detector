import re
import tldextract
from .classifier import predict
from .legit_sources import LEGIT_DOMAINS

# -----------------------------
# Context phrases
# -----------------------------
LEGIT_CONTEXT_PHRASES = [
    "no action required",
    "this is to inform you",
    "successfully completed",
    "transaction receipt",
    "payment confirmation",
    "for your records",
    "thank you for using",
    "withdrawal processed",
    "earnings have been sent",
]

PRESSURE_PHRASES = [
    "act now",
    "immediately",
    "within 24 hours",
    "failure to",
    "will be suspended",
    "verify now",
    "urgent action required",
]

HIGH_RISK_KEYWORDS = {"urgent", "verify", "click", "password", "suspend"}

SHORT_URL_DOMAINS = {
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly',
    'is.gd', 'buff.ly', 'cutt.ly', 'bit.do'
}

# Subtle “too-good-to-be-true” keywords for fake-safe detection
FAKE_SAFE_KEYWORDS = [
    "bonus", "free account", "kick-start", "claim now", "limited offer",
    "click here", "your money", "digital card"
]

# -----------------------------
# Utility functions
# -----------------------------
def check_legit_sender(sender):
    """Check if sender domain matches known legitimate domains."""
    if "@" not in sender:
        return False, sender
    domain = sender.split("@")[-1].lower()
    for legit in LEGIT_DOMAINS:
        if domain.endswith(legit):
            return True, domain
    return False, domain

def extract_urls(text):
    """Extract URLs from text."""
    return re.findall(r'https?://\S+', text)

def check_short_urls(urls):
    """Detect shortened URLs."""
    return [u for u in urls if tldextract.extract(u).registered_domain in SHORT_URL_DOMAINS]

# -----------------------------
# Main analysis function
# -----------------------------
def analyze(subject, body, sender, mode='email'):
    """Hybrid AI + rule-based threat analysis for emails and SMS."""
    text = f"{subject or ''} {body or ''}" if mode == 'email' else (body or '')
    text_lower = text.lower()
    triggered = []

    # ---- AI MODEL PREDICTION ----
    ml_label, ml_prob = predict(text, mode=mode)
    if ml_prob is None:
        ml_prob = 0.0

    # ---- URL EXTRACTION (Universal across both) ----
    urls = extract_urls(body or "")
    short_urls = check_short_urls(urls)

    # ---- RULE-BASED ADJUSTMENTS ----
    rule_risk = 0.0

    # 1. URL Checks
    if short_urls:
        rule_risk += 0.25
        triggered.append(f"Shortened URL detected: {short_urls[0]}")

    # 2. Sender Domain Verification (Emails only)
    if mode == 'email':
        is_legit_sender, sender_domain = check_legit_sender(sender)
        if not is_legit_sender:
            rule_risk += 0.20
            triggered.append(f"Unrecognized sender domain ({sender_domain})")
        sender_check_text = "Recognized legitimate sender" if is_legit_sender else f"Unrecognized sender domain ({sender_domain})"
    else:
        # SMS paths don't check domain records
        sender_check_text = f"SMS Sender Identity: {sender}"

    # 3. Urgency & Pressure Checks
    pressure_hits = sum(p in text_lower for p in PRESSURE_PHRASES)
    if pressure_hits:
        rule_risk += 0.15
        triggered.append(f"Pressure phrases detected ({pressure_hits} hit(s))")

    # 4. Fake-Safe Content Detection
    fake_safe_hits = sum(k in text_lower for k in FAKE_SAFE_KEYWORDS)
    if fake_safe_hits:
        rule_risk += 0.15 * min(fake_safe_hits, 3)  # max 45% bump
        triggered.append(f"Fake-safe keywords detected ({fake_safe_hits} hit(s))")

    # ---- ADJUSTED PROBABILITY (Unified math range) ----
    adjusted_prob = max(0.0, min(ml_prob + rule_risk, 1.0))

    # ---- FINAL VERDICT ----
    if adjusted_prob >= 0.6:
        final_label = f"High Risk: Fraudulent {mode.upper()}"
    elif adjusted_prob >= 0.4:
        final_label = "Needs Review: Suspicious"
    else:
        final_label = "Low Risk: Safe"

    # ---- CONTEXT HITS ----
    legit_context_hits = sum(p in text_lower for p in LEGIT_CONTEXT_PHRASES)

    # ---- EXPLANATION OBJECT ----
    score_explanation = {
        "rules_triggered": ", ".join(triggered) if triggered else "None",
        "sender_check": sender_check_text,
        "urls_found": ", ".join(urls) if urls else "None",
        "ai_confidence": f"{round(adjusted_prob * 100, 1)}%",
        "context_hits": legit_context_hits,
        "pressure_hits": pressure_hits,
        "fake_safe_hits": fake_safe_hits,
    }

    # ---- USER GUIDANCE (Tailored context hints) ----
    if mode == 'email':
        user_guidance = "Always verify sender addresses and avoid clicking links directly from emails. "
    else:
        user_guidance = "Be careful with text messages offering sudden rewards or claiming package delivery updates. "

    if final_label.startswith("High Risk"):
        user_guidance += f"This {mode} shows strong indicators of scam activity. Do NOT interact with or click links."
    elif final_label.startswith("Needs Review"):
        user_guidance += f"This {mode} has suspicious indicators. Cross-check from an official application source."
    else:
        user_guidance += f"This {mode} appears safe, but maintain standard caution guidelines."

    # ---- FINAL RESPONSE ----
    return {
        "final_label": final_label,
        "ml_label": "Fraudulent" if ml_label == 1 else "Safe",
        "ml_prob": round(ml_prob * 100, 1),   # Pure model confidence formatted as %
        "score": round(adjusted_prob * 100, 1), # Risk factor formatted as %
        "rules": triggered,
        "details": score_explanation,
        "urls": urls,
        "user_guidance": user_guidance,
    }