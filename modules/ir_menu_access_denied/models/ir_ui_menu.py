# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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



import base64
import operator
import re
import threading

import openerp.modules
from openerp import fields, models
from openerp import api, tools
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _

class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.multi
    @api.returns('self')
    def _filter_visible_menus(self):
        """ filter all views thats in the tab menu_denied_access
        """
        groups = self.env.user.groups_id

        # visibility is entirely based on the user's groups;
        # self._menu_cache[key] gives the ids of all visible menus

        _filter_visible_menus = super(ir_ui_menu, self)._filter_visible_menus()
        # visibility is entirely based on the user's groups;
        # self._menu_cache[key] gives the ids of all visible menus
        invisible = groups.mapped('menu_denied_access').mapped('id')
        res = _filter_visible_menus.filtered(lambda menu: menu.id not in invisible)
        return res



    groups_denied_id = fields.Many2many('res.groups', 'ir_ui_menu_group_denied_rel',
                                  'menu_id', 'gid', 'Groups',
                                  help="If you have groups, the visibility of this menu will be based on these groups. " \
                                       "If this field is empty, Odoo will compute visibility based on the related object's read access.")

class res_groups(models.Model):
    _inherit = "res.groups"
    _description = "Access Denied Groups"
    _order = 'name'

    menu_denied_access = fields.Many2many('ir.ui.menu', 'ir_ui_menu_group_denied_rel', 'gid', 'menu_id', 'Access Menu')