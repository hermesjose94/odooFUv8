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

from openerp.osv import fields, osv
from openerp import api, models

class FiscalBookWizard(osv.osv_memory):
    
    _inherit = "fiscal.book.wizard"
    
    
#_22SEP2016_rsosa: Se sobreescribe el método original para que busque
#                          las referencias a los reportes nuevos.

    def _print_report(self, cr, uid, ids, data, context=None):
        if data['form']['type'] == 'sale':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'fiscal.book.sale.seniat', 'datas': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fiscal.book.purchase.seniat', 'datas': data}
        
