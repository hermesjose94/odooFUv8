# -*- coding: UTF-8 -*-
#    type of the change:  Created
#    Comments: Creacion de generacion de codigo para clientes y proveedores (depends for res_partner)



from openerp.osv import fields, osv
from datetime import datetime
from dateutil import relativedelta
from curses.ascii import isdigit
import re

class gc_cliente_proveedor(osv.Model):
    _inherit = 'res.partner'
    _columns = {
        'child_ids': fields.many2many('res.partner', 'res_partner_rel','parent_id', 'child_id', 'Contacts', domain=[('active', '=', True)]),

    }


    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):

        if context.get('contact'):

            if view_type == 'tree':
                view_id = self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', 'view_contact_tree')], limit=1)


            elif view_type == 'form':
                view_id = self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', 'res.contacts.form')], limit=1)

            if view_id:
                return super(osv.Model, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                                     context=context, toolbar=toolbar, submenu=submenu)

        return super(gc_cliente_proveedor, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)


    def validar_rif_d(self, cr, uid, ids, context={}):
        for partner in self.browse(cr, uid, ids, context):
            if partner.vat:
                rif_id = self.search(cr, uid, [('vat', '=', partner.vat)])
                if len(rif_id) > 1:
                    return False

            return True

    def validar_ci(self, cr, uid, ids, context={}):

        for partner in self.browse(cr, uid, ids, context):
            if partner.ci:
                ci_id = self.search(cr, uid, [('ci', '=', partner.ci)])
                if len(ci_id) > 1: return False
        return True

    def onchange_id_nbr(self, cr, uid, ids, value, context=None):
        if context is None:
            was = {

            }
        validos = "0123456789"
        res = {}
        warning_shown = {}

        if value:
            for caracter in value:
                if validos.find(caracter) != -1:
                    res = {'ci': value}
                else:
                    res = {'ci': False}
                    warning_shown = {
                        'title': ("Advertencia!!"),
                        'message': ('La cedula de identidad debe contener solo numeros')
                    }
                    break
        else:
            res = {'ci': False}

        return {'value': res, 'warning': warning_shown}


    _constraints = [
        (validar_rif_d, "El RIF que esta intentando ingresar ya existe", ['vat']),
        (validar_ci, "La CI que esta intentando ingresar ya existe", ['ci']),
    ]
gc_cliente_proveedor()



