from django.shortcuts import render
from .forms import EmailForm
from .models import ScannedEmail
from .engine.analyzer import analyze
from .engine.classifier import model_exists
from email import message_from_bytes

def index(request):
    form = EmailForm(request.POST or None, request.FILES or None)
    result = None

    if request.method == "POST":
        # 1. Capture the structural mode state flag from the hidden input element
        mode = request.POST.get("analysis_mode", "email")
        
        # 2. Check if the core engine files exist on disk
        if not model_exists(mode=mode):
            result = {"error": f"The model weight file for {mode.upper()} does not exist. Please train it first."}
        
        # --- PATH A: PROCESS SMS TEXT DATA ---
        elif mode == "sms":
            sms_text = request.POST.get("sms_text", "").strip()
            
            if not sms_text:
                result = {"error": "Please enter some text content to analyze."}
            else:
                # SMS skips sender authentication checks, pass placeholder identifier metadata
                result = analyze(subject="", body=sms_text, sender="SMS_Inbox", mode="sms")
                
                # Log to your storage schema database if desired (Optional)
                ScannedEmail.objects.create(
                    subject="[SMS Message Scan]",
                    sender="SMS_Inbox",
                    body=sms_text,
                    rules_triggered=",".join(result["rules"]),
                    ml_label=result["ml_label"],
                    final_label=result["final_label"],
                    score=result["score"]
                )

        # --- PATH B: PROCESS INCOMING EMAIL CHANNELS ---
        elif mode == "email" and form.is_valid():
            uploaded_file = request.FILES.get('email_file')
            if not uploaded_file:
                result = {"error": "Please provide a valid .eml asset artifact."}
            else:
                file_bytes = uploaded_file.read()
                msg = message_from_bytes(file_bytes)

                sender = msg.get('From', 'Unknown Sender')
                subject = msg.get('Subject', '(No Subject)')

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition'))
                        if content_type == 'text/plain' and 'attachment' not in content_disposition:
                            body = part.get_payload(decode=True).decode(errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')

                # Pass configuration flags down the execution stream
                result = analyze(subject, body, sender, mode="email")

                ScannedEmail.objects.create(
                    subject=subject,
                    sender=sender,
                    body=body,
                    rules_triggered=",".join(result["rules"]),
                    ml_label=result["ml_label"],
                    final_label=result["final_label"],
                    score=result["score"]
                )

    return render(request, "detector/index.html", {"form": form, "result": result})