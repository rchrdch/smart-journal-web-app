"""
 +-------------------------------------------------------------------+
 |                  H T M L - C A L E N D A R   (v2.16)              |
 |                                                                   |
 | Copyright Gerd Tentler               www.gerd-tentler.de/tools    |
 | Created: May 27, 2003                Last modified: Feb. 12, 2012 |
 +-------------------------------------------------------------------+
 | This program may be used and hosted free of charge by anyone for  |
 | personal purpose as long as this copyright notice remains intact. |
 |                                                                   |
 | Obtain permission before selling the code for this program or     |
 | hosting this software on a commercial website or redistributing   |
 | this software over the Internet or in any other medium. In all    |
 | cases copyright must remain intact.                               |
 +-------------------------------------------------------------------+
=========================================================================================================
"""

import time
import math
import db
import app
from flask import session


cal_ID = 0

class MonthlyCalendar:
	"""creates a monthly calendar"""
	def __init__(self, year = None, month = None, week = None):
#========================================================================================================
# Configuration
#========================================================================================================
		self.tFontFace = 'Poppins, sans-serif' # title: font family (CSS-spec, e.g. "Poppins, sans-serif")
		self.tFontSize = 40                 # title: font size (pixels)
		self.tFontColor = '#333333'         # title: font color
		self.tBGColor = '#ffffff'           # title: background color

		self.hFontFace = 'Poppins, sans-serif' # heading: font family (CSS-spec, e.g. "Poppins, sans-serif")
		self.hFontSize = 25                 # heading: font size (pixels)
		self.hFontColor = '#333333'         # heading: font color
		self.hBGColor = '#ffffff'           # heading: background color

		self.dFontFace = 'Poppins, sans-serif' # days: font family (CSS-spec, e.g. "Poppins, sans-serif")
		self.dFontSize = 20                 # days: font size (pixels)
		self.dFontColor = '#333333'         # days: font color
		self.dBGColor = '#FFFFFF'           # days: background color

		self.wFontFace = 'Poppins, sans-serif' # weeks: font family (CSS-spec, e.g. "Poppins, sans-serif")
		self.wFontSize = 20                 # weeks: font size (pixels)
		self.wFontColor = '#333333'         # weeks: font color
		self.wBGColor = '#ffffff'           # weeks: background color

		self.saFontColor = '#333333'        # Saturdays: font color
		self.saBGColor = '#ffffff'          # Saturdays: background color

		self.suFontColor = '#333333'        # Sundays: font color
		self.suBGColor = '#ffffff'          # Sundays: background color

		self.tdBorderColor = 'blue'      # today: border color

		self.borderColor = '#333333'        # border color
		self.hilightColor = '#FFFF00'       # hilight color (works only in combination with link)

		self.link = ''                      # page to link to when day is clicked
		self.linkTarget = ''				# link target frame or window, e.g. parent.myFrame
		self.offset = 1                     # week start: 0 - 6 (0 = Saturday, 1 = Sunday, 2 = Monday ...)
		self.weekNumbers = 0                # view week numbers: 1 = yes, 0 = no

#--------------------------------------------------------------------------------------------------------
# You should change these variables only if you want to translate them into your language:
#--------------------------------------------------------------------------------------------------------
		# weekdays: must start with Saturday because January 1st of year 1 was a Saturday
		self.weekdays = ('Sa', 'Su', 'Mo', 'Tu', 'We', 'Th', 'Fr')

		# months: must start with January
		self.months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

		# error messages
		self.error = ('Year must be 1 - 3999!', 'Month must be 1 - 12!')
#========================================================================================================

		if year is None and month is None:
			year = time.localtime().tm_year
			month = time.localtime().tm_mon
		elif year is None and month is not None: year = time.localtime().tm_year
		elif month is None: month = 1
		if week is None: week = 0;
		self.year = int(year)
		self.month = int(month)
		self.week = int(week)
		self.specDays = {}
		self.specDays2 = {}
		if self.linkTarget == '': self.linkTarget = 'document'

	__size = 0
	__mDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

	def set_styles(self):
		"""set calendar styles"""
		globals()['cal_ID'] += 1
		html = '<style> .cssTitle' + str(globals()['cal_ID']) + ' { '
		if self.tFontFace: html += 'font-family: ' + self.tFontFace + '; '
		if self.tFontSize: html += 'font-size: ' + str(self.tFontSize) + 'px; '
		if self.tFontColor: html += 'color: ' + self.tFontColor + '; '
		if self.tBGColor: html += 'background-color: ' + self.tBGColor + '; '
		html += '} .cssHeading' + str(globals()['cal_ID']) + ' { '
		if self.hFontFace: html += 'font-family: ' + self.hFontFace + '; '
		if self.hFontSize: html += 'font-size: ' + str(self.hFontSize) + 'px; '
		if self.hFontColor: html += 'color: ' + self.hFontColor + '; '
		if self.hBGColor: html += 'background-color: ' + self.hBGColor + '; '
		html += '} .cssDays' + str(globals()['cal_ID']) + ' { '
		if self.dFontFace: html += 'font-family: ' + self.dFontFace + '; '
		if self.dFontSize: html += 'font-size: ' + str(self.dFontSize) + 'px; '
		if self.dFontColor: html += 'color: ' + self.dFontColor + '; '
		if self.dBGColor: html += 'background-color: ' + self.dBGColor + '; '
		html += '} .cssWeeks' + str(globals()['cal_ID']) + ' { '
		if self.wFontFace: html += 'font-family: ' + self.wFontFace + '; '
		if self.wFontSize: html += 'font-size: ' + str(self.wFontSize) + 'px; '
		if self.wFontColor: html += 'color: ' + self.wFontColor + '; '
		if self.wBGColor: html += 'background-color: ' + self.wBGColor + '; '
		html += '} .cssSaturdays' + str(globals()['cal_ID']) + ' { '
		if self.dFontFace: html += 'font-family: ' + self.dFontFace + '; '
		if self.dFontSize: html += 'font-size: ' + str(self.dFontSize) + 'px; '
		if self.saFontColor: html += 'color: ' + self.saFontColor + '; '
		if self.saBGColor: html += 'background-color: ' + self.saBGColor + '; '
		html += '} .cssSundays' + str(globals()['cal_ID']) + ' { '
		if self.dFontFace: html += 'font-family: ' + self.dFontFace + '; '
		if self.dFontSize: html += 'font-size: ' + str(self.dFontSize) + 'px; '
		if self.suFontColor: html += 'color: ' + self.suFontColor + '; '
		if self.suBGColor: html += 'background-color: ' + self.suBGColor + '; '
		html += '} .cssHilight' + str(globals()['cal_ID']) + ' { '
		if self.dFontFace: html += 'font-family: ' + self.dFontFace + '; '
		if self.dFontSize: html += 'font-size: ' + str(self.dFontSize) + 'px; '
		if self.dFontColor: html += 'color: ' + self.dFontColor + '; '
		if self.hilightColor: html += 'background-color: ' + self.hilightColor + '; '
		html += 'cursor: default;'
		html += '} </style>'
		return html

# ------------------------------------------------------------------------------------------------------------

	def leap_year(self, year):
		"""check if year is a leap year"""
		return not (year % 4) and (year < 1582 or year % 100 or not (year % 400))

# ------------------------------------------------------------------------------------------------------------

	def get_weekday(self, year, days):
		"""return weekday (0 - 6) of nth day in year"""
		a = days
		if year: a += (year - 1) * 365
		for i in range(1, year):
			if self.leap_year(i): a += 1
		if year > 1582 or (year == 1582 and days > 277): a -= 10
		if a: a = (a - self.offset) % 7
		elif self.offset: a += 7 - self.offset
		return a

# ------------------------------------------------------------------------------------------------------------

	def get_week(self, year, days):
		"""return week number of nth day in year"""
		firstWDay = self.get_weekday(year, 0)
		if year == 1582 and days > 277: days -= 10

		return int(math.floor((days + firstWDay) / 7) + (firstWDay <= 3))

# ------------------------------------------------------------------------------------------------------------

	def table_cell(self, content, cls, date = '', style = ''):
		"""return formatted table cell with content"""
		size = int(round(self.__size * 1.5))
		html = '<td align=center width=' + str(size) + ' class="' + cls + '"'

		if content != '&nbsp;' and cls.lower().find('day') != -1:
			link = self.link
			bgColor = ''
			events = []

			if content in self.specDays:
				for v in self.specDays[content]:
					if v[0]: bgColor = v[0]
					if v[1]: events.append(v[1])
					if v[2]: link = v[2]
				html += ' title="' + ' &middot; '.join(events) + '"'
				if bgColor: style += 'background-color:' + bgColor

			if link:
				link += (link.find('?') != -1) and '&date=' + date or '?date=' + date
				html += ' onMouseOver="this.className=\'cssHilight' + str(globals()['cal_ID']) + '\'"'
				html += ' onMouseOut="this.className=\'' + cls + '\'"'
				html += ' onClick="' + self.linkTarget + '.location.href=\'' + link + '\'"'
		if style: html += ' style="' + style + '"'
		html += '>' + content + '</td>'
		return html

# ------------------------------------------------------------------------------------------------------------

	def table_head(self, content):
		"""return formatted table head with content"""
		cols = self.weekNumbers and '8' or '7'
		html = '<tr><td colspan=' + cols + ' class="cssTitle' + str(globals()['cal_ID']) + '" align=center><b>' + \
			content + '</b></td></tr><tr>'
		for i in range(len(self.weekdays)):
			ind = (i + self.offset) % 7
			wDay = self.weekdays[ind]
			html += self.table_cell(wDay, 'cssHeading' + str(globals()['cal_ID']))
		if self.weekNumbers: html += self.table_cell('&nbsp;', 'cssHeading' + str(globals()['cal_ID']))
		html += '</tr>'
		return html
		
# ------------------------------------------------------------------------------------------------------------

	def viewEvent(self, start, end, color, title, link = ''):
		"""add event to calendar"""
		if start > end: return
		if start < 1 or start > 31: return
		if end < 1 or end > 31: return
		while start <= end:
			if not self.specDays.has_key(str(start)): self.specDays[str(start)] = []
			self.specDays[str(start)].append((color, title, link))
			start += 1

# ------------------------------------------------------------------------------------------------------------

	def viewEventEach(self, weekday, color, title, link = ''):
		"""add event to calendar"""
		if weekday < 0 or weekday > 6: return
		if not self.specDays2.has_key(str(weekday)): self.specDays2[str(weekday)] = []
		self.specDays2[str(weekday)].append((color, title, link))

# ------------------------------------------------------------------------------------------------------------

	def create(self):
		"""create monthly calendar"""
		self.__size = (self.hFontSize > self.dFontSize) and self.hFontSize or self.dFontSize
		if self.wFontSize > self.__size: self.__size = self.wFontSize

		date = time.strftime('%Y-%m-%d', time.localtime())
		(curYear, curMonth, curDay) = [int(v) for v in date.split('-')]

		if self.year < 1 or self.year > 3999: html = '<b>' + self.error[0] + '</b>'
		elif self.month < 1 or self.month > 12: html = '<b>' + self.error[1] + '</b>'
		else:
			self.__mDays[1] = self.leap_year(self.year) and 29 or 28
			days = 0
			for i in range(self.month - 1): days += self.__mDays[i]

			start = self.get_weekday(self.year, days)
			stop = self.__mDays[self.month-1]

			html = self.set_styles()
			html += '<table border=2 cellspacing=0 cellpadding=0><tr>'
			html += '<td' + (self.borderColor and ' bgcolor=' + self.borderColor) + '>'
			html += '<table border=1 cellspacing=1 cellpadding=5>'
			title = self.months[self.month-1] + ' ' + str(self.year)
			html += self.table_head(title)
			daycount = 1

			if self.year == curYear and self.month == curMonth: inThisMonth = 1
			else: inThisMonth = 0

			if self.weekNumbers or self.week: weekNr = self.get_week(self.year, days)

			for i in range(self.__mDays[self.month-1] + 1):
				for j, v in self.specDays2.items():
					if self.get_weekday(self.year, days + i) == int(j) - self.offset + 1:
						if not self.specDays.has_key(str(i)): self.specDays[str(i)] = []
						for v in self.specDays2[j]:
							self.specDays[str(i)].append(v)

			while daycount <= stop:
				if self.week and self.week != weekNr:
					daycount += 7 - (daycount == 1 and start or 0)
					weekNr += 1
					continue
				html += '<tr>'
				wdays = 0

				for i in range(len(self.weekdays)):
					ind = (i + self.offset) % 7
					if ind == 0: cls = 'cssSaturdays'
					elif ind == 1: cls = 'cssSundays'
					else: cls = 'cssDays'

					style = ''
					date = "%4d-%02d-%02d" % (self.year, self.month, daycount)

					if (daycount == 1 and i < start) or daycount > stop: content = '&nbsp;'
					else:
						content = str(daycount)
						# Custom code
						
						date_for_mongodb = "%02d/%02d/%4d" % (self.month, daycount, self.year)
						bad = db.db.collection.find_one({"name": session.get('user'), "date": date_for_mongodb, "sentiment": {"$lt": 0}})
						good = db.db.collection.find_one({"name": session.get('user'), "date": date_for_mongodb, "sentiment": {"$gt": 0}})
						if (daycount <= curDay):
							if (bad != None):
								if (str(date_for_mongodb) == bad['date']):
									style = 'padding: 0px; background-color: red' + ';'
							elif (good != None):
								if (str(date_for_mongodb) == good['date']):
									style = 'padding: 0px; background-color: green' + ';'

						if inThisMonth and daycount == curDay:
							style = 'padding: 0px; border: 3px solid ' + self.tdBorderColor + ';'
						elif self.year == 1582 and self.month == 10 and daycount == 4: daycount = 14
						daycount += 1
						wdays += 1

					html += self.table_cell(content, cls + str(globals()['cal_ID']), date, style)

				if self.weekNumbers:
					if not weekNr:
						if self.year == 1: content = '&nbsp;'
						elif self.year == 1583: content = '51'
						else: content = str(self.get_week(self.year - 1, 365))
					elif self.month == 12 and weekNr >= 52 and wdays < 4: content = '1'
					else: content = str(weekNr)

					html += self.table_cell(content, 'cssWeeks' + str(globals()['cal_ID']))
					weekNr += 1

				html += '</tr>'
			html += '</table></td></tr></table>'
		return html


