from database.connection import get_db
from modules.students import search_student
from tabulate import tabulate

# KTU Activity Points structure (2024 Scheme)
ACTIVITIES = {
    "GROUP_I": {
        "cap": 40,
        "label": "Co-curricular Activities",
        "items": {
            "1.1":  ("Participation in Sports, Arts & Cultural Activities", 10),
            "1.2":  ("Winners - Single Events (Sports, Arts & Cultural)", 15),
            "1.3":  ("Winners - Group Events (Sports, Arts & Cultural)", 10),
            "1.4":  ("College Magazine Publication", 5),
            "1.5":  ("Four-Wheeler Driving License", 5),
            "1.6":  ("Community Service (2 days)", 5),
            "1.7":  ("Community Service (up to 1 week)", 10),
            "1.8":  ("Blood Donation", 5),
            "1.9":  ("THRIVE Project (Govt. of Kerala)", 20),
            "1.10": ("Tree Planting (Geo-tagged)", 5),
            "1.11": ("NSS Volunteer (2 years)", 30),
            "1.12": ("University Leadership Camp (100 hours)", 20),
            "1.13": ("Winners - State NSS Events", 15),
            "1.14": ("Special Service / Appreciation Certificate", 40),
            "1.15": ("State / National Awards", 40),
            "1.16": ("Approved National Camps / NIC / NYF", 15),
            "1.17": ("10-Day Volunteer Service (50 hours)", 15),
            "1.18": ("RDC / IDC / International Events", 25),
            "1.19": ("NCC Certificates", 30),
            "1.20": ("First Aid / CPR / Fire Safety Training", 10),
            "1.21": ("Swimming Proficiency", 5),
        }
    },
    "GROUP_II": {
        "cap": 40,
        "label": "Professional Development",
        "items": {
            "2.1":  ("MOOC / Online Course Completion", 15),
            "2.2":  ("Paper Publication - International Journal", 30),
            "2.3":  ("Paper Publication - National Journal", 20),
            "2.4":  ("Paper Presentation - International Conference", 20),
            "2.5":  ("Paper Presentation - National Conference", 15),
            "2.6":  ("Patent Filed", 25),
            "2.7":  ("Patent Granted", 40),
            "2.8":  ("Industrial / Research Internship (4 weeks)", 20),
            "2.9":  ("Hackathon / Coding Contest Participation", 10),
            "2.10": ("Hackathon / Coding Contest Winner", 20),
            "2.11": ("Technical Fest Participation", 5),
            "2.12": ("Technical Fest Winner", 15),
            "2.13": ("Professional Society Membership (IEEE etc.)", 10),
            "2.14": ("Workshop / Seminar / FDP Attended", 5),
            "2.15": ("Workshop / Seminar Organized", 10),
        }
    },
    "GROUP_III": {
        "cap": 40,
        "label": "Advanced Achievements",
        "items": {
            "3.1":  ("Entrepreneurship / Startup (Registered)", 40),
            "3.2":  ("Social Initiative / NGO (Founded)", 30),
            "3.3":  ("Book / Chapter Publication", 30),
            "3.4":  ("National Level Sports / Arts Representation", 30),
            "3.5":  ("International Level Sports / Arts Representation", 40),
            "3.6":  ("Government Recognized Award", 35),
            "3.7":  ("GATE / CAT / GRE Score (Qualified)", 20),
            "3.8":  ("Competitive Exam Rank (State/National)", 25),
            "3.9":  ("Foreign Language Proficiency Certificate", 15),
            "3.10": ("Elected Student Representative (University Level)", 20),
        }
    }
}

REQUIRED_TOTAL = 120
REQUIRED_PER_GROUP = 40

def display_activities_menu():
    """Print all available activities grouped."""
    for group_key, group in ACTIVITIES.items():
        print(f"\n  📂 {group_key} — {group['label']} (Max: {group['cap']} pts)")
        table = [
            [code, desc, pts]
            for code, (desc, pts) in group["items"].items()
        ]
        print(tabulate(table,
            headers=["Code", "Activity", "Max Points"],
            tablefmt="simple"))

def get_group_for_code(code):
    """Find which group an activity code belongs to."""
    for group_key, group in ACTIVITIES.items():
        if code in group["items"]:
            return group_key
    return None

def add_activity():
    db = get_db()
    print("\n--- Add Activity Points ---")
    student = search_student()
    if not student:
        return

    display_activities_menu()

    code = input("\nEnter Activity Code (e.g. 1.2, 2.9): ").strip()
    group_key = get_group_for_code(code)

    if not group_key:
        print("❌ Invalid activity code.")
        return

    desc, max_pts = ACTIVITIES[group_key]["items"][code]
    print(f"\nSelected: {desc}")
    print(f"Maximum points for this activity: {max_pts}")

    points = int(input(f"Points awarded (1 - {max_pts}): ").strip())
    if points < 1 or points > max_pts:
        print(f"❌ Points must be between 1 and {max_pts}.")
        return

    note = input("Note (e.g. 'University level', 'NPTEL 12 weeks'): ").strip()

    activity_entry = {
        "group": group_key,
        "activity_code": code,
        "description": desc,
        "points_awarded": points,
        "note": note
    }

    # Get or create the student's activity record
    record = db.activity_points.find_one({"student_id": student["_id"]})

    if not record:
        db.activity_points.insert_one({
            "student_id": student["_id"],
            "activities": [activity_entry],
        })
    else:
        db.activity_points.update_one(
            {"student_id": student["_id"]},
            {"$push": {"activities": activity_entry}}
        )

    # Recalculate totals
    _recalculate_totals(db, student["_id"])
    print(f"✅ Activity added successfully!")
    _show_eligibility(db, student)

def view_activity_points():
    db = get_db()
    print("\n--- View Activity Points ---")
    student = search_student()
    if not student:
        return

    record = db.activity_points.find_one({"student_id": student["_id"]})
    if not record or not record.get("activities"):
        print(f"⚠️  No activity points recorded for {student['name']}.")
        return

    print(f"\n📋 Activity Points — {student['name']} ({student['roll_no']})")

    for group_key, group in ACTIVITIES.items():
        group_activities = [
            a for a in record["activities"] if a["group"] == group_key
        ]
        if not group_activities:
            continue

        cap = group["cap"]
        group_total = record.get("group_totals", {}).get(group_key, 0)
        print(f"\n  📂 {group_key} — {group['label']}")

        table = [
            [a["activity_code"], a["description"][:45],
             a["points_awarded"], a.get("note", "")]
            for a in group_activities
        ]
        print(tabulate(table,
            headers=["Code", "Activity", "Points", "Note"],
            tablefmt="grid"))
        print(f"  Group Total: {group_total} / {cap} pts")

    _show_eligibility(db, student)

def delete_activity():
    db = get_db()
    print("\n--- Delete Activity Entry ---")
    student = search_student()
    if not student:
        return

    record = db.activity_points.find_one({"student_id": student["_id"]})
    if not record or not record.get("activities"):
        print("⚠️  No activities found.")
        return

    table = [
        [i+1, a["activity_code"], a["description"][:40],
         a["points_awarded"], a.get("note", "")]
        for i, a in enumerate(record["activities"])
    ]
    print(tabulate(table,
        headers=["#", "Code", "Activity", "Points", "Note"],
        tablefmt="grid"))

    idx = int(input("\nEnter entry number to delete: ")) - 1
    if idx < 0 or idx >= len(record["activities"]):
        print("❌ Invalid selection.")
        return

    removed = record["activities"].pop(idx)
    db.activity_points.update_one(
        {"student_id": student["_id"]},
        {"$set": {"activities": record["activities"]}}
    )

    _recalculate_totals(db, student["_id"])
    print(f"✅ Removed: {removed['description']} ({removed['points_awarded']} pts)")
    _show_eligibility(db, student)

def _recalculate_totals(db, student_id):
    """Recalculate group totals and overall total, enforcing caps."""
    record = db.activity_points.find_one({"student_id": student_id})
    if not record:
        return

    group_totals = {}
    for group_key, group in ACTIVITIES.items():
        raw = sum(
            a["points_awarded"]
            for a in record["activities"]
            if a["group"] == group_key
        )
        group_totals[group_key] = min(raw, group["cap"])  # enforce cap

    total = sum(group_totals.values())
    is_eligible = (
        total >= REQUIRED_TOTAL and
        all(group_totals.get(g, 0) >= REQUIRED_PER_GROUP for g in ACTIVITIES)
    )

    db.activity_points.update_one(
        {"student_id": student_id},
        {"$set": {
            "group_totals": group_totals,
            "total_points": total,
            "is_eligible": is_eligible
        }}
    )

def _show_eligibility(db, student):
    """Print a summary eligibility box for the student."""
    record = db.activity_points.find_one({"student_id": student["_id"]})
    if not record:
        return

    totals = record.get("group_totals", {})
    total = record.get("total_points", 0)
    eligible = record.get("is_eligible", False)

    print(f"\n{'='*45}")
    print(f"  Eligibility Summary — {student['name']}")
    print(f"{'='*45}")

    rows = []
    for group_key, group in ACTIVITIES.items():
        pts = totals.get(group_key, 0)
        status = "✅" if pts >= REQUIRED_PER_GROUP else "❌"
        rows.append([f"{status} {group_key}", pts, f"/ {group['cap']} (min {REQUIRED_PER_GROUP})"])

    total_status = "✅" if total >= REQUIRED_TOTAL else "❌"
    rows.append([f"{total_status} TOTAL", total, f"/ {REQUIRED_TOTAL}"])

    print(tabulate(rows, headers=["Group", "Points", "Requirement"], tablefmt="simple"))

    if eligible:
        print("\n  🎉 ELIGIBLE for Activity Points clearance!")
    else:
        print("\n  ⚠️  NOT YET ELIGIBLE. Keep adding activities.")
    print(f"{'='*45}")