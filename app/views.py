from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ScoreHistory   


# ---------------- HOME PAGE (SUBJECT SELECTION) ----------------
@login_required
def home(request):
    return render(request, "index.html")


# ---------------- ANSWER PAGE (TEXT INPUT) ----------------
@login_required
def answer_page(request):
    # Coming from subject selection
    if request.method == "POST":
        subject = request.POST.get("subject")

        if not subject:
            return redirect("home")

        # store subject for "Try Again"
        request.session["subject"] = subject

        return render(request, "answer.html", {
            "subject": subject
        })

    # Coming from "Try Again"
    subject = request.session.get("subject")
    if subject:
        return render(request, "answer.html", {
            "subject": subject
        })

    return redirect("home")

@login_required
def clear_history(request):
    # ❌ Guests should not clear history
    if request.user.username == "guest":
        return redirect("history")

    ScoreHistory.objects.filter(user=request.user).delete()
    return redirect("history")


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")

        return render(request, "login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "login.html")


# ---------------- SIGNUP ----------------
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "signup.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "Username already exists"
            })

        User.objects.create_user(username=username, password=password1)
        return redirect("login")

    return render(request, "signup.html")


# ---------------- GUEST LOGIN ----------------
def guest_login(request):
    user, created = User.objects.get_or_create(username="guest")
    if created:
        user.set_unusable_password()
        user.save()

    login(request, user)
    return redirect("home")


# ---------------- AI SCORE CHECKER ----------------
@login_required
def check_score(request):
    if request.method != "POST":
        return redirect("home")

    subject = request.POST.get("subject")
    answer = request.POST.get("answer", "").lower()

    # identify guest
    is_guest = request.user.username == "guest"

    SUBJECT_KEYWORDS = {
        "Python": [
            "python", "variable", "datatype", "list", "tuple", "dictionary",
            "loop", "function", "class", "object", "inheritance", "module"
        ],
        "Java": [
            "java", "class", "object", "inheritance", "polymorphism",
            "encapsulation", "interface", "exception", "thread"
        ],
        "C Programming": [
            "c", "function", "pointer", "array", "structure",
            "loop", "if", "switch", "memory", "file"
        ],
        "C++": [
            "c++", "class", "object", "inheritance", "polymorphism",
            "template", "stl", "constructor", "destructor"
        ],
        "HTML": [
            "html", "tag", "element", "attribute", "head", "body",
            "form", "table", "link", "image", "semantic"
        ],
        "CSS": [
            "css", "selector", "property", "color", "font",
            "margin", "padding", "flex", "grid", "responsive"
        ],
        "JavaScript": [
            "javascript", "variable", "function", "event",
            "dom", "array", "object", "async", "promise"
        ],
        "SQL": [
            "sql", "select", "insert", "update", "delete",
            "where", "join", "group by", "order by", "constraint"
        ],
        "Machine Learning": [
            "machine learning", "dataset", "algorithm",
            "training", "testing", "model", "regression",
            "classification", "accuracy"
        ]
    }

    keywords = SUBJECT_KEYWORDS.get(subject, [])
    matched = sum(1 for word in keywords if word in answer)
    score = int((matched / len(keywords)) * 100) if keywords else 0

    # 🎯 Result logic
    if score < 40:
        level = "Beginner"
        feedback = f"You are just getting started in {subject}."
        bar_class = "low"
        is_perfect = False

    elif score < 70:
        level = "Intermediate"
        feedback = f"You have a fair understanding of {subject}."
        bar_class = "medium"
        is_perfect = False

    elif score < 100:
        level = "Advanced"
        feedback = f"Excellent knowledge of {subject}!"
        bar_class = "high"
        is_perfect = False

    else:  # 💯 PERFECT
        level = "Expert"
        feedback = "Outstanding! You demonstrated perfect mastery 🚀"
        bar_class = "high"
        is_perfect = True

    # 💾 SAVE HISTORY (only real users)
    if not is_guest:
        ScoreHistory.objects.create(
            user=request.user,
            subject=subject,
            score=score,
            level=level
        )

    return render(request, "result.html", {
        "subject": subject,
        "score": None if is_guest else score,
        "level": None if is_guest else level,
        "feedback": None if is_guest else feedback,
        "bar_class": bar_class,
        "is_guest": is_guest,
        "is_perfect": is_perfect
    })


# ---------------- SCORE HISTORY PAGE ----------------
@login_required
def history(request):
    scores = ScoreHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "history.html", {
        "scores": scores
    })


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("login")
