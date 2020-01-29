# coding: utf-8
###########################################################################
#    Modulo escrito para Odoo, Open Source Management Solution
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

{
    'name' : 'Notas de Credito - Validaciones y ajustes varios',
    'version' : '1.0',
    'author' : '',
    'category' : 'Accounting & Finance',
    'description' : """
Ajustes y modificaciones para las Notas de Credito.
===================================================

    * Se evita que se puedan crear notas de credito por un monto mayor al de la factura original
    * Se evita que se pueda repetir el numero de control para las facturas y las notas de credito

Colaborador: RSosa
    """,
    'website': '',
    'depends' : ['account'],
    'data': ['account_invoice_view.xml'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: