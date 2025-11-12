{
    'name': 'Borrowed Book Management',
    'version': '1.0.0',
    'category': 'Library',
    'summary': 'Library book lending and reservation system',
    'license': 'LGPL-3',
    'description': """Library Borrow & Reservation Management System.
                        Includes:
                        - Book catalog
                        - Physical copies tracking
                        - Borrow & return
                        - Reservation queue
                        - Fine management""",
    'depends': ['base', 'mail'],
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence.xml',
        'data/cron_jobs.xml',
        'data/mail_template.xml',

        'views/book_view.xml',
        'views/book_copy_view.xml',
        'views/member_view.xml',
        'views/loan_view.xml',
        'views/reservation_view.xml',
        'views/fine_view.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}