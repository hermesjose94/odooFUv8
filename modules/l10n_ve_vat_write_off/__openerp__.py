# coding: utf-8
{
    "name": "VAT Write Off",
    "version": "0.5",
    "depends": ["base",
                "account",
                "decimal_precision",
                "l10n_ve_fiscal_requirements","l10n_ve_imex",
                "report_webkit"],
    "author": "Vauxoo",
    "license": "AGPL-3",
    "website": "http://openerp.com.ve",
    "category": "Generic Modules/Accounting",
    "data": [
        "report/l10n_ve_vat_write_off_report.xml",
        "view/l10n_ve_vat_write_off.xml",
    ],
    "installable": True,
}
