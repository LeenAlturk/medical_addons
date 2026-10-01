# -*- coding: utf-8 -*-
# from odoo import http


# class MedicalClinic(http.Controller):
#     @http.route('/medical_clinic/medical_clinic', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/medical_clinic/medical_clinic/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('medical_clinic.listing', {
#             'root': '/medical_clinic/medical_clinic',
#             'objects': http.request.env['medical_clinic.medical_clinic'].search([]),
#         })

#     @http.route('/medical_clinic/medical_clinic/objects/<model("medical_clinic.medical_clinic"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('medical_clinic.object', {
#             'object': obj
#         })
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


from odoo import http
from odoo.http import request
import json


class MedicalClinicAPI(http.Controller):

    @http.route(
        '/api/doctors',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False
    )
    def get_doctors(self):

        doctors = request.env['res.users'].sudo().search([
            ('is_doctor', '=', True)
        ])

        data = [{

            'id': doctor.id,

            'name': doctor.name,

            'image': doctor.image_1920.decode('utf-8')
if doctor.image_1920 else '',

            'specialties': [
                specialty.specialties_name
                for specialty in doctor.specialties_ids
            ],

        } for doctor in doctors]

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )


    @http.route('/api/doctors/<int:doctor_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_doctor_details(self, doctor_id):

        doctor = request.env['res.users'].sudo().browse(doctor_id)

        if not doctor.exists() or not doctor.is_doctor:
            return request.make_response(
                json.dumps({'error': 'Doctor not found'}),
                headers=[('Content-Type', 'application/json')],
                status=404
            )

        data = {
            'id': doctor.id,
            'name': doctor.name,
            'email': doctor.email,
            'image': doctor.image_1920.decode('utf-8')
            if doctor.image_1920 else '',
            'specialties': [specialty.specialties_name for specialty in doctor.specialties_ids],
            'working_hours': [
                {
                    'day': dict(work._fields['day'].selection).get(work.day),
                    'from_hour': work.from_hour,
                    'to_hour': work.to_hour,
                } for work in doctor.working_hours_ids
            ]
        }

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route(
        '/api/appointments',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False
    )
    def create_appointment(self, **kwargs):

        import pytz
        from datetime import datetime
        from odoo.http import request

        try:

            data = request.get_json_data()

            doctor_id = int(data.get('doctor_id'))
            patient_id = int(data.get('patient_id'))

            app_date_str = data.get('app_date')
            note = data.get('note', '')

            user_tz = pytz.timezone('Asia/Riyadh')

            # 1. تحويل الوقت ومعالجته
            naive_dt = datetime.strptime(
                app_date_str,
                '%Y-%m-%d %H:%M:%S'
            )

            local_dt = user_tz.localize(naive_dt)

            hour = local_dt.hour + (
                    local_dt.minute / 60.0
            )

            day = local_dt.strftime('%a').lower()[:3]

            # 2. التحقق من دوام الطبيب
            schedule = request.env['working.dr'].sudo().search([
                ('doctor_id', '=', doctor_id),
                ('day', '=', day)
            ], limit=1)

            if not schedule:
                return {
                    'success': False,
                    'error': 'Doctor doesn\'t work today'
                }

            # 3. التحقق من الوقت
            if not (
                    schedule.from_hour <= hour <= schedule.to_hour
            ):
                return {
                    'success': False,
                    'error':
                        f'Out of working hours. '
                        f'Doctor works from '
                        f'{schedule.from_hour} '
                        f'to {schedule.to_hour}'
                }

            # 4. تحويل UTC
            utc_date = local_dt.astimezone(
                pytz.utc
            ).replace(
                second=0,
                microsecond=0
            )

            # 5. إنشاء الحجز
            appointment = request.env[
                'the.appointments'
            ].sudo().create({

                'patient_id': patient_id,

                'doctor_id': doctor_id,

                'app_date':
                    utc_date.strftime(
                        '%Y-%m-%d %H:%M:%S'
                    ),

                'note': note,

                'state': 'draft',
            })

            return {
                'success': True,
                'id': appointment.id
            }

        except Exception as e:

            return {
                'success': False,
                'error': str(e)
            }

    @http.route(
        '/api/patient/appointments/<int:patient_id>',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False
    )
    def get_patient_appointments(self, patient_id):

        import json

        appointments = request.env[
            'the.appointments'
        ].sudo().search([

            ('patient_id', '=', patient_id)

        ], order='app_date desc')

        data = []

        for appointment in appointments:

            prescriptions = []

            for prescription in appointment.Prescription_ids:
                prescriptions.append({

                    'id': prescription.id,

                    'medicine': (
                        prescription.medicine_id.m_name
                        if prescription.medicine_id
                        else ''
                    ),

                    'dosage': prescription.dosage,

                    'unit': prescription.unit,

                    'frequency': prescription.frequency,

                    'time': prescription.time,

                    'food_relation':
                        prescription.food_relation,

                    'duration': prescription.duration,

                    'start_date': (
                        str(prescription.start_date)
                        if prescription.start_date
                        else ''
                    ),

                    'prn': prescription.prn,

                    'notes': prescription.notes or '',
                })

            data.append({

                'appointment_id': appointment.id,

                'appointment_code': appointment.name,

                'doctor_name': appointment.doctor_id.name,

                'app_date': str(appointment.app_date),

                'state': appointment.state,

                'note': appointment.note or '',

                'prescriptions': prescriptions,
            })

        return request.make_response(

            json.dumps(data),

            headers=[
                ('Content-Type', 'application/json')
            ],

            status=200
        )
    @http.route('/api/appointments/cancel/<int:appointment_id>', type='http', auth='public', methods=['POST'],
                csrf=False)
    def cancel_appointment(self, appointment_id):

        import json

        appointment = request.env['the.appointments'].sudo().browse(appointment_id)

        if not appointment.exists():
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': 'Appointment not found'
                }),
                headers=[('Content-Type', 'application/json')],
                status=404
            )

        appointment.write({
            'state': 'cancel'
        })

        return request.make_response(
            json.dumps({
                'success': True,
                'appointment_id': appointment.id,
                'state': appointment.state,
                'message': 'Appointment cancelled successfully'
            }),
            headers=[('Content-Type', 'application/json')],
            status=200
        )

    @http.route('/api/patient/register', type='http', auth='public', methods=['POST'], csrf=False)
    def patient_register(self, **kwargs):

        import json
        import random
        from datetime import timedelta
        from odoo.fields import Datetime

        try:
            name = request.params.get('name')
            phone = request.params.get('phone')
            gender = request.params.get('gender')
            birthdate = request.params.get('birthdate')
            email = request.params.get('email')
            password = request.params.get('password')

            if not name or not phone or not email or not password:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Name, phone, email and password are required'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            existing_patient = request.env['res.partner'].sudo().search([
                '|',
                ('phone', '=', phone),
                ('email', '=', email)
            ], limit=1)

            if existing_patient:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Patient already exists'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=409
                )

            otp = str(random.randint(100000, 999999))

            patient = request.env['res.partner'].sudo().create({
                'name': name,
                'phone': phone,
                'gender': gender,
                'birthdate': birthdate,
                'email': email,
                'password': password,
                'is_patient': True,
                'otp_code': otp,
                'otp_expiry': Datetime.now() + timedelta(minutes=10),
                'is_verified': False,
            })

            mail_values = {
                'subject': 'Your Verification Code',
                'body_html': f'<p>Wellcome to AL Rahma Clinic app Your OTP code is: <strong>{otp}</strong></p>',
                'email_to': patient.email,
                'email_from': 'zizozizoalturk@gmail.com',
            }

            mail = request.env['mail.mail'].sudo().create(mail_values)
            mail.send()

            return request.make_response(
                json.dumps({
                    'success': True,
                    'patient_id': patient.id,
                    'message': 'Patient registered successfully. OTP sent to email.'
                }),
                headers=[('Content-Type', 'application/json')],
                status=201
            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    @http.route('/api/patient/verify-otp', type='http', auth='public', methods=['POST'], csrf=False)
    def verify_patient_otp(self, **kwargs):

        import json
        from odoo.fields import Datetime

        try:
            email = request.params.get('email')
            otp = request.params.get('otp')

            patient = request.env['res.partner'].sudo().search([
                ('email', '=', email),
                ('is_patient', '=', True)
            ], limit=1)

            if not patient:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Patient not found'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            if patient.otp_code != otp:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Invalid OTP'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            if patient.otp_expiry and patient.otp_expiry < Datetime.now():
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'OTP expired'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            patient.sudo().write({
                'is_verified': True,
                'otp_code': False,
            })

            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Account verified successfully'
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    @http.route('/api/patient/login', type='http', auth='public', methods=['POST'], csrf=False)
    def patient_login(self, **kwargs):

        import json

        try:
            email = request.params.get('email')
            password = request.params.get('password')

            if not email or not password:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Email and password are required'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            patient = request.env['res.partner'].sudo().search([
                ('email', '=', email),
                ('is_patient', '=', True)
            ], limit=1)

            if not patient:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Patient not found'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            if not patient.is_verified:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Account not verified'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=403
                )

            if patient.password != password:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Invalid password'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=401
                )

            return request.make_response(
                json.dumps({
                    'success': True,
                    'patient_id': patient.id,
                    'name': patient.name,
                    'email': patient.email,
                    'phone': patient.phone,
                    'age': patient.age,
                    'gender': patient.gender,
                    'is_active_patient': patient.is_active_patient,
                    'message': 'Login successful'
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    @http.route('/api/patient/profile/<int:patient_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def patient_profile(self, patient_id):

        import json

        patient = request.env['res.partner'].sudo().browse(patient_id)

        if not patient.exists() or not patient.is_patient:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': 'Patient not found'
                }),
                headers=[('Content-Type', 'application/json')],
                status=404
            )

        data = {
            'success': True,
            'patient_id': patient.id,
            'name': patient.name,
            'phone': patient.phone,
            'email': patient.email,
            'gender': patient.gender,
            'birthdate': str(patient.birthdate) if patient.birthdate else '',
            'age': patient.age,
            'chronic_diseases': [
                disease.name for disease in patient.chronic_disease_ids
            ]
        }

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
            status=200
        )

    @http.route('/api/patient/edit-profile/<int:patient_id>', type='http', auth='public', methods=['POST'], csrf=False)
    def edit_patient_profile(self, patient_id, **kwargs):

        import json

        try:
            patient = request.env['res.partner'].sudo().browse(patient_id)

            if not patient.exists() or not patient.is_patient:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Patient not found'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            update_vals = {}

            name = request.params.get('name')
            phone = request.params.get('phone')
            gender = request.params.get('gender')
            birthdate = request.params.get('birthdate')

            print("NAME:", name)
            print("PHONE:", phone)
            print("ALL PARAMS:", request.params)
            if name:
                update_vals['name'] = name

            if phone:
                existing_phone = request.env['res.partner'].sudo().search([
                    ('phone', '=', phone),
                    ('id', '!=', patient.id)
                ], limit=1)

                if existing_phone:
                    return request.make_response(
                        json.dumps({
                            'success': False,
                            'error': 'Phone already in use'
                        }),
                        headers=[('Content-Type', 'application/json')],
                        status=409
                    )

                update_vals['phone'] = phone

            if gender:
                update_vals['gender'] = gender

            if birthdate:
                update_vals['birthdate'] = birthdate

            patient.sudo().write(update_vals)

            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'patient_id': patient.id,
                    'name': patient.name,
                    'phone': patient.phone,
                    'gender': patient.gender,
                    'birthdate': str(patient.birthdate) if patient.birthdate else '',
                    'age': patient.age
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    @http.route('/api/patient/forgot-password', type='http', auth='public', methods=['POST'], csrf=False)
    def forgot_password(self, **kwargs):

        import json
        import random
        from datetime import timedelta
        from odoo.fields import Datetime

        try:
            email = request.params.get('email')

            if not email:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Email is required'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            patient = request.env['res.partner'].sudo().search([
                ('email', '=', email),
                ('is_patient', '=', True)
            ], limit=1)

            if not patient:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Patient not found'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            otp = str(random.randint(100000, 999999))

            patient.sudo().write({
                'otp_code': otp,
                'otp_expiry': Datetime.now() + timedelta(minutes=10),
            })

            mail_values = {
                'subject': 'Password Reset OTP',
                'body_html': f'<p>Your password reset OTP is: <strong>{otp}</strong></p>',
                'email_to': patient.email,
                'email_from': 'zizozizoalturk@gmail.com',
            }

            mail = request.env['mail.mail'].sudo().create(mail_values)
            mail.sudo().send()

            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'OTP sent to your email'
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    @http.route('/api/patient/reset-password', type='http', auth='public', methods=['POST'], csrf=False)
    def reset_password(self, **kwargs):

        import json
        from odoo.fields import Datetime

        try:
            print("PARAMS:", request.params)
            email = request.params.get('email')
            otp = request.params.get('otp')
            new_password = request.params.get('new_password')

            if not email or not otp or not new_password:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Email, OTP and new password are required'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            patient = request.env['res.partner'].sudo().search([
                ('email', '=', email),
                ('is_patient', '=', True)
            ], limit=1)

            if not patient:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Patient not found'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            if patient.otp_code != otp:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Invalid OTP'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            if patient.otp_expiry and patient.otp_expiry < Datetime.now():
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'OTP expired'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            patient.sudo().write({
                'password': new_password,
                'otp_code': False,
            })

            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Password reset successfully'
                }),
                headers=[('Content-Type', 'application/json')],
                status=200

            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    @http.route('/api/patient/resend-otp', type='http', auth='public', methods=['POST'], csrf=False)
    def resend_otp(self, **kwargs):

        import json
        import random
        from datetime import timedelta
        from odoo.fields import Datetime

        try:
            email = request.params.get('email')

            if not email:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Email is required'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            patient = request.env['res.partner'].sudo().search([
                ('email', '=', email),
                ('is_patient', '=', True)
            ], limit=1)

            if not patient:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Patient not found'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            otp = str(random.randint(100000, 999999))

            patient.sudo().write({
                'otp_code': otp,
                'otp_expiry': Datetime.now() + timedelta(minutes=10),
            })

            mail_values = {
                'subject': 'Your New Verification Code',
                'body_html': f'<p>Your new OTP code is: <strong>{otp}</strong></p>',
                'email_to': patient.email,
                'email_from': 'zizozizoalturk@gmail.com',
            }

            mail = request.env['mail.mail'].sudo().create(mail_values)
            mail.send()

            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'New OTP sent successfully'
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    @http.route('/api/doctor/available-slots/<int:doctor_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_available_slots(self, doctor_id, **kwargs):
        import json
        from datetime import datetime, timedelta
        import pytz  # مكتبة التحويل الزمني

        try:
            # جلب التاريخ من الرابط (Query Params)
            date_str = request.params.get('date') or kwargs.get('date')

            if not date_str:
                return request.make_response(
                    json.dumps({'success': False, 'error': 'Date is required'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            doctor = request.env['res.users'].sudo().browse(doctor_id)
            if not doctor.exists() or not doctor.is_doctor:
                return request.make_response(
                    json.dumps({'success': False, 'error': 'Doctor not found'}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
            day_code = day_map[target_date.weekday()]

            working_schedule = request.env['working.dr'].sudo().search([
                ('doctor_id', '=', doctor_id),
                ('day', '=', day_code)
            ], limit=1)

            if not working_schedule:
                return request.make_response(
                    json.dumps({'success': False, 'error': 'Doctor is not available on this day'}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # 1. تحديد المنطقة الزمنية (تأكد أنها نفس المنطقة المستخدمة في الحجز)
            user_tz = pytz.timezone('Asia/Riyadh')

            # 2. جلب المواعيد المحجوزة (المخزنة بـ UTC)
            booked_appointments = request.env['the.appointments'].sudo().search([
                ('doctor_id', '=', doctor_id),
                ('app_date', '>=', f'{date_str} 00:00:00'),
                ('app_date', '<=', f'{date_str} 23:59:59'),
                ('state', '!=', 'cancel')
            ])

            # 3. تحويل المواعيد المحجوزة إلى التوقيت المحلي واستخراج (ساعة:دقيقة) فقط
            booked_times = []
            for appointment in booked_appointments:
                # تحويل قيمة الـ Datetime من القاعدة إلى UTC ثم إلى المحلي
                utc_dt = pytz.utc.localize(appointment.app_date)
                local_dt = utc_dt.astimezone(user_tz)
                # تخزين "الساعة:الدقيقة" فقط لضمان دقة المقارنة وتجنب مشاكل الثواني
                booked_times.append(local_dt.strftime('%H:%M'))

            available_slots = []

            # 4. بناء وقت البداية والنهاية بناءً على جدول الطبيب
            # معالجة الكسور (مثل 8.5 لتصبح 08:30)
            start_hour = int(working_schedule.from_hour)
            start_minute = int((working_schedule.from_hour % 1) * 60)

            end_hour = int(working_schedule.to_hour)
            end_minute = int((working_schedule.to_hour % 1) * 60)

            current_time = target_date.replace(
                hour=start_hour,
                minute=start_minute,
                second=0,
                microsecond=0
            )

            end_time = target_date.replace(
                hour=end_hour,
                minute=end_minute,
                second=0,
                microsecond=0
            )

            # 5. توليد الفترات الزمنية
            while current_time < end_time:
                # وقت الفترة الحالية بصيغة ساعة:دقيقة للمقارنة
                slot_compare = current_time.strftime('%H:%M')

                if slot_compare not in booked_times:
                    # إذا لم تكن محجوزة، تضاف للقائمة المتاحة
                    available_slots.append(
                        current_time.strftime('%Y-%m-%d %H:%M:%S')
                    )

                current_time += timedelta(minutes=30)

            return request.make_response(
                json.dumps({
                    'success': True,
                    'doctor_id': doctor.id,
                    'doctor_name': doctor.name,
                    'date': date_str,
                    'available_slots': available_slots
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'success': False, 'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

    # -*- coding: utf-8 -*-

    from odoo import http
    from odoo.http import request
    import json

    class SpecialtyApi(http.Controller):

        @http.route(
            '/api/specialties',
            type='http',
            auth='public',
            methods=['GET'],
            csrf=False,
        )
        def get_specialties(self, **kwargs):

            try:
                specialties = request.env['specialties'].sudo().search([])

                data = []

                for specialty in specialties:
                    data.append({
                        'id': specialty.id,
                        'name': specialty.specialties_name,
                    })

                return request.make_response(
                    json.dumps({
                        'success': True,
                        'count': len(data),
                        'data': data,
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=200,
                )

            except Exception as e:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': str(e),
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400,
                )

        # -*- coding: utf-8 -*-

        from odoo import http
        from odoo.http import request
        import json

        class AdvertisementApi(http.Controller):

            @http.route(
                '/api/advertisements',
                type='http',
                auth='public',
                methods=['GET'],
                csrf=False,
            )
            def get_advertisements(self, **kwargs):

                try:

                    advertisements = request.env['advertisement'].sudo().search([
                        ('active', '=', True)
                    ])

                    data = []

                    for advertisement in advertisements:

                        poster = False

                        if advertisement.poster:
                            poster = advertisement.poster.decode('utf-8')

                        data.append({
                            'id': advertisement.id,
                            'name': advertisement.name,
                            'description': advertisement.description,
                            'poster': poster,
                        })

                    return request.make_response(
                        json.dumps({
                            'success': True,
                            'count': len(data),
                            'data': data,
                        }),
                        headers=[
                            ('Content-Type', 'application/json')
                        ],
                        status=200,
                    )

                except Exception as e:

                    return request.make_response(
                        json.dumps({
                            'success': False,
                            'error': str(e),
                        }),
                        headers=[
                            ('Content-Type', 'application/json')
                        ],
                        status=400,
                    )

