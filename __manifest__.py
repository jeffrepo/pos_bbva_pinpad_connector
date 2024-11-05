# -*- coding: utf-8 -*-
{
    'name': "pos_bbva_pinpad_connector",

    'summary': """
        Integración del Pin Pad BBVA con el Punto de Venta (POS) de Odoo.
        """,

    'description': """
        Este módulo permite la integración del Pin Pad BBVA con el Punto de Venta (POS) de Odoo, facilitando el procesamiento de pagos con tarjeta directamente desde el sistema de punto de venta.

            Características principales:
            - Conexión directa con el Pin Pad BBVA.
            - Procesamiento seguro de pagos con tarjeta en el POS.
            - Registro automático de transacciones en Odoo.
            - Actualización en tiempo real del estado de los pagos.

            Ideal para tiendas físicas que utilizan el sistema de punto de venta de Odoo y desean una integración directa con dispositivos de pago BBVA.
    """,

    'author': "Geordie Castaneda",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_payment_method_views.xml',        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'assets': {
        'point_of_sale.assets': [
            'pos_bbva_pinpad_connector/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            # 'pos_bbva_pinpad_connector/static/src/js/models.js',
            'pos_bbva_pinpad_connector/static/src/js/payment_total_pos.js',
            'pos_bbva_pinpad_connector/static/src/js/total_pos_connector.js',
        ]
    },
}
