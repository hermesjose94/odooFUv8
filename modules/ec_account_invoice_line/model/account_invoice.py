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
##############################################################################

from openerp import api
from openerp.osv import fields, osv
import num2cad

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    def _conver_mont(self, cr, uid, ids, amount_total, arg=None, context=None):
        result=dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context):
            if obj.amount_total:
                monto=str(obj.amount_total)
                cadena= num2cad.EnLetras(monto)
                cantidad= cadena.largo
                letra = cadena.escribir
                result[obj.id]= letra
            return result

    _columns = {

        'monto_letra':fields.function(_conver_mont, type='char',
            store=True, string='Monto En Letra', )
    }



