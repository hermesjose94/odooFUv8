# coding: utf-8
# from openerp import fields, models, api
# Edit for Clickway 31/01/2020
from datetime import datetime, timedelta, date
import calendar
from openerp.osv import fields, osv
from dateutil import relativedelta, rrule
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payslip(osv.osv):
    _inherit ='hr.payslip'

    # @api.v7
    def get_years_service(self, fecha_inicio, fecha_fin=None):
        dias = 0
        meses = 0
        anios = 0
        res = {}
        if fecha_inicio and fecha_fin:
            antiguedad = relativedelta.relativedelta(datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT),
                                                     datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT))
            res = {
                'dias': antiguedad.days,
                'meses': antiguedad.months,
                'anios': antiguedad.years,
            }
        return res

    # @api.v7
    def get_dias_bono_vacacional(self, cr, uid, tiempo_servicio):
        res = {}
        pay_days = []
        service_year = []
        asignacion = asignacionR = 0

        if tiempo_servicio:
            vacaciones_obj = self.pool.get("hr.payroll.dias.vacaciones")
            valores = vacaciones_obj.search(cr, uid, [])
            if valores:
                tamanio = len(valores) - 1
                inicio_fin = vacaciones_obj.browse(cr, uid, [valores[0],valores[tamanio]])
                for v in inicio_fin:
                    pay_days.append(v.pay_days)
                    service_year.append(v.service_years)
                if tiempo_servicio['anios'] == 0 and tiempo_servicio['meses'] >= 3:  # antiguedad menor a un anio y mayor a 3 meses
                    asignacion = (float(tiempo_servicio['meses']) / float(12)) * float(pay_days[0])
                    asignacionR = pay_days[0]
                else:
                    if service_year[0] <= tiempo_servicio['anios'] < service_year[1]:
                        vacation_id = vacaciones_obj.search(cr, uid,[('service_years', '=', tiempo_servicio['anios'])])
                        asignacion = vacaciones_obj.browse(cr, uid, vacation_id[0]).pay_days
                    else:
                        asignacion = pay_days[1]
                    asignacionR = asignacion
            else:
                raise Warning((u'No se han calculado los días de bono vacacional, debido a que\n'
                               u' no se ha cargado la lista de días a pagar por años de servicio.\n'
                               u' Por favor consulte con el administrador!'))
        res = {
            'asignacion': asignacion,
            'asignacionR': asignacionR,
        }
        return res

    # @api.v7
    def calculo_sueldo_promedio(self, cr, uid, employee_id, fecha_desde, meses, tipo_nomina=None, limite=None):
        config_obj = self.pool.get('hr.config_parameter')
        if 'fideicomiso' in tipo_nomina.lower() :
            codes_str = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.salario.integral.fideicomiso', True)
        elif 'vacaciones' in tipo_nomina.lower():
            codes_str = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.salario.integral.vacaciones', True)
        elif 'utilidad' in tipo_nomina.lower():
            codes_str = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.salario.integral.utilidades', True)
        elif 'liquidacion' in tipo_nomina.lower():
            codes_str = 1
            # codes_str = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.salario.integral.liquidacion', True)
        else:
            codes_str = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.codigos.salario.integral', True)
        code = str(codes_str).strip().split(
            ',')  # para obtener los conceptos a agregar al salario integrarel monto BRUTO a cobrar
        ultimo_sueldo = self.get_amount(cr, uid, code, employee_id.id, fecha_desde, meses,tipo_nomina, limite)  # para tomar la fecha en que se genera la nomina
        # ultimo_sueldo = self.get_amount(cr, uid, code, employee_id.id, fecha_desde, 0)     #para tomar la fecha maxima del rango en que se genera la nomina
        return ultimo_sueldo

    # @api.v7
    def get_amount(self, cr, uid, code=None, employee_id=None, fecha_desde=None, meses=0, tipo_nomina=None, limite=None):
        amount = 0.0
        promedio = 0.0
        domain_ps = []
        domain_psl = []
        p_ids = []
        payslip_line_obj = self.pool.get('hr.payslip.line')
        payslip_obj = self.pool.get('hr.payslip')
        payslip_run_obj = self.pool.get('hr.payslip.run')
        if employee_id:
            domain_ps.append(('employee_id', '=', employee_id))
            domain_psl.append(('employee_id', '=', employee_id))

        domain_ps.append(('state', '=', 'done'))

        if not fecha_desde:
            fecha_desde = datetime.now().strftime('%Y-%m-%d')

        rango = self.rango_mes_anterior(fecha_desde, meses)
        if rango:
            if 'liquidacion' in tipo_nomina:
                domain_ps.append(('date_from', '<=', fecha_desde))
                payslip_ids = payslip_obj.search(cr, uid, domain_ps, limit=limite)
            else:
                domain_ps.append(('date_from', '>=', rango[0]))
                domain_ps.append(('date_from', '<=', rango[1]))
                payslip_ids = payslip_obj.search(cr, uid, domain_ps)
            if payslip_ids:
                payslip_run_ids = payslip_obj.read(cr, uid, payslip_ids, ['payslip_run_id'])
                for dict in payslip_run_ids:
                    if dict['payslip_run_id']:
                        id = payslip_run_obj.search(cr, uid, [('id', '=', dict['payslip_run_id'][0]),
                                                          ('check_special_struct', '=', False)])
                        if id:
                            p_ids.append(dict['id'])
                    else:
                        p_ids.append(payslip_ids[0])
                domain_psl.append(('slip_id', 'in', p_ids))
            else:
                if tipo_nomina != 'normal':
                    raise Warning(('Advertencia!'), (u'No se han confirmado las nóminas correspondientes al mes anterior.\n \
                                                    Por favor verifique y proceda a realizar la confirmación requerida.'))
        if code:
            domain_psl.append(('code', 'in', code))

        payslip_line_ids = payslip_line_obj.search(cr, uid, domain_psl)
        payslip_line_net_obj = payslip_line_obj.browse(cr, uid, payslip_line_ids)

        if payslip_line_net_obj:
            for i in payslip_line_net_obj:
                amount = amount + i.amount
                promedio = amount

        return promedio


    # @api.v7
    def calculo_alic_bono_vac(self, cr, uid, sueldo_normal, dias_b_v=0):
        config_obj = self.pool.get('hr.config_parameter')
        alicuota = 0.0
        dias_str = config_obj.hr_get_parameter(cr, uid, 'hr.dias.x.mes')
        dias_x_anio = 	config_obj.hr_get_parameter(cr, uid, 'hr.payroll.max.dias.año')
        #alicuota = (sueldo_normal / float(dias_str)) * (float(dias_b_v) / float(dias_x_anio))
        fact = (float(dias_str) / float(dias_x_anio))
        sal_dia= (sueldo_normal / float(dias_str))
        alicuota = (sal_dia * fact)
        return alicuota

    # @api.v7
    def calculo_alic_util(self, cr, uid, sueldo_normal, alicuota_bv):
        config_obj = self.pool.get('hr.config_parameter')
        alicuota = 0.0
        dias_str = config_obj.hr_get_parameter(cr, uid, 'hr.dias.x.mes')
        dias_x_anio = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.max.dias.año')
        dias_max_str = config_obj.hr_get_parameter(cr, uid, 'hr.payroll.max.utili.days.year')
        fac_utilidades = float(dias_max_str)/ float(dias_x_anio)
        alicuota = ((sueldo_normal / float(dias_str))) * fac_utilidades
        return alicuota

    def rango_mes_anterior(self, date_base, meses):
        date_range = []

        mes_anterior = datetime.strptime(date_base, DEFAULT_SERVER_DATE_FORMAT) - relativedelta.relativedelta(months=meses)
        local_date = datetime.strftime(mes_anterior, DEFAULT_SERVER_DATE_FORMAT).split('-')
        date_range.append(date(int(local_date[0]), int(local_date[1]), 1))  # primer dia del mes
        date_range.append(date(int(local_date[0]), int(local_date[1]),
                               calendar.monthrange(int(local_date[0]), int(local_date[1]))[1]))  # ultimo dia del mes

        return date_range

    def calcula_dias_x_periodo(self, date_from, date_to):
        res = {}
        sab = [5]
        dom = [6]
        lun = [0]
        laborales = [0, 1, 2, 3, 4]
        fecha_desde = date_from.split('-')
        fecha_hasta = date_to.split('-')
        date_from = datetime(int(fecha_desde[0]), int(fecha_desde[1]), int(fecha_desde[2]))
        date_to = datetime(int(fecha_hasta[0]), int(fecha_hasta[1]), int(fecha_hasta[2]))
        totalDiasLaborales = rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to, byweekday=laborales).count()
        totalSabados = rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to, byweekday=sab).count()
        totalDomingos = rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to, byweekday=dom).count()
        totalLunes = rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to, byweekday=lun).count()

        res = {
            'laborales': totalDiasLaborales,
            'sabados': totalSabados,
            'domingos': totalDomingos,
            'lunes': totalLunes,
        }
        return res

    def get_feriados_2(self, cr, uid, ids, date_from, date_to, context=None):
        dias = totalHollydayWeekend = 0
        hollyday_on_w = [5, 6]
        test = self.pool.get('hr.payroll.hollydays')

        hollyday_ids = test.search(cr, uid, [('date_from','>=',date_from),
                                             ('date_from','<=',date_to),
                                             ('date_to','>=',date_from),
                                             ('date_to','<=',date_to)])
        if hollyday_ids:
            hollydays = test.browse(cr, uid, hollyday_ids, context)
            for h in hollydays:
                if h.date_from == h.date_to:
                    h_from = datetime.strptime(h.date_from, DEFAULT_SERVER_DATE_FORMAT)
                    h_to = datetime.strptime(h.date_to, DEFAULT_SERVER_DATE_FORMAT)
                    dias = dias + 1
                else:
                    h_from = datetime.strptime(h.date_from,DEFAULT_SERVER_DATE_FORMAT)
                    h_to = datetime.strptime(h.date_to,DEFAULT_SERVER_DATE_FORMAT)
                    diferencia = h_to - h_from
                    dias = dias + 1 + diferencia.days
                totalHollydayWeekend = totalHollydayWeekend + rrule.rrule(rrule.DAILY, dtstart=h_from, until=h_to,
                                                       byweekday=hollyday_on_w).count()
            dias = dias - totalHollydayWeekend
        return dias

    # Funcion que calcula la fraccion de dias de utilidades a pagar (artículo 131 de la lottt.)
    def get_fraccion_dias_util(self, cr, uid, ids, fecha_ingreso, fecha=None):
        rate = 1.0
        if not fecha_ingreso:
            raise Warning(('Advertencia!'),
                                 (u'La fecha de ingreso del empleado es inválida, por favor verifique.'))
        if not fecha:
            fecha = datetime.now().strftime('%Y-%m-%d')
        periodo = relativedelta.relativedelta(datetime.strptime(fecha, DEFAULT_SERVER_DATE_FORMAT),
                                              datetime.strptime(fecha_ingreso, DEFAULT_SERVER_DATE_FORMAT))
        if periodo.years == 0:
            restar_mes = self.get_first_workeday(cr, uid, ids, fecha_ingreso)
            meses = periodo.months
            if restar_mes:
                meses -= 1
            rate = meses / float(12)
        return rate


class hr_payroll_dias_vacaciones(osv.osv):
    _name = 'hr.payroll.dias.vacaciones'
    _description = 'Factor de Calculo para las Vacaciones'

    _columns = {
        'service_years':fields.integer('Anos de Servicio', required=True),
        'pay_days':fields.integer('Dias a Pagar', required=True),
    }
hr_payroll_dias_vacaciones()

class hr_payroll_utilidades(osv.osv):
    _name = 'hr.payroll.utilidades'
    _description = u'Monto maximo de utilidades por año'


    _columns = {
        'utilidades_name':fields.integer('Referencia', required=True),
        'utilidades_pay_days':fields.integer('Dias a Pagar', required=True),
    }

    def get_last_util_max_days(self, cr, uid, year=None, context=None):
        days = 0
        if year:
            util_id = self.search(cr, uid, [('utilidades_name','=', year)], context=context, limit=1, order='utilidades_name, write_date desc')
        else:
            util_id = self.search(cr, uid,[], context=context, limit=1, order='utilidades_name, write_date desc')
        for u in self.browse(cr, uid,util_id, context=context):
            days = u.utilidades_pay_days
        return days