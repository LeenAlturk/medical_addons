from odoo import models, fields
from odoo.exceptions import ValidationError

class PatientReportWizard(models.TransientModel):
    _name = 'patient.report.wizard'
    _description = 'Patient Report Wizard'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    patient_id = fields.Many2one('res.partner')

    def action_print_report(self):

        if self.date_from > self.date_to:
            raise ValidationError("From Date must be before To Date")

        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'patient_id': self.patient_id.id if self.patient_id else False,
        }

        return self.env.ref('medical_clinic.patient_report_action').report_action(self, data=data)