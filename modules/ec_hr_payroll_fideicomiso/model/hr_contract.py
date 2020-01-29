# coding: utf-8
from openerp import fields, models, api
from openerp.osv import osv
from openerp.exceptions import Warning
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_contract(models.Model):
    _inherit= 'hr.contract'

    monto_acumulado = fields.Float('Monto acumulado contrato', digits=(10,2))
    fecha_ult_actualizacion = fields.Date('Fecha ultima actualizacion')
    anticipo_check = fields.Boolean('Anticipo check')
    anticipo_value = fields.Float('Anticipo value', digits=(10, 2))
    capitalizacion = fields.Boolean('Capitalizacion')
    interes_acumulado_check = fields.Boolean('Interes Acumulado check')
    interes_acumulado_value = fields.Float('Interes Acumulado value', digits=(10, 2))

    @api.onchange('anticipo_value')
    def onchange_anticipo_value(self):
        monto_75 = self.monto_acumulado*0.75
        if monto_75 < self.anticipo_value:
            raise Warning (("El monto del anticipo no puede ser mayor al 75% del monto acumulado"))

    @api.v7
    def write(self, cr, uid, ids, values, context=None):
        if context is None: context = {}
        if not hasattr(ids, '__iter__'): ids = [ids]
        if values.get('anticipo_value', False):
            acumulado = self.read(cr, uid, ids,['monto_acumulado'])[0]['monto_acumulado']
            monto_75 = acumulado * 0.75
            if monto_75 < values.get('anticipo_value',0.0) and values.get('come_from',False) and values.get('come_from',False)=='':
                raise Warning (("El monto del anticipo no puede ser mayor al 75% del monto acumulado"))
        res = super(hr_contract, self).write(cr, uid, ids, values, context=context)
        return res

    @api.v7
    def create(self, cr, uid, values, context=None):
        if context is None: context = {}
        res = {}
        if values.get('anticipo_value', False):
            monto_75 = values.get('monto_acumulado', 0.0) * 0.75
            if monto_75 < values.get('anticipo_value', 0.0):
                raise Warning (("El monto del anticipo no puede ser mayor al 75% del monto acumulado"))
        res = super(hr_contract, self).create(cr, uid, values, context=context)
        return res

class hr_historico_fideicomiso(models.Model):
    _inherit= 'hr.historico.fideicomiso'

    def procesar_capitalizacion(self, cr, uid):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')

        history_values = {}
        employee_ids = employee_obj.search(cr, uid, [])
        ahora = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        contract_ids = contract_obj.search(cr, uid, ['employee_id', 'in', employee_ids])
        contract_data = contract_obj.read(cr, uid, contract_ids, ['capitalizacion', 'employee_id'])
        for c in contract_data:
            if c['capitalizacion']:
                history = self.get_last_history_fi(cr, uid, c['employee_id'], None)
                monto = history.monto_acumulado + history.monto_total_intereses
                cedula = employee_obj.get_employee_cedula(c['employee_id'])
                history_values.update({'employee_id': c['employee_id'],
                                       'cedula_identidad': cedula,
                                       'type_record': 'intereses',
                                       'fecha_anticipo_intereses': ahora,
                                       'monto_acumulado': monto,
                                       'monto_total_intereses': 0.0,
                                       'fecha_anticipo': history.fecha_anticipo,
                                       'anticipo': history.anticipo,
                                       'salario_diario': history.salario_diario,
                                       'fecha_inicio': history.fecha_inicio,
                                       'fecha_fin': history.fecha_fin,
                                       'fecha_aporte': history.fecha_aporte,
                                       'dias_aporte': history.dias_aporte,
                                       'dias_acumulados': history.dias_acumulados,
                                       'dias_adicionales': history.dias_adicionales,
                                       'aporte_dias_adic': history.aporte_dias_adic,
                                       'monto_tri_ant': history.monto_tri_ant,
                                       'total_anticipos': history.total_anticipos,
                                       'anticipo_intereses': history.anticipo_intereses,
                                       })

                self.create(cr, uid, history_values)

    def procesar_interes_mensual(self, cr, uid):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')

        history_values = {}
        employee_ids = employee_obj.search(cr, uid, [])
        ahora = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        contract_ids = contract_obj.search(cr, uid, ['employee_id', 'in', employee_ids])
        contract_data = contract_obj.read(cr, uid, contract_ids, ['capitalizacion', 'employee_id'])
        for c in contract_data:
            if c['capitalizacion']:
                history = self.get_last_history_fi(cr, uid, c['employee_id'], None)
                monto = history.monto_acumulado + history.monto_total_intereses
                cedula = employee_obj.get_employee_cedula(c['employee_id'])
                history_values.update({'employee_id': c['employee_id'],
                                       'cedula_identidad': cedula,
                                       'type_record': 'intereses',
                                       'fecha_anticipo_intereses': ahora,
                                       'monto_acumulado': monto,
                                       'monto_total_intereses': 0.0,
                                       'fecha_anticipo': history.fecha_anticipo,
                                       'anticipo': history.anticipo,
                                       'salario_diario': history.salario_diario,
                                       'fecha_inicio': history.fecha_inicio,
                                       'fecha_fin': history.fecha_fin,
                                       'fecha_aporte': history.fecha_aporte,
                                       'dias_aporte': history.dias_aporte,
                                       'dias_acumulados': history.dias_acumulados,
                                       'dias_adicionales': history.dias_adicionales,
                                       'aporte_dias_adic': history.aporte_dias_adic,
                                       'monto_tri_ant': history.monto_tri_ant,
                                       'total_anticipos': history.total_anticipos,
                                       'anticipo_intereses': history.anticipo_intereses,
                                       })

                self.create(cr, uid, history_values)

class hr_employee(models.Model):
    _inherit='hr.employee'

    def get_employee_cedula(self, employee_id):
        cedula= ''
        employee = self.read(employee_id, ['identification_id_2'])
        for e in employee:
            cedula = e['identification_id_2']
        return cedula