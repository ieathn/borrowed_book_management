from odoo import models, fields, api
from datetime import date, timedelta
from odoo.exceptions import UserError


class LibraryTransaction(models.Model):
    _name = 'library.transaction'
    _description = 'Library Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Transaction ID",
        default=lambda self: self.env['ir.sequence'].next_by_code('library.transaction'),
        readonly=True
    )

    member_id = fields.Many2one('library.member', string="Borrower", required=True, tracking=True)
    book_copy_id = fields.Many2one('library.book.copy', string="Book Copy", required=True, tracking=True)
    book_id = fields.Many2one(related='book_copy_id.book_id', store=True, string="Book Title")
    borrow_date = fields.Date(default=fields.Date.today, tracking=True)
    expected_return_date = fields.Date(default=lambda self: fields.Date.today() + timedelta(days=7))
    return_date = fields.Date(string="Return Date")
    
    status = fields.Selection([
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('late', 'Late')
    ], string="Status", default='borrowed', tracking=True)

    late_days = fields.Integer(string="Late Days", compute='_compute_late_days', store=True)
    is_overdue = fields.Boolean(string="Overdue", compute='_compute_late_days', store=True)

    fine_amount = fields.Float(string="Fine Amount", compute='_compute_fine_amount', store=True)
    fine_record_id = fields.Many2one('library.fine', string="Fine Record", readonly=True)

    # --- Compute Functions ---
    @api.depends('expected_return_date', 'return_date', 'status')
    def _compute_late_days(self):
        for rec in self:
            if rec.status == 'late' and rec.return_date and rec.expected_return_date:
                rec.late_days = (rec.return_date - rec.expected_return_date).days
                rec.is_overdue = True
            elif rec.status == 'borrowed' and rec.expected_return_date < fields.Date.today():
                rec.late_days = (fields.Date.today() - rec.expected_return_date).days
                rec.is_overdue = True
            else:
                rec.late_days = 0
                rec.is_overdue = False

    @api.depends('late_days')
    def _compute_fine_amount(self):
        for rec in self:
            rec.fine_amount = rec.late_days * 3000 if rec.late_days > 0 else 0

    # --- Onchange / Triggers ---
    @api.onchange('status')
    def _onchange_status(self):
        """Đồng bộ status giữa các models liên quan"""
        for rec in self:
            if not rec.book_copy_id:
                continue
            # Cập nhật trạng thái book copy
            rec.book_copy_id.status = (
                'available' if rec.status == 'returned'
                else 'borrowed' if rec.status == 'borrowed'
                else 'reserved'
            )

            # Nếu có loan liên quan → đồng bộ trạng thái loan
            loan = self.env['library.loan'].search([('book_copy_id', '=', rec.book_copy_id.id)], limit=1)
            if loan:
                loan.status = rec.status

            # Nếu trễ → tạo hoặc cập nhật fine
            if rec.status == 'late' and rec.fine_amount > 0:
                Fine = self.env['library.fine']
                existing = Fine.search([('loan_id.book_copy_id', '=', rec.book_copy_id.id), ('paid', '=', False)], limit=1)
                if not existing:
                    fine = Fine.create({
                        'loan_id': loan.id if loan else False,
                        'paid': False,
                    })
                    rec.fine_record_id = fine.id

    # --- Action Buttons ---
    def action_mark_returned(self):
        for rec in self:
            rec.return_date = fields.Date.today()
            rec.status = 'returned'
            rec.book_copy_id.status = 'available'

    def action_mark_late(self):
        for rec in self:
            rec.status = 'late'
            rec.book_copy_id.status = 'borrowed'

    def action_mark_borrowed(self):
        for rec in self:
            rec.status = 'borrowed'
            rec.book_copy_id.status = 'borrowed'
