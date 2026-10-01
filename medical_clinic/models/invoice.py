from  odoo import models,api,fields,_
from odoo.exceptions import ValidationError
class ClinicInvoice(models.Model):

    _name ="clinic.invoice"
    _description = "Clinic Invoice"
    name = fields.Char(
        string='invoice Number',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True
    )

    appointment_id = fields.Many2one(
        'the.appointments',
        string='Appointment'
    )

    invoice_date = fields.Date(
        default=fields.Date.today
    )

    consultation_fee = fields.Monetary(
        string='Consultation Fee',
        currency_field='currency_id'
    )

    extra_fees = fields.Monetary(
        string='Extra Fees',
        currency_field='currency_id'
    )

    total_amount = fields.Monetary(
        string='Total Amount',
        currency_field='currency_id',
        compute='_compute_total',
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], default='draft')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'inv.sequence'
                ) or _('New')
        return super().create(vals_list)

    def mark_as_paid(self):
          self.state = 'paid'

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state ='draft'

    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
            self.consultation_fee = self.appointment_id.consultation_fee
            self.state =self.appointment_id.state

    @api.depends('consultation_fee', 'extra_fees')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = rec.consultation_fee + rec.extra_fees