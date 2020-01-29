# -*- coding: UTF-8 -*-
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
#    type of the change:  Created for Roselyn Volcan
#    Change:   rvolcan **  07/07/2016 **  hr **  Modified
#    Comments: Campos y funciones para el modulo de hr_datos_familiares.
#
##############################################################################


from openerp import fields, models, exceptions, api
from datetime import datetime
from dateutil import relativedelta
from openerp.exceptions import Warning
#rvolcan: formato de fecha yyyy-mm-dd
_DATETIME_FORMAT = "%Y-%m-%d"
#from curses.ascii import isdigit
import re

class hr_employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee antiguedad"

    TIPO_CUENTA = [
        ('0', 'Corriente'),
        ('1', 'Ahorro'),
    ]

    #Datos para Antiguedad
    fecha_inicio = fields.Date("Fecha de Ingreso", required=True)
    fecha_fin = fields.Date("Fecha de Egreso")
    dias_antig = fields.Integer('Dias', help="Total de dias de Antiguedad.", readonly=True, default=0)
    mes_antig = fields.Integer('Mes', help="Total de Meses de Antiguedad.", readonly=True, default=0)
    ano_antig = fields.Integer('Año', help="Total de Años de Antiguedad.", readonly=True, default=0)
    m_egreso = fields.Many2one('hr.egress.conditions.motivo','Motivo de Egreso')
    bank_account_id_emp_2 = fields.Many2one('res.partner.bank', 'Banco de Nomina', help="Payslip bank")
    account_number_2 = fields.Char('Nro. de Cuenta', size=20)
    account_type_2 = fields.Selection(TIPO_CUENTA, 'Tipo de Cuenta')

    _sql_constraints = [
        ('uniq_account_number_2', 'UNIQUE(account_number_2)', "El numero de cuenta ya esta registrado! Debe indicar otro."),
    ]

    #Calculo y validacion de los dias de antiguedad
    @api.onchange('fecha_inicio')
    def onchange_fecha_ingreso(self):
        fecha = self.fecha_inicio
        if fecha:
            age = self.calcular_antiguedad(fecha)
            if age['days'] >= 0 and age['months'] >= 0 and age['years'] >= 0:
                self.dias_antig = age['days']
                self.mes_antig = age['months']
                self.ano_antig = age['years']
            else:
                self.dias_antig = False
                self.mes_antig = False
                self.ano_antig = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    @api.onchange('account_number_2')
    def onchange_account_number(self):
        if self.account_number_2:
            res = self.validate_number(self.account_number_2)
            if not res:
                self.account_number = ''
                return {'warning':{'title': "Advertencia!", 'message': u'El número de cuenta tiene el formato incorrecto. Ej: 01234567890123456789. Por favor intente de nuevo'}}

    @api.multi
    def validate_number(self, number):
        res = {}
        number_obj = re.compile(r"""^\d{20}""", re.X)

        if number_obj.search(number):
            res = {
                'valor': number
            }
        return res

    @api.multi
    def calcular_antiguedad(self, fecha):
        res = {}
        ahora = datetime.now().strftime(_DATETIME_FORMAT)
        if fecha:
            diferencia = relativedelta.relativedelta(datetime.strptime(ahora, _DATETIME_FORMAT), datetime.strptime(fecha, _DATETIME_FORMAT))
            res.update({'years':diferencia.years})
            res.update({'months': diferencia.months})
            res.update({'days': diferencia.days})
            #self.write(res)
        return res


    def actualizar_antiguedad(self, cr, uid):
        print ("====Inicio Cambio de antiguedad====")
        employee_ids = self.search(cr, uid, [])
        employees = self.browse(cr, uid, employee_ids)
        values = {}
        res = {}
        ahora = datetime.now().strftime(_DATETIME_FORMAT)
        for emp in employees:
            fecha = emp.fecha_inicio
            if fecha:
                diferencia = relativedelta.relativedelta(datetime.strptime(ahora, _DATETIME_FORMAT), datetime.strptime(fecha, _DATETIME_FORMAT))
                res.update({'ano_antig': diferencia.years})
                res.update({'mes_antig': diferencia.months})
                res.update({'dias_antig': diferencia.days})
                self.write(cr, uid, emp.id,res)
        print ("====Cambio de nombres Ejecutado====")

    @api.multi
    def write(self, values):
        acc_num = values.get('account_number_2',False)
        if acc_num:
            res = self.validate_number(acc_num)
            if not res:
                self.account_number_2 = ''
                raise Warning(u'El número de cuenta tiene el formato incorrecto. Ej: 01234567890123456789. Por favor intente de nuevo')
        res = super(hr_employee, self).write(values)
        return res

    @api.model
    def create(self, values):
        acc_num = values.get('account_number_2', False)
        if acc_num:
            res = self.validate_number(acc_num)
            if not res:
                raise Warning(
                    u'El número de cuenta tiene el formato incorrecto. Ej: 01234567890123456789. Por favor intente de nuevo')
        wh_iva_id = super(hr_employee, self).create(values)
        return wh_iva_id
hr_employee()