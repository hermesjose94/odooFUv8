#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Luis Torres.
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Luis Torres
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
{
    "name" : "Conversión de Numero a Letra – Total del monto en la Factura",
     'version' : '1.0',
    'author' : '',
    'website': '',
    "category": "Contabilidad",
    "summary": "Monto Total en letra",
    "description": """

==============================================\n
\n
     Convierte el monto tota de la facturacion a letra\n

     Nota: El monto en letra se encuentra oculto, para generar el reporte es con el campo "monto_letra"\n
==============================================\n
    colaborador: EUranga
                   """,
    "depends" : ["base",
                "account",
                ],
    'data': [
        "view/account_invoice_view.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
