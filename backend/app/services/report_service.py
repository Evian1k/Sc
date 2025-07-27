import io
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from flask import current_app
import tempfile

class ReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for reports"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generate_student_report_card(self, student_id, academic_year, term):
        """Generate comprehensive student report card"""
        try:
            from app.models import Student, School, ExamResult, Exam, Subject, Class
            
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            school = School.query.get(student.school_id)
            
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Build content
            content = []
            
            # Header with school logo and info
            if school.logo_url:
                try:
                    logo = Image(school.logo_url, width=1*inch, height=1*inch)
                    content.append(logo)
                except:
                    pass
            
            content.append(Paragraph(school.name, self.styles['CustomTitle']))
            content.append(Paragraph(f"Student Report Card - {academic_year} - {term}", 
                                   self.styles['CustomHeading']))
            content.append(Spacer(1, 20))
            
            # Student Information
            student_info = [
                ['Student Name:', student.full_name],
                ['Student ID:', student.student_id],
                ['Class:', student.class_enrolled.name if student.class_enrolled else 'N/A'],
                ['Academic Year:', academic_year],
                ['Term:', term],
                ['Date Generated:', datetime.now().strftime('%Y-%m-%d')]
            ]
            
            student_table = Table(student_info, colWidths=[2*inch, 3*inch])
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(student_table)
            content.append(Spacer(1, 20))
            
            # Academic Performance
            content.append(Paragraph("Academic Performance", self.styles['CustomHeading']))
            
            # Get exam results for the term
            exams = Exam.query.filter_by(
                school_id=student.school_id,
                academic_year=academic_year,
                term=term
            ).all()
            
            results_data = [['Subject', 'CAT 1', 'CAT 2', 'End Term', 'Total', 'Grade', 'Position']]
            
            total_marks = 0
            total_possible = 0
            
            for exam in exams:
                exam_results = ExamResult.query.filter_by(
                    exam_id=exam.id,
                    student_id=student.id
                ).all()
                
                subject_results = {}
                for result in exam_results:
                    subject_name = result.subject.name
                    if subject_name not in subject_results:
                        subject_results[subject_name] = {}
                    subject_results[subject_name][exam.exam_type] = {
                        'marks': result.marks_obtained,
                        'total': result.total_marks,
                        'grade': result.grade,
                        'position': result.position_in_subject
                    }
                
                for subject, results in subject_results.items():
                    cat1 = results.get('cat', {}).get('marks', '-')
                    cat2 = results.get('mid-term', {}).get('marks', '-')
                    end_term = results.get('final', {}).get('marks', '-')
                    
                    # Calculate total (example: CAT1(30%) + CAT2(30%) + EndTerm(40%))
                    subject_total = 0
                    if cat1 != '-': subject_total += float(cat1) * 0.3
                    if cat2 != '-': subject_total += float(cat2) * 0.3
                    if end_term != '-': subject_total += float(end_term) * 0.4
                    
                    grade = self.calculate_grade(subject_total)
                    position = results.get('final', {}).get('position', '-')
                    
                    results_data.append([
                        subject, str(cat1), str(cat2), str(end_term),
                        f"{subject_total:.1f}", grade, str(position)
                    ])
                    
                    total_marks += subject_total
                    total_possible += 100
            
            # Add overall performance
            if total_possible > 0:
                overall_percentage = (total_marks / total_possible) * 100
                overall_grade = self.calculate_grade(overall_percentage)
                
                results_data.append(['', '', '', '', '', '', ''])
                results_data.append([
                    'OVERALL', '', '', '',
                    f"{overall_percentage:.1f}%", overall_grade, ''
                ])
            
            results_table = Table(results_data)
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (-3, -1), (-1, -1), colors.lightgreen)
            ]))
            
            content.append(results_table)
            content.append(Spacer(1, 20))
            
            # Attendance Summary
            content.append(Paragraph("Attendance Summary", self.styles['CustomHeading']))
            
            attendance_percentage = student.get_attendance_percentage()
            attendance_data = [
                ['Attendance Percentage:', f"{attendance_percentage}%"],
                ['Days Present:', 'XX'],  # Would calculate from actual data
                ['Days Absent:', 'XX'],
                ['Late Arrivals:', 'XX']
            ]
            
            attendance_table = Table(attendance_data, colWidths=[2*inch, 1.5*inch])
            attendance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(attendance_table)
            content.append(Spacer(1, 20))
            
            # Teacher's Comments
            content.append(Paragraph("Teacher's Comments", self.styles['CustomHeading']))
            comments = "Excellent performance this term. Keep up the good work!"
            content.append(Paragraph(comments, self.styles['CustomNormal']))
            content.append(Spacer(1, 20))
            
            # Class Teacher Signature
            content.append(Paragraph("Class Teacher: ___________________ Date: ___________", 
                                   self.styles['CustomNormal']))
            content.append(Spacer(1, 10))
            content.append(Paragraph("Principal: ______________________ Date: ___________", 
                                   self.styles['CustomNormal']))
            
            # Build PDF
            doc.build(content)
            
            # Get PDF data
            buffer.seek(0)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Convert to base64 for easy handling
            pdf_base64 = base64.b64encode(pdf_data).decode()
            
            return {
                'success': True,
                'pdf_base64': pdf_base64,
                'filename': f"report_card_{student.student_id}_{academic_year}_{term}.pdf"
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_fee_statement(self, student_id, academic_year):
        """Generate student fee statement"""
        try:
            from app.models import Student, School, Fee, FeeStructure
            
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            school = School.query.get(student.school_id)
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            content = []
            
            # Header
            content.append(Paragraph(school.name, self.styles['CustomTitle']))
            content.append(Paragraph("Fee Statement", self.styles['CustomHeading']))
            content.append(Spacer(1, 20))
            
            # Student Info
            student_info = [
                ['Student Name:', student.full_name],
                ['Student ID:', student.student_id],
                ['Class:', student.class_enrolled.name if student.class_enrolled else 'N/A'],
                ['Academic Year:', academic_year],
                ['Statement Date:', datetime.now().strftime('%Y-%m-%d')]
            ]
            
            student_table = Table(student_info, colWidths=[2*inch, 3*inch])
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            
            content.append(student_table)
            content.append(Spacer(1, 20))
            
            # Fee Details
            content.append(Paragraph("Fee Details", self.styles['CustomHeading']))
            
            fees = Fee.query.filter_by(
                student_id=student.id,
                academic_year=academic_year
            ).all()
            
            fee_data = [['Description', 'Amount Due', 'Amount Paid', 'Balance', 'Due Date', 'Status']]
            
            total_due = 0
            total_paid = 0
            total_balance = 0
            
            for fee in fees:
                balance = fee.amount - fee.amount_paid
                total_due += fee.amount
                total_paid += fee.amount_paid
                total_balance += balance
                
                fee_data.append([
                    fee.fee_type,
                    f"{school.get_setting('currency', 'KES')} {fee.amount:,.2f}",
                    f"{school.get_setting('currency', 'KES')} {fee.amount_paid:,.2f}",
                    f"{school.get_setting('currency', 'KES')} {balance:,.2f}",
                    fee.due_date.strftime('%Y-%m-%d') if fee.due_date else 'N/A',
                    fee.status
                ])
            
            # Add totals
            fee_data.append(['', '', '', '', '', ''])
            fee_data.append([
                'TOTAL',
                f"{school.get_setting('currency', 'KES')} {total_due:,.2f}",
                f"{school.get_setting('currency', 'KES')} {total_paid:,.2f}",
                f"{school.get_setting('currency', 'KES')} {total_balance:,.2f}",
                '', ''
            ])
            
            fee_table = Table(fee_data)
            fee_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 1), (-3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen)
            ]))
            
            content.append(fee_table)
            content.append(Spacer(1, 20))
            
            # Payment Instructions
            content.append(Paragraph("Payment Instructions", self.styles['CustomHeading']))
            payment_info = """
            Please make payments to:
            Bank: XYZ Bank
            Account Name: """ + school.name + """
            Account Number: XXXXXXXXXX
            Reference: """ + student.student_id + """
            """
            content.append(Paragraph(payment_info, self.styles['CustomNormal']))
            
            doc.build(content)
            buffer.seek(0)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            pdf_base64 = base64.b64encode(pdf_data).decode()
            
            return {
                'success': True,
                'pdf_base64': pdf_base64,
                'filename': f"fee_statement_{student.student_id}_{academic_year}.pdf"
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_class_performance_report(self, class_id, exam_id):
        """Generate class performance analysis report"""
        try:
            from app.models import Class, Exam, ExamResult, Student
            
            class_obj = Class.query.get(class_id)
            exam = Exam.query.get(exam_id)
            
            if not class_obj or not exam:
                return {'success': False, 'error': 'Class or exam not found'}
            
            # Generate charts first
            chart_paths = self.generate_performance_charts(class_id, exam_id)
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            content = []
            
            # Header
            content.append(Paragraph(f"Class Performance Report", self.styles['CustomTitle']))
            content.append(Paragraph(f"Class: {class_obj.name} | Exam: {exam.name}", 
                                   self.styles['CustomHeading']))
            content.append(Spacer(1, 20))
            
            # Summary Statistics
            results = ExamResult.query.filter_by(exam_id=exam_id, class_id=class_id).all()
            
            if results:
                scores = [r.percentage for r in results if r.percentage]
                avg_score = sum(scores) / len(scores) if scores else 0
                highest_score = max(scores) if scores else 0
                lowest_score = min(scores) if scores else 0
                
                summary_data = [
                    ['Total Students:', str(len(results))],
                    ['Average Score:', f"{avg_score:.1f}%"],
                    ['Highest Score:', f"{highest_score:.1f}%"],
                    ['Lowest Score:', f"{lowest_score:.1f}%"],
                    ['Pass Rate:', f"{len([s for s in scores if s >= 50]) / len(scores) * 100:.1f}%"]
                ]
                
                summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ]))
                
                content.append(summary_table)
                content.append(Spacer(1, 20))
            
            # Include charts if generated
            for chart_path in chart_paths:
                if os.path.exists(chart_path):
                    img = Image(chart_path, width=6*inch, height=4*inch)
                    content.append(img)
                    content.append(Spacer(1, 20))
            
            doc.build(content)
            
            # Clean up temporary chart files
            for chart_path in chart_paths:
                if os.path.exists(chart_path):
                    os.remove(chart_path)
            
            buffer.seek(0)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            pdf_base64 = base64.b64encode(pdf_data).decode()
            
            return {
                'success': True,
                'pdf_base64': pdf_base64,
                'filename': f"class_performance_{class_obj.name}_{exam.name}.pdf"
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_performance_charts(self, class_id, exam_id):
        """Generate performance analysis charts"""
        try:
            from app.models import ExamResult
            
            results = ExamResult.query.filter_by(exam_id=exam_id, class_id=class_id).all()
            
            if not results:
                return []
            
            chart_paths = []
            
            # Grade distribution chart
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                grades = [r.grade for r in results if r.grade]
                grade_counts = pd.Series(grades).value_counts().sort_index()
                
                plt.figure(figsize=(8, 6))
                grade_counts.plot(kind='bar', color='skyblue')
                plt.title('Grade Distribution')
                plt.xlabel('Grades')
                plt.ylabel('Number of Students')
                plt.xticks(rotation=0)
                plt.tight_layout()
                plt.savefig(tmp.name)
                plt.close()
                
                chart_paths.append(tmp.name)
            
            # Score distribution histogram
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                scores = [r.percentage for r in results if r.percentage]
                
                plt.figure(figsize=(8, 6))
                plt.hist(scores, bins=10, color='lightgreen', alpha=0.7)
                plt.title('Score Distribution')
                plt.xlabel('Percentage Score')
                plt.ylabel('Number of Students')
                plt.tight_layout()
                plt.savefig(tmp.name)
                plt.close()
                
                chart_paths.append(tmp.name)
            
            return chart_paths
        
        except Exception as e:
            return []
    
    def calculate_grade(self, percentage):
        """Calculate grade based on percentage"""
        if percentage >= 80:
            return 'A'
        elif percentage >= 75:
            return 'A-'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 65:
            return 'B'
        elif percentage >= 60:
            return 'B-'
        elif percentage >= 55:
            return 'C+'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 45:
            return 'C-'
        elif percentage >= 40:
            return 'D+'
        elif percentage >= 35:
            return 'D'
        elif percentage >= 30:
            return 'D-'
        else:
            return 'E'

# Global report service instance
report_service = ReportService()