# coding: utf-8
from openerp import fields, models, api

class hr_special_days(models.Model):
    _inherit = 'hr.payslip.run'

    STATES_VALUES = [
            ('draft', 'Draft'),
            ('done', 'Confirmado'),
            ('close', 'Close'),
        ]

    state = fields.Selection(STATES_VALUES, 'Status', select=True, readonly=True, copy=False)

    @api.multi
    def hr_payslip_multi(self):
        for payroll in self:
            payroll.slip_ids.signal_workflow('hr_verify_sheet')     #rEALIZA EL CALCULO DE LA NOMINA
            payroll.slip_ids.signal_workflow('process_sheet')       #REALIZA LOS ASIENTOS CONTABLES
        self.write({'state': 'done'})