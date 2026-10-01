# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class Patient(models.Model):

    _inherit = 'res.partner'
    name = fields.Char(
        default='Patient'
    )
    is_patient = fields.Boolean(string="Is Patient" , default = True)
    is_active_patient = fields.Boolean(
        string="Active Patient",
        compute="_compute_active_patient",
        store=True
    )
    birthdate = fields.Date(string="Birthdate")
    #age = fields.Integer(string="Age")
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string="Gender"
    )
    chronic_disease_ids = fields.One2many(
        'chronic.disease',
        'patient_id',
        string="Chronic Diseases"
    )
    app_count=fields.Integer(string='Count',compute='get_app_count')
    next_app=fields.Integer(string='Next_Appointments' ,compute='get_next_app_count')
    appointment_ids = fields.One2many(
        'the.appointments',
        'patient_id',
        string="Appointments"
    )

    password = fields.Char(string="Password")
    otp_code = fields.Char(string="OTP Code")
    otp_expiry = fields.Datetime(string="OTP Expiry")
    is_verified = fields.Boolean(string="Verified", default=False)

    def get_appointments(self):
        action = {
            'name' :'appointments',
            'res_model':'the.appointments',
            'view_mode':'list,form',
            'type': 'ir.actions.act_window',
            'domain':[('patient_id','=', self.id)]
        }
        return action

    def get_app_count(self):
        count=self.env['the.appointments'].search_count([('patient_id','=',self.id)])
        self.app_count = count
    def get_next_app(self):
        action = {
            'name': 'next appointments',
            'res_model': 'next.appointments',
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
            'domain':[('patient_id','=', self.id)]
        }
        return action

    def get_next_app_count(self):
        next_count=self.env['next.appointments'].search_count([('patient_id','=',self.id)])
        self.next_app =next_count

    @api.depends('birthdate')
    def _compute_age(self):
        for rec in self:
            if rec.birthdate:
                # Calculate difference between today and birthdate
                age = relativedelta(date.today(), rec.birthdate).years
                rec.age = age
            else:
                rec.age = 0

    @api.depends('appointment_ids')
    def _compute_active_patient(self):
        for rec in self:
            rec.is_active_patient = len(rec.appointment_ids) > 0


