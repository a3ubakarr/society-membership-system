from flask import Blueprint, render_template, request, redirect, session
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import random
import os
import time

from ..models.member_model import (
    add_member,
    delete_member,
    find_by_student_id,
    find_by_society,
    update_member,
    count_members_by_society
)

member_bp = Blueprint("member", __name__)

# ================= CONSTANTS =================

SOCIETIES = [
    "UMT IEEE",
    "UMT ACM",
    "UMT CSS",
    "UMT IEEE-WIE",
    "UMT Robotics",
    "UMT Cybersecurity"
]

POSITIONS = [
    "Volunteer",
    "President",
    "Vice President",
    "Vice President Female",
    "Treasurer",
    "General Secretary",
    "Media Secretary"
]

POSITION_PRIORITY = {
    "President": 1,
    "Vice President": 2,
    "Vice President Female": 3,
    "General Secretary": 4,
    "Treasurer": 5,
    "Media Secretary": 6,
    "Volunteer": 7
}

# ================= GRAPH FUNCTION =================

def generate_members_graph():
    data = count_members_by_society()

    # DB → dict
    db_counts = {row[0]: row[1] for row in data}

    # FIXED societies (X-axis never changes)
    societies = SOCIETIES
    counts = [db_counts.get(s, 0) for s in societies]

    colors = [
        "#" + "".join(random.choices("0123456789ABCDEF", k=6))
        for _ in societies
    ]

    plt.figure(figsize=(9, 5))
    bars = plt.bar(societies, counts, color=colors)

    plt.xlabel("Society Name")
    plt.ylabel("Number of Student Members")
    plt.title("Society-wise Members Graph")
    plt.xticks(rotation=30)

    ax = plt.gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Optional: show values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            str(int(height)),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig("app/static/members_graph.png")
    plt.close()

# ================= HOME ROUTE =================

@member_bp.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/")

    message = ""
    message_type = ""

    if request.method == "POST":
        action = request.form.get("action")

        # ---------- ADD ----------
        if action == "add":
            data = (
                request.form["first_name"],
                request.form["last_name"],
                request.form["gender"],
                request.form["student_id"],
                request.form["society"],
                request.form["date_joined"],
                request.form["position"]
            )
            try:
                add_member(data)
                message = "Member added successfully"
                message_type = "success"
            except Exception as e:
                message = str(e)
                message_type = "error"

        # ---------- FIND BY ID ----------
        elif action == "find_id":
            session["results"] = find_by_student_id(
                request.form["student_id"]
            )

        # ---------- FIND BY SOCIETY ----------
        elif action == "find_society":
            session["results"] = find_by_society(
                request.form["society"]
            )

        # ---------- UPDATE ----------
        elif action == "update":
            student_id = request.form["student_id"]
            data = (
                request.form["first_name"],
                request.form["last_name"],
                request.form["gender"],
                request.form["society"],
                request.form["date_joined"],
                request.form["position"]
            )
            try:
                update_member(student_id, data)
                message = "Member updated successfully"
                message_type = "success"
            except Exception as e:
                message = str(e)
                message_type = "error"

        # ---------- DELETE ----------
        elif action == "delete":
            try:
                delete_member(request.form["student_id"])
                message = "Member deleted successfully"
                message_type = "success"
            except Exception as e:
                message = str(e)
                message_type = "error"

        # ---------- SORT ----------
        elif action == "sort":
            results = session.get("results", [])
            sort_by = request.form.get("sort_by")

            if sort_by == "gender":
                results.sort(key=lambda x: 0 if x[3].lower() == "female" else 1)
            elif sort_by == "position_asc":
                results.sort(key=lambda x: POSITION_PRIORITY.get(x[7], 99))
            elif sort_by == "position_desc":
                results.sort(
                    key=lambda x: POSITION_PRIORITY.get(x[7], 99),
                    reverse=True
                )

            session["results"] = results

    # 🔥 GRAPH ALWAYS REGENERATES
    generate_members_graph()

    return render_template(
        "home.html",
        societies=SOCIETIES,
        positions=POSITIONS,
        results=session.get("results", []),
        message=message,
        message_type=message_type,
        graph_ts=int(time.time())
    )
