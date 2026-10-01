# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LabtestLine(models.Model):
    """ This model represents labtest.line."""
    _name = 'labtest.line'
    _description = 'LabtestLine'
    laboratory_request_id = fields.Many2one(
        'labtest',
        string='Laboratory Request',
        ondelete='cascade'
    )

    radiology_request_id = fields.Many2one(
        'labtest',
        string='Radiology Request',
        ondelete='cascade'
    )

    cardiology_request_id = fields.Many2one(
        'labtest',
        string='Cardiology Request',
        ondelete='cascade'
    )

    other_request_id = fields.Many2one(
        'labtest',
        string='Other Request',
        ondelete='cascade'
    )
    test_type_id = fields.Many2one(
        'labtest.name',
        string='Test',

    )
    Result = fields.Text(
        string="Result",

    )

    Description=fields.Text(
        string="Description",

    )

    Doctor_Notes=fields.Text(
        string="Doctor Notes",

    )

    category = fields.Selection(
        related='test_type_id.category',
        store=True,
        readonly=True
    )

    Result_Date = fields.Datetime(string="Result Date" )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments"
    )






