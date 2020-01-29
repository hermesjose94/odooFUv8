# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Vauxoo C.A.
#    Planified by: Humberto Arocha
#    Audited by: Vauxoo C.A.
#############################################################################

from openerp.osv import fields, orm


class add_contacts(orm.TransientModel):
    _name = 'add.contacts'


    def _set_default_partner_ids(self, cr, uid, context={}):
        child_ids = [child_id.id for partner in self.pool.get('res.partner').browse(cr, uid, context.get('active_id'), context=context) for child_id in partner.child_ids if partner.child_ids]
        return child_ids


    def set_contacts(self, cr, uid, ids, context={}):
        contact_ids = [partner.id for add in self.browse(cr, uid, ids, context) for partner in add.partner_ids]
        self.pool.get('res.partner').write(cr, uid, context.get('active_id'), {'child_ids': [(6, 0, contact_ids)]})
        return {'type': 'ir.actions.act_window_close'}

    _columns = {
        'partner_ids' : fields.many2many('res.partner', 'res_partner_for_contacts_rel', 'contacts_id', 'partner_id',
                                       'Contactos'),
    }
    _defaults = {
        'partner_ids': _set_default_partner_ids,
    }


