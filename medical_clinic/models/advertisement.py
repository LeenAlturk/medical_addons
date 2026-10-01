# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Advertisement(models.Model):
    """ This model represents advertisement."""
    _name = 'advertisement'
    _description = 'Advertisement'

    name = fields.Char(string=' Advertisement Name', required=True)
    description=fields.Char(string="Description", required=True)
    active = fields.Boolean(default=True)
    poster = fields.Image(string="Photo",required=True)

