import qrcode
import io
import base64
import uuid
import json
from datetime import datetime, timedelta
from flask import current_app
import jwt
from PIL import Image, ImageDraw, ImageFont
import os

class QRCodeService:
    def __init__(self):
        self.qr_version = 1
        self.qr_error_correction = qrcode.constants.ERROR_CORRECT_L
        self.qr_box_size = 10
        self.qr_border = 4
    
    def generate_student_qr_code(self, student_id, school_id, valid_hours=24):
        """Generate QR code for student attendance"""
        try:
            # Create payload with student info and expiration
            payload = {
                'student_id': student_id,
                'school_id': school_id,
                'generated_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=valid_hours)).isoformat(),
                'type': 'attendance',
                'uuid': str(uuid.uuid4())
            }
            
            # Create JWT token for security
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=self.qr_version,
                error_correction=self.qr_error_correction,
                box_size=self.qr_box_size,
                border=self.qr_border,
            )
            
            qr.add_data(token)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for easy storage/transmission
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            base64_image = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                'success': True,
                'qr_token': token,
                'qr_image_base64': base64_image,
                'expires_at': payload['expires_at'],
                'uuid': payload['uuid']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_class_qr_code(self, class_id, school_id, valid_minutes=60):
        """Generate QR code for class-based attendance"""
        try:
            payload = {
                'class_id': class_id,
                'school_id': school_id,
                'generated_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(minutes=valid_minutes)).isoformat(),
                'type': 'class_attendance',
                'uuid': str(uuid.uuid4())
            }
            
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            qr = qrcode.QRCode(
                version=self.qr_version,
                error_correction=self.qr_error_correction,
                box_size=self.qr_box_size,
                border=self.qr_border,
            )
            
            qr.add_data(token)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            base64_image = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                'success': True,
                'qr_token': token,
                'qr_image_base64': base64_image,
                'expires_at': payload['expires_at'],
                'uuid': payload['uuid']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_event_qr_code(self, event_id, school_id, valid_hours=12):
        """Generate QR code for event attendance"""
        try:
            payload = {
                'event_id': event_id,
                'school_id': school_id,
                'generated_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=valid_hours)).isoformat(),
                'type': 'event_attendance',
                'uuid': str(uuid.uuid4())
            }
            
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            qr = qrcode.QRCode(
                version=self.qr_version,
                error_correction=self.qr_error_correction,
                box_size=self.qr_box_size,
                border=self.qr_border,
            )
            
            qr.add_data(token)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            base64_image = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                'success': True,
                'qr_token': token,
                'qr_image_base64': base64_image,
                'expires_at': payload['expires_at'],
                'uuid': payload['uuid']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_qr_code(self, qr_token):
        """Verify and decode QR code token"""
        try:
            # Decode JWT token
            payload = jwt.decode(
                qr_token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload['expires_at'])
            if datetime.utcnow() > expires_at:
                return {
                    'success': False,
                    'error': 'QR code has expired'
                }
            
            return {
                'success': True,
                'payload': payload
            }
        
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'QR code has expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Invalid QR code'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_attendance_scan(self, qr_token, scanner_user_id=None):
        """Process QR code scan for attendance"""
        try:
            # Verify QR code
            verification = self.verify_qr_code(qr_token)
            if not verification['success']:
                return verification
            
            payload = verification['payload']
            
            # Import here to avoid circular imports
            from app.models import Student, Class, Event, Attendance, EventRegistration
            from app import db
            
            current_time = datetime.utcnow()
            
            if payload['type'] == 'attendance':
                # Student attendance
                student = Student.query.get(payload['student_id'])
                if not student:
                    return {'success': False, 'error': 'Student not found'}
                
                # Check if attendance already recorded today
                today = current_time.date()
                existing_attendance = Attendance.query.filter_by(
                    student_id=student.id,
                    date=today
                ).first()
                
                if existing_attendance:
                    return {
                        'success': False,
                        'error': 'Attendance already recorded for today',
                        'existing_status': existing_attendance.status
                    }
                
                # Record attendance
                attendance = Attendance(
                    student_id=student.id,
                    date=today,
                    time_in=current_time.time(),
                    status='present',
                    marked_by_id=scanner_user_id,
                    method='qr_scan'
                )
                
                db.session.add(attendance)
                db.session.commit()
                
                # Send notification to parents
                from app.services.notification_service import notification_service
                notification_service.send_attendance_alert(
                    student.id, 
                    'present', 
                    today
                )
                
                return {
                    'success': True,
                    'student_name': student.full_name,
                    'status': 'present',
                    'time': current_time.strftime('%H:%M:%S'),
                    'message': f'Attendance recorded for {student.full_name}'
                }
            
            elif payload['type'] == 'class_attendance':
                # Class-based attendance
                class_obj = Class.query.get(payload['class_id'])
                if not class_obj:
                    return {'success': False, 'error': 'Class not found'}
                
                return {
                    'success': True,
                    'type': 'class_attendance',
                    'class_id': class_obj.id,
                    'class_name': class_obj.name,
                    'message': f'Ready to mark attendance for {class_obj.name}'
                }
            
            elif payload['type'] == 'event_attendance':
                # Event attendance
                event = Event.query.get(payload['event_id'])
                if not event:
                    return {'success': False, 'error': 'Event not found'}
                
                return {
                    'success': True,
                    'type': 'event_attendance',
                    'event_id': event.id,
                    'event_name': event.title,
                    'message': f'Ready to mark attendance for {event.title}'
                }
            
            else:
                return {'success': False, 'error': 'Unknown QR code type'}
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_branded_qr_code(self, data, school_logo_path=None, student_info=None):
        """Generate branded QR code with school logo and student information"""
        try:
            # Generate basic QR code
            qr = qrcode.QRCode(
                version=self.qr_version,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction for logo
                box_size=10,
                border=4,
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to RGB for manipulation
            qr_img = qr_img.convert('RGB')
            
            # Add logo if provided
            if school_logo_path and os.path.exists(school_logo_path):
                logo = Image.open(school_logo_path)
                
                # Calculate logo size (10% of QR code)
                qr_width, qr_height = qr_img.size
                logo_size = int(qr_width * 0.1)
                
                # Resize logo
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Create a white background for the logo
                logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), 'white')
                logo_bg.paste(logo, (10, 10))
                
                # Calculate position (center of QR code)
                logo_pos = ((qr_width - logo_size - 20) // 2, (qr_height - logo_size - 20) // 2)
                
                # Paste logo on QR code
                qr_img.paste(logo_bg, logo_pos)
            
            # Add student information if provided
            if student_info:
                # Create a larger image to include text
                text_height = 100
                final_img = Image.new('RGB', (qr_img.width, qr_img.height + text_height), 'white')
                final_img.paste(qr_img, (0, 0))
                
                # Add text
                draw = ImageDraw.Draw(final_img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
                
                # Draw student information
                text_y = qr_img.height + 10
                text_lines = [
                    f"Name: {student_info.get('name', '')}",
                    f"ID: {student_info.get('student_id', '')}",
                    f"Class: {student_info.get('class', '')}"
                ]
                
                for line in text_lines:
                    text_bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = (final_img.width - text_width) // 2
                    draw.text((text_x, text_y), line, fill='black', font=font)
                    text_y += 25
                
                qr_img = final_img
            
            # Convert to base64
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            base64_image = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                'success': True,
                'qr_image_base64': base64_image
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def bulk_generate_student_qr_codes(self, student_ids, school_id):
        """Generate QR codes for multiple students"""
        try:
            results = []
            
            for student_id in student_ids:
                result = self.generate_student_qr_code(student_id, school_id)
                results.append({
                    'student_id': student_id,
                    'result': result
                })
            
            return {
                'success': True,
                'results': results
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global QR service instance
qr_service = QRCodeService()