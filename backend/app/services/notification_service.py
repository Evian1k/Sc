import os
import logging
from flask import current_app
from twilio.rest import Client as TwilioClient
from flask_mail import Mail, Message as MailMessage
import africastalking
import requests
import json
from datetime import datetime
from app import db
from app.models import User, Student, Parent, Staff, School

class NotificationService:
    def __init__(self):
        self.twilio_client = None
        self.africastalking_client = None
        self.mail = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize notification service clients"""
        try:
            # Initialize Twilio
            if current_app.config.get('TWILIO_ACCOUNT_SID') and current_app.config.get('TWILIO_AUTH_TOKEN'):
                self.twilio_client = TwilioClient(
                    current_app.config['TWILIO_ACCOUNT_SID'],
                    current_app.config['TWILIO_AUTH_TOKEN']
                )
            
            # Initialize Africa's Talking
            if current_app.config.get('AFRICASTALKING_USERNAME') and current_app.config.get('AFRICASTALKING_API_KEY'):
                africastalking.initialize(
                    current_app.config['AFRICASTALKING_USERNAME'],
                    current_app.config['AFRICASTALKING_API_KEY']
                )
                self.africastalking_client = africastalking.SMS
            
        except Exception as e:
            logging.error(f"Error initializing notification clients: {str(e)}")
    
    def send_sms_twilio(self, phone_number, message, school_id=None):
        """Send SMS using Twilio"""
        try:
            if not self.twilio_client:
                return {'success': False, 'error': 'Twilio not configured'}
            
            if not phone_number.startswith('+'):
                phone_number = '+254' + phone_number.lstrip('0')  # Kenyan format
            
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=current_app.config['TWILIO_PHONE_NUMBER'],
                to=phone_number
            )
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status
            }
        
        except Exception as e:
            logging.error(f"Twilio SMS error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_sms_africastalking(self, phone_numbers, message, school_id=None):
        """Send SMS using Africa's Talking"""
        try:
            if not self.africastalking_client:
                return {'success': False, 'error': 'Africa\'s Talking not configured'}
            
            # Format phone numbers
            if isinstance(phone_numbers, str):
                phone_numbers = [phone_numbers]
            
            formatted_numbers = []
            for phone in phone_numbers:
                if not phone.startswith('+'):
                    phone = '+254' + phone.lstrip('0')
                formatted_numbers.append(phone)
            
            response = self.africastalking_client.send(
                message=message,
                recipients=formatted_numbers,
                sender_id=current_app.config.get('AFRICASTALKING_SENDER_ID')
            )
            
            return {
                'success': True,
                'response': response
            }
        
        except Exception as e:
            logging.error(f"Africa's Talking SMS error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_email(self, recipients, subject, content, html_content=None, school_id=None):
        """Send email notification"""
        try:
            from app import mail
            
            if isinstance(recipients, str):
                recipients = [recipients]
            
            msg = MailMessage(
                subject=subject,
                recipients=recipients,
                body=content,
                html=html_content,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            mail.send(msg)
            
            return {'success': True, 'recipients': recipients}
        
        except Exception as e:
            logging.error(f"Email sending error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_whatsapp(self, phone_number, message, school_id=None):
        """Send WhatsApp message (requires WhatsApp Business API)"""
        try:
            if not current_app.config.get('WHATSAPP_API_URL'):
                return {'success': False, 'error': 'WhatsApp API not configured'}
            
            headers = {
                'Authorization': f"Bearer {current_app.config['WHATSAPP_API_TOKEN']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': phone_number,
                'type': 'text',
                'text': {'body': message}
            }
            
            response = requests.post(
                current_app.config['WHATSAPP_API_URL'],
                headers=headers,
                data=json.dumps(data)
            )
            
            return {
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        
        except Exception as e:
            logging.error(f"WhatsApp sending error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_attendance_alert(self, student_id, status, date=None):
        """Send attendance alert to parents"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            school = School.query.get(student.school_id)
            date_str = date.strftime('%Y-%m-%d') if date else datetime.now().strftime('%Y-%m-%d')
            
            # Create message
            if status == 'absent':
                message = f"Dear Parent, your child {student.full_name} was marked absent on {date_str}. Please contact {school.name} if this is incorrect."
            else:
                message = f"Dear Parent, your child {student.full_name} has arrived safely at {school.name} on {date_str}."
            
            # Get parents
            parents = student.get_parents()
            results = []
            
            for parent in parents:
                # Check parent's notification preferences
                relationship = next((r for r in student.parent_student_relationships 
                                   if r.parent_id == parent.id and r.can_receive_notifications), None)
                
                if not relationship:
                    continue
                
                parent_user = parent.user
                
                # Send SMS if enabled and phone available
                if (parent.get_notification_preference('attendance_alerts') and 
                    parent_user.phone_number and 
                    school.is_feature_enabled('sms_notifications')):
                    
                    sms_result = self.send_sms_africastalking(
                        parent_user.phone_number, 
                        message, 
                        student.school_id
                    )
                    results.append({'type': 'sms', 'recipient': parent_user.phone_number, 'result': sms_result})
                
                # Send email if enabled
                if (parent.get_notification_preference('attendance_alerts') and 
                    parent_user.email and 
                    school.is_feature_enabled('email_notifications')):
                    
                    email_result = self.send_email(
                        parent_user.email,
                        f"Attendance Alert - {student.full_name}",
                        message,
                        school_id=student.school_id
                    )
                    results.append({'type': 'email', 'recipient': parent_user.email, 'result': email_result})
            
            return {'success': True, 'results': results}
        
        except Exception as e:
            logging.error(f"Attendance alert error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_fee_reminder(self, student_id, amount_due, due_date):
        """Send fee payment reminder to parents"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            school = School.query.get(student.school_id)
            currency = school.get_setting('currency', 'KES')
            
            message = (f"Dear Parent, this is a reminder that {student.full_name} has "
                      f"an outstanding fee balance of {currency} {amount_due:.2f} "
                      f"due on {due_date.strftime('%Y-%m-%d')}. "
                      f"Please make payment at your earliest convenience. - {school.name}")
            
            parents = student.get_parents()
            results = []
            
            for parent in parents:
                relationship = next((r for r in student.parent_student_relationships 
                                   if r.parent_id == parent.id and r.can_view_fees), None)
                
                if not relationship:
                    continue
                
                parent_user = parent.user
                
                # Send SMS
                if (parent.get_notification_preference('fee_reminders') and 
                    parent_user.phone_number):
                    
                    sms_result = self.send_sms_africastalking(
                        parent_user.phone_number, 
                        message, 
                        student.school_id
                    )
                    results.append({'type': 'sms', 'recipient': parent_user.phone_number, 'result': sms_result})
                
                # Send email
                if (parent.get_notification_preference('fee_reminders') and 
                    parent_user.email):
                    
                    email_result = self.send_email(
                        parent_user.email,
                        f"Fee Payment Reminder - {student.full_name}",
                        message,
                        school_id=student.school_id
                    )
                    results.append({'type': 'email', 'recipient': parent_user.email, 'result': email_result})
            
            return {'success': True, 'results': results}
        
        except Exception as e:
            logging.error(f"Fee reminder error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_exam_result_notification(self, student_id, exam_name, subject_results):
        """Send exam results to parents"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            school = School.query.get(student.school_id)
            
            # Format results
            results_text = f"Exam Results for {student.full_name} - {exam_name}:\n"
            for result in subject_results:
                results_text += f"{result['subject']}: {result['marks']}/{result['total_marks']} ({result['grade']})\n"
            
            results_text += f"\nRegards,\n{school.name}"
            
            parents = student.get_parents()
            results = []
            
            for parent in parents:
                relationship = next((r for r in student.parent_student_relationships 
                                   if r.parent_id == parent.id and r.can_view_grades), None)
                
                if not relationship:
                    continue
                
                parent_user = parent.user
                
                # Send SMS
                if (parent.get_notification_preference('exam_results') and 
                    parent_user.phone_number):
                    
                    sms_result = self.send_sms_africastalking(
                        parent_user.phone_number, 
                        results_text, 
                        student.school_id
                    )
                    results.append({'type': 'sms', 'recipient': parent_user.phone_number, 'result': sms_result})
                
                # Send email
                if (parent.get_notification_preference('exam_results') and 
                    parent_user.email):
                    
                    email_result = self.send_email(
                        parent_user.email,
                        f"Exam Results - {student.full_name} - {exam_name}",
                        results_text,
                        school_id=student.school_id
                    )
                    results.append({'type': 'email', 'recipient': parent_user.email, 'result': email_result})
            
            return {'success': True, 'results': results}
        
        except Exception as e:
            logging.error(f"Exam result notification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_broadcast_message(self, school_id, recipient_groups, subject, message, channels=None):
        """Send broadcast message to multiple recipients"""
        try:
            if channels is None:
                channels = ['sms', 'email']
            
            school = School.query.get(school_id)
            if not school:
                return {'success': False, 'error': 'School not found'}
            
            recipients = []
            
            for group in recipient_groups:
                if group == 'all_students':
                    students = Student.query.filter_by(school_id=school_id, is_active=True).all()
                    recipients.extend([s.user for s in students])
                elif group == 'all_parents':
                    parents = Parent.query.filter_by(school_id=school_id, is_active=True).all()
                    recipients.extend([p.user for p in parents])
                elif group == 'all_staff':
                    staff = Staff.query.filter_by(school_id=school_id, is_active=True).all()
                    recipients.extend([s.user for s in staff])
                elif group.startswith('class_'):
                    class_id = group.split('_')[1]
                    students = Student.query.filter_by(
                        school_id=school_id, 
                        class_id=class_id, 
                        is_active=True
                    ).all()
                    recipients.extend([s.user for s in students])
            
            # Remove duplicates
            recipients = list(set(recipients))
            
            results = []
            
            for recipient in recipients:
                # Send SMS
                if 'sms' in channels and recipient.phone_number:
                    sms_result = self.send_sms_africastalking(
                        recipient.phone_number, 
                        message, 
                        school_id
                    )
                    results.append({'type': 'sms', 'recipient': recipient.phone_number, 'result': sms_result})
                
                # Send email
                if 'email' in channels and recipient.email:
                    email_result = self.send_email(
                        recipient.email,
                        subject,
                        message,
                        school_id=school_id
                    )
                    results.append({'type': 'email', 'recipient': recipient.email, 'result': email_result})
            
            return {'success': True, 'total_sent': len(results), 'results': results}
        
        except Exception as e:
            logging.error(f"Broadcast message error: {str(e)}")
            return {'success': False, 'error': str(e)}

# Global notification service instance
notification_service = NotificationService()