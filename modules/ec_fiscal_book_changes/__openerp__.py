# coding: utf-8
##############################################################################
#
# <contacto>
# <Telefono: +58(212) 237.77.53>
# Caracas, Venezuela.
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
    'name': 'Libros Fiscales - Formato SENIAT actualizado y ajustes varios.',
    'version': '1.0',
    'category': 'Generic Modules/Accounting',
    'summary': 'Ajuste del formato SENIAT de Libros Fiscales, y otras modificaciones',
    'description': """
Libros Fiscales - Formato SENIAT actualizado y ajuste varios
============================================================

Se ajusta el formato de los Libros Fiscales segun la norma emitida en <<datos de la gaceta donde se establece el cambi>>

Ajustes varios:
 * Se agrega por defecto el id de la empresa.
 * Se corrigen completamente los formatos de Libros Fiscales, ajustandolos a la normativa venezolana.
 * Se corrigen las nomenclaturas del tipo de transacción.
 * Se separan los renglones de las retenciones de IVA de su factura correspondiente.
 * Los montos de las Retenciones aparecen con signo positivo.
 

Colaborador: Roger Sosa
    """,

    'author': '',
    'website': '',
    'depends': ['l10n_ve_fiscal_book'],
    'data': ['report/fiscal_book_report.xml'],
    #'demo': [],
    #'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: