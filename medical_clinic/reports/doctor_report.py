# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DoctorReport(models.AbstractModel):
    _name = 'report.medical_clinic.doctor_report_template'
    _description = 'Doctor Report'

    def _get_report_values(self, docids, data=None):

        domain = []

        if data.get('doctor_id'):
            domain.append(('doctor_id', '=', data.get('doctor_id')))

        if data.get('date_from'):
            domain.append(('app_date', '>=', data.get('date_from')))

        if data.get('date_to'):
            domain.append(('app_date', '<=', data.get('date_to')))

        appointments = self.env['the.appointments'].search(domain)

        result = {}

        for app in appointments:
            doctor = app.doctor_id.name

            if doctor not in result:
                result[doctor] = {
                    'count': 0,
                    'dates': []
                }

            result[doctor]['count'] += 1
            result[doctor]['dates'].append(app.app_date)

        final = []

        for doctor, vals in result.items():
            dates = vals['dates']

            final.append({
                'doctor': doctor,
                'count': vals['count'],
                'first_date': min(dates) if dates else False,
                'last_date': max(dates) if dates else False,
            })

        return {
            'docs': final,
            'date_from': data.get('date_from'),
            'date_to': data.get('date_to'),
        }