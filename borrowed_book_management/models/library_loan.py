from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Loan'
    _inherit = ['mail.thread']

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('library.loan'))
    member_id = fields.Many2one('library.member', required=True)
    book_copy_id = fields.Many2one('library.book.copy', required=True)
    book_id = fields.Many2one(related="book_copy_id.book_id", store=True)
    borrow_date = fields.Date(default=fields.Date.today)
    expected_return = fields.Date(default=lambda self: fields.Date.today() + timedelta(days=7))
    return_date = fields.Date()
    status = fields.Selection([
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('late', 'Late'),
    ], default='borrowed', tracking=True)

    late_days = fields.Integer(compute="_compute_late")
    fine_amount = fields.Float(compute="_compute_late")

    @api.depends('expected_return', 'return_date')
    def _compute_late(self):
        for loan in self:
            if loan.return_date and loan.return_date > loan.expected_return:
                loan.late_days = (loan.return_date - loan.expected_return).days
                loan.fine_amount = loan.late_days * 3000
            else:
                loan.late_days = 0
                loan.fine_amount = 0
            
    @api.model
    def _cron_check_overdue(self):
        """Chạy hàng ngày: mark loans overdue & tạo fine nếu cần"""
        today = fields.Date.context_today(self)
        loans = self.search([('status', '=', 'borrowed'), ('expected_return', '<', today)])
        Fine = self.env['library.fine']
        for loan in loans:
            # mark late
            loan.write({'status': 'late'})
            # compute fine (sử dụng compute field hoặc hàm)
            # tạo record fine nếu chưa có fine chưa paid cho loan này
            existing = Fine.search([('loan_id', '=', loan.id), ('paid', '=', False)])
            if not existing and loan.fine_amount > 0:
                Fine.create({
                    'loan_id': loan.id,
                    'fine_amount': loan.fine_amount,
                    'paid': False,
                })
            # send overdue email
            try:
                template = self.env.ref('borrowed_book_management.email_template_overdue_notice')
                if template:
                    template.with_context(lang=loan.member_id.lang or 'en_US').send_mail(loan.id, force_send=False)
            except Exception as e:
                _logger = self.env['ir.logging']
                # just log; don't interrupt cron
                self.env['ir.logging'].sudo().create({
                    'name': 'library.cron',
                    'type': 'server',
                    'dbname': self.env.cr.dbname,
                    'level': 'ERROR',
                    'message': f'Error sending overdue email for loan {loan.id}: {e}',
                    'path': 'library.loan._cron_check_overdue',
                })

    @api.model
    def _cron_send_return_reminders(self):
        """Gửi nhắc trả 2 ngày trước due date"""
        today = fields.Date.context_today(self)
        remind_date = today + timedelta(days=2)
        loans = self.search([('status', '=', 'borrowed'), ('expected_return', '=', remind_date)])
        for loan in loans:
            try:
                template = self.env.ref('borrowed_book_management.email_template_return_reminder')
                if template:
                    template.with_context(lang=loan.member_id.lang or 'en_US').send_mail(loan.id, force_send=False)
            except Exception as e:
                # log error
                self.env['ir.logging'].sudo().create({
                    'name': 'library.cron',
                    'type': 'server',
                    'dbname': self.env.cr.dbname,
                    'level': 'ERROR',
                    'message': f'Error sending reminder for loan {loan.id}: {e}',
                    'path': 'library.loan._cron_send_return_reminders',
                })
