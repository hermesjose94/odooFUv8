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

{
    'name': 'Selection of exchange rate for foreign currency',
    'version': '0.2',
    'description': '''
    Permite efectuar la selección de una tasa de cambio específica segun la fecha de ingreso de la misma
    para las operaciones de compra a proveedores internacionales.  La tasa seleccionada sera la utilizada
    en los calculos de Presupuesto, asi como en los asientos contables.
    
    Collaborator: Roger Sosa 
    ''',
    'author': '',
    'website': '',
    'data': ['view/purchase_order_view.xml',
             'view/account_invoice_view.xml',
             'view/account_move_view.xml'],
             #'view/wh_iva_tax_line.xml'],
    'depends': ['base',
                'account',
                'l10n_ve_account_check_debit_note',
                'l10n_ve_fiscal_requirements',
                'l10n_ve_withholding',
                'l10n_ve_withholding_islr',
                'l10n_ve_withholding_iva',
                'purchase',
                'stock'],
    #'license': 'Other OSI approved licence',
    'installable': True,
    'active': False,
}