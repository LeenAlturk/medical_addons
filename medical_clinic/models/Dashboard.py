# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Dashboard(models.Model):
    """ This model represents dashboard."""

    _name = 'clinic.dashboard'
    _description = 'Dashboard'
    name = fields.Char(
        default='Dashboard'
    )
    patient_count = fields.Integer(string='patient count', compute='_compute_count')
    doctor_count = fields.Integer(string='Doctor Count', compute='_compute_count')
    appointment_count = fields.Integer(
        compute='_compute_count'
    )

    invoice_count = fields.Integer(
        compute='_compute_count'
    )


    def _compute_count(self):
        """Compute the value of the field computed_field."""
        for record in self:
            record.patient_count = self.env['res.partner'].search_count([('is_patient','=',True )])
            record.doctor_count=self.env['res.users'].search_count([('is_doctor','=', 'True')])
            record.appointment_count=self.env['the.appointments'].search_count([])
            record.invoice_count = self.env['clinic.invoice'].search_count([])

    def action_open_patients(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patients',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('is_patient', '=', True)],
        }

    def action_open_doctors(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Doctors',
            'res_model': 'res.users',
            'view_mode': 'list,form',
            'domain': [('is_doctor', '=', True)],
        }

    def action_open_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments',
            'res_model': 'the.appointments',
            'view_mode': 'list,form',
        }

    def action_open_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'clinic.invoice',
            'view_mode': 'list,form',
        }