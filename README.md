# 🎓 KTU Student Manager

A command-line application built with **Python** and **MongoDB** to manage KTU student academic records and activity points.

Micro Project for DBMS(KTU S4 CSE).

---

## 📌 Features

- Add, view, search, update and delete students
- Record semester-wise grades and auto-calculate SGPA & CGPA
- Track KTU Activity Points across all 3 groups (2024 Scheme)
- Enforces group caps (40 pts per group) and eligibility rules (120 pts total)
- Reports: Top students by CGPA, activity eligibility, semester performance, branch summary

---

## 🛠️ Tech Stack

| Layer      | Technology        |
|------------|-------------------|
| Language   | Python 3.13       |
| Database   | MongoDB 8.2       |
| Driver     | PyMongo           |
| CLI Tables | Tabulate          |
| Config     | python-dotenv     |

---

## 📁 Folder Structure
```
ktu-student-manager/
├── database/
│   └── connection.py        # MongoDB connection setup
├── modules/
│   ├── students.py          # Student CRUD operations
│   ├── grades.py            # Grade management & SGPA/CGPA calculation
│   ├── activity_points.py   # KTU activity points tracking
│   └── reports.py           # Aggregated reports & queries
├── .env                     # MongoDB connection string (not pushed to GitHub)
├── .gitignore
├── main.py                  # Entry point — main menu
├── README.md
└── requirements.txt
```

---

## 🗄️ Database Schema

### Collection: `students`
```json
{
  "_id": "ObjectId",
  "name": "Deepam J",
  "roll_no": "TVE24CS008",
  "semester": 4,
  "branch": "CSE",
  "type": "regular"
}
```

### Collection: `grades`
```json
{
  "student_id": "ObjectId",
  "semester": 4,
  "subjects": [
    { "code": "CST202", "name": "DBMS", "credits": 4, "grade": "A+" }
  ],
  "sgpa": 9.2
}
```

### Collection: `activity_points`
```json
{
  "student_id": "ObjectId",
  "activities": [
    {
      "group": "GROUP_I",
      "activity_code": "1.8",
      "description": "Blood Donation",
      "points_awarded": 5,
      "note": "March 2025"
    }
  ],
  "group_totals": { "GROUP_I": 25, "GROUP_II": 40, "GROUP_III": 15 },
  "total_points": 80,
  "is_eligible": false
}
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.13
- MongoDB Community Server
- Git

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/your-username/ktu-student-manager.git
cd ktu-student-manager
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create your `.env` file**
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=ktu_student_manager
```

**5. Run the application**
```bash
python main.py
```

---

## 📊 MongoDB Concepts Demonstrated

| Concept | Where Used |
|---|---|
| Document model & collections | students, grades, activity_points |
| CRUD operations | All modules |
| Embedded documents | subjects array inside grades |
| Referenced documents | student_id linking across collections |
| Aggregation pipeline | Branch summary report |
| Regex queries | Student search by name or roll number |
| Cascade delete | Deleting a student removes grades & activity data |

---

## 🎯 KTU Activity Points Rules (2024 Scheme)

- Regular B.Tech students require **120 total points**
- Minimum **40 points per group**
- 3 Groups:
  - **Group I** — Co-curricular Activities
  - **Group II** — Professional Development
  - **Group III** — Advanced Achievements
- Group caps are automatically enforced by the application

---

## 📷 Sample Output
```
╔══════════════════════════════╗
║   KTU STUDENT MANAGER        ║
╠══════════════════════════════╣
║  1. Student Management       ║
║  2. Grades Management        ║
║  3. Activity Points          ║
║  4. Reports                  ║
║  0. Exit                     ║
╚══════════════════════════════╝

✅ Eligibility Summary
═══════════════════════════════════════════════
  Group         Points   Requirement
  ✅ GROUP_I      40      / 40 (min 40)
  ✅ GROUP_II     40      / 40 (min 40)
  ❌ GROUP_III    15      / 40 (min 40)
  ❌ TOTAL        95      / 120
═══════════════════════════════════════════════
  ⚠️  NOT YET ELIGIBLE. Keep adding activities.
```

---

## 👤 Author

**deepamj**
Micro Project — Database Management Systems

---

## 📄 License

This project is open source and available