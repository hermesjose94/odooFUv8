# coding: utf-8
# from openerp import fields, models, api
from openerp.osv import osv, fields
from openerp.exceptions import Warning
from datetime import datetime, time, date
from dateutil import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'

    _columns = {
        'salario_mensual_util': fields.float('Salario Mensual Utilidades', digits=(10, 4)),
        'salario_integral_util': fields.float('Salario Integral Utilidades', digits=(10, 4)),
        'total_util': fields.float('Total a pagar', digits=(10, 4)),
        'alic_bono_vac_util': fields.float('Alicuota Bono Vacacional', digits=(10, 4)),
        'anticipos_util': fields.float('Anticipos Utilidades', digits=(10, 4)),
        'util_days_to_pay_ps': fields.integer('Dias a pagar utilidades'),
    }


    _defaults = {
        'sueldo_promedio':True,
    }

    # @api.v7
    def compute_sheet(self, cr, uid, ids, context=None):
        # res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        special_struct_obj = self.pool.get('hr.payroll.structure')
        run_obj = self.pool.get('hr.payslip.run')
        config_obj = self.pool.get('hr.config_parameter')
        util_obj = self.pool.get('hr.payroll.utilidades')
        res_config_obj = self.pool.get('hr.config.settings')
        contract_obj = self.pool.get('hr.contract')
        config_values = {}
        factor_x_dias_x_mes_adic = dias_adic = dias_acum = dias_util = 0
        salario_integral_diario = alic_b_v = alic_util = salario_integral = sueldo_promedio = total_a_pagar = 0.0
        period_init = period_end = None
        active_id = context.get('active_id', False)
        tiempo_servicio = {}
        vacaciones = {}
        payslip_values = {}
        tipo_nomina = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.nomina.utilidades', True)
        is_special = context.get('is_special', False)
        special_id = context.get('special_id', False)
        recalculate = context.get('come_from', False)
        config_data = False
        is_anticipo = False
        if is_special and special_id and active_id:
            psr = run_obj.browse(cr, uid, active_id)
            is_anticipo = psr.is_anticipo
            if tipo_nomina in psr.struct_id.code:
                for payslip in self.browse(cr, uid, ids, context=context):
                    if payslip.contract_id.date_end:    #Si el contrato no esta ctivo no ss hace nomina de utilidades
                        continue
                    dias_str = config_obj.hr_get_parameter(cr, uid, 'hr.dias.bono.vacacional')
                    tiempo_servicio = self.get_years_service(payslip.contract_id.date_start, payslip.date_to)
                    vacaciones = self.get_dias_bono_vacacional(cr, uid, tiempo_servicio)
                    config_values = res_config_obj.get_config_values(cr)
                    # max_days_year = float(config_obj.hr_get_parameter(cr, uid, 'hr.payroll.max.days.year', True))
                    if config_values and config_values[0]['module_hr_utilidades_add_calculo'] == True:
                        if is_anticipo:
                            dias_util = run_obj.get_days_util_to_pay(cr, uid, active_id)
                            period_init = payslip.date_from
                            period_end = payslip.date_to
                            max_day_util = util_obj.get_last_util_max_days(cr, uid,
                                                                           int(payslip.date_from.split('-')[0]))
                        else:
                            period_init = config_values[0]['module_hr_utilidades_add_date_start']
                            period_end = config_values[0]['module_hr_utilidades_add_date_end']
                            max_day_util = util_obj.get_last_util_max_days(cr, uid, int(period_init.split('-')[0]), context=context)
                            dias_util = max_day_util
                        config_data = True
                    else:
                        #TODO proceso para calculo de utilidades utilizando el ultimo salario del mes
                        period_end = None
                        max_day_util = util_obj.get_last_util_max_days(cr, uid, int(payslip.date_from.split('-')[0]))
                        if is_anticipo:
                            dias_util = run_obj.get_days_util_to_pay(cr, uid, active_id)
                        else:
                            dias_util = max_day_util
                        period_init = payslip.date_from
                        period_end = payslip.date_to
                    if is_anticipo:
                        if dias_util > max_day_util:
                            raise Warning(('Advertencia!'), (
                                u'El Número de días a pagar es mayor que el máximo establecido! Por favor verifie e intente nuevamente.'))
                        elif dias_util == 0:
                            raise Warning(('Advertencia!'), (
                                u'El Número de días a pagar no puede ser 0! Por favor verifie e intente nuevamente.'))
                    sueldo_promedio = self.calculo_sueldo_promedio_util(cr, uid, payslip.employee_id, period_init,
                                                                        period_end, config_data, is_anticipo,
                                                                        payslip.contract_id.date_start, context=context)
                    salario_integral, salario_integral_diario, alic_b_v= self.calculo_salrio_integral(
                        cr, uid, payslip.id, sueldo_promedio, vacaciones.get('asignacion')  if int(dias_str) == 0 else int(dias_str), dias_util)
                    total_a_pagar = salario_integral_diario*dias_util
                    if is_anticipo:
                        contract_obj.set_anticipo_data(cr, uid, payslip.contract_id.id, total_a_pagar, payslip.date_from, payslip.date_to, special_id, context=context)
                    total_anticipos = contract_obj.get_anticipo_acum(cr, uid, payslip.contract_id.id, context=context)
                    payslip_values.update({
                        'salario_mensual_util': sueldo_promedio,
                        'salario_integral_util': salario_integral_diario,
                        'util_days_to_pay_ps': dias_util,
                        'total_util': total_a_pagar,
                        'alic_bono_vac_util':alic_b_v,
                        'anticipos_util':total_anticipos if not period_end else 0.0
                    })
                    self.write(cr, uid, [payslip.id], payslip_values, context=context)
        res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        return res

    # @api.v7
    def get_days_util_to_pay(self, cr, uid, id):
        local_obj = self.browse(cr, uid, id)
        return local_obj.util_days_to_pay

    # @api.v7
    def calculo_salrio_integral(self, cr, uid, ids, sueldo_normal, dias_b_v, dias_adic=None):
        monto_diario = 0.0
        alic_b_v = 0.0
        config_obj = self.pool.get('hr.config_parameter')
        # Total de dias por mes (para calculo del salario diario)
        dias_str = config_obj.hr_get_parameter(cr, uid, 'hr.dias.x.mes')

        alic_b_v = self.calculo_alic_bono_vac(cr, uid, sueldo_normal, dias_b_v)#/ float(dias_str)
        monto_diario = (sueldo_normal / float(dias_str)) + alic_b_v # salario integral diario
        return monto_diario * float(dias_adic), monto_diario, alic_b_v

    # @api.v7
    def calculo_sueldo_promedio_util(self, cr, uid, employee_id, fecha_desde, fecha_hasta, config_data=False, is_anticipo=False, contract_date_start=None, context=None):
        config_obj = self.pool.get('hr.config_parameter')
        ultimo_sueldo = sueldo_x_mes = sueldo_temp = 0.0
        mes_ult_sueldo = 0
        date_start = None
        if context is None: context = {}

        codes_str = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.salario.integral.utilidades',True)  # salario normal
        code = str(codes_str).strip().split(',')  # para obtener los conceptos a agregar al salario integrarel monto BRUTO a cobrar
        dias_hab_periodo = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.utilidades.dias.habiles',True)  # dias habiles de utilidades

        periodo = relativedelta.relativedelta(datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT),
                                              datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT))
       # if is_anticipo:
        if config_data and not is_anticipo:
            mes_pago = int(config_obj.hr_get_parameter(cr, uid, 'hr.payroll.utilidades.mes.pago',False))
            fecha_desde = datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT)
            fecha_hasta = datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT)
            #EL PERIODO INICIA EN LA FECHA DE INGRESO DEL EMPLEADO SI TIENE MENOS DE UN AÑO DE ANTIGÜEDAD
            if contract_date_start:
                date_start = datetime.strptime(contract_date_start, DEFAULT_SERVER_DATE_FORMAT)
                if date_start > fecha_desde:
                    fecha_desde = date_start
            while fecha_desde.month <= fecha_hasta.month and mes_pago > fecha_desde.month:
                rango = self.rango_mes_anterior( datetime.strftime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT), 0)
                sueldo_temp = self.get_amount_util(cr, uid, code, employee_id.id, rango[0],rango[1], is_anticipo, True)  # ultimo sueldo
                fecha_desde = fecha_desde + relativedelta.relativedelta(months=+1)
                ultimo_sueldo += sueldo_temp
                mes_ult_sueldo = fecha_desde.month
                if sueldo_temp == 0:
                    break
                sueldo_x_mes = sueldo_temp
            ultimo_sueldo = ultimo_sueldo + sueldo_x_mes*(mes_pago - mes_ult_sueldo)
        else:
            fecha_desde = datetime.strftime(
                datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT) + relativedelta.relativedelta(months=-1),
                DEFAULT_SERVER_DATE_FORMAT)
            fecha_hasta = datetime.strftime(
                datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT) + relativedelta.relativedelta(months=-1),
                DEFAULT_SERVER_DATE_FORMAT)
            ultimo_sueldo = self.get_amount_util(cr, uid, code, employee_id.id, fecha_desde, fecha_hasta, is_anticipo)  # ultimo sueldo


        return ultimo_sueldo / (periodo.months if periodo.months > 0 else 1)

    # @api.v7
    def get_amount_util(self, cr, uid, code=None, employee_id=None, fecha_desde=None, fecha_hasta=None, is_anticipo=False, config_data=False):
        amount = 0.0
        amount_month = 0.0
        domain_ps = []
        domain_psl = []
        p_ids = []
        rango = []
        payslip_line_obj = self.pool.get('hr.payslip.line')
        payslip_obj = self.pool.get('hr.payslip')
        payslip_run_obj = self.pool.get('hr.payslip.run')
        config_obj = self.pool.get('hr.config_parameter')
        if employee_id:
            domain_ps.append(('employee_id', '=', employee_id))
            domain_psl.append(('employee_id', '=', employee_id))

        domain_ps.append(('state', '=', 'done'))
        fecha_desde = fecha_desde or datetime.now().strftime('%Y-%m-%d')

        domain_ps.append(('date_from', '>=', fecha_desde))
        domain_ps.append(('date_from', '<=', fecha_hasta))
        domain_ps.append(('payslip_run_id', '!=', False))
        payslip_ids = payslip_obj.search(cr, uid, domain_ps)
        if payslip_ids:
            payslip_run_ids = payslip_obj.read(cr, uid, payslip_ids, ['payslip_run_id'])
            for dict in payslip_run_ids:
                id = payslip_run_obj.search(cr, uid, [('id', '=', dict['payslip_run_id'][0]),('check_special_struct', '=', False)])
                if id:
                    p_ids.append(dict['id'])
            domain_psl.append(('slip_id', 'in', p_ids))
        else:
            if not is_anticipo and not config_data:
                raise osv.except_osv(('Advertencia!'), ('No se han confirmado las nóminas correspondientes al mes anterior.\n \
                                                Por favor verifique y proceda a realizar la confirmación de las nóminas\n \
                                                correspondientes.'))
            else:
                return amount
        if code:
            domain_psl.append(('code', 'in', code))
        payslip_line_ids = payslip_line_obj.search(cr, uid, domain_psl)
        for i in  payslip_line_obj.browse(cr, uid, payslip_line_ids):
            amount += i.amount

        return amount

class hr_payslip_run(osv.osv):
    _inherit = 'hr.payslip.run'

    _columns = {
        'util_days_to_pay': fields.integer('Dias a pagar utilidades', size=3),
        'is_util': fields.boolean('Es Utilidades'),
        'is_anticipo': fields.boolean('Anticipos'),
    }


    # @api.v7
    def onchange_struct_id(self, cr, uid, ids, value, context=None):
        res = {}
        is_util = False
        struct_obj = self.pool.get('hr.payroll.struct')
        for s in struct_obj.browse(cr, uid, value, context=context):
            if s.struct_category == 'especial' and 'utilidad' in s.struct_id_payroll_category:
                is_util = True
        res = {'value': {'is_util': is_util}}
        return res

    # @api.v7
    def get_days_util_to_pay(self, cr, uid, id):
        local_obj = self.browse(cr, uid, id)
        return local_obj.util_days_to_pay

    # @api.v7
    def validate_util_days_to_pay(self, cr, uid, id, values, come_from, context=None):
        fecha =None
        dias = values.get('util_days_to_pay',False)
        especial = values.get('check_special_struct', False)
        struct_obj = self.pool.get('hr.payroll.structure')
        struct_id = values.get('struct_id', False)
        is_anticipo = values.get('is_anticipo', False)
        if especial or struct_id:
            struct = struct_obj.read(cr, uid, struct_id, ['name'], context=context )
            if 'UTILIDAD' in struct['name'].upper() and is_anticipo and dias == 0:
                raise Warning(('Advertencia!'), (
                    u'El Número de días a pagar no puede ser 0! Por favor verifique e intente nuevamente.'))
        else:
            hr_util_obj = self.pool.get('hr.payroll.utilidades')
            # for psr in self.browse(cr, uid, id, context=context):
            #     fecha = psr.date_start
            fecha = values['date_start'].split('-')[0]
            year = fecha if fecha else datetime.now().strftime('%Y-%m-%d').split('-')[0]
            total = hr_util_obj.get_last_util_max_days(cr, uid, year)
            # d = total - dias
            if dias > total:
                raise Warning(('Advertencia!'), (
                    u'El Número de días a pagar es mayor que el máximo establecido! Por favor verifie e intente nuevamente.'))
            # elif dias == 0:
            #     raise Warning(('Advertencia!'), (
            #         u'El Número de días a pagar no puede ser 0! Por favor verifie e intente nuevamente.'))

        return True

    # @api.v7
    def write(self, cr, uid, ids, values, context=None):
        if context is None: context = {}
        if not hasattr(ids, '__iter__'): ids = [ids]
        if values.get('check_special_struct', False) or values.get('struct_id', False):
            self.validate_util_days_to_pay(cr, uid, ids, values, 'write', context)
        res = super(hr_payslip_run, self).write(cr, uid, ids, values, context)
        return res

    # @api.v7
    def create(self, cr, uid, values, context=None):
        if context is None: context = {}
        res = {}
        if values.get('check_special_struct',False):
            self.validate_util_days_to_pay(cr, uid, None, values, 'create', context=context)
        res = super(hr_payslip_run, self).create(cr, uid, values, context=context)
        return res


