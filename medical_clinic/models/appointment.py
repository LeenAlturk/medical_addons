# -*- coding: utf-8 -*-


from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.fields import Datetime


class TheAppointments(models.Model):
    _name = "the.appointments"
    _description = 'Appointments module'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Appointment Id',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )

    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        domain=[('is_patient', '=', True)]
    )

    patient_age = fields.Integer(
        string='Age',
        related='patient_id.age',
        readonly=True
    )

    patient_phone = fields.Char(
        string='Phone',
        related='patient_id.phone',
        readonly=True
    )

    patient_gender = fields.Selection(
        related='patient_id.gender',
        string='Gender',
        readonly=True
    )

    note = fields.Char(string="Note")

    app_date = fields.Datetime(
        string="App Date",
        required=True
    )


    doctor_id = fields.Many2one(
        'res.users',
        string='Doctor',
        required=True,
        domain=[('is_doctor', '=', True)]
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments"
    )
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('confirm', 'confirm'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),

    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    Prescription_ids = fields.One2many('the.prescription',inverse_name='appointment_id')
    chronic_count = fields.Integer(
        string="Chronic Diseases",
        compute="_compute_chronic_count"
    )
    test_count = fields.Integer(string='Medical Request',compute="get_test_count")
    app_rev_count =fields.Integer(string="App Revision" ,compute="get_rev_app_count")
    weight = fields.Float(string="Weight" )
    Height = fields.Float(string="Height")
    blood_Pressure=fields.Float(string='', digits=(16, 2))
    temperature=fields.Integer(string='Temperature')
    pulse_rate = fields.Float(string = "plus Rate")
    Media_Diagnosis=fields.Text(string='Media Diagnosis')

    consultation_fee = fields.Monetary(
        related='doctor_id.consultation_fee',
        currency_field='currency_id',
        store=True,
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    invoice_id = fields.Many2one(
        'clinic.invoice',
        string='Invoice',
        readonly=True
    )

    invoice_count= fields.Float(string='Count', compute='_invoice_count_field', store=True)

    @api.depends('invoice_id')
    def _invoice_count_field(self):

        for record in self:
            record.invoice_count = 1 if record.invoice_id else 0


    def get_test_count(self):
        for record in self:
            record.test_count = self.env['labtest'].search_count([
                ('appointment_id', '=', record.id)
            ])

    def get_rev_app_count(self):
        for record in self:
            record.app_rev_count = self.env["next.appointments"].search_count([
                ('last_appointment_id', '=', record.id)
            ])



    def action_test_req(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Medical Tests',
            'res_model': 'labtest',
            'view_mode': 'list,form',
            'domain': [('appointment_id', '=', self.id)],
        }

    def action_app_rev(self):
        self.ensure_one()
        return {
            'type' :'ir.actions.act_window',
            'name':'Next app',
            'res_model':'next.appointments',
            'view_mode':'list,form',
            'domain':[('last_appointment_id', '=', self.id)]
        }

    def action_view_invoice(self):
        self.ensure_one()

        if not self.invoice_id:
            return  False

        return{
            'type':'ir.actions.act_window',
            'res_model':'clinic.invoice',
            'view_mode':'form',
            'res_id' :self.invoice_id.id,
            'target' : "current",

        }





    @api.depends('patient_id')
    def _compute_chronic_count(self):
        for rec in self:
            rec.chronic_count = len(rec.patient_id.chronic_disease_ids)


    def action_view_chronic(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chronic Diseases',
            'res_model': 'chronic.disease',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {'default_patient_id': self.patient_id.id},
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'the.appointments.sequence'
                ) or _('New')
        return super().create(vals_list)

    def button_in_confirm(self):
        self.write({'state': "confirm"})

    def button_in_done(self):
        for rec in self:
            if not rec.Media_Diagnosis:
                raise ValidationError("please Add Medical Diagnosis of your patient")
            if not rec.Prescription_ids:
                raise ValidationError('please Add Prescription of your patient')


        self.write({'state': "done"})

    def button_in_scheduled(self):
        self.write({'state': "scheduled"})

    def write(self, vals):
        for rec in self:
            if rec.state == 'done':
                if 'state' in vals:
                    continue
                raise ValidationError("You are not able to Edit done appointment")
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise ValidationError("You are not able to Delete done appointment")

        return super().unlink()

    @api.constrains('app_date', 'doctor_id')
    def _check_available(self):
        from datetime import timedelta
        import pytz

        for rec in self:
            if not rec.app_date or not rec.doctor_id:
                continue

            # 1. تحديد المنطقة الزمنية (اجعلها ثابتة أو اجلبها من إعدادات الطبيب)
            tz_name = self.env.user.tz or 'Asia/Riyadh'
            user_tz = pytz.timezone(tz_name)

            # 2. تحويل وقت الموعد (المخزن بـ UTC) إلى وقت المنطقة الزمنية المطلوبة
            # نستخدم pytz.utc.localize لإخبار النظام أن الوقت القادم من القاعدة هو UTC
            utc_dt = pytz.utc.localize(rec.app_date)
            local_dt = utc_dt.astimezone(user_tz)

            # 3. حساب اليوم والساعة بناءً على الوقت المحلي المحول
            day_index = local_dt.weekday()
            map_days = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
            day = map_days.get(day_index)

            # تحويل الساعة والدقائق إلى رقم عشري (مثلاً 15:30 تصبح 15.5)
            hour = local_dt.hour + (local_dt.minute / 60.0)

            # 4. البحث في جدول الطبيب
            schedules = self.env['working.dr'].sudo().search([
                ('doctor_id', '=', rec.doctor_id.id),
                ('day', '=', day)
            ])

            if not schedules:
                raise ValidationError(_("Doctor Not Working in this Day (%s)") % day)

            valid = any(s.from_hour <= hour <= s.to_hour for s in schedules)
            if not valid:
                raise ValidationError(_("Time (%.2f) out of Doctor Working Hours") % hour)
    @api.constrains('app_date', 'doctor_id')
    def _check_double_booking(self):
        for rec in self:
            if not rec.app_date or not rec.doctor_id:
                continue

            conflict = self.search([
                ('doctor_id', '=', rec.doctor_id.id),
                ('app_date', '=', rec.app_date),
                ('id', '!=', rec.id)
            ])

            if conflict:
                raise ValidationError(" This Time already Taken")

    def action_create_revision(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Revision',
            'res_model': 'next.appointments',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.doctor_id.id,
                'default_last_appointment_id': self.id,
            }
        }
    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
             raise ValidationError(_('Validation error message'))

        invoice= self.env['clinic.invoice'].create({
               'patient_id': self.patient_id.id,
               'appointment_id': self.id,
               'consultation_fee': self.consultation_fee,
        })
        self.invoice_id = invoice.id
        return {
         'type' : 'ir.actions.act_window',
         'res_model': 'clinic.invoice',
         'view_mode':'form',
         'res_id': invoice.id,
         'target': 'current',
        }

    def action_create_lab_test(self):
        self.ensure_one()
        lab_test = self.env['labtest'].create({
                'patient_id' :self.patient_id.id,
                'doctor_id' :self.doctor_id.id,
                'appointment_id':self.id,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model':'labtest',
            'view_mode': 'form',
            'res_id': lab_test.id,
            'target' :'current',
        }