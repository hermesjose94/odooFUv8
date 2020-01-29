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
#    Change:  **  05/07/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para la ficha del trabajador
#
# ##############################################################################################################################################################################

from openerp.osv import fields, osv
# importando el modulo de regex de python
import re
import datetime
from dateutil import relativedelta

_DATETIME_FORMAT = "%Y-%m-%d"

class hr_employee(osv.osv):
    _name = 'hr.employee'
    _inherit = "hr.employee"

    GRUPO_SANGUINEO = [
        ('O', 'O'),
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB')]

    FACTOR_RH = [
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo')]

    MARITAL_STATUS = [
        ('S', 'Single'),
        ('C', 'Married'),
        ('U', 'Union Estable de Hecho'),
        ('V', 'Widower'),
        ('D', 'Divorced'),
        ]

    NVEL_EDUCATIVO = [
        ('01', u'Básica'),
        ('02', 'Bachiller'),
        ('03', 'TSU'),
        ('04', 'Universitario'),]

    NACIONALIDAD = [
        ('V','Venezolano'),
        ('E','Extranjero')]

    _columns = {
        'identification_id_2': fields.char('Cedula de Identidad', size=15, required=True),
        'nationality': fields.selection(NACIONALIDAD, string="Tipo Documento", required=True),
        'rif':fields.char('Rif', size=15, required=True),
        'personal_email':fields.char('Correo Electronico Personal', size=240, required=True),
        'education':fields.selection(NVEL_EDUCATIVO,'Nivel Educativo'),
        'profesion_id':fields.many2one('hr.profesion','Profesion'),
        'country_birth_id': fields.many2one('res.country', 'Pais de nacimiento'),                                            #PAIS DE NACIMIENTO
        'state_id': fields.many2one('res.country.state', 'Estado de nacimiento', domain="[('country_id','=',240)]"),    #ESTADO DE NACIMIENTO
        'city_id': fields.many2one('hr.ciudad', 'Ciudad de nacimiento'),                                              #CIUDAD DE NACIMIENTO
        'employee_age' : fields.integer("Edad"),
        'marriage_certificate':fields.boolean('Entrego acta de matrimonio?'),
        'marital_2': fields.selection(MARITAL_STATUS, 'Marital Status'),
        'Nro_de_Hijos': fields.integer('Numero de hijos', size=2),
        'grupo_sanguineo': fields.selection(GRUPO_SANGUINEO, 'Grupo Sangineo'),
        'factor_rh': fields.selection(FACTOR_RH, 'Factor RH'),
        #INFORMACION DE CONTACTO
        'street': fields.char('Av./Calle', size=50),
        'house': fields.char('Edif. Quinta o Casa', size=50),
        'piso': fields.char('Piso', size=2),
        'apto': fields.char('No. de apartamento.', size=50),
        'state_id_res': fields.many2one('res.country.state', 'Estado', domain="[('country_id','=',240)]"),
        'city_id_res': fields.many2one('hr.ciudad', 'Ciudad'),
        'telf_hab': fields.char('Telefono Habitacion', size=12),
        'telf_Contacto': fields.char('Telefono Contacto', size=12),
    }

    def onchange_email_addr(self, cr, uid, ids, email, field, context=None):
        res = {}

        if email:
            res = self.validate_email_addrs(email, field)
            if not res:
                raise osv.except_osv(('Advertencia!'), ('El email es incorrecto. Ej: cuenta@dominio.xxx. Por favor intente de nuevo'))
        return {'value':res}

    def validate_email_addrs(self, email, field):
        res = {}

        mail_obj = re.compile(r"""
                \b             # comienzo de delimitador de palabra
                [\w.%+-]       # usuario: Cualquier caracter alfanumerico mas los signos (.%+-)
                +@             # seguido de @
                [\w.-]         # dominio: Cualquier caracter alfanumerico mas los signos (.-)
                +\.            # seguido de .
                [a-zA-Z]{2,3}  # dominio de alto nivel: 2 a 6 letras en minúsculas o mayúsculas.
                \b             # fin de delimitador de palabra
                """, re.X)     # bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar
                               # el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if mail_obj.search(email):
            res = {
                field:email
            }
        return res

    def onchange_phone_number(self, cr, uid, ids, phone, field, context=None):
        res = {}
        if phone:
            res = self.validate_phone_number(phone, field)
            if not res:
                raise osv.except_osv(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        return {'value':res}

    def validate_phone_number(self, phone, field):
        res = {}

        phone_obj = re.compile(r"""^0\d{3}-\d{7}""", re.X)
                # ^: inicio de linea
                # 0\d{3}: codigo de area: cuantro (4) caracteres numericos comenzando con 0
                # -: seguido de -
                # \d{7}: numero de telefono: cualquier caracter numerico del 0 al 9. 7 numeros
                # re.X: bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if phone_obj.search(phone):
            res = {
                field:phone
            }
        return res

    def onchange_identification_id(self, cr, uid, ids, valor, field, context=None):
        res = {}
        value = {}
        if valor:
            res = self.validate_identification_id(cr, uid, valor, field)
            if res:
                value.update({field: res.get(field)})
                if res.get('warning'):
                    value.update({'warning': res.get('warning')})
            else :
                raise osv.except_osv(('Advertencia!'), (u'La cédula de identidad debe contener solo números. Ej. 19763505'))

        return value

    def validate_identification_id(self, cr, uid, valor, field):
        res = {}
        warn = {}
        mensaje = u'El número de cédula ya se encuentra registrado. El empleado está incativo.'
        ci_obj = re.compile(r"""^\d{7,15}""", re.X)
        if ci_obj.search(valor):
            #validacion de la cedula Repetida
            res = {field:valor,'warning':warn}
            identification_id = self.search(cr, uid, [(field, '=', valor)])
            if identification_id:
                for employee in self.browse(cr, uid, identification_id ):
                    if employee.active != True:
                        mensaje = mensaje + u' Valor: ' + valor
                        warn = {'title': ("Advertencia!!"),
                            'message': (mensaje)}
                        return { field: valor,'warning' : warn}
                    else:
                        raise osv.except_osv(('Advertencia!'), (u'El empleado ya existe y se encuentra activo. Cédula: %s')%(employee.identification_id_2))

        return res

    def onchange_date_of_birth(self, cr, uid, ids,field_name, field_value, context=None):
        res = {}
        warning_shown = {}
        if field_value:
            age = self.calculate_date_of_birth(field_value)
            if age >= 0:
                if field_name == "birthday":
                    res = {
                           'employee_age': age
                           }
            else :
                warning_shown = {
                                 'title': ("Advertencia!!"),
                                 'message': ('La fecha seleccionada es mayor al la fecha\n de hoy. Por favor intente de nuevo')
                                 }
        return {'value':res,'warning' : warning_shown}

    def calculate_date_of_birth(self, value):
        age = 0
        ahora = datetime.datetime.now().strftime(_DATETIME_FORMAT)
        age = relativedelta.relativedelta(datetime.datetime.strptime(ahora,_DATETIME_FORMAT),datetime.datetime.strptime(value,_DATETIME_FORMAT)).years
        return age

    def onchange_rif_er(self, cr, uid, ids, field_value, context=None):
        res = {}

        if field_value:
            res = self.validate_rif_er(field_value)
            if not res:
                raise osv.except_osv(('Advertencia!'), ('El rif tiene el formato incorrecto. Ej: VEV012345678 o VEE012345678. Por favor intente de nuevo'))
        return {'value':res}

    def validate_rif_er(self, field_value):
        res = {}

        rif_obj = re.compile(r"^VE[V|E][\d]{9}", re.X)
        if rif_obj.search(field_value):
            res = {
                'rif':field_value
            }
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = {}
        if vals.get('identification_id_2'):
            res =self.validate_identification_id(cr, uid, vals.get('identification_id_2'),'identification_id_2')
            if res:
                if res.get('warning'):
                    raise osv.except_osv(('Advertencia!'), (u'El número de cédula ya se encuentra registrado. El empleado está incativo.'))
            else:
                raise osv.except_osv(('Advertencia!'), (u'La cédula de identidad debe contener solo números. Ej. 19763505'))
        if vals.get('rif'):
            res =self.validate_rif_er(vals.get('rif'))
            if not res:
                raise osv.except_osv(('Advertencia!'), ('El rif tiene el formato incorrecto. Ej: VEV012345678 o VEE012345678. Por favor intente de nuevo'))
        if vals.get('personal_email'):
            res =self.validate_email_addrs(vals.get('personal_email'),'personal_email')
            if not res:
                raise osv.except_osv(('Advertencia!'), ('El email es incorrecto. Ej: cuenta@dominio.xxx. Por favor intente de nuevo'))
        if vals.get('telf_hab'):
            res =self.validate_phone_number(vals.get('telf_hab'),'telf_hab')
            if not res:
                raise osv.except_osv(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        if vals.get('telf_Contacto'):
            res =self.validate_phone_number(vals.get('telf_Contacto'),'telf_Contacto')
            if not res:
                raise osv.except_osv(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        return super(hr_employee, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        res = {}
        if vals.get('identification_id_2'):
            res =self.validate_identification_id(cr, uid, vals.get('identification_id_2'),'identification_id_2')
            if res:
                if res.get('warning'):
                    raise osv.except_osv(('Advertencia!'), (u'El número de cédula ya se encuentra registrado. El empleado está incativo.'))
            else:
                raise osv.except_osv(('Advertencia!'), (u'La cédula de identidad debe contener solo números. Ej. 19763505'))
        if vals.get('rif'):
            res =self.validate_rif_er(vals.get('rif'))
            if not res:
                raise osv.except_osv(('Advertencia!'), ('El rif tiene el formato incorrecto. Ej: VEV012345678 o VEE012345678. Por favor intente de nuevo'))
        if vals.get('personal_email'):
            res =self.validate_email_addrs(vals.get('personal_email'),'personal_email')
            if not res:
                raise osv.except_osv(('Advertencia!'), ('El email es incorrecto. Ej: cuenta@dominio.xxx. Por favor intente de nuevo'))
        if vals.get('telf_hab'):
            res =self.validate_phone_number(vals.get('telf_hab'),'telf_hab')
            if not res:
                raise osv.except_osv(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        if vals.get('telf_Contacto'):
            res =self.validate_phone_number(vals.get('telf_Contacto'),'telf_Contacto')
            if not res:
                raise osv.except_osv(('Advertencia!'), (u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
        res = super(hr_employee, self).create(cr, uid, vals, context)
        return res

hr_employee()

class hr_profesion(osv.osv):

    def _get_profesion_position(self, cr, uid, ids, context=None):
        res = []
        for employee in self.pool.get('hr.employee').browse(cr, uid, ids, context=context):
            if employee.profesion_id:
                res.append(employee.profesion_id.id)
        return res

    _name = "hr.profesion"
    _description = "Profesion Description"
    _columns = {
        'name': fields.char('Profesion Name', size=128, required=True, select=True),
        #'employee_ids': fields.one2many('hr.employee', 'profesion_id', 'Employees'),
                }

hr_profesion()

class hr_ciudad(osv.osv):

    def _get_ciudad_position(self, cr, uid, ids, context=None):
        res = []
        for employee in self.pool.get('hr.employee').browse(cr, uid, ids, context=context):
            if employee.city_id:
                res.append(employee.city_id.id)
        return res

    _name = "hr.ciudad"
    _description = "Ciudad Description"
    _columns = {
        'name': fields.char('Ciudad Name', size=50, required=True, select=True),
        'employee_ids': fields.one2many('hr.employee', 'city_id', 'Employees'),
        'estate_id' : fields.many2one('res.country.state', 'Estado'),
    }

hr_ciudad()