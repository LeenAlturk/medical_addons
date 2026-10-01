from odoo import  fields,models,api

class MedicalTestWizard(models.TransientModel):
    _name = 'medical.test.wizard'
    _description = 'Medical.test.wizard'

    appointment_id=fields.Many2one(
        comodel_name='the.appointments',
        string="appointment Number"
    )
    type = fields.Selection([
            ('request', 'Request'),
            ('result', 'Result')
      ], string='Report Type', default='request')

    category = fields.Selection(
        [
            ('lab', 'Laboratory'),
            ('radio', 'Radiology'),
            ('cardio', 'Cardiology'),
            ('other', 'Other'),
        ],
        required=True,
        default='lab'
    )

    def action_print(self):
            data = {
                'appointment_id': self.appointment_id.id,
                'type': self.type,
                'category': self.category,
                'print_date':fields.Date.today()
            }

            return self.env.ref('medical_clinic.medical_tests_action_report').report_action(self, data=data)




