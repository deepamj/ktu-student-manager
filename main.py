from database.connection import get_db, close_db
from modules import students, grades, activity_points, reports

def students_menu():
    while True:
        print("""
╔══════════════════════════════╗
║       STUDENT MANAGEMENT     ║
╠══════════════════════════════╣
║  1. Add Student              ║
║  2. View All Students        ║
║  3. Search Student           ║
║  4. Update Student           ║
║  5. Delete Student           ║
║  0. Back                     ║
╚══════════════════════════════╝""")
        choice = input("Choose: ").strip()
        if choice == "1":
            students.add_student()
        elif choice == "2":
            students.view_all_students()
        elif choice == "3":
            students.search_student(display=True)
        elif choice == "4":
            students.update_student()
        elif choice == "5":
            students.delete_student()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")

def grades_menu():
    while True:
        print("""
╔══════════════════════════════╗
║       GRADES MANAGEMENT      ║
╠══════════════════════════════╣
║  1. Add Grades               ║
║  2. View Grades & CGPA       ║
║  3. Update a Grade           ║
║  0. Back                     ║
╚══════════════════════════════╝""")
        choice = input("Choose: ").strip()
        if choice == "1":
            grades.add_grades()
        elif choice == "2":
            grades.view_grades()
        elif choice == "3":
            grades.update_grades()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")

def activity_menu():
    while True:
        print("""
╔══════════════════════════════╗
║     ACTIVITY POINTS          ║
╠══════════════════════════════╣
║  1. Add Activity             ║
║  2. View Points & Eligibility║
║  3. Delete Activity Entry    ║
║  0. Back                     ║
╚══════════════════════════════╝""")
        choice = input("Choose: ").strip()
        if choice == "1":
            activity_points.add_activity()
        elif choice == "2":
            activity_points.view_activity_points()
        elif choice == "3":
            activity_points.delete_activity()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")

def reports_menu():
    while True:
        print("""
╔══════════════════════════════╗
║          REPORTS             ║
╠══════════════════════════════╣
║  1. Top Students by CGPA     ║
║  2. Activity Eligibility     ║
║  3. Semester Performance     ║
║  4. Branch Summary           ║
║  0. Back                     ║
╚══════════════════════════════╝""")
        choice = input("Choose: ").strip()
        if choice == "1":
            reports.report_top_students()
        elif choice == "2":
            reports.report_activity_eligibility()
        elif choice == "3":
            reports.report_semester_performance()
        elif choice == "4":
            reports.report_branch_summary()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")

def main():
    print("\n✅ Connected to MongoDB successfully.")
    get_db()  # initialize connection

    while True:
        print("""
╔══════════════════════════════╗
║   KTU STUDENT MANAGER        ║
╠══════════════════════════════╣
║  1. Student Management       ║
║  2. Grades Management        ║
║  3. Activity Points          ║
║  4. Reports                  ║
║  0. Exit                     ║
╚══════════════════════════════╝""")
        choice = input("Choose: ").strip()
        if choice == "1":
            students_menu()
        elif choice == "2":
            grades_menu()
        elif choice == "3":
            activity_menu()
        elif choice == "4":
            reports_menu()
        elif choice == "0":
            close_db()
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
