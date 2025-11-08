from django.shortcuts import render
from .forms import EmailForm
from .models import ScannedEmail
from .engine.analyzer import analyze
from .engine.classifier import model_exists

def index(request):
    form = EmailForm(request.POST or None)
    result = None

    if request.method == "POST" and form.is_valid():
        sender = form.cleaned_data['sender']
        subject = form.cleaned_data['subject']
        body = form.cleaned_data['body']

        # ensure model exists
        if not model_exists():
            result = {"error": "Model not found. Please train the model first."}
        else:
            # run the analyzer (rules + ML)
            analysis = analyze(subject, body, sender)

            # Convert numeric or raw ML label into readable form if needed
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
                # if analyze() already returns readable labels
                ai_label = raw_label

            # update the result dict for rendering
            analysis["ml_label"] = ai_label
            analysis["ml_prob"] = ml_prob

            # save in database
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
