# coding: utf-8
# from openerp import fields, models, api
from openerp.osv import fields, osv
from dateutil import relativedelta
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning

class hr_payslip(osv.osv):
    _inherit ='hr.payslip'

    _columns = {
        'salario_mensual_fi':fields.float('Salario mensual fideicomiso', digits=(10,2)),
        'salario_integral_fi':fields.float('Salario integral fideicomiso', digits=(10,2)),
        'alic_bono_vac_fi':fields.float('Alicuota de bono vacacional',digits=(10,2)),
        'alic_util_fi':fields.float('Alicuota de utilidades',digits=(10,2)),
        'dias_adicionales':fields.integer('Dias Adicionales'),
        'dias_acumulados':fields.integer('Dias acumulados'),
    }

    # @api.v7
    def compute_sheet(self, cr, uid, ids, context=None):
        special_struvct_obj = self.pool.get('hr.payroll.structure')
        fi_hist_obj = self.pool.get('hr.historico.fideicomiso')
        config_obj = self.pool.get('hr.config_parameter')
        factor_x_dias_x_mes_adic = dias_adic = dias_acum = 0
        salario_integral_diario = alic_b_v = alic_util = salario_integral = sueldo_promedio = 0.0
        # recalculate = context.get('come_from', False)
        active_id = context.get('active_id', False)
        tiempo_servicio = {}
        vacaciones = {}
        payslip_values = {}
        tipo_nomina = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.nomina.prestaciones',True)
        is_special = context.get('is_special', False)
        special_id = context.get('special_id', False)
        special_obj = special_struvct_obj.browse(cr, uid, special_id, context=context)
        if is_special and special_id and tipo_nomina in special_obj.code:
            for payslip in self.browse(cr, uid, ids, context=context):
                if active_id:
                    dias_str = config_obj.hr_get_parameter(cr, uid, 'hr.dias.bono.vacacional')
                    tiempo_servicio = self.get_years_service(payslip.contract_id.date_start, payslip.date_to)
                    vacaciones = self.get_dias_bono_vacacional(cr, uid, tiempo_servicio)
                    sueldo_promedio = self.calculo_sueldo_promedio(cr, uid, payslip.employee_id, payslip.date_to, 0, 'fideicomiso')
                    if not payslip.contract_id:
                        raise Warning((u'El emleado %s no tiene contrato o la fecha de ingreso es posterior al período seleccionado.\n'
                                 u' Por favor consulte con su supervisor inmediato!')%payslip.employee_id.name)
                    #factor = self.get_days_utilidades(cr, uid) / float(12)
                    salario_integral, factor_x_dias_x_mes, salario_integral_diario, alic_b_v, alic_util = self.calculo_fideicomiso(
                        cr, uid, payslip.id, sueldo_promedio, vacaciones.get('asignacion') if int(dias_str) == 0 else int(dias_str), payslip.contract_id.date_start, payslip.date_to, None, context=context)

                    dias_adic = self.get_fi_dias_adicionales(cr, uid, payslip.contract_id.date_start, payslip.date_to, payslip.date_from)
                    if dias_adic < 0:
                        raise Warning((u'La fecha de ingreso del empleado %s es posterior al período seleccionado.\n'
                                       u' Por favor consulte con su supervisor inmediato!')%payslip.employee_id.name)
                    elif dias_adic > 0:
                         salario_integral_dias_adic, factor_x_dias_x_mes_adic, salario_integral_diario, alic_b_v, alic_util = self.calculo_fideicomiso(
                             cr, uid, payslip.id, sueldo_promedio, vacaciones.get('asignacion'), payslip.contract_id.date_start, payslip.date_to,
                             dias_adic, context=context)
                    # dias_acum = fi_hist_obj.get_last_history_fi(cr, uid,payslip.employee_id.id, None, context=context).dias_acumuluados
                    payslip_values.update({
                        'salario_mensual_fi': sueldo_promedio,
                        'salario_integral_fi': salario_integral_diario,
                        # 'salario_integral_fi': salario_integral,
                        'dias_adicionales': dias_adic,
                        'dias_acumulados': factor_x_dias_x_mes,
                    })
                    self.write(cr, uid, [payslip.id], payslip_values, context=context)
        res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        return res

    # @api.v7
    def calculo_fideicomiso(self, cr, uid, ids, sueldo_normal, dias_b_v, date_start, fecha_hasta, dias_adic=None, context=None):
        monto_diario = 0.0
        alic_b_v = 0.0
        alic_util = 0.0
        factor_x_dias_x_mes = 0
        config_obj = self.pool.get('hr.config_parameter')
        # Total de dias por mes (para calculo del salario diario)
        dias_str = config_obj.hr_get_parameter(cr, uid, 'hr.dias.x.mes')

        # total meses a pagar de fideicomiso
        total_meses_str = config_obj.hr_get_parameter(cr, uid, 'hr.fideicomiso.total.meses')

        factor = self.get_fact_fidei_x_mes(cr, uid, date_start, fecha_hasta, float(total_meses_str))

        # total de dias a pagar de fideicomiso
        if dias_adic:
            factor_x_dias_x_mes = float(dias_adic)
        else:
            fi_dias_x_mes_str = config_obj.hr_get_parameter(cr, uid, 'hr.fideicomiso.dias.x.mes')
            factor_x_dias_x_mes = factor * float(fi_dias_x_mes_str)
        alic_b_v = self.calculo_alic_bono_vac(cr, uid, sueldo_normal, dias_b_v)
        alic_util = self.calculo_alic_util(cr, uid, sueldo_normal, alic_b_v)
        monto_diario = (sueldo_normal / float(dias_str)) + alic_b_v + alic_util  # salario integral diario
        return monto_diario * factor_x_dias_x_mes, factor_x_dias_x_mes, monto_diario, alic_b_v, alic_util

    # @api.v7
    def get_fact_fidei_x_mes(self, cr, uid, date_start, fecha_hasta, total_meses):
        factor = 0.0
        diferencia = relativedelta.relativedelta(datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT),
                                                 datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT))
        if diferencia.years > 0:
            factor = total_meses
        elif diferencia.years == 0:
            if diferencia.months >= total_meses:
                factor = total_meses
            else:
                factor = diferencia.months + 1
        else:
            raise Warning((u'La fecha de ingreso del empleado es posterior al período seleccionado.\n'
                           u' Por favor consulte con su supervisor inmediato!'))
        return factor

    def get_fi_dias_adicionales(self, cr, uid, date_start, fecha_hasta, fecha_desde):
        config_obj = self.pool.get('hr.config_parameter')
        fecha = None
        dias = 0
        anios = 0

        # ULTIMA LIQUIDACION COLECTIVA
        ult_liqu_colectiva_str = config_obj.hr_get_parameter(cr, uid, 'hr.payslip.ultima.liquidacion.colectiva', True)

        # Años establecidos por ley para comenzar a pagar los dias adicionales
        anios_ley_str = config_obj.hr_get_parameter(cr, uid, 'hr.fi.antiguedad.ley')

        # Maximo dias a pagar
        maximo_str = config_obj.hr_get_parameter(cr, uid, 'hr.dias.x.mes')

        if datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT) < datetime.strptime(ult_liqu_colectiva_str, DEFAULT_SERVER_DATE_FORMAT):
            fecha = ult_liqu_colectiva_str
        else:
            fecha = date_start
        # años de servicio desde la fecha de ingreso
        anios = self.get_years_service(fecha, fecha_hasta)['anios']

        diferencia = datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        diferencia2 = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT)

        if int(fecha_desde.split('-')[1]) <= int(date_start.split('-')[1]) <= int(fecha_hasta.split('-')[1]):
            factor_str = config_obj.hr_get_parameter(cr, uid, 'hr.fi.factor.dias.adicionales')
            if anios == int(anios_ley_str):
                anios = 1
            elif anios > 0:
                anios = anios - 1
            dias = int(factor_str) * anios
            if dias > int(maximo_str): dias = int(maximo_str)
        elif diferencia.days < 0:
            dias = -1
        elif diferencia2.days < 0:
            dias = 0
        return dias

class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns = {
        'fecha_modificado': fields.date('Bono Nocturno Valor'),
        'fideicomiso': fields.float('Bono Nocturno', digits=(10, 2)),
    }




