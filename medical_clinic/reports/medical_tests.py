from odoo import models
from odoo.exceptions import UserError


class MedicalTestReport(models.AbstractModel):
    _name = "report.medical_clinic.medical_tests_document"
    _description = "Medical Test"

    def _get_report_values(self, docids, data=None):

        domain = []

        if data.get("appointment_id"):
            domain.append(("appointment_id", "=", data.get("appointment_id")))

        labtest = self.env["labtest"].search(domain, limit=1)

        if not labtest:
            raise UserError("No Medical Test Request Found.")

        return {
            "doc_ids": labtest.ids,
            "doc_model": "labtest",
            "docs": labtest,
            "data": data,
        }