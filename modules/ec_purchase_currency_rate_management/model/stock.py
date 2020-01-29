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

from openerp.osv import osv

class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        ctx = isinstance(context, dict) and context.copy() or {}
        origin = move.origin
        purchase_obj = self.pool.get('purchase.order')
        pur_id = purchase_obj.search(cr, uid, [('name','=',origin)])
        if pur_id:
            pur_brw = purchase_obj.browse(cr, uid, pur_id[0], context)
            rate = pur_brw.res_currency_rate
            #amount_total = pur_brw.amount_total
            if rate: ctx.update({'rate_currency': rate})
        return super(stock_move, self)._create_product_valuation_moves(cr, uid, move, context=ctx)
    
    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        
        res = super(stock_move, self)._create_account_move_line(cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=context)
        if context and context.get('rate_currency') and res:
            rate = context.get('rate_currency')
            amount = res[0][2]['amount_currency'] * rate
            res[0][2].update({'debit': amount, 'rate_currency': rate})
            res[1][2].update({'credit': amount, 'rate_currency': rate})
        return res