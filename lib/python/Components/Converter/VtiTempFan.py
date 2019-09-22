from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll
import os

class VtiTempFan(Poll, Converter, object):
    TEMPINFO = 1
    FANINFO = 2
    ALL = 5

    def __init__(self, type):
        Poll.__init__(self)
        Converter.__init__(self, type)
        self.type = type
        self.poll_interval = 5000
        self.poll_enabled = True
        if type == "TempInfo":
            self.type = self.TEMPINFO
        elif type == "FanInfo":
            self.type = self.FANINFO
        elif type == "AllInfo":
            self.type = self.ALL
        else:
            self.type = self.ALL

    @cached
    def getText(self):
        textvalue = ""
        if self.type == self.TEMPINFO:
            textvalue = self.tempfile()
        elif self.type == self.FANINFO:
            textvalue = self.fanfile()
        elif self.type == self.ALL:
            textvalue = self.tempfile() + "  " + self.fanfile()
        else:
            textvalue = self.tempfile() + "  " + self.fanfile()
        return textvalue

    text = property(getText)

    def tempfile(self):
	tempinfo = ""
	if os.path.exists('/proc/stb/sensors/temp0/value'):
		f = open('/proc/stb/sensors/temp0/value', 'r')
		tempinfo = f.read()
		f.close()
	elif os.path.exists('/proc/stb/fp/temp_sensor'):
		f = open('/proc/stb/fp/temp_sensor', 'r')
		tempinfo = f.read()
		f.close()
	elif os.path.exists('/proc/stb/sensors/temp/value'):
		f = open('/proc/stb/sensors/temp/value', 'r')
		tempinfo = f.read()
		f.close()
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		mark = str('\xc2\xb0')
		tempinfo = _("Temp:") + tempinfo.replace('\n', '').replace(' ','') + mark + "C"
	return tempinfo

    def fanfile(self):
        fan = ""
        try:
            f = open("/proc/stb/fp/fan_speed", "rb")
            fan = f.readline().strip()
            f.close()
            faninfo = str(fan)
            return faninfo
        except:
            pass

    def changed(self, what):
        if what[0] == self.CHANGED_POLL:
            Converter.changed(self, what)

