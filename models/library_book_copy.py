from odoo import models, fields

class LibraryBookCopy(models.Model):
    _name = 'library.book.copy'
    _description = 'Physical Book Copy'
    _inherit = ['mail.thread']

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('library.book.copy'))
    book_id = fields.Many2one('library.book', required=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('lost', 'Lost'),
    ], default='available', tracking=True)

    borrower_id = fields.Many2one('library.member', string="Current Borrower")
