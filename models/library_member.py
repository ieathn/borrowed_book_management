from odoo import models, fields

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _inherit = ['mail.thread']

    name = fields.Char("Reader Name", required=True)
    student_code = fields.Char("Student Code")
    phone = fields.Char("Phone")
    loan_ids = fields.One2many('library.loan', 'member_id', string="Loans")
    total_loans = fields.Integer(compute="_compute_total_loans")

    def _compute_total_loans(self):
        for r in self:
            r.total_loans = len(r.loan_ids)
