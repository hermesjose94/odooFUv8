# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Change:  **  12/05/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para el modulo de contratos
#
# ##############################################################################################################################################################################

from openerp import fields, models, api
from openerp.osv import osv
from datetime import datetime
from dateutil import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    dias_acum_fideicomiso = fields.Integer('Dias acumulados fideicomiso')
    dias_adic_fideicomiso = fields.Integer('Dias adicionales fideicomiso')
    total_acum_anticipo_ps = fields.Float('Total Anticipos pretacioens sociales')
    total_acum_ps = fields.Float('Total cumulado prestaciones sociales')
    vacaciones_vencidas_check = fields.Boolean('Vacaciones vencidas')
    vacaciones_vencidas_value = fields.Float('Vacaciones vencidas')
    vacaciones_fraccionadas_check = fields.Boolean('Vacaciones fraccionadas')
    literal_a =  fields.Boolean('Literal A')
    literal_b =  fields.Boolean('Literal B')
    literal_c =  fields.Boolean('Literal C')

hr_contract()

class hr_payslip_run(models.Model):
    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'

    @api.v7
    def close_payslip_run(self, cr, uid, ids, context=None):
        config_obj = self.pool.get('hr.config_parameter')
        if context is None: context = {}
        if not hasattr(ids, '__iter__'): ids = [ids]
        for pro in self.browse(cr, uid, ids, context):
            if pro.check_special_struct and config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.nomina.prestaciones',True) in pro.struct_id.code:
                self.actualiza_dias_acum_fi(cr, uid, pro.slip_ids)
        res = super(hr_payslip_run, self).close_payslip_run(cr, uid, ids, context)
        return res

    @api.v7
    def actualiza_dias_acum_fi(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        payslip_ids = payslip_obj.search(cr, uid, [('id', '=', [s.id for s in ids])])
        payslips = payslip_obj.browse(cr, uid, payslip_ids, context)
        for p in payslips:
            acumulado = p.contract_id.dias_acum_fideicomiso + p.dias_acumulados
            adicionales = p.contract_id.dias_adic_fideicomiso + p.dias_adicionales
            contract_obj.write(cr, uid, [p.contract_id.id], {
                    'dias_acum_fideicomiso': acumulado,
                    'dias_adic_fideicomiso': adicionales}, context=None)

    @api.v7
    def close_payslip_run(self, cr, uid, ids, context=None):
        res = super(hr_payslip_run, self).close_payslip_run(cr, uid, ids, context=context)
        payslip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        fi_hist_obj = self.pool.get('hr.historico.fideicomiso')
        config_obj = self.pool.get('hr.config_parameter')
        line_obj = self.pool.get('hr.payslip.line')
        history = None
        contract_values = {}
        tipo_nomina = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.nomina.prestaciones', True)
        psr = self.browse(cr, uid, ids[0], context=context)
        payslip_ids = payslip_obj.search(cr, uid, [('payslip_run_id', '=', ids[0])], context=context)
        payslips = payslip_obj.browse(cr, uid, payslip_ids, context=context)
        if psr.check_special_struct and tipo_nomina in psr.struct_id.code:
            for p in payslips:
                contract_id = p.contract_id
                # REGISTRO DEL HISTORICO DE PRESTACIONES SOCIALES
                history = fi_hist_obj.get_last_history_fi(cr, uid, p.employee_id.id, None, context=context)
                contract_values.update({'total_acum_ps': history.monto_acumulado,
                                        'total_acum_anticipo_ps': history.total_anticipos,
                                        'dias_acum_fideicomiso': history.dias_acumuluados,
                                        'dias_adic_fideicomiso': history.dias_adicionales})
                contract_obj.write(cr, uid, contract_id.id, contract_values, context=context)
        else:
            # ANTICIPOS
            for p in payslips:
                # ANTICIPO DE PRESTACIONES SOCIALES
                code_anticipo = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.anticipo.prestaciones', False)
                line_id = line_obj.search(cr, uid, [('slip_id', '=', p.id), ('code', '=', code_anticipo)])
                if line_id:
                    history = fi_hist_obj.get_last_history_fi(cr, uid, p.employee_id.id, None, context=context)
                    contract_values.update({'total_acum_ps': history.monto_acumulado,
                                            'total_acum_anticipo_ps': history.total_anticipos,
                                            'dias_acum_fideicomiso': history.dias_acumuluados,
                                            'dias_adic_fideicomiso': history.dias_adicionales})
                    contract_obj.write(cr, uid, p.contract_id.id, contract_values, context=context)
        return res

hr_payslip_run()



