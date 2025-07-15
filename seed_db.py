from app import app, User, db, Course, Subject, CollegeFee
import random
from werkzeug.security import generate_password_hash
# import os
from datetime import datetime
import traceback


course_data = {
        "Computer Science": {
            "1": ["Mathematics-I", "C Programming", "Physics", "Basic Electrical", "Engineering Mechanics"],
            "2": ["Mathematics-II", "Data Structures", "Digital Logic", "Chemistry", "Environmental Studies"],
            "3": ["Discrete Mathematics", "OOP with Java", "Computer Organization", "Operating Systems", "DBMS"],
            "4": ["Theory of Computation", "Algorithms", "Microprocessors", "Software Engineering", "Probability & Stats"],
            "5": ["Compiler Design", "Computer Networks", "Web Tech", "Machine Learning", "Unix Programming"],
            "6": ["Data Mining", "Cloud Computing", "AI", "Mobile App Dev", "IoT"],
            "7": ["Project Phase I", "Seminar", "Elective I"],
            "8": ["Project Phase II", "Internship", "Elective II"]
        },
        "Electronics & Communication": {
            "1": ["Mathematics-I", "Engineering Physics", "Basic Electronics", "Problem Solving", "Mechanics"],
            "2": ["Mathematics-II", "Signals & Systems", "Network Analysis", "Digital Electronics", "Python"],
            "3": ["Analog Electronics", "Electromagnetics", "Control Systems", "Probability", "OOP"],
            "4": ["Microcontrollers", "Communication Theory", "Linear ICs", "Analog Comm", "DSP"],
            "5": ["VLSI Design", "Digital Comm", "Antenna Theory", "Verilog HDL", "Instrumentation"],
            "6": ["Wireless Comm", "Embedded Systems", "Optical Comm", "RTOS", "IoT"],
            "7": ["Project Phase I", "Seminar", "Elective I"],
            "8": ["Project Phase II", "Internship", "Elective II"]
        },
        "Aeronautical": {
            "1": ["Mathematics-I", "Engineering Mechanics", "Physics", "Intro to Aero", "Graphics"],
            "2": ["Mathematics-II", "Thermodynamics", "Materials", "CAD", "Workshop Practice"],
            "3": ["Fluid Mechanics", "Aero Structures-I", "Propulsion-I", "Flight Mechanics", "Instrumentation"],
            "4": ["Aero Structures-II", "Propulsion-II", "Avionics", "Control Engineering", "Wind Tunnel"],
            "5": ["Aircraft Design", "Flight Dynamics", "Vibration Analysis", "CFD", "Aero Materials"],
            "6": ["Space Mechanics", "UAV Design", "Gas Dynamics", "Rocket Propulsion", "Simulations"],
            "7": ["Project Phase I", "Seminar", "Elective I"],
            "8": ["Project Phase II", "Internship", "Elective II"]
        },
        "Mechanical": {
            "1": ["Mathematics-I", "Engineering Physics", "Mechanics", "Workshop", "Engineering Drawing"],
            "2": ["Mathematics-II", "Thermodynamics", "Fluid Mechanics", "Materials", "Python"],
            "3": ["Machine Drawing", "Kinematics", "Mechanics of Materials", "Manufacturing Process", "Metrology"],
            "4": ["Dynamics", "CAD/CAM", "IC Engines", "Theory of Machines", "Heat Transfer"],
            "5": ["Machine Design", "Hydraulics", "Refrigeration", "Robotics", "Industrial Management"],
            "6": ["Automobile", "Power Plant", "Finite Element", "Additive Manufacturing", "Control Engineering"],
            "7": ["Project Phase I", "Seminar", "Elective I"],
            "8": ["Project Phase II", "Internship", "Elective II"]
        },
        "Civil": {
            "1": ["Mathematics-I", "Engineering Mechanics", "Geology", "Surveying", "Physics"],
            "2": ["Mathematics-II", "Building Materials", "Fluid Mechanics", "Strength of Materials", "Environmental Studies"],
            "3": ["Structural Analysis", "Concrete Tech", "Transportation", "Hydrology", "Soil Mechanics"],
            "4": ["Steel Structures", "Construction Mgmt", "Foundation Engineering", "CAD", "Survey Project"],
            "5": ["Bridge Design", "Irrigation", "Structural Design", "Prestressed Concrete", "Waste Mgmt"],
            "6": ["Estimation", "Advanced Foundation", "Earthquake Engg", "Tunneling", "Environmental Engg"],
            "7": ["Project Phase I", "Seminar", "Elective I"],
            "8": ["Project Phase II", "Internship", "Elective II"]
        },
        "Biomedical": {
            "1": ["Mathematics-I", "Human Anatomy", "Engineering Physics", "Biochemistry", "Intro to BM"],
            "2": ["Mathematics-II", "Digital Electronics", "Physiology", "Medical Instrumentation", "Chemistry"],
            "3": ["Signals", "Biofluid Mechanics", "Analog Electronics", "Sensors", "Human Psychology"],
            "4": ["Control Systems", "Imaging Techniques", "DSP", "Pathology", "Pharmacology"],
            "5": ["Radiology", "Biomedical Equipments", "Rehabilitation", "Diagnostic Tools", "Surgery Tech"],
            "6": ["Telemedicine", "Biostatistics", "Wearables", "Clinical Engineering", "Nano Devices"],
            "7": ["Project Phase I", "Seminar", "Elective I"],
            "8": ["Project Phase II", "Internship", "Elective II"]
        },
        "Biotechnology": {
            "1": ["Mathematics-I", "Biology", "Chemistry", "Physics", "Intro to Biotech"],
            "2": ["Mathematics-II", "Cell Biology", "Genetics", "Organic Chemistry", "Computer Programming"],
            "3": ["Microbiology", "Biochemistry", "Bioprocess Engg", "Molecular Biology", "Enzymology"],
            "4": ["Genetic Engg", "Bioinformatics", "Immunology", "Downstream Processing", "Plant Biotech"],
            "5": ["Animal Biotech", "Industrial Biotech", "Environmental Biotech", "Protein Engg", "Metabolic Engg"],
            "6": ["Bioreactor Design", "Food Biotech", "Stem Cells", "Genomics", "Pharma Biotech"],
            "7": ["Project Phase I", "Seminar", "Elective I"],
            "8": ["Project Phase II", "Internship", "Elective II"]
        },
        "Electrical & Electronics": {
            "1": ["Mathematics-I", "Physics", "Basic Electrical", "Engineering Drawing", "Chemistry"],
            "2": ["Mathematics-II", "Digital Logic", "Electric Circuits", "EM Theory", "Programming"],
            "3": ["Control Systems", "Measurements", "Power Systems", "Machines-I", "OOP"],
            "4": ["Power Electronics", "Signals", "Machines-II", "Energy Systems", "Analog Electronics"],
            "5": ["Switchgear", "Microcontrollers", "High Voltage", "Drives", "DSP"],
            "6": ["Smart Grid", "Renewable Energy", "HVDC", "IoT for Power", "Electric Vehicles"],
            "7": ["Project Phase I", "Seminar", "Elective I"],
            "8": ["Project Phase II", "Internship", "Elective II"]
        }
    }

# Insert data
# with app.app_context():
#     for course_name, semesters in course_data.items():
#         course = Course(name=course_name, signature_path='', photo_path='')
#         db.session.add(course)
#         db.session.flush()  # to get course.id

#         for sem, subjects in semesters.items():
#             for subj in subjects:
#                 db.session.add(Subject(name=subj, semester=sem, course_id=course.id))

#     db.session.commit()
#     print("✅ Courses, Semesters, and Subjects added successfully.")
# student_counter = 1
# for course_name, semesters in course_data.items():
#     course_obj = Course.query.filter_by(name=course_name).first()

#     for sem_num in semesters.keys():
#             for i in range(30):
#                 usn = f"1RV{str(student_counter).zfill(5)}"
#                 name = f"Student {student_counter}"
#                 email = f"student{student_counter}@college.edu"
#                 fee_paid = random.choice([True, True, False])  # 2/3 chance of fee paid

#                 user = User(
#                     usn=usn,
#                     name=name,
#                     email=email,
#                     course=course_name,
#                     semester=int(sem_num),
#                     fee_paid=fee_paid,
#                     password="test123"  # or hashed version if needed
#                 )

#                 db.session.add(user)
#                 student_counter += 1

#     db.session.commit()
#     print("✅ Student data seeded successfully.")
# with app.app_context():
#     try:
#         print("🧹 Cleaning old data...")
#         db.session.query(Subject).delete()
#         db.session.query(User).delete()
#         db.session.query(Course).delete()
#         db.session.commit()
#         print("✅ Old data cleared.")

#         print("📚 Seeding Courses and Subjects...")
#         course_objs = {}
#         for course_name, semesters in course_data.items():
#             course = Course(name=course_name)
#             db.session.add(course)
#             db.session.flush()  # Get course.id for Subject FKs
#             course_objs[course_name] = course

#             for sem, subjects in semesters.items():
#                 for subject_name in subjects:
#                     subject = Subject(name=subject_name, semester=sem, course_id=course.id)
#                     db.session.add(subject)

#         db.session.commit()
#         print("✅ Courses and Subjects seeded.")

#         print("👥 Seeding Users...")
#         student_counter = 1
#         for course_name, semesters in course_data.items():
#             course = course_objs.get(course_name)
#             if not course:
#                 print(f"❌ Course object missing for: {course_name}")
#                 continue

#             for sem_str in semesters:
#                 sem = int(sem_str)
#                 for i in range(30):
#                     usn = f"1RV{str(student_counter).zfill(5)}"
#                     name = f"Student {student_counter}"
#                     email = f"student{student_counter}@college.edu"
#                     raw_password = f"pass{student_counter}"
#                     hashed_password = generate_password_hash(raw_password)
#                     fee_paid = random.choice([True, True, False])

#                     user = User(
#                         usn=usn,
#                         name=name,
#                         email=email,
#                         password=hashed_password,
#                         fee_paid=fee_paid
#                     )

#                     db.session.add(user)

#                     if student_counter % 100 == 0:
#                         print(f"✅ Seeded {student_counter} users...")

#                     student_counter += 1

#         db.session.commit()
#         print("✅ All users seeded successfully.")

#     except Exception as e:
#         print("❌ ERROR during seeding:", e)
#         traceback.print_exc()
#         db.session.rollback()
with app.app_context():
    try:
        print("🧹 Cleaning old data...")
        db.session.query(Subject).delete()
        db.session.query(CollegeFee).delete()
        db.session.query(User).delete()
        db.session.query(Course).delete()
        db.session.commit()
        print("✅ Old data cleared.")

        print("📚 Seeding Courses and Subjects...")
        course_objs = {}
        for course_name, semesters in course_data.items():
            course = Course(name=course_name)
            db.session.add(course)
            db.session.flush()  # Get course.id for Subject FKs
            course_objs[course_name] = course

            for sem, subjects in semesters.items():
                for subject_name in subjects:
                    subject = Subject(name=subject_name, semester=sem, course_id=course.id)
                    db.session.add(subject)

        db.session.commit()
        print("✅ Courses and Subjects seeded.")

        print("👥 Seeding Users and College Fees...")
        student_counter = 1
        for course_name, semesters in course_data.items():
            course = course_objs.get(course_name)
            if not course:
                print(f"❌ Course object missing for: {course_name}")
                continue

            for sem_str in semesters:
                sem = int(sem_str)
                for i in range(30):
                    usn = f"1RV{str(student_counter).zfill(5)}"
                    name = f"Student {student_counter}"
                    email = f"student{student_counter}@college.edu"
                    raw_password = f"pass{student_counter}"
                    hashed_password = generate_password_hash(raw_password)
                    fee_paid = random.choice([True, True, False])  # 2/3 chance paid

                    user = User(
                        usn=usn,
                        name=name,
                        email=email,
                        # course=course_name,
                        # semester=sem,
                        password=hashed_password,
                        fee_paid=fee_paid
                    )
                    db.session.add(user)
                    db.session.flush()  # Get user.id for CollegeFee FK

                    fee_status = "Paid" if fee_paid else "Unpaid"
                    paid_on_date = datetime.now() if fee_paid else None

                    fee = CollegeFee(
                        user_id=user.id,
                        status=fee_status,
                        paid_on=paid_on_date
                    )
                    db.session.add(fee)

                    if student_counter % 100 == 0:
                        print(f"✅ Seeded {student_counter} users...")

                    student_counter += 1

        db.session.commit()
        print("✅ All users and college fees seeded successfully.")

    except Exception as e:
        print("❌ ERROR during seeding:", e)
        traceback.print_exc()
        db.session.rollback()