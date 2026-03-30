from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
import json, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ktu_student_manager")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

GRADE_POINTS = {
    "S": 10, "A+": 9, "A": 8.5, "B+": 8,
    "B": 7.5, "C+": 7, "C": 6.5, "D": 6,
    "P": 5.5, "F": 0
}

ACTIVITIES = {
    "GROUP_I": {
        "cap": 40, "label": "Co-curricular Activities",
        "items": {
            "1.1": ("Participation in Sports, Arts & Cultural Activities", 10),
            "1.2": ("Winners - Single Events (Sports, Arts & Cultural)", 15),
            "1.3": ("Winners - Group Events (Sports, Arts & Cultural)", 10),
            "1.4": ("College Magazine Publication", 5),
            "1.5": ("Four-Wheeler Driving License", 5),
            "1.6": ("Community Service (2 days)", 5),
            "1.7": ("Community Service (up to 1 week)", 10),
            "1.8": ("Blood Donation", 5),
            "1.9": ("THRIVE Project (Govt. of Kerala)", 20),
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
        "cap": 40, "label": "Professional Development",
        "items": {
            "2.1": ("MOOC / Online Course Completion", 15),
            "2.2": ("Paper Publication - International Journal", 30),
            "2.3": ("Paper Publication - National Journal", 20),
            "2.4": ("Paper Presentation - International Conference", 20),
            "2.5": ("Paper Presentation - National Conference", 15),
            "2.6": ("Patent Filed", 25),
            "2.7": ("Patent Granted", 40),
            "2.8": ("Industrial / Research Internship (4 weeks)", 20),
            "2.9": ("Hackathon / Coding Contest Participation", 10),
            "2.10": ("Hackathon / Coding Contest Winner", 20),
            "2.11": ("Technical Fest Participation", 5),
            "2.12": ("Technical Fest Winner", 15),
            "2.13": ("Professional Society Membership (IEEE etc.)", 10),
            "2.14": ("Workshop / Seminar / FDP Attended", 5),
            "2.15": ("Workshop / Seminar Organized", 10),
        }
    },
    "GROUP_III": {
        "cap": 40, "label": "Advanced Achievements",
        "items": {
            "3.1": ("Entrepreneurship / Startup (Registered)", 40),
            "3.2": ("Social Initiative / NGO (Founded)", 30),
            "3.3": ("Book / Chapter Publication", 30),
            "3.4": ("National Level Sports / Arts Representation", 30),
            "3.5": ("International Level Sports / Arts Representation", 40),
            "3.6": ("Government Recognized Award", 35),
            "3.7": ("GATE / CAT / GRE Score (Qualified)", 20),
            "3.8": ("Competitive Exam Rank (State/National)", 25),
            "3.9": ("Foreign Language Proficiency Certificate", 15),
            "3.10": ("Elected Student Representative (University Level)", 20),
        }
    }
}

def parse_json(data):
    return json.loads(json_util.dumps(data))

def calculate_sgpa(subjects):
    total_credits = sum(s["credits"] for s in subjects)
    total_points = sum(s["credits"] * GRADE_POINTS.get(s["grade"], 0) for s in subjects)
    return round(total_points / total_credits, 2) if total_credits else 0.0

def recalculate_activity_totals(student_id):
    record = db.activity_points.find_one({"student_id": ObjectId(student_id)})
    if not record:
        return
    group_totals = {}
    for gk, g in ACTIVITIES.items():
        raw = sum(a["points_awarded"] for a in record["activities"] if a["group"] == gk)
        group_totals[gk] = min(raw, g["cap"])
    total = sum(group_totals.values())
    is_eligible = total >= 120 and all(group_totals.get(g, 0) >= 40 for g in ACTIVITIES)
    db.activity_points.update_one(
        {"student_id": ObjectId(student_id)},
        {"$set": {"group_totals": group_totals, "total_points": total, "is_eligible": is_eligible}}
    )

# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# Students
@app.route("/api/students", methods=["GET"])
def get_students():
    students = list(db.students.find())
    return jsonify(parse_json(students))

@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.json
    if db.students.find_one({"roll_no": data["roll_no"]}):
        return jsonify({"error": f"Roll number {data['roll_no']} already exists"}), 400
    result = db.students.insert_one(data)
    return jsonify({"id": str(result.inserted_id)}), 201

@app.route("/api/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.json
    db.students.update_one({"_id": ObjectId(student_id)}, {"$set": data})
    return jsonify({"success": True})

@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    oid = ObjectId(student_id)
    db.students.delete_one({"_id": oid})
    db.grades.delete_many({"student_id": oid})
    db.activity_points.delete_many({"student_id": oid})
    return jsonify({"success": True})

# Grades
@app.route("/api/grades/<student_id>", methods=["GET"])
def get_grades(student_id):
    records = list(db.grades.find({"student_id": ObjectId(student_id)}).sort("semester", 1))
    all_subjects = []
    for r in records:
        all_subjects.extend(r["subjects"])
    cgpa = calculate_sgpa(all_subjects)
    return jsonify({"records": parse_json(records), "cgpa": cgpa})

@app.route("/api/grades", methods=["POST"])
def add_grades():
    data = request.json
    student_id = ObjectId(data["student_id"])
    semester = data["semester"]
    if db.grades.find_one({"student_id": student_id, "semester": semester}):
        return jsonify({"error": f"Grades for Semester {semester} already exist"}), 400
    subjects = data["subjects"]
    sgpa = calculate_sgpa(subjects)
    db.grades.insert_one({"student_id": student_id, "semester": semester, "subjects": subjects, "sgpa": sgpa})
    return jsonify({"sgpa": sgpa}), 201

@app.route("/api/grades/<student_id>/<int:semester>", methods=["PUT"])
def update_grade(student_id, semester):
    data = request.json
    record = db.grades.find_one({"student_id": ObjectId(student_id), "semester": semester})
    if not record:
        return jsonify({"error": "Record not found"}), 404
    subjects = record["subjects"]
    subjects[data["index"]]["grade"] = data["grade"]
    new_sgpa = calculate_sgpa(subjects)
    db.grades.update_one({"_id": record["_id"]}, {"$set": {"subjects": subjects, "sgpa": new_sgpa}})
    return jsonify({"sgpa": new_sgpa})

# Activity Points
@app.route("/api/activities", methods=["GET"])
def get_activity_list():
    result = {}
    for gk, g in ACTIVITIES.items():
        result[gk] = {
            "label": g["label"], "cap": g["cap"],
            "items": [{"code": c, "desc": d, "max": m} for c, (d, m) in g["items"].items()]
        }
    return jsonify(result)

@app.route("/api/activities/<student_id>", methods=["GET"])
def get_student_activities(student_id):
    record = db.activity_points.find_one({"student_id": ObjectId(student_id)})
    if not record:
        return jsonify({"activities": [], "group_totals": {}, "total_points": 0, "is_eligible": False})
    return jsonify(parse_json(record))

@app.route("/api/activities/<student_id>", methods=["POST"])
def add_activity(student_id):
    data = request.json
    oid = ObjectId(student_id)
    entry = {
        "group": data["group"], "activity_code": data["code"],
        "description": data["description"], "points_awarded": data["points"], "note": data.get("note", "")
    }
    existing = db.activity_points.find_one({"student_id": oid})
    if not existing:
        db.activity_points.insert_one({"student_id": oid, "activities": [entry]})
    else:
        db.activity_points.update_one({"student_id": oid}, {"$push": {"activities": entry}})
    recalculate_activity_totals(student_id)
    record = db.activity_points.find_one({"student_id": oid})
    return jsonify(parse_json(record)), 201

@app.route("/api/activities/<student_id>/<int:index>", methods=["DELETE"])
def delete_activity(student_id, index):
    oid = ObjectId(student_id)
    record = db.activity_points.find_one({"student_id": oid})
    if not record:
        return jsonify({"error": "Not found"}), 404
    activities = record["activities"]
    activities.pop(index)
    db.activity_points.update_one({"student_id": oid}, {"$set": {"activities": activities}})
    recalculate_activity_totals(student_id)
    updated = db.activity_points.find_one({"student_id": oid})
    return jsonify(parse_json(updated))

# Reports
@app.route("/api/reports/top-students", methods=["GET"])
def top_students():
    students = list(db.students.find())
    rankings = []
    for s in students:
        records = list(db.grades.find({"student_id": s["_id"]}))
        all_subjects = []
        for r in records:
            all_subjects.extend(r["subjects"])
        if all_subjects:
            rankings.append({"name": s["name"], "roll_no": s["roll_no"], "branch": s["branch"], "cgpa": calculate_sgpa(all_subjects)})
    rankings.sort(key=lambda x: x["cgpa"], reverse=True)
    return jsonify(rankings)

@app.route("/api/reports/eligibility", methods=["GET"])
def eligibility_report():
    students = list(db.students.find())
    result = []
    for s in students:
        record = db.activity_points.find_one({"student_id": s["_id"]})
        totals = record.get("group_totals", {}) if record else {}
        result.append({
            "name": s["name"], "roll_no": s["roll_no"],
            "g1": totals.get("GROUP_I", 0), "g2": totals.get("GROUP_II", 0),
            "g3": totals.get("GROUP_III", 0),
            "total": record.get("total_points", 0) if record else 0,
            "eligible": record.get("is_eligible", False) if record else False
        })
    return jsonify(result)

@app.route("/api/reports/branch-summary", methods=["GET"])
def branch_summary():
    pipeline = [{"$group": {"_id": "$branch", "count": {"$sum": 1}, "students": {"$push": {"id": "$_id", "name": "$name"}}}}, {"$sort": {"_id": 1}}]
    branches = list(db.students.aggregate(pipeline))
    result = []
    for b in branches:
        cgpas = []
        for s in b["students"]:
            records = list(db.grades.find({"student_id": s["id"]}))
            all_subs = []
            for r in records:
                all_subs.extend(r["subjects"])
            if all_subs:
                cgpas.append(calculate_sgpa(all_subs))
        result.append({"branch": b["_id"], "count": b["count"], "avg_cgpa": round(sum(cgpas)/len(cgpas), 2) if cgpas else 0, "students": [s["name"] for s in b["students"]]})
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)