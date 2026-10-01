# -*- coding: utf-8 -*-
{
    'name': "Al Rahma clinic",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',
        'views/doctor_view.xml',
        'reports/prescription_report.xml',
        'views/Appitments.xml',
        'views/nextapp.xml',
        'views/medicine.xml',
		'views/Specialties.xml',
		'views/WorkingDr.xml',
		'views/patient_report_wizard_view.xml',
		'reports/patient_report.xml',
		'views/doctor_report_wizard.xml',
		'reports/doctor_report.xml',
		'views/advertisement.xml',
        'reports/invoice_report.xml',
		'views/invoice.xml',
		'views/dashboard.xml',
		'views/labtest.xml',
		'views/lab_test_name.xml',
		'views/Medical_test_wizard.xml',
		'reports/medical_tests.xml',
],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

