from database.connection import get_db
from bson.objectid import ObjectId
from tabulate import tabulate

def add_student():
    db = get_db()
    print("\n--- Add New Student ---")
    name = input("Full Name: ").strip()
    roll_no = input("Roll Number (e.g. TVM22CS001): ").strip()
    
    # Check for duplicate roll number
    if db.students.find_one({"roll_no": roll_no}):
        print(f"❌ Student with roll number {roll_no} already exists.")
        return

    semester = int(input("Current Semester (1-8): ").strip())
    branch = input("Branch (e.g. CSE): ").strip().upper()
    
    print("Student Type: 1. Regular  2. Lateral Entry  3. PwD")
    type_choice = input("Choose (1/2/3): ").strip()
    type_map = {"1": "regular", "2": "lateral", "3": "pwd"}
    student_type = type_map.get(type_choice, "regular")

    student = {
        "name": name,
        "roll_no": roll_no,
        "semester": semester,
        "branch": branch,
        "type": student_type
    }

    result = db.students.insert_one(student)
    print(f"✅ Student '{name}' added successfully! (ID: {result.inserted_id})")

def view_all_students():
    db = get_db()
    students = list(db.students.find())
    if not students:
        print("\n⚠️  No students found.")
        return

    table = []
    for s in students:
        table.append([
            str(s["_id"]),
            s["name"],
            s["roll_no"],
            s["semester"],
            s["branch"],
            s["type"].capitalize()
        ])

    headers = ["ID", "Name", "Roll No", "Sem", "Branch", "Type"]
    print("\n--- All Students ---")
    print(tabulate(table, headers=headers, tablefmt="grid"))

def search_student(display=False):
    db = get_db()
    print("\n--- Search Student ---")
    query = input("Enter Name or Roll Number: ").strip()
    results = list(db.students.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"roll_no": {"$regex": query, "$options": "i"}}
        ]
    }))

    if not results:
        print("❌ No matching students found.")
        return None

    if len(results) == 1:
        if display:
            table = [[
                str(results[0]["_id"]),
                results[0]["name"],
                results[0]["roll_no"],
                results[0]["semester"],
                results[0]["branch"],
                results[0]["type"].capitalize()
            ]]
            headers = ["ID", "Name", "Roll No", "Sem", "Branch", "Type"]
            print(tabulate(table, headers=headers, tablefmt="grid"))
        return results[0]
    # Multiple results — let user pick
    table = [[i+1, s["name"], s["roll_no"], s["branch"]] for i, s in enumerate(results)]
    print(tabulate(table, headers=["#", "Name", "Roll No", "Branch"], tablefmt="grid"))
    choice = int(input("Select student number: ")) - 1
    return results[choice]

def update_student():
    db = get_db()
    print("\n--- Update Student ---")
    student = search_student()
    if not student:
        return

    print(f"\nEditing: {student['name']} ({student['roll_no']})")
    print("Leave blank to keep current value.\n")

    name = input(f"Name [{student['name']}]: ").strip() or student["name"]
    semester = input(f"Semester [{student['semester']}]: ").strip()
    semester = int(semester) if semester else student["semester"]
    branch = input(f"Branch [{student['branch']}]: ").strip().upper() or student["branch"]

    db.students.update_one(
        {"_id": student["_id"]},
        {"$set": {"name": name, "semester": semester, "branch": branch}}
    )
    print("✅ Student updated successfully!")

def delete_student():
    db = get_db()
    print("\n--- Delete Student ---")
    student = search_student()
    if not student:
        return

    confirm = input(f"⚠️  Delete '{student['name']}' and ALL their data? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    db.students.delete_one({"_id": student["_id"]})
    db.grades.delete_many({"student_id": student["_id"]})
    db.activity_points.delete_many({"student_id": student["_id"]})
    print(f"✅ Student '{student['name']}' and all related data deleted.")