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
#rvolcan: formato de fecha yyyy-mm-dd
_DATETIME_FORMAT = "%Y-%m-%d"
#from curses.ascii import isdigit
import re

class hr_employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee familiar"

    #Datos Familiares
    son = fields.Boolean(string="Hijos")
    son_ids = fields.One2many('hr.son', 'employee_id', 'Hijos')
    mother_name = fields.Char("Nombre y Apellido de la madre", size=256)
    mother_date = fields.Date("Fecha de Nacimiento de la madre")
    mother_age = fields.Integer("Edad de la madre")
    mother_nationality = fields.Selection([('v.-','V.-'), ('E.-','E.-')], string="Nacionalidad de la madre")
    mother_ci = fields.Integer("Cedula de Identidad de la madre", size=8)
    mother_live = fields.Boolean(string="Vive (madre)")
    father_name = fields.Char("Nombre y Apellido del padre", size=256)
    father_date = fields.Date("Fecha de Nacimiento del padre")
    father_age = fields.Integer("Edad del padre")
    father_nationality = fields.Selection([('v.-','V.-'), ('E.-','E.-')], string="Nacionalidad del padre")
    father_ci = fields.Integer("Cedula de Identidad del padre", size=8)
    father_live = fields.Boolean(string="Vive (padre)")
    spouse = fields.Boolean(string="Conyugue")
    spouse_name = fields.Char("Nombre y Apellido del conyugue", size=256)
    spouse_date = fields.Date("Fecha de Nacimiento del conyugue")
    spouse_age = fields.Integer("Edad del conyugue")
    spouse_nationality = fields.Selection([('V.-','V.-'), ('E.-','E.-')], string="Nacionalidad del conyugue")
    spouse_ci = fields.Integer("Cedula de Identidad del conyugue", size=8)

    #Calculo y validacion de la edad de la madre
    @api.onchange('mother_date')
    def onchange_date_of_birth_mother(self):
        fecha = self.mother_date
        if fecha:
            age = self._calculate_date_of_birth(self.mother_date)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.mother_age = age.years
                #self.age_sons_months = age.months Campos para el calculo en  dias y meses.
                #self.age_sons_days = age.days
            else:
                self.mother_age = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    #Calculo y validacion de la edad del padre
    @api.onchange('father_date')
    def onchange_date_of_birth_father(self):
        fecha = self.father_date
        if fecha:
            age = self._calculate_date_of_birth(self.father_date)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.father_age = age.years
                #self.age_sons_months = age.months Campos para el calculo en  dias y meses.
                #self.age_sons_days = age.days
            else:
                self.father_age = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    #Calculo y validacion de la edad del esposo
    @api.onchange('spouse_date')
    def onchange_date_of_birth_spouse(self):
        fecha = self.spouse_date
        if fecha:
            age = self._calculate_date_of_birth(self.spouse_date)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.spouse_age = age.years
                #self.age_sons_months = age.months Campos para el calculo en  dias y meses.
                #self.age_sons_days = age.days
            else:
                self.spouse_age = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    @api.multi

    def _calculate_date_of_birth(self, value):
            age = 0
            if value:
                ahora = datetime.now().strftime(_DATETIME_FORMAT)
                age = relativedelta.relativedelta(datetime.strptime(ahora,_DATETIME_FORMAT), datetime.strptime(value,_DATETIME_FORMAT))
            return age


class hr_son(models.Model):
    _name = "hr.son"

    #Datos de los ninos
    name_sons = fields.Char(string="Nombre y Apellido del hijo", size=256)
    sex_sons = fields.Selection([('f','Femenino'), ('m','Masculino')], string="Sexo del hijo")
    date_sons = fields.Date(string="Fecha de Nacimiento del hijo")
    age_sons = fields.Char(string="Edad del hijo", size=10)
    nationality_sons = fields.Selection([('v.-','V.-'), ('E.-','E.-')], string="Nacionalidad del hijo")
    ci_sons = fields.Integer("Cedula de identidad del hijo", size=8)
    disability_sons = fields.Boolean(string="Discapacidad (hijo)")
    constancia_inscripcion = fields.Boolean(string="Constancia de Inscripción del hijo")
    employee_id = fields.Many2one('hr.employee', 'Employee', ondelete="cascade")


    #Calculo y validacion de la edad de los ninos
    @api.onchange('date_sons')
    def onchange_date_of_birth(self):
        fecha = self.date_sons
        if fecha:
            age = self._calculate_date_of_birth(self.date_sons)
            if age.days >= 0 and age.months >= 0 and age.years >= 0:
                self.age_sons = age.years
                #self.age_sons_months = age.months Campos para el calculo en  dias y meses.
                #self.age_sons_days = age.days
            else:
                self.age_sons = False
                return {'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    @api.multi
    def _calculate_date_of_birth(self, value):
            age = 0
            if value:
                ahora = datetime.datetime.now().strftime(_DATETIME_FORMAT)
                age = relativedelta.relativedelta(datetime.datetime.strptime(ahora,_DATETIME_FORMAT),datetime.datetime.strptime(value,_DATETIME_FORMAT))
            return age



