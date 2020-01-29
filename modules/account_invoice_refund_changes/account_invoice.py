# coding: utf-8
###########################################################################
#    Module Writen to Odoo, Open Source Management Solution
###############################################################################
#    Credits:
#    Coded by: Roger Sosa
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp import models, fields, api, _

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    
    @api.multi
    def change_price_unit(self, monto):
        '''
        Se usa este metodo para evitar que, al generar una nota de credito, se coloque un monto superior al de la factura original
        '''
        res = {}
        if self.invoice_id.type in ['in_refund', 'out_refund']:
            valor_original = self.price_unit
            res = {'value': {'price_unit': valor_original}}
            if monto > valor_original:
                res.update({'warning': {'title': "Advertencia!", 'message': "No puede ingresar un monto mayor al de la factura original!"}})
            else:
                res['value']['price_unit'] = monto 
            
        return res