from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class LibraryReservation(models.Model):
    _name = 'library.reservation'
    _description = 'Book Reservation'

    member_id = fields.Many2one('library.member', required=True)
    book_id = fields.Many2one('library.book', required=True)
    reserve_date = fields.Date(default=fields.Date.today)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('expired', 'Expired')
    ], default='pending')
    expire_date = fields.Date(string="Expire Date", compute='_compute_expire_date', store=True)

    @api.depends('reserve_date')
    def _compute_expire_date(self):
        for rec in self:
            if rec.reserve_date:
                rec.expire_date = fields.Date.to_date(rec.reserve_date) + relativedelta(days=2)
            else:
                rec.expire_date = False

    @api.model
    def _cron_expire_reservations(self):
        """Hàng ngày: expire reservation nếu quá hạn & thông báo người kế tiếp"""
        today = fields.Date.context_today(self)
        reservations = self.search([('status', '=', 'pending'), ('expire_date', '<', today)])
        for r in reservations:
            r.write({'status': 'expired'})
            # Optional: notify next in queue or admin (not implemented here)
