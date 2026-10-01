# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Prescription(models.Model):
    _name = "the.prescription"
    _description = "Prescription"

    medicine_id = fields.Many2one(
        'the.medicine',
        string="Medicine",
        required=True
    )

    dosage = fields.Float(string="Dosage", required=True)
    unit = fields.Selection([
        ('mg', 'mg'),
        ('ml', 'ml'),
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
    ], string="Unit", required=True)

    frequency = fields.Integer(string="Times per Day", default=1)

    time = fields.Selection([
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('night', 'Night'),
        ('morning/night', 'Morning/Night'),
        ('morning/evening', 'Morning/Evening'),
        ('night/evening', 'Night/Evening'),
    ], string='Time', default='morning')
    food_relation = fields.Selection([
        ('before_food', 'Before Food'),
        ('after_food', 'After Food'),
    ], string="Food Relation", default='after_food')

    duration = fields.Integer(string="Duration (Days)")

    start_date = fields.Date(string="Start Date", default=fields.Date.today)

    prn = fields.Boolean(string="As Needed")

    notes = fields.Text(string="Notes")

    appointment_id = fields.Many2one(
        'the.appointments',
        string='Appointment'
    )
    @api.constrains('dosage')
    def _check_dosage(self):
        for rec in self:
            if rec.dosage <= 0:
                raise ValidationError("Dosage must be greater than zero.")

    @api.constrains('frequency')
    def _check_frequency(self):
        for rec in self:
            if rec.frequency <= 0:
                raise ValidationError("Frequency must be at least 1.")
