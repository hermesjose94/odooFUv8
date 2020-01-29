# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class purchase_order_rate_currency(osv.osv):
    
    _inherit = 'purchase.order'
    
    def _get_currency_default(self, cr, uid, ids, context=None):
        if context is None: context = {}
        res_company = self.pool.get('res.company')
        company_default = res_company._company_default_get(cr, uid, context=context)
        company_currency_id = res_company.browse(cr, uid, company_default).currency_id.id
        return company_currency_id
    
    
    _columns = {
        'date_currency': fields.date('Fecha Tasa de Cambio'),
        'res_currency_rate': fields.float('Tasa de cambio', digits=(6,6), readonly = True),
        'company_currency_id_default': fields.many2one('res.currency', string='Moneda por defecto de la compañia', store=False),
        'flag_currency': fields.boolean('Bandera de seleccion de tasa', store=False),
    }
    
    _defaults = {
        'company_currency_id_default': _get_currency_default,
        'flag_currency': False
    }
    
    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, company_currency_id_default, context=None):
        if not context: context = {}
        if not pricelist_id: return False
        res = {}
        currency_id = self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context).currency_id.id
        if currency_id:
            res = {'value': {'currency_id': currency_id, 'flag_currency': False}}
        if currency_id != company_currency_id_default: res['value'].update({'flag_currency': True})
        return res
    
    def onchange_date_currency(self, cr, uid, ids, date_currency, currency_id, company_currency_id_default, context=None):
        ctx =  isinstance(context, dict) and context.copy() or {}
        val = {'date_currency': False, 'res_currency_rate': False}
        warn = {}
        if currency_id and currency_id != company_currency_id_default:
            currency_rate_obj = self.pool.get('res.currency.rate')
            rate_list_ids = currency_rate_obj.search(cr, uid, [('currency_id','=', currency_id),('name','ilike', str(date_currency) + '%')])
            if len(rate_list_ids) > 1:
                warn = {'title': 'Error de Validacion', 'message': 'Se encontro mas de una tasa para la fecha especificada. Debe haber solo una tasa por dia.  Comuniquese con el departamento de Contabilidad'}
            elif len(rate_list_ids) == 1:
                rate_id = currency_rate_obj.browse(cr, uid, rate_list_ids[0], ctx)
                if rate_id.rate > 0.0:
                    val.update({'date_currency': date_currency, 'res_currency_rate': rate_id.rate})
                else:
                    warn = {'title': 'Error de Validacion', 'message': 'La tasa registrada en la fecha indicada no es válida, se le recomienda contactar al departamento de contabilidad'}
            elif len(rate_list_ids) == 0:
                warn = {'title': 'Error de Validacion', 'message': 'La fecha ingresada no esta registrada en la moneda configurada en la tarifa de compra.  Seleccione una fecha distinta o contacte al departamento de Contabilidad'}
        return {'value': val, 'warning': warn}

    
    def action_invoice_create(self, cr, uid, ids, context=None):
        if not context: context = {}
        res = super(purchase_order_rate_currency, self).action_invoice_create(cr, uid, ids, context=context)
        if res:
            inv_brw = self.pool.get('account.invoice').browse(cr, uid, res, context=context)
            date_c = self.browse(cr, uid, ids[0], context).date_currency
            rate = self.browse(cr, uid, ids[0], context).res_currency_rate
            inv_brw.write({'date_currency': date_c, 'res_currency_rate': rate, 'flag_currency': True})
        return res
