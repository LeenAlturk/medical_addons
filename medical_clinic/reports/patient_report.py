from odoo import models

class PatientReport(models.AbstractModel):
    _name = 'report.medical_clinic.patient_report_template'
    _description = 'Patient Report'

    def _get_report_values(self, docids, data=None):
        appointments = self._get_appointments(data)

        result = []

        for app in appointments:
            next_app = self._get_next_appointment(app)
            result.append(self._prepare_line(app, next_app))

        return {'docs': result}



    def _get_appointments(self, data):
        domain = []

        if data.get('patient_id'):
            domain.append(('patient_id', '=', data.get('patient_id')))

        if data.get('date_from'):
            domain.append(('app_date', '>=', data.get('date_from')))

        if data.get('date_to'):
            domain.append(('app_date', '<=', data.get('date_to')))

        return self.env['the.appointments'].search(domain)


    def _get_next_appointment(self, app):
        return self.env['next.appointments'].search([
            ('last_appointment_id', '=', app.id)
        ], limit=1)

    def _prepare_line(self, app, next_app):
        return {
            'patient': app.patient_id.name,
            'visit_date': app.app_date,
            'next_date': next_app.next_app_date if next_app else False,
            'doctor':app.doctor_id.name,
        }

