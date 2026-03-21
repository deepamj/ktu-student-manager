from database.connection import get_db
from modules.students import search_student
from tabulate import tabulate

# KTU grade to grade point mapping
GRADE_POINTS = {
    "S": 10, "A+": 9, "A": 8.5, "B+": 8,
    "B": 7.5, "C+": 7, "C": 6.5, "D": 6,
    "P": 5.5, "F": 0
}

def calculate_sgpa(subjects):
    total_credits = sum(s["credits"] for s in subjects)
    total_points = sum(s["credits"] * GRADE_POINTS.get(s["grade"], 0) for s in subjects)
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)

def add_grades():
    db = get_db()
    print("\n--- Add Grades ---")
    student = search_student()
    if not student:
        return

    semester = int(input("Enter Semester number: ").strip())

    # Check if grades already exist for this semester
    existing = db.grades.find_one({
        "student_id": student["_id"],
        "semester": semester
    })
    if existing:
        print(f"❌ Grades for Semester {semester} already exist. Use 'Update Grades' instead.")
        return

    print(f"\nEntering grades for {student['name']} — Semester {semester}")
    print("Valid grades: S, A+, A, B+, B, C+, C, D, P, F")
    print("Type 'done' as subject code when finished.\n")

    subjects = []
    while True:
        code = input("Subject Code (or 'done'): ").strip().upper()
        if code == "DONE":
            break
        name = input("Subject Name: ").strip()
        credits = int(input("Credits: ").strip())
        grade = input("Grade: ").strip().upper()

        while grade not in GRADE_POINTS:
            print(f"❌ Invalid grade. Choose from: {', '.join(GRADE_POINTS.keys())}")
            grade = input("Grade: ").strip().upper()

        subjects.append({
            "code": code,
            "name": name,
            "credits": credits,
            "grade": grade
        })
        print(f"✅ Added {name}\n")

    if not subjects:
        print("No subjects entered. Cancelled.")
        return

    sgpa = calculate_sgpa(subjects)

    db.grades.insert_one({
        "student_id": student["_id"],
        "semester": semester,
        "subjects": subjects,
        "sgpa": sgpa
    })

    print(f"\n✅ Grades saved! SGPA for Semester {semester}: {sgpa}")

def view_grades():
    db = get_db()
    print("\n--- View Grades ---")
    student = search_student()
    if not student:
        return

    records = list(db.grades.find(
        {"student_id": student["_id"]}
    ).sort("semester", 1))

    if not records:
        print(f"⚠️  No grades found for {student['name']}.")
        return

    print(f"\n📋 Grade Report — {student['name']} ({student['roll_no']})")

    all_subjects = []
    sgpa_summary = []

    for record in records:
        print(f"\n  Semester {record['semester']} | SGPA: {record['sgpa']}")
        table = [
            [s["code"], s["name"], s["credits"], s["grade"],
             GRADE_POINTS.get(s["grade"], 0)]
            for s in record["subjects"]
        ]
        print(tabulate(table,
            headers=["Code", "Subject", "Credits", "Grade", "Grade Points"],
            tablefmt="grid"))
        sgpa_summary.append([record["semester"], record["sgpa"]])
        all_subjects.extend(record["subjects"])

    # Calculate CGPA
    cgpa = calculate_sgpa(all_subjects)
    print(f"\n{'='*40}")
    print(tabulate(sgpa_summary, headers=["Semester", "SGPA"], tablefmt="simple"))
    print(f"\n🎓 Overall CGPA: {cgpa}")
    print(f"{'='*40}")

def update_grades():
    db = get_db()
    print("\n--- Update Grades ---")
    student = search_student()
    if not student:
        return

    semester = int(input("Enter Semester number to update: ").strip())
    record = db.grades.find_one({
        "student_id": student["_id"],
        "semester": semester
    })

    if not record:
        print(f"❌ No grades found for Semester {semester}. Add them first.")
        return

    print(f"\nUpdating Semester {semester} grades for {student['name']}")
    print("Current subjects:")

    table = [[i+1, s["code"], s["name"], s["credits"], s["grade"]]
             for i, s in enumerate(record["subjects"])]
    print(tabulate(table,
        headers=["#", "Code", "Subject", "Credits", "Grade"],
        tablefmt="grid"))

    idx = int(input("\nEnter subject number to update grade: ")) - 1
    subject = record["subjects"][idx]

    print(f"Current grade for {subject['name']}: {subject['grade']}")
    new_grade = input("New grade: ").strip().upper()

    while new_grade not in GRADE_POINTS:
        print(f"❌ Invalid grade. Choose from: {', '.join(GRADE_POINTS.keys())}")
        new_grade = input("New grade: ").strip().upper()

    record["subjects"][idx]["grade"] = new_grade
    new_sgpa = calculate_sgpa(record["subjects"])

    db.grades.update_one(
        {"_id": record["_id"]},
        {"$set": {
            "subjects": record["subjects"],
            "sgpa": new_sgpa
        }}
    )

    print(f"✅ Grade updated! New SGPA for Semester {semester}: {new_sgpa}")