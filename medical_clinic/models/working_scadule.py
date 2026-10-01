# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WorkingDr(models.Model):
    _name = 'working.dr'
    _description = 'Working Doctor Schedule'

    day = fields.Selection([
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
    ], string="Day")

    from_hour = fields.Float(string="From Hour", required=True)
    to_hour = fields.Float(string="To Hour", required=True)

    doctor_id = fields.Many2one(
        'res.users',
        string="Doctor"
    )
    @api.constrains('from_hour','to_hour')
    def _check_hours(self):
        for rec in self:
            if rec.from_hour >= rec.to_hour:
                raise ValidationError(" From Hour must be less than To Hour")
