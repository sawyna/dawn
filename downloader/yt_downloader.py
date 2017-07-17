from youtube_dl import YoutubeDL
from logger import Logger
import urllib2
import re
import json
from dbconnect import DB
from config import download_config

INSERT_DL_QUERY = "insert into downloads_info (proc_id, is_downloading) values ('%(id)s', 1)"
UPDATE_DL_START_QUERY = """
update downloads_info 
set is_downloading=1, percent_complete=NULL, eta=NULL 
where proc_id = '%(id)s')
"""
UPDATE_DL_QUERY = "update downloads_info set percent_complete = %(percent)s, eta = '%(eta)s' where proc_id = '%(id)s'"
SELECT_STAT_QUERY = "select * from downloads_info where proc_id = '%(id)s'"


class YTDownloader(object):

	def __init__(self, dbconfig, id='1'):
		self.id = id
		self.dbconfig = dbconfig

	def download(self, params):
		url = params['url']
		dl = YoutubeDL(self.get_opts())
		m = re.search("^https://www.youtube.com/watch\?(.*)$", url)
		id = m.group(1)
		self.id = id
		db = self.connecttoDB()
		
		success = db.execute(
			INSERT_DL_QUERY % {
				'id': id
			}
		)

		if not success:
			db.execute(
				UPDATE_DL_START_QUERY %  {
					'id': id
				}
			)

		dl.download([url])

	def get_status(self, params):
		id = params['id']
		db = self.connecttoDB()
		print "Succesfully connected"
		db_result = db.get(
				SELECT_STAT_QUERY % {
					'id': id
				}
		)
		ret_val = {}
		print db_result
		if db_result:
			ret_val['percent'] = db_result[4]
			ret_val['eta'] = db_result[5]
		return ret_val
		

	def connecttoDB(self):
		print self.dbconfig
		return DB(self.dbconfig['host'], self.dbconfig['port'], self.dbconfig['user'], self.dbconfig['password'], self.dbconfig['schema'])


	def get_opts(self):

		return {
			'progress_hooks': [self.dl_hook],
			'outtmpl': download_config['download_location'] + '%(title)s.%(ext)s',
			'logger': Logger()
		}

	def dl_hook(self, d):
		db = self.connecttoDB()
		if d['status'] == 'finished':
			Logger().info("Downloading finished")

		elif d['status'] == 'downloading':
			db.execute(
				UPDATE_DL_QUERY % {
					'percent': str(d['_percent_str'])[0:-1],
					'eta': d['eta'],
					'id': self.id
				}
			)
			Logger().info(("filename %s, percent completed %s, ETA %s" %(d['filename'], d['_percent_str'], d['_eta_str'])))



