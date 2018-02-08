from odoo import models, fields, api
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class rfid_employee(models.Model):
	_inherit = "hr.employee"

	server_id = fields.Integer()

class rifd_attendance(models.Model):
	_inherit = "hr.attendance"

	wrong_entry = fields.Char()
	server_id = fields.Integer()

	@api.model
	def check_validate(self, args):		
		rfid_code = args['rfid_code']
		scanner_code = args['scanner_code']
		check_in = args['check_in']
		check_out = args['check_out']

			
		emp_model = self.env['hr.employee']
		attendance_model = self.env['hr.attendance']
		emp_found = emp_model.search([('barcode', '=', rfid_code)], limit=1)
		
		if emp_found:
			attendance_found = attendance_model.search([('employee_id', '=', emp_found['id'])],order="id desc", limit=1)
			emp_id = emp_found['id']
			record_id = attendance_found['id']

			if scanner_code == 'in':
				if attendance_found['check_out'] != False or record_id == False:

					attendance_vals = {'check_in':check_in,'employee_id':emp_id}
					attendance_res = attendance_model.create(attendance_vals)
				else:
					attendance_vals = {'check_out':check_in,'wrong_entry':'Check IN'}
					attendance_found.write(attendance_vals)
					attendance_vals = {'check_in':datetime.now() + timedelta(seconds = 1),'employee_id':emp_id}
					attendance_res = attendance_model.create(attendance_vals)			
			else:
				if attendance_found['check_in'] != False and attendance_found['check_out'] == False:
					attendance_vals = {'check_out':check_out}
					attendance_res = attendance_found.write(attendance_vals)
				else:
					attendance_vals = {'check_in':check_out,'wrong_entry':'Check OUT','employee_id':emp_id,'check_out':check_out}
					attendance_res = attendance_model.create(attendance_vals)
			return True
		else:
			return False


	def _compute_worked_hours(self):
		get_param = self.env['ir.config_parameter'].sudo().get_param
		break_start_time = get_param('break_start_time', default='')
		break_finish_time = get_param('break_finish_time', default='')

		
		for attendance in self:
			if attendance.wrong_entry:
				attendance.worked_hours = timedelta(seconds = 0)
				continue

			if attendance.check_out:

				break_start_time_utc = datetime.combine(datetime.now().date(),datetime.strptime(break_start_time,DEFAULT_SERVER_DATETIME_FORMAT).time())
				break_finish_time_utc = datetime.combine(datetime.now().date(),datetime.strptime(break_finish_time,DEFAULT_SERVER_DATETIME_FORMAT).time())
				check_out = datetime.strptime(attendance.check_out,DEFAULT_SERVER_DATETIME_FORMAT)
				check_in = datetime.strptime(attendance.check_in,DEFAULT_SERVER_DATETIME_FORMAT)
				
				if check_out.date() != check_in.date():
					attendance_vals = {'check_out':check_out,'wrong_entry':'Skipped Check OUT'}
					attendance_found = self.env['hr.attendance'].search([('employee_id', '=', attendance.employee_id['id'])],order="id desc", limit=1)
					attendance_res = attendance_found.write(attendance_vals)
					attendance.worked_hours = timedelta(seconds = 0)
					continue
				if ((check_out  <= break_start_time_utc and check_in  < break_start_time_utc)) or ((check_out > break_finish_time_utc and check_in >= break_finish_time_utc)):
					delta = check_out - check_in

				elif check_out >= break_start_time_utc and check_out <= break_finish_time_utc:
					if check_in < break_start_time_utc:
						delta = break_start_time_utc - check_in
					else:
						delta = timedelta(seconds = 0)
				elif check_out > break_finish_time_utc:
					if check_in > break_start_time_utc and check_in < break_finish_time_utc:
						delta = check_out - break_finish_time_utc
					elif check_in > break_finish_time_utc:
						delta = check_out - check_in
					elif check_in < break_start_time_utc:
						delta = (check_out-check_in) - (break_finish_time_utc-break_start_time_utc)
				attendance.worked_hours = delta.total_seconds() / 3600.0


		# 14711172117
		# 1449770213


