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
    "name" : "Validacion de Factura contra Fecha del Servidor",
     'version' : '1.0',
    'author' : '',
    'website': '',
    "category": "Contabilidad",
    "summary": "Fecha de Documentacion automatizada ",
    "description": """

==============================================\n
\n
     Este modulo permite que al validad la factura acutomaticamente se carge la fecha de documentacion
==============================================\n
    colaborador: EUranga
                   """,
    "depends" : ["base",
                "l10n_ve_fiscal_requirements",
                "account",
                ],
    'data': [
        "view/invoice_view.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
