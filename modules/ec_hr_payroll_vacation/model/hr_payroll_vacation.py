# coding: utf-8
# from openerp import fields, models, api
from openerp.osv import fields, osv
from dateutil import relativedelta
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payslip(osv.osv):
    _inherit ='hr.payslip'

    _columns = {
        'dias_a_pagar_va':fields.integer('Dias a pagar vacaciones'),
        'tiempo_servicio_va':fields.integer('Tiempo de servicio vacaciones'),
        'salario_mensual_va':fields.float('Salario mensual vacaciones',digits=(10,2)),
        'domingos':fields.integer('Domingos vacacioneas'),
        'dias_porcion':fields.float('Dias Porcion',digits=(10,2)),
        # 'dias_adicional':fields.integer('Dias adicionales'),
        'dias_festivos': fields.integer('Dias festivos'),
    }

    # @api.v7
    def compute_sheet(self, cr, uid, ids, context=None):
        # res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        special_struct_obj = self.pool.get('hr.payroll.structure')
        run_obj = self.pool.get('hr.payslip.run')
        config_obj = self.pool.get('hr.config_parameter')
        feriados = 0
        sueldo_promedio = 0.0
        active_id = context.get('active_id', False)
        tiempo_servicio = {}
        vacaciones = {}
        payslip_values = {}
        dias_x_periodo = {}
        tipo_nomina = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.nomina.vacaciones', True)
        is_special = context.get('is_special', False)
        special_id = context.get('special_id', False)
        psr = None
        if active_id:
            psr = run_obj.browse(cr, uid, active_id)
        if is_special and special_id:
            for payslip in self.browse(cr, uid, ids, context=context):
                special_obj = special_struct_obj.browse(cr, uid, special_id, context=context)
                if  special_obj.code in tipo_nomina:
                    dias_x_periodo = self.calcula_dias_x_periodo(payslip.date_from, payslip.date_to)
                    feriados = self.get_feriados_2(cr, uid, ids, payslip.date_from, payslip.date_to)
                    tiempo_servicio = self.get_years_service(payslip.contract_id.date_start, payslip.date_to)
                    vacaciones = self.get_dias_bono_vacacional(cr, uid, tiempo_servicio)
                    sueldo_promedio = self.calculo_sueldo_promedio(cr, uid, payslip.employee_id, payslip.date_from, 1, 'vacaciones')
                payslip_values.update({
                    'salario_mensual_va':  sueldo_promedio,
                    'domingos': dias_x_periodo.get('domingos',False),
                    'dias_festivos': feriados,
                    'dias_porcion': vacaciones.get('asignacion',False),
                    'dias_a_pagar_va':vacaciones.get('asignacion',False),
                    'tiempo_servicio_va':tiempo_servicio.get('anios',False),
                })
                self.write(cr, uid, [payslip.id], payslip_values, context=context)
        res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        return res
#
# class hr_contract(osv.osv):
#     _inherit = 'hr.contract'
#     _columns = {
#         'fecha_modificado': fields.date('Bono Nocturno Valor'),
#         'fideicomiso': fields.float('Bono Nocturno', digits=(10, 2)),
#     }





