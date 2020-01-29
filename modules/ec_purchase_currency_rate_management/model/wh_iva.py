# coding: utf-8
##############################################################################
#

#
# Colaborador: Roger Sosa <rsosa>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.addons import decimal_precision as dp
from openerp import models, fields, api  #, exceptions, _

class AccountWhIvaLineTax(models.Model):

    _inherit = 'account.wh.iva.line.tax'
    
    @api.multi
    @api.depends('inv_tax_id')
    def _get_base_amount(self):
        """ Return withholding amount
            Overwriting by _15DIC2016_rsosa
        """
        for record in self:
            flag = record.inv_tax_id.invoice_id.flag_currency or False
            rate_c = flag and record.inv_tax_id.invoice_id.res_currency_rate or 1.0
            f_xc = self.env['l10n.ut'].sxc(
                record.inv_tax_id.invoice_id.currency_id.id,
                record.inv_tax_id.invoice_id.company_id.currency_id.id,
                record.wh_vat_line_id.retention_id.date)
            record.base = flag and (record.inv_tax_id.base * rate_c) or f_xc(record.inv_tax_id.base)
            record.amount = flag and (record.inv_tax_id.amount * rate_c) or f_xc(record.inv_tax_id.amount)

    
    base = fields.Float(
        string='Tax Base', digit=dp.get_precision('Withhold'),
        store=True, compute=_get_base_amount,
        help="Tax Base")
    amount = fields.Float(
        string='Taxed Amount', digits=dp.get_precision('Withhold'),
        store=True, compute=_get_base_amount,
        help="Withholding tax amount")
    