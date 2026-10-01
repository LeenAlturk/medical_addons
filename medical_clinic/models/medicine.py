# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.api import readonly


class Medicine(models.Model):
    _name = "the.medicine"
    _description = "Medicine"
    _rec_name = "m_name"
    m_name = fields.Char(string="Medicine Name", required=True)

    effective_material = fields.Char(
        string="Active Ingredient",
        required=True
    )

    prescription_ids = fields.One2many(
        'the.prescription',
        'medicine_id',
        string="Prescriptions"
    )
    type = fields.Selection([
        ('tablet', 'Tablet'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
    ])
    company = fields.Char(string="Manufacturer")
    lotNo = fields.Char(string='LotNo')

