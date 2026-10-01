# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.fields import Datetime


class NexAppointments(models.Model):
    _name = "next.appointments"
    _description = "Next Appointments"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Next Appointment ID",
        readonly=True,
        copy=False,
        default=lambda self: _('New')
    )

    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        domain=[('is_patient', '=', True)],
        tracking=True
    )

    doctor_id = fields.Many2one(
        'res.users',
        string='Doctor',
        required=True,
        domain=[('is_doctor', '=', True)],
        tracking=True
    )

    next_app_date = fields.Datetime(
        string="Next Appointment Date",
        required=True,
        tracking=True
    )

    note = fields.Text(string="Note")

    last_appointment_id = fields.Many2one(
        'the.appointments',
        string="Last Appointment"
    )

    # 🔹 تاريخ آخر موعد (للعرض فقط)
    last_app_date = fields.Datetime(
        string="Last Appointment Date",
        related='last_appointment_id.app_date',
        readonly=True
    )

    # 🔹 طبيب آخر موعد
    last_doctor_id = fields.Many2one(
        'res.users',
        string="Last Appointment Doctor",
        related='last_appointment_id.doctor_id',
        readonly=True
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

    def button_in_confirm(self):
        self.write({'state': "confirm"})

    def button_in_done(self):
        self.write({'state': "done"})

    def button_in_scheduled(self):
        self.write({'state': "scheduled"})
    @api.depends('patient_id')
    def _compute_last_appointment(self):
        for record in self:
            if record.patient_id:
                last_app = self.env['the.appointments'].search(
                    [('patient_id', '=', record.patient_id.id)],
                    order='app_date desc',
                    limit=1
                )
                record.last_appointment_id = last_app
            else:
                record.last_appointment_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'next.appointments.sequence'
                ) or _('New')
        return super().create(vals_list)

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

    @api.constrains('next_app_date','doctor_id')
    def _check_available(self):
        for rec in self:
            if not rec.next_app_date or not rec.doctor_id:
                continue
            local_dt = Datetime.context_timestamp(self, rec.next_app_date)
            day_index = local_dt.weekday()
            map_days = {
                0: 'mon',
                1: 'tue',
                2: 'wed',
                3: 'thu',
                4: 'fri',
                5: 'sat',
                6: 'sun',
            }
            day = map_days.get(day_index)
            local_dt = fields.Datetime.context_timestamp(self, rec.next_app_date)
            hour = local_dt.hour + (local_dt.minute / 60.0)

            schedules = self.env['working.dr'].search([
                ('doctor_id', '=', rec.doctor_id.id),
                ('day', '=', day)
            ])
            if not schedules:
                raise ValidationError("Doctor Not Working in this Day")

            valid = any(s.from_hour <= hour <= s.to_hour for s in schedules)
            if not valid:
                raise ValidationError("Time out of Doctor Working Hour")

    @api.constrains('next_app_date', 'doctor_id')
    def _check_double_booking(self):
        for rec in self:
            if not rec.next_app_date or not rec.doctor_id:
                continue

            conflict = self.search([
                ('doctor_id', '=', rec.doctor_id.id),
                ('next_app_date', '=', rec.next_app_date),
                ('id', '!=', rec.id)
            ])

            if conflict:
                raise ValidationError(" This Time already Taken")

