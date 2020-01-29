#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, tools, api, _
from openerp.osv import osv

class hr_payslip_struct(models.Model):
    _inherit = "hr.payslip.run"
    _description = "Nomina Especial"

    check_special_struct = fields.Boolean('Nomina Especial')
    struct_id = fields.Many2one('hr.payroll.structure', 'Tipo de Nomina Especial', states={'draft': [('readonly', False)]}, )

    @api.onchange('check_special_struct')
    def onchange_check_special_struct(self):
        res = {}
        if self.check_special_struct == False:
           res = {'value': {'struct_id_payroll': False}}

        return res

class hr_payroll_structure_special(models.Model):
    _inherit = 'hr.payroll.structure'
    _description = "Employee familiar"

    STRUCT_CATEGORY = [
        ('normal', 'Normal'),
        ('especial', 'Especial'),
    ]

    PAYROLL_CATEGORY =[
        ('ticket', 'Cestatickets'),
        ('fideicomiso', 'Fideicomiso'),
        ('vacaciones', 'Vacaciones'),
        ('utilidad', 'Utilidades'),
        ('liquidacion', 'Liquidaciones'),
        ('militar', 'Militar'),
        ('habitacional', 'Banavih'),
        ('gurderia', 'Guarderia'),
    ]

    DEDUCTION_MODE = [
        ('star_m', 'Principio de Mes'),
        ('end_m', 'Fin de Mes'),
        ('iq', 'Cada pago')
    ]

    struct_category = fields.Selection(STRUCT_CATEGORY, 'Categoria de Nomina', select=True, required=True)
    struct_id_payroll_category = fields.Selection(PAYROLL_CATEGORY, 'Referencia de Nomina')
    struct_id_reference = fields.Many2one('hr.payroll.reference', 'Referencia de Nomina')
    deductions_pay_mode = fields.Selection(DEDUCTION_MODE, 'Decuentos a:')

class hr_contract(osv.osv):
    _inherit = 'hr.contract'

    @api.cr_uid_ids_context
    def get_all_structures(self, cr, uid, contract_ids, context=None):
        # ret = super(hr_contract, self).get_all_structures(cr, uid, contract_ids, context=context)
        is_special = context.get('is_special', False)
        #Si es una nomina especial asigna el mismo id de nomina a cada contrato
        if is_special and is_special == 1:
            structure_ids = [context.get('special_id', False)]
        else:
            structure_ids = [contract.struct_id.id for contract in self.browse(cr, uid, contract_ids, context=context) if contract.struct_id]

        if not structure_ids:
            return []
        return list(set(self.pool.get('hr.payroll.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))


class hr_payslip_employees(osv.osv_memory):
    _inherit = 'hr.payslip.employees'

    @api.cr_uid_id_context
    def compute_sheet(self, cr, uid, ids, context=None):
        active_id = context.get('active_id', False)
        special_fields = self.pool.get('hr.payslip.run').read(cr, uid, active_id, ['check_special_struct', 'struct_id'])
        is_special = special_fields['check_special_struct'] if special_fields else False
        if is_special:
            context.update({'is_special':1,
                            'special_id' : special_fields['struct_id'][0]})
        context.update({'come_from': 'hr.payslip.employees'})
        ret = super(hr_payslip_employees, self).compute_sheet(cr, uid, ids, context=context)

        return ret

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'

    @api.cr_uid_id_context
    def compute_sheet(self, cr, uid, ids, context=None):
        ctx = context.copy()
        payslip_run_obj = self.pool.get('hr.payslip.run')
        come_from = ctx.get('come_from', False)
        if come_from and come_from == 'payoff':
            for ps in self.browse(cr, uid, ids, context=ctx):
                ctx.update({'is_special': 1, 'special_id': ps.struct_id.id,'slip_id':ids[0]})
        else:
            for ps in self.browse(cr,uid,ids,context=ctx):
                for psr in payslip_run_obj.browse(cr, uid, ps.payslip_run_id.id, context=ctx):
                    is_special = psr.check_special_struct
                    if is_special:
                        ctx.update({'is_special': 1,'special_id': psr.struct_id.id})
        ret = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=ctx)

        return ret

class hr_payroll_reference(models.Model):
    _name = 'hr.payroll.reference'
    _description = "Referencia para Nominas Especiales"

    name = fields.Char('Referencia de Nómina', size=20)
    description = fields.Char('Descripcion de la Referencia de Nómina')