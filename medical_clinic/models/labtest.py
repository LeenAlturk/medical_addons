# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Labtest(models.Model):
    _name = 'labtest'
    _description = 'Labtest'

    name = fields.Char(
        string='Request Number',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )

    appointment_id = fields.Many2one(
        'the.appointments',
        string="Appointment",
        required=True
    )

    patient_id = fields.Many2one(
        'res.partner',
        string="Patient",
        readonly=True
    )

    doctor_id = fields.Many2one(
        'res.users',
        string="Doctor",
        readonly=True
    )

    request_date = fields.Date(
        default=fields.Date.today
    )

    laboratory_line_ids = fields.One2many(
        'labtest.line',
        'laboratory_request_id',
        string='Laboratory'
    )

    radiology_line_ids = fields.One2many(
        'labtest.line',
        'radiology_request_id',
        string='Radiology'
    )

    cardiology_line_ids = fields.One2many(
        'labtest.line',
        'cardiology_request_id',
        string='Cardiology'
    )

    other_line_ids = fields.One2many(
        'labtest.line',
        'other_request_id',
        string='Other'
    )

    laboratory_test_ids = fields.Many2many(
        'labtest.name',
        'labtest_laboratory_rel',
        'labtest_id',
        'test_id',
        string='Laboratory Tests',
        domain="[('category','=','lab')]"
    )

    radiology_test_ids = fields.Many2many(
        'labtest.name',
        'labtest_radiology_rel',
        'labtest_id',
        'test_id',
        string='Radiology Tests',
        domain="[('category','=','radio')]"
    )

    cardiology_test_ids = fields.Many2many(
        'labtest.name',
        'labtest_cardiology_rel',
        'labtest_id',
        'test_id',
        string='Cardiology Tests',
        domain="[('category','=','cardio')]"
    )

    other_test_ids = fields.Many2many(
        'labtest.name',
        'labtest_other_rel',
        'labtest_id',
        'test_id',
        string='Other Tests',
        domain="[('category','=','other')]"
    )
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'lab.sequence'
                ) or _('New')
        return super().create(vals_list)

    # ---------------- Laboratory ----------------

    @api.onchange('laboratory_test_ids')
    def _onchange_laboratory_test_ids(self):
        for record in self:

            current_tests = record.laboratory_line_ids.mapped('test_type_id')

            for test in record.laboratory_test_ids:
                if test not in current_tests:
                    record.laboratory_line_ids += self.env['labtest.line'].new({
                        'test_type_id': test.id,
                    })

            for line in record.laboratory_line_ids[:]:
                if line.test_type_id not in record.laboratory_test_ids:
                    record.laboratory_line_ids -= line

    # ---------------- Radiology ----------------
    @api.onchange('radiology_test_ids')
    def _onchange_radiology_test_ids(self):
        for record in self:

            current_tests = record.radiology_line_ids.mapped('test_type_id')

            for test in record.radiology_test_ids:
                if test not in current_tests:
                    record.radiology_line_ids += self.env['labtest.line'].new({
                        'test_type_id': test.id,
                    })

            for line in record.radiology_line_ids[:]:
                if line.test_type_id not in record.radiology_test_ids:
                    record.radiology_line_ids -= line

    # ---------------- Cardiology ----------------
    @api.onchange('cardiology_test_ids')
    def _onchange_cardiology_test_ids(self):
        for record in self:

            current_tests = record.cardiology_line_ids.mapped('test_type_id')

            for test in record.cardiology_test_ids:
                if test not in current_tests:
                    record.cardiology_line_ids += self.env['labtest.line'].new({
                        'test_type_id': test.id,
                    })

            for line in record.cardiology_line_ids[:]:
                if line.test_type_id not in record.cardiology_test_ids:
                    record.cardiology_line_ids -= line
    # ---------------- Other ----------------

    @api.onchange('other_test_ids')
    def _onchange_other_test_ids(self):
        for record in self:

            current_tests = record.other_line_ids.mapped('test_type_id')

            for test in record.other_test_ids:
                if test not in current_tests:
                    record.other_line_ids += self.env['labtest.line'].new({
                        'test_type_id': test.id,
                    })

            for line in record.other_line_ids[:]:
                if line.test_type_id not in record.other_test_ids:
                    record.other_line_ids -= line