import xmlrpclib
from odoo import fields, models ,api   



class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    client_attendance_server_ip = fields.Char(string='Server IP')
    client_attendance_database_name = fields.Char(string='Database Name')
    client_attendance_odoo_username = fields.Char(string='Odoo Username')
    client_attendance_odoo_password = fields.Char(string='Odoo Password')

    break_start_time = fields.Datetime(string="Start Time (UTC)")
    break_finish_time = fields.Datetime(string="Finish Time (UTC)")

    def set_client_attendance_server_ip(self):
        client_attendance_server_ip = self[0].client_attendance_server_ip or ''
        self.env['ir.config_parameter'].set_param('client_attendance_server_ip', client_attendance_server_ip,  groups=['base.group_system'])

    def set_client_attendance_database_name(self):
        client_attendance_database_name = self[0].client_attendance_database_name or ''
        self.env['ir.config_parameter'].set_param('client_attendance_database_name', client_attendance_database_name,  groups=['base.group_system'])

    def set_client_attendance_database_username(self):
        client_attendance_odoo_username = self[0].client_attendance_odoo_username or ''
        self.env['ir.config_parameter'].set_param('client_attendance_odoo_username', client_attendance_odoo_username,  groups=['base.group_system'])

    def set_client_attendance_odoo_password(self):
        client_attendance_odoo_password = self[0].client_attendance_odoo_password or ''
        self.env['ir.config_parameter'].set_param('client_attendance_odoo_password', client_attendance_odoo_password,  groups=['base.group_system'])

    def set_break_start_time(self):
        break_start_time = self[0].break_start_time or ''
        self.env['ir.config_parameter'].set_param('break_start_time', break_start_time,  groups=['base.group_system'])

    def set_break_finish_time(self):
        break_finish_time = self[0].break_finish_time or ''
        self.env['ir.config_parameter'].set_param('break_finish_time', break_finish_time,  groups=['base.group_system'])

    def get_default_client_attendance(self, fields=None):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        client_attendance_server_ip = get_param('client_attendance_server_ip', default='')
        client_attendance_database_name = get_param('client_attendance_database_name', default='')
        client_attendance_odoo_username = get_param('client_attendance_odoo_username', default='')
        client_attendance_odoo_password = get_param('client_attendance_odoo_password', default='')
        break_start_time = get_param('break_start_time', default='')
        break_finish_time = get_param('break_finish_time', default='')
        return {
            'client_attendance_server_ip': client_attendance_server_ip,
            'client_attendance_database_name': client_attendance_database_name,
            'client_attendance_odoo_username': client_attendance_odoo_username,
            'client_attendance_odoo_password': client_attendance_odoo_password,
            'break_start_time':break_start_time,
            'break_finish_time':break_finish_time,   
        }
    
    def sync_emp_data(self):
        server_url = self.client_attendance_server_ip
        db = self.client_attendance_database_name
        uid = self.client_attendance_odoo_username
        password = self.client_attendance_odoo_password

        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format((server_url)))
        uid = common.authenticate(db, uid, password, {})
        models = None
        if uid:
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(server_url))
            server_emp_model = self.env['hr.employee']
            client_emp_all = models.execute_kw(db, uid, password,'hr.employee', 'search_read',[[]],{})                      

            if client_emp_all:
                for lst_1 in client_emp_all:
                    server_emp_found = server_emp_model.search_read([['server_id','=',lst_1['id']]])
                    
                    if server_emp_found:
                        # Update Exisiting Emplyoee
                        for lst_2 in server_emp_found:
                            server_emp_model.browse(lst_2['id']).write({'barcode':lst_1['barcode']})
                    else:
                        # Create New Emplyoee
                        create_val = {'name':lst_1['name_related'],'pin':lst_1['pin'],'barcode':lst_1['barcode'],'server_id':lst_1['id']}
                        server_emp_model.create(create_val)

    def sync_attendance_data(self):        

            server_url = self.client_attendance_server_ip
            db = self.client_attendance_database_name
            uid = self.client_attendance_odoo_username
            password = self.client_attendance_odoo_password

            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format((server_url)))
            uid = common.authenticate(db, uid, password, {})
            server_attendance_model = self.env['hr.attendance']
            models = None

            if uid:

                models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(server_url))
                server_attendance_record =  server_attendance_model.search([])

                for lst in reversed(server_attendance_record):
                    server_rpi_read = server_attendance_model.search_read([['id','=',lst['id']]])
                    client_attendance_found = models.execute_kw(db, uid, password,'hr.attendance', 'read',[lst['server_id']],{})

                    if client_attendance_found:
                        # Updating Record

                        create_val = {'check_in':server_rpi_read[0]['check_in'],'check_out':server_rpi_read[0]['check_out']}
                        models.execute_kw(db, uid, password,'hr.attendance', 'write',[[client_attendance_found[0]['id']],create_val])
                    else:
                        #Feching Emp Id
                        
                        server_emp_model = self.env['hr.employee']
                        server_emp_rec = server_emp_model.search_read([['id','=',server_rpi_read[0]['employee_id'][0]]])
                        
                        # Creating Record

                        create_val = {'employee_id':server_emp_rec[0]['server_id'],'check_in':server_rpi_read[0]['check_in'],'check_out':server_rpi_read[0]['check_out']}
                        result_id = models.execute_kw(db, uid, password,'hr.attendance', 'create',[create_val])
                        server_attendance_model.browse(server_rpi_read[0]['id']).write({'server_id':result_id})



class attendance_cron(models.Model):
    _name = 'attendance.cron'

    def sync_attendance_data(self,context=None):
            print "Cron Job Called...!! RPI"
            server_url = self.client_attendance_server_ip
            db = self.client_attendance_database_name
            uid = self.client_attendance_odoo_username
            password = self.client_attendance_odoo_password

            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format((server_url)))
            uid = common.authenticate(db, uid, password, {})
            server_attendance_model = self.env['hr.attendance']
            models = None
            
            if uid:
                models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(server_url))
                server_attendance_record =  server_attendance_model.search([])

                for lst in reversed(server_attendance_record):
                    server_rpi_read = server_attendance_model.search_read([['id','=',lst['id']]])
                    client_attendance_found = models.execute_kw(db, uid, password,'hr.attendance', 'read',[lst['server_id']],{})

                    if client_attendance_found:
                        # Updating Record

                        create_val = {'check_in':server_rpi_read[0]['check_in'],'check_out':server_rpi_read[0]['check_out']}
                        models.execute_kw(db, uid, password,'hr.attendance', 'write',[[client_attendance_found[0]['id']],create_val])
                    else:

                        #Feching Emp Id
                        
                        server_emp_model = self.env['hr.employee']
                        server_emp_rec = server_emp_model.search_read([['id','=',server_rpi_read[0]['employee_id'][0]]])
                        
                        # Creating Record

                        create_val = {'employee_id':server_emp_rec[0]['server_id'],'check_in':server_rpi_read[0]['check_in'],'check_out':server_rpi_read[0]['check_out']}
                        result_id = models.execute_kw(db, uid, password,'hr.attendance', 'create',[create_val])
                        server_attendance_model.browse(server_rpi_read[0]['id']).write({'server_id':result_id})




