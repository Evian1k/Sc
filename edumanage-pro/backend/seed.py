from app import create_app, db
from app.models import User, Student, Staff, Class, Subject, Attendance, Grade, Fee
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        print("Creating classes...")
        # Create classes
        classes = [
            Class(name="Grade 1A", section="A", grade_level=1, academic_year="2023-2024"),
            Class(name="Grade 1B", section="B", grade_level=1, academic_year="2023-2024"),
            Class(name="Grade 2A", section="A", grade_level=2, academic_year="2023-2024"),
            Class(name="Grade 3A", section="A", grade_level=3, academic_year="2023-2024"),
            Class(name="Grade 4A", section="A", grade_level=4, academic_year="2023-2024"),
            Class(name="Grade 5A", section="A", grade_level=5, academic_year="2023-2024"),
        ]
        
        for cls in classes:
            db.session.add(cls)
        
        db.session.commit()
        
        print("Creating subjects...")
        # Create subjects
        subjects = [
            Subject(name="Mathematics", code="MATH101", description="Basic Mathematics", credits=3),
            Subject(name="English", code="ENG101", description="English Language Arts", credits=3),
            Subject(name="Science", code="SCI101", description="General Science", credits=3),
            Subject(name="Social Studies", code="SS101", description="Social Studies", credits=2),
            Subject(name="Physical Education", code="PE101", description="Physical Education", credits=1),
            Subject(name="Art", code="ART101", description="Visual Arts", credits=1),
            Subject(name="Music", code="MUS101", description="Music Education", credits=1),
        ]
        
        for subject in subjects:
            db.session.add(subject)
        
        db.session.commit()
        
        print("Creating admin user...")
        # Create admin user
        admin_user = User(username="admin", email="admin@edumanage.com", role="admin")
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()
        
        # Create admin staff profile
        admin_staff = Staff(
            user_id=admin_user.id,
            staff_id="ADM001",
            first_name="System",
            last_name="Administrator",
            date_of_birth=date(1980, 1, 1),
            gender="Other",
            phone="555-0000",
            address="School Campus",
            position="Principal",
            department="Administration",
            salary=Decimal("80000.00"),
            qualification="Master's in Education Administration"
        )
        db.session.add(admin_staff)
        
        print("Creating teachers...")
        # Create teacher users and staff profiles
        teachers_data = [
            {
                "username": "john_teacher", "email": "john@edumanage.com",
                "first_name": "John", "last_name": "Smith",
                "staff_id": "TCH001", "position": "Math Teacher", "department": "Mathematics",
                "salary": "50000.00"
            },
            {
                "username": "mary_teacher", "email": "mary@edumanage.com",
                "first_name": "Mary", "last_name": "Johnson",
                "staff_id": "TCH002", "position": "English Teacher", "department": "English",
                "salary": "48000.00"
            },
            {
                "username": "david_teacher", "email": "david@edumanage.com",
                "first_name": "David", "last_name": "Wilson",
                "staff_id": "TCH003", "position": "Science Teacher", "department": "Science",
                "salary": "52000.00"
            },
            {
                "username": "sarah_teacher", "email": "sarah@edumanage.com",
                "first_name": "Sarah", "last_name": "Brown",
                "staff_id": "TCH004", "position": "Social Studies Teacher", "department": "Social Studies",
                "salary": "47000.00"
            }
        ]
        
        teacher_users = []
        for teacher_data in teachers_data:
            user = User(username=teacher_data["username"], email=teacher_data["email"], role="teacher")
            user.set_password("teacher123")
            db.session.add(user)
            db.session.flush()
            
            staff = Staff(
                user_id=user.id,
                staff_id=teacher_data["staff_id"],
                first_name=teacher_data["first_name"],
                last_name=teacher_data["last_name"],
                date_of_birth=date(1985, random.randint(1, 12), random.randint(1, 28)),
                gender=random.choice(["Male", "Female"]),
                phone=f"555-{random.randint(1000, 9999)}",
                address=f"{random.randint(100, 999)} Teacher St",
                position=teacher_data["position"],
                department=teacher_data["department"],
                salary=Decimal(teacher_data["salary"]),
                qualification="Bachelor's Degree in Education",
                emergency_contact=f"Emergency Contact {teacher_data['first_name']}",
                emergency_phone=f"555-{random.randint(1000, 9999)}"
            )
            db.session.add(staff)
            teacher_users.append(user)
        
        db.session.commit()
        
        print("Creating students...")
        # Create student users and profiles
        students_data = [
            {"first_name": "Alice", "last_name": "Johnson", "class_id": 1},
            {"first_name": "Bob", "last_name": "Smith", "class_id": 1},
            {"first_name": "Charlie", "last_name": "Brown", "class_id": 1},
            {"first_name": "Diana", "last_name": "Wilson", "class_id": 2},
            {"first_name": "Emily", "last_name": "Davis", "class_id": 2},
            {"first_name": "Frank", "last_name": "Miller", "class_id": 2},
            {"first_name": "Grace", "last_name": "Taylor", "class_id": 3},
            {"first_name": "Henry", "last_name": "Anderson", "class_id": 3},
            {"first_name": "Ivy", "last_name": "Thomas", "class_id": 4},
            {"first_name": "Jack", "last_name": "Jackson", "class_id": 4},
            {"first_name": "Kelly", "last_name": "White", "class_id": 5},
            {"first_name": "Liam", "last_name": "Harris", "class_id": 5},
            {"first_name": "Mia", "last_name": "Martin", "class_id": 6},
            {"first_name": "Noah", "last_name": "Thompson", "class_id": 6},
            {"first_name": "Olivia", "last_name": "Garcia", "class_id": 1},
        ]
        
        student_users = []
        for i, student_data in enumerate(students_data, 1):
            username = f"{student_data['first_name'].lower()}_student"
            email = f"{student_data['first_name'].lower()}@student.edumanage.com"
            
            user = User(username=username, email=email, role="student")
            user.set_password("student123")
            db.session.add(user)
            db.session.flush()
            
            student = Student(
                user_id=user.id,
                student_id=f"STU{i:03d}",
                first_name=student_data["first_name"],
                last_name=student_data["last_name"],
                date_of_birth=date(2015, random.randint(1, 12), random.randint(1, 28)),
                gender=random.choice(["Male", "Female"]),
                phone=f"555-{random.randint(1000, 9999)}",
                address=f"{random.randint(100, 999)} Student Ave",
                class_id=student_data["class_id"],
                parent_name=f"Parent of {student_data['first_name']}",
                parent_phone=f"555-{random.randint(1000, 9999)}",
                parent_email=f"parent_{student_data['first_name'].lower()}@email.com"
            )
            db.session.add(student)
            student_users.append((user, student))
        
        db.session.commit()
        
        print("Creating attendance records...")
        # Create sample attendance records for the last 30 days
        students = Student.query.all()
        for student in students:
            for i in range(30):
                attendance_date = date.today() - timedelta(days=i)
                if attendance_date.weekday() < 5:  # Only weekdays
                    status = random.choices(
                        ['present', 'absent', 'late'],
                        weights=[85, 10, 5]
                    )[0]
                    
                    attendance = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=status,
                        check_in_time=datetime.now().time() if status != 'absent' else None,
                        marked_by=teacher_users[0].id if teacher_users else admin_user.id
                    )
                    db.session.add(attendance)
        
        db.session.commit()
        
        print("Creating grades...")
        # Create sample grades
        assessment_types = ['exam', 'quiz', 'assignment', 'project']
        for student in students:
            for subject in subjects[:4]:  # First 4 subjects
                for assessment_type in assessment_types:
                    marks_obtained = random.randint(60, 100)
                    total_marks = 100
                    
                    grade = Grade(
                        student_id=student.id,
                        subject_id=subject.id,
                        assessment_type=assessment_type,
                        assessment_name=f"{assessment_type.title()} 1",
                        marks_obtained=Decimal(str(marks_obtained)),
                        total_marks=Decimal(str(total_marks)),
                        semester="Fall 2023",
                        academic_year="2023-2024",
                        teacher_id=teacher_users[0].id if teacher_users else admin_user.id,
                        date_assessed=date.today() - timedelta(days=random.randint(1, 60))
                    )
                    grade.calculate_percentage()
                    grade.calculate_grade_letter()
                    db.session.add(grade)
        
        db.session.commit()
        
        print("Creating fee records...")
        # Create sample fee records
        fee_types = ['tuition', 'library', 'lab', 'transport', 'activity']
        for student in students:
            for fee_type in fee_types:
                amount = random.choice([500, 750, 1000, 1500, 2000])
                due_date = date.today() + timedelta(days=random.randint(1, 90))
                
                fee = Fee(
                    student_id=student.id,
                    fee_type=fee_type,
                    amount=Decimal(str(amount)),
                    due_date=due_date,
                    semester="Fall 2023",
                    academic_year="2023-2024"
                )
                
                # Randomly pay some fees
                if random.random() < 0.7:  # 70% chance of payment
                    payment_amount = random.choice([
                        amount,  # Full payment
                        amount * 0.5,  # Partial payment
                        amount * 0.8   # Most of payment
                    ])
                    fee.paid_amount = Decimal(str(payment_amount))
                    fee.payment_date = date.today() - timedelta(days=random.randint(1, 30))
                    fee.payment_method = random.choice(['cash', 'card', 'online', 'bank_transfer'])
                    fee.transaction_id = f"TXN{random.randint(100000, 999999)}"
                    fee.collected_by = admin_user.id
                
                fee.update_status()
                db.session.add(fee)
        
        db.session.commit()
        
        print("Database seeded successfully!")
        print(f"Created:")
        print(f"  - {len(classes)} classes")
        print(f"  - {len(subjects)} subjects")
        print(f"  - {len(teachers_data) + 1} staff members")
        print(f"  - {len(students_data)} students")
        print(f"  - Sample attendance, grades, and fee records")
        print("\nDefault login credentials:")
        print("  Admin: username=admin, password=admin123")
        print("  Teacher: username=john_teacher, password=teacher123")
        print("  Student: username=alice_student, password=student123")

if __name__ == '__main__':
    seed_database()