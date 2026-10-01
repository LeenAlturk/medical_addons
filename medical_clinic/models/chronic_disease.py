# -*- coding: utf-8 -*-
from odoo import api, fields, models
class ChronicDisease(models.Model):
    _name = 'chronic.disease'
    _description = 'Chronic Disease'

    patient_id = fields.Many2one('res.partner', string="Patient")
    name = fields.Char(string="Disease Name")
    notes = fields.Text(string="Notes")
    status = fields.Selection(
        [('active', 'Active'),
         ('controlled', 'Controlled')],
        string="Status"
    )

