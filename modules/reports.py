from database.connection import get_db
from modules.grades import calculate_sgpa
from tabulate import tabulate

def report_top_students():
    db = get_db()
    print("\n--- 🏆 Top Students by CGPA ---")

    students = list(db.students.find())
    if not students:
        print("⚠️  No students found.")
        return

    rankings = []
    for student in students:
        grade_records = list(db.grades.find({"student_id": student["_id"]}))
        if not grade_records:
            continue

        all_subjects = []
        for record in grade_records:
            all_subjects.extend(record["subjects"])

        cgpa = calculate_sgpa(all_subjects)
        rankings.append([
            student["name"],
            student["roll_no"],
            student["branch"],
            cgpa
        ])

    if not rankings:
        print("⚠️  No grade data available yet.")
        return

    # Sort by CGPA descending
    rankings.sort(key=lambda x: x[3], reverse=True)

    # Add rank column
    ranked = [[i+1] + row for i, row in enumerate(rankings)]

    print(tabulate(ranked,
        headers=["Rank", "Name", "Roll No", "Branch", "CGPA"],
        tablefmt="grid"))

def report_activity_eligibility():
    db = get_db()
    print("\n--- 📋 Activity Points Eligibility Report ---")

    students = list(db.students.find())
    if not students:
        print("⚠️  No students found.")
        return

    eligible = []
    not_eligible = []

    for student in students:
        record = db.activity_points.find_one({"student_id": student["_id"]})
        if not record:
            not_eligible.append([
                student["name"],
                student["roll_no"],
                0, 0, 0, 0,
                "No data"
            ])
            continue

        totals = record.get("group_totals", {})
        total = record.get("total_points", 0)
        is_eligible = record.get("is_eligible", False)

        row = [
            student["name"],
            student["roll_no"],
            totals.get("GROUP_I", 0),
            totals.get("GROUP_II", 0),
            totals.get("GROUP_III", 0),
            total,
            "✅ Eligible" if is_eligible else "❌ Not Yet"
        ]

        if is_eligible:
            eligible.append(row)
        else:
            not_eligible.append(row)

    headers = ["Name", "Roll No", "Grp I", "Grp II", "Grp III", "Total", "Status"]

    if eligible:
        print("\n  ✅ Eligible Students:")
        print(tabulate(eligible, headers=headers, tablefmt="grid"))

    if not_eligible:
        print("\n  ❌ Not Yet Eligible:")
        print(tabulate(not_eligible, headers=headers, tablefmt="grid"))

    print(f"\n  Summary: {len(eligible)} eligible / {len(not_eligible)} not yet eligible")

def report_semester_performance():
    db = get_db()
    print("\n--- 📈 Semester-wise Performance Report ---")

    students = list(db.students.find())
    if not students:
        print("⚠️  No students found.")
        return

    for student in students:
        grade_records = list(db.grades.find(
            {"student_id": student["_id"]}
        ).sort("semester", 1))

        if not grade_records:
            continue

        print(f"\n  👤 {student['name']} ({student['roll_no']})")

        rows = []
        all_subjects = []
        for record in grade_records:
            all_subjects.extend(record["subjects"])
            fail_count = sum(
                1 for s in record["subjects"] if s["grade"] == "F"
            )
            rows.append([
                f"Semester {record['semester']}",
                record["sgpa"],
                len(record["subjects"]),
                fail_count
            ])

        cgpa = calculate_sgpa(all_subjects)
        print(tabulate(rows,
            headers=["Semester", "SGPA", "Subjects", "Fails"],
            tablefmt="simple"))
        print(f"  CGPA: {cgpa}")

def report_branch_summary():
    db = get_db()
    print("\n--- 🏫 Branch-wise Summary Report ---")

    pipeline = [
        {
            "$group": {
                "_id": "$branch",
                "count": {"$sum": 1},
                "students": {"$push": {"id": "$_id", "name": "$name"}}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    branches = list(db.students.aggregate(pipeline))
    if not branches:
        print("⚠️  No students found.")
        return

    for branch in branches:
        branch_name = branch["_id"]
        count = branch["count"]
        student_ids = [s["id"] for s in branch["students"]]

        # Calculate average CGPA for the branch
        cgpas = []
        for sid in student_ids:
            records = list(db.grades.find({"student_id": sid}))
            if records:
                all_subjects = []
                for r in records:
                    all_subjects.extend(r["subjects"])
                cgpas.append(calculate_sgpa(all_subjects))

        avg_cgpa = round(sum(cgpas) / len(cgpas), 2) if cgpas else "N/A"

        print(f"\n  🔹 {branch_name} — {count} student(s) | Avg CGPA: {avg_cgpa}")

        table = [[s["name"]] for s in branch["students"]]
        print(tabulate(table, headers=["Students"], tablefmt="simple"))