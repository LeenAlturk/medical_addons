# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Doctor( models.Model):
    _inherit = 'res.users'
    is_doctor= fields.Boolean(string="is_doctor")
    is_supervisor = fields.Boolean(string="is supervisor")

    appointment_ids = fields.One2many('the.appointments', 'doctor_id')
    specialties_ids = fields.Many2many(
        'specialties',
        'doctor_specialties_rel',
        'doctor_id',
        'specialty_id',
        string="Specialties"
    )
    working_hours_ids = fields.One2many(
        'working.dr',
        'doctor_id',
        string="Working Hours"
    )
    consultation_fee = fields.Monetary(
        string='Consultation Fee',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id
    )
    show_clinic_info = fields.Boolean(
        compute="_compute_show_clinic_info"
    )

    @api.depends("groups_id")
    def _compute_show_clinic_info(self):
        doctor_group = self.env.ref("medical_clinic.group_doctor")
        for user in self:
            user.show_clinic_info = doctor_group in user.groups_id

    @api.onchange("groups_id")
    def _onchange_groups_id(self):
        doctor_group = self.env.ref("medical_clinic.group_doctor")
        self.show_clinic_info = doctor_group in self.groups_id

