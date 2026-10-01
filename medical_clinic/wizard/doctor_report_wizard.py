from odoo import models,fields

class DoctorReportWizard (models.TransientModel):
    _name = 'doctor.report.wizard'
    _description = 'Doctor Report Wizard'
    date_from =fields.Date()
    date_to =fields.Date()
    doctor_id=fields.Many2one('res.users')

    def action_print_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'doctor_id': self.doctor_id.id if self.doctor_id else False,
        }

        return self.env.ref('medical_clinic.doctor_report_action').report_action(self,data=data)

