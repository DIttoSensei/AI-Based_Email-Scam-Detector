from django.shortcuts import render
from .forms import EmailForm
from .models import ScannedEmail
from .engine.analyzer import analyze
from .engine.classifier import model_exists

# 1. IMPORT PYTHON'S NATIVE EMAIL UTILITIES
from email import message_from_bytes

def index(request):
    # File forms require both request.POST and request.FILES data matrices
    form = EmailForm(request.POST or None, request.FILES or None)
    result = None

    if request.method == "POST" and form.is_valid():
        # 2. READ THE FILE BYTES
        uploaded_file = request.FILES['email_file']
        file_bytes = uploaded_file.read()

        # 3. TRANSLATE BYTES INTO AN EMAIL MESSAGE OBJECT
        msg = message_from_bytes(file_bytes)

        # 4. EXTRACT THE HEADERS
        # msg.get() safely falls back to a default string if a header is completely missing
        sender = msg.get('From', 'Unknown Sender')
        subject = msg.get('Subject', '(No Subject)')

        # 5. EXTRACT THE BODY PAYLOAD
        # Emails can be a single plain text string, or a complex multipart structure 
        # containing HTML versions, text versions, and attachments.
        body = ""
        if msg.is_multipart():
            # Walk through every block component inside the email package
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                
                # We only want raw unformatted text, ignoring image/file attachments
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            # Single-part emails are straightforward
            body = msg.get_payload(decode=True).decode(errors='ignore')

        # From here down, your engine code stays completely untouched!
        if not model_exists():
            result = {"error": "Model not found. Please train the model first."}
        else:
            analysis = analyze(subject, body, sender)

            raw_label = analysis.get("ml_label")
            ml_prob = round(analysis.get("ml_prob", 0.0) * 100, 2)

            if isinstance(raw_label, (int, float)):
                if raw_label == 1:
                    ai_label = "Fraudulent"
                elif raw_label == -1:
                    ai_label = "Suspicious"
                else:
                    ai_label = "Safe"
            else:
                ai_label = raw_label

            analysis["ml_label"] = ai_label
            analysis["ml_prob"] = ml_prob

            ScannedEmail.objects.create(
                subject=subject,
                sender=sender,
                body=body,
                rules_triggered=",".join(analysis["rules"]),
                ml_label=ai_label,
                final_label=analysis["final_label"],
                score=analysis["score"]
            )

            result = analysis

    return render(request, "detector/index.html", {"form": form, "result": result})