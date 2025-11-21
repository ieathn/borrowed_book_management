from odoo import models, fields

class LibraryFine(models.Model):
    _name = 'library.fine'
    _description = 'Library Fine'

    loan_id = fields.Many2one('library.loan', required=True)
    member_id = fields.Many2one(related="loan_id.member_id", store=True)
    fine_amount = fields.Float(related="loan_id.fine_amount")
    paid = fields.Boolean(default=False)
    payment_date = fields.Date()
