from odoo import models, fields

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Book Title", required=True, tracking=True)
    author = fields.Char("Author")
    publisher = fields.Char("Publisher")
    publish_year = fields.Integer("Published Year")
    isbn = fields.Char("ISBN", required=True)
    category = fields.Char("Category")
    price = fields.Float("Price")

    total_copies = fields.Integer("Total Copies", compute="_compute_counts")
    available_copies = fields.Integer("Available Copies", compute="_compute_counts")

    copy_ids = fields.One2many('library.book.copy', 'book_id', string="Copies")

    def _compute_counts(self):
        for book in self:
            book.total_copies = len(book.copy_ids)
            book.available_copies = len(book.copy_ids.filtered(lambda x: x.status == 'available'))
