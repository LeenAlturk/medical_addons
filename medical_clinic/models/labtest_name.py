# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LabtestName(models.Model):
    """ This model represents labtest.name."""
    _name = 'labtest.name'
    _description = 'LabtestName'

    name = fields.Char(
        string="Test Name",
        required=True
    )

    category = fields.Selection([
        ('lab', 'Laboratory'),
        ('radio', 'Radiology'),
        ('cardio', 'Cardiology'),
        ('other', 'Other'),
    ], string="Category", required=True)

