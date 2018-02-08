from threading import Thread
import os

def worker1():
	os.system('python IN/run_main.py')

def worker2():
	os.system('python OUT/run_main.py')

def worker3():
	os.system('odoo/community/./odoo-bin --addons-path=odoo/community/addons/')

Thread(target=worker1).start()
Thread(target=worker2).start()
Thread(target=worker3).start()