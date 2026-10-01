# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Specialties(models.Model):
    _name = 'specialties'
    _description = 'Specialties'
    _rec_name ="specialties_name"
    specialties_name = fields.Char()
    doctor_ids = fields.Many2many(
        'res.users',
        'doctor_specialties_rel',
        'specialty_id',
        'doctor_id',
        string="Doctors"
    )
