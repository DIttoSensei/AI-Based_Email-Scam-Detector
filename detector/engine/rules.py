# rules.py
import re
from urllib.parse import urlparse
import tldextract

# lightweight suspicous keywords
SUSPICIOUS_KEYWORDS = [
    'urgent', 'password', 'verify', 'account', 'login', 'click', 'update', 'security', 'alert', 'suspend', 'confirm', 'bank',
    'limited', 'immediate', 'action', 'request', 'access', 'identity', 'billing', 'invoice', 'payment', 'failure', 'reset',
    'bank', 'lottery', 'winner', 'prize', 'congratulations', 'claim', 'reward', 'offer', 'free', 'gift', 'cash',
    'transfer', 'transcation', 'cbn', 'nibss',
]

SHORTENER_DOMAINS = {'bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd', 'buff.ly', 'adf.ly', 'bit.do', 'cutt.ly', 'lc.chat'}

def extract_domains_from_text(text):
    urls = re.findall(r'(https?://\S)', text)
    domains = []
    for u in urls:
        try:
            p = urlparse(u)
            dom = tldextract.extract(p.netloc).registered_domain
            if not dom:
                dom = p.netloc
            domains.append((u, dom.lower()))
        except Exception:
            continue
    return urls, domains

def check_sender_domain_mismatch(sender, from_display=None):
    # sender: user@domain.com
    if "@" not in sender:
        return True
    try:
        local, domain = sender.split("@", 1)
        if from_display:
            # if display name contains an org name, check similarity
            if from_display.lower().strip() in domain.lower():
                return False
        return False
    except Exception:
        return True

def rule_check(subject, body, sender):
    reason_list = []
    text = f"{subject or ''}\n{body or ''}".lower()

    # keyword checks
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in text:
            reason_list.append(f"keyword:{kw}")

    # URL checks
    urls, domains = extract_domains_from_text(text)
    for u, dom in domains:
        if dom in SHORTENER_DOMAINS:
            reason_list.append(f"shortened_url:{u}")
        # IP-based link?
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', dom):
            reason_list.append(f"ip_link:{u}")

    # malformed sender
    if "@" not in sender or sender.count("@") != 1:
        reason_list.append("malformed_sender")

    # basic domain mismatch (simple)
    if check_sender_domain_mismatch(sender):
        reason_list.append("sender_domain_mismatch")

    # uppercase/exclamation heuristic
    if len(re.findall(r'[A-Z]{2,}', body or '')) > 5:
        reason_list.append("uppercase_abuse")
    if "!" in text and text.count("!") > 2:
        reason_list.append("many_exclamations")

    # return unique reasons
    return list(dict.fromkeys(reason_list))