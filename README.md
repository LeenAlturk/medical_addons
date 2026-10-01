# Medical Clinic Management System

An Odoo 18 custom module for managing clinic operations, patients, appointments, consultations, diagnoses, prescriptions, medical reports, and invoicing.

## Overview

The Medical Clinic Management System is a custom Odoo module developed to simplify and organize daily clinic operations through an integrated workflow.

The module connects patient management, appointments, medical consultations, prescriptions, reports, and billing within Odoo.

## Features

- Patient Management
- Doctor Management
- Appointment Management
- Medical Consultations
- Vital Signs
- Diagnosis Management
- Prescription Management
- Medical Reports
- Patient Visit History
- Consultation Fees
- Invoice Management
- Appointment-to-Invoice Integration
- Smart Buttons for related records
- Custom PDF Reports
- Search and Filter Views

## Main Workflow

The basic workflow is:

Patient
→ Appointment
→ Medical Consultation
→ Diagnosis / Prescription
→ Medical Report
→ Invoice

## Technical Stack

- Odoo 18
- Python
- XML
- PostgreSQL
- Odoo ORM
- QWeb Reports

## Module Structure

```text
medical_addons/
└── medical_clinic/
    ├── models/
    ├── views/
    ├── wizard/
    ├── reports/
    ├── security/
    ├── data/
    ├── __init__.py
    └── __manifest__.py
