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
#    Modulo que permite la anulacion de cheques antes de ser emitidos
#    autor: Roger Sosa, para Grupo AMN, c.a.
#
##############################################################################

from openerp import fields, models, api, exceptions

import logging
_logger = logging.getLogger(__name__)
import time

class account_issued_check(models.Model):
    _inherit = 'account.issued.check'

    @api.multi
    def onchange_number(self, number):

        def anulado(num):
            if not num:
                return False
            check_cancel_obj = self.env['check.cancel']
            check_cancel_number = check_cancel_obj.search([('number','=',num)])
            if check_cancel_number:
                return True
            else:
                return False

        def usado(num):
            if not num:
                return False
            issued_check_obj = self.pool.get('account.issued.check')
            issued_check_number = issued_check_obj.search([('number','=',num)])
            if issued_check_number:
                return True
            else:
                return False

        res = {}
        number_str = str(number)
        if len(number_str) != 8:
            res = {'value':{'number': 0}}
            res.update({'warning': {'title': ("Error"), 'message': ('El numero de cheque debe ser de 8 digitos !')}})
        else:
            while anulado(number) or usado(number):
                number = str((long(number) + 1))
            res.update({'value':{'number':number}})
        return res

class check_cancel(models.Model):

    _name = 'check.cancel'
    _description = 'Permite la anulacion de numeros de cheques antes de su emision'


    number = fields.Char('Numero de Cheque', size=8, required=True, select=True, readonly=True, states={'draft': [('readonly', False)]})
    actual = fields.Char('Cheque Actual', size=8)
    ultimo = fields.Char('Ultimo Cheque', size=8)
    checkbook_id = fields.Many2one('account.checkbook','Chequera', select=True, readonly=True, required=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users','Usuario')
    date = fields.Date('Fecha')
    notas = fields.Text('Notas')
    state = fields.Selection([('draft','Borrador'),('cancel','Anulado')], string='Estatus', readonly=True, select=True, track_visibility='onchange')


    @api.multi
    def _get_checkbook_id(self):
        res={}

        checkbook_pool = self.env['account.checkbook']

        res = checkbook_pool.search([('state', '=', 'active')])

        if res:
            return res.id
        else:
            return False


    def onchange_checkbook(self, checkbook_id):
        res = {}
        if not checkbook_id:
            return {}
        chequera = self.env['account.checkbook'].browse(checkbook_id)
        if chequera:
            actual = chequera.actual_number
            ultimo = chequera.range_hasta
            return {'value': {'actual': actual, 'number': actual, 'ultimo': ultimo}}
        else:
            return {}

    _defaults = {
            'user_id': lambda s, cr, u, c: u,
            'checkbook_id': _get_checkbook_id,
            'date': lambda *a: time.strftime('%Y-%m-%d'),
            'state': 'draft',
                 }


    def onchange_number(self, cr, uid, ids, actual, number, ultimo, context=None):
        if number and ultimo and actual:
            if len(str(number)) != 8:
                warning_shown = {
                             'title': ("Error"),
                             'message': ('El numero introducido debe ser de 8 digitos')
                             }
                return {'value':{'number': False}, 'warning': warning_shown}

            issued_obj = self.pool.get('account.issued.check')
            issued_list = issued_obj.search([('number','=', number)])
            if issued_list:
                warning_shown = {
                             'title': ("Error"),
                             'message': ('El numero indicado ya fue usado')
                             }
                return {'value':{'number': False}, 'warning': warning_shown}

            if (long(number) < long(actual)) or (long(number) > long(ultimo)):
                warning_shown = {
                             'title': ("Error"),
                             'message': ('El numero indicado ya fue usado, o no pertenece a la chequera seleccionada')
                             }
                return {'value':{'number': False}, 'warning': warning_shown}

            anulados_list = self.search(cr, uid, [])
            #i = 0
            ya_anulados = []
            for id in anulados_list:
                anulados_obj = self.browse(cr, uid, id, context=context)
                ya_anulados.append(anulados_obj.number)
                #i += 1

            for n in ya_anulados:
                if number == n: # and n[i].state == 'cancel'
                    warning_shown = {
                             'title': ("Error"),
                             'message': ('El numero indicado ya fue anulado o esta marcado para ser anulado')
                             }
                    return {'value':{'number': False}, 'warning': warning_shown}

            return {'value': {'number':number}}
        else:
            return {'value':{'number': False}}


    def wkf_cancel(self, cr, uid, ids, context=None):
        if ids:
            estado = self.browse(cr, uid, ids, context=context)
            numero = estado[0].number
            if estado[0].state == 'draft':
                estado[0].state = 'cancel'
                estado[0].write({'state':'cancel'})

            id_chequera = self.browse(cr, uid, ids[0], context=context).checkbook_id.id
            chequeras=self.pool.get('account.checkbook')
            chequera_obj = chequeras.browse(cr, uid, id_chequera, context=context)
            if chequera_obj.actual_number == numero:
                siguiente = long(numero) + 1
                siguiente = str(siguiente)
                chequeras.write(cr, uid, [id_chequera], {'actual_number': siguiente}, context=context)
        return True

    def wkf_undo(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'draft' })
        return True
