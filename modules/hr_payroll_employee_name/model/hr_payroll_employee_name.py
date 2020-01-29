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

import time

from openerp.osv import fields, osv
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _

class hr_employee(osv.osv):
    '''
    Pay Slip
    '''
    _inherit = 'hr.employee'
    _description = 'Pay Slip'

    _columns = {
        'full_name': fields.char('Nombre', size=256, required=True),
        'firstname': fields.char('Nombre', size=64),
        'firstname2': fields.char('2do. Nombre', size=64),
        'lastname': fields.char('Apellido', size=64, required=True),
        'lastname2': fields.char('2do. Apellido', size=64),
    }

    def onchange_concat_name(self, name1, name2, lastname, lastname2):
        code = [' ', ' ', ' ', ' ', ' ', ' ', ' ']
        if name1 != False and lastname != False:
            code[0] = lastname
            code[2] = lastname2 or ''
            code[4] = name1
            code[6] = name2 or ''
            codigo = code[0] + code[1] + code[2] + code[3] + code[4] + code[5] + code[6]
            return (codigo)
        if name1 == '' and lastname == '':
            return ('')

    def onchange_name_filed(self, cr, uid, ids, name1, name2, lastname, lastname2):
        res = {
            'value': {
                'full_name': self.onchange_concat_name(name1, name2, lastname, lastname2),
            },
        }
        return res

    def actualizar_nombre(self, cr, uid):
        print ("====Inicio Cambio de nombres Ejecutado====")
        employee_ids = self.search(cr, uid,[])
        employees = self.browse(cr, uid,employee_ids)
        values = {}
        for emp in employees:
            nom = emp.name_related
            nom = nom.split(' ')
            values = {
                'full_name': emp.name_related,
                'firstname': nom[2] if len(nom) > 2 else '',
                'firstname2': nom[3] if len(nom) > 3 else '',
                'lastname': nom[0],
                'lastname2': nom[1] if len(nom) > 1 else '',
            }
            self.write(cr, uid,emp.id,values)
        print ("====Cambio de nombres Ejecutado====")

    def write(self, cr, uid, ids, values, context=None):
        """
        funcion que permite actualizar el nombre segun es conveniente
        """
        if context is None:
            context = {}
        if not hasattr(ids, '__iter__'): ids = [ids]

        res = super(hr_employee, self).write(cr, uid, ids, values, context)
        for hr in self.browse(cr, uid, ids):
            firstname = hr.firstname or False
            lastname = hr.lastname or False
            firstname2 = hr.firstname2 or False
            lastname2 = hr.lastname2 or False
            if firstname or lastname:
                names = (lastname, lastname2, firstname, firstname2)
                super(hr_employee, self).write(cr, uid, hr.id, {'name': " ".join(s for s in names if s)}, context)
            else:
                super(hr_employee, self).write(cr, uid, hr.id, {'lastname': hr.name}, context)
                # FIN DE CODIGO TOMADO DEL MODULO hr_employee_firstname

            try:
                # : 20/04/2016 Se agrega validacion para que no ejecute el cambio sobre los mensajes de bienvanida en el sistema
                if values.get('firstname', False) or values.get('lastname', False) or values.get('firstname2',
                                                                                                 False) or values.get(
                        'lastname2', False):
                    (model, mail_group_id) = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mail',
                                                                                                 'group_all_employees')

                    self.pool.get('mail.group').message_post(cr, uid, [mail_group_id],
                                                             body=_(
                                                                 'Welcome to %s! Please help him/her take the first steps with OpenERP!') % (
                                                                      hr.name),
                                                             subtype='mail.mt_comment', context=context)
            except:
                pass

        return res

    def create(self, cr, uid, data, context=None):
        # CODIGO TOMADO DEL MODULO hr_employee_firstname
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        firstname2 = data.get('firstname2')
        lastname2 = data.get('lastname2')
        if firstname or lastname:
            names = (lastname, lastname2, firstname, firstname2)
            data['name'] = " ".join(s for s in names if s)
        else:
            data['lastname'] = data['name']
            # FIN DE CODIGO TOMADO DEL MODULO hr_employee_firstname
        employee_id = super(hr_employee, self).create(cr, uid, data, context=context)
        try:
            (model, mail_group_id) = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mail',
                                                                                         'group_all_employees')
            employee = self.browse(cr, uid, employee_id, context=context)
            self.pool.get('mail.group').message_post(cr, uid, [mail_group_id],
                                                     body=_(
                                                         'Welcome to %s! Please help him/her take the first steps with OpenERP!') % (
                                                          employee.name),
                                                     subtype='mail.mt_comment', context=context)
        except:
            pass  # group deleted: do not push a message
        return employee_id
hr_employee()