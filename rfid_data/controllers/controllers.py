# -*- coding: utf-8 -*-
from odoo import http

# class RfidData(http.Controller):
#     @http.route('/rfid_data/rfid_data/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rfid_data/rfid_data/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rfid_data.listing', {
#             'root': '/rfid_data/rfid_data',
#             'objects': http.request.env['rfid_data.rfid_data'].search([]),
#         })

#     @http.route('/rfid_data/rfid_data/objects/<model("rfid_data.rfid_data"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rfid_data.object', {
#             'object': obj
#         })