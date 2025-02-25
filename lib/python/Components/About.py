from boxbranding import getImageVersion, getMachineBuild, getBoxType
from sys import modules
import socket
import fcntl
import struct

def getFFmpegVersionString():
	try:
		from glob import glob
		ffmpeg = [x.split("Version: ") for x in open(glob("/var/lib/opkg/info/ffmpeg.control")[0], "r") if x.startswith("Version:")][0]
		version = ffmpeg[1].split("-")[0].replace("\n","")
		return "%s" % version.split("+")[0]
	except:
		return ""

def getVersionString():
	return getImageVersion()


def getFlashDateString():
	try:
		f = open("/etc/install", "r")
		flashdate = f.read()
		f.close()
		return flashdate
	except:
		return _("unknown")


def getEnigmaVersionString():
	return getImageVersion()


def getGStreamerVersionString():
	try:
		from glob import glob
		gst = [x.split("Version: ") for x in open(glob("/var/lib/opkg/info/gstreamer[0-9].[0-9].control")[0], "r") if x.startswith("Version:")][0]
		return "%s" % gst[1].split("+")[0].replace("\n", "")
	except:
		return _("unknown")


def getKernelVersionString():
	try:
		f = open("/proc/version", "r")
		kernelversion = f.read().split(' ', 4)[2].split('-', 2)[0]
		f.close()
		return kernelversion
	except:
		return _("unknown")


def getIsBroadcom():
	try:
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n', '')
				if splitted[0].startswith("Hardware"):
					system = splitted[1].split(' ')[0]
				elif splitted[0].startswith("system type"):
					if splitted[1].split(' ')[0].startswith('BCM'):
						system = 'Broadcom'
		file.close()
		if 'Broadcom' in system:
			return True
		else:
			return False
	except:
		return False


def getChipSetString():
	if getMachineBuild() in ('dm800se', 'dm800sev2', 'dm500hd', 'dm500hdv2'):
		return "7405"
	elif getMachineBuild() in ('dm7080', 'dm820'):
		return "7435"
	elif getMachineBuild() in ('dm8000',):
		return "7400"
	elif getMachineBuild() in ('dm520', 'dm525'):
		return "73625"
	elif getMachineBuild() in ('dm900', 'dm920', 'et13000', 'sf5008'):
		return "7252S"
	elif getMachineBuild() in ('hd51', 'vs1500', 'h7'):
		return "7251S"
	elif getMachineBuild() in ('alien5',):
		return "S905D"
	else:
		try:
			f = open('/proc/stb/info/chipset', 'r')
			chipset = f.read()
			f.close()
			return str(chipset.lower().replace('\n', '').replace('bcm', '').replace('brcm', '').replace('sti', ''))
		except IOError:
			return _("unavailable")


def getCPUSpeedMHzInt():
	cpu_speed = 0
	try:
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		file.close()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n', '')
				if splitted[0].startswith("cpu MHz"):
					cpu_speed = float(splitted[1].split(' ')[0])
					break
	except IOError:
		print "[About] getCPUSpeedMHzInt, /proc/cpuinfo not available"

	if cpu_speed == 0:
		if getMachineBuild() in ('h7', 'hd51', 'hd52', 'sf4008'):
			try:
				import binascii
				f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
				clockfrequency = f.read()
				f.close()
				cpu_speed = round(int(binascii.hexlify(clockfrequency), 16) / 1000000, 1)
			except IOError:
				cpu_speed = 1700
		else:
			try: # Solo4K
				file = open('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq', 'r')
				cpu_speed = float(file.read()) / 1000
				file.close()
			except IOError:
				print "[About] getCPUSpeedMHzInt, /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq not available"
	return int(cpu_speed)


def getCPUSpeedString():
	cpu_speed = float(getCPUSpeedMHzInt())
	if cpu_speed > 0:
		if cpu_speed >= 1000:
			cpu_speed = "%s GHz" % str(round(cpu_speed / 1000, 1))
		else:
			cpu_speed = "%s MHz" % str(int(cpu_speed))
		return cpu_speed
	return _("unavailable")


def getCPUArch():
	if getBoxType() in ('osmio4k',):
		return "ARM V7"
	if "ARM" in getCPUString():
		return getCPUString()
	return _("Mipsel")


def getCPUString():
	system = _("unavailable")
	try:
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n', '')
				if splitted[0].startswith("system type"):
					system = splitted[1].split(' ')[0]
				elif splitted[0].startswith("model name"):
					system = splitted[1].split(' ')[0]
				elif splitted[0].startswith("Processor"):
					system = splitted[1].split(' ')[0]
		file.close()
		return system
	except IOError:
		return _("unavailable")


def getCpuCoresInt():
	cores = 0
	try:
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		file.close()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n', '')
				if splitted[0].startswith("processor"):
					cores = int(splitted[1]) + 1
	except IOError:
		pass
	return cores


def getCpuCoresString():
	cores = getCpuCoresInt()
	return {
			0: _("unavailable"),
			1: _("Single core"),
			2: _("Dual core"),
			4: _("Quad core"),
			8: _("Octo core")
			}.get(cores, _("%d cores") % cores)


def _ifinfo(sock, addr, ifname):
	iface = struct.pack('256s', ifname[:15])
	info = fcntl.ioctl(sock.fileno(), addr, iface)
	if addr == 0x8927:
		return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].upper()
	else:
		return socket.inet_ntoa(info[20:24])


def getIfConfig(ifname):
	ifreq = {'ifname': ifname}
	infos = {}
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# offsets defined in /usr/include/linux/sockios.h on linux 2.6
	infos['addr'] = 0x8915 # SIOCGIFADDR
	infos['brdaddr'] = 0x8919 # SIOCGIFBRDADDR
	infos['hwaddr'] = 0x8927 # SIOCSIFHWADDR
	infos['netmask'] = 0x891b # SIOCGIFNETMASK
	try:
		for k, v in infos.items():
			ifreq[k] = _ifinfo(sock, v, ifname)
	except:
		pass
	sock.close()
	return ifreq


def getIfTransferredData(ifname):
	f = open('/proc/net/dev', 'r')
	for line in f:
		if ifname in line:
			data = line.split('%s:' % ifname)[1].split()
			rx_bytes, tx_bytes = (data[0], data[8])
			f.close()
			return rx_bytes, tx_bytes


def getPythonVersionString():
	import sys
	return "%s.%s.%s" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)


def getEnigmaUptime():
	from time import time
	import os
	location = "/etc/enigma2/profile"
	try:
		seconds = int(time() - os.path.getmtime(location))
		return formatUptime(seconds)
	except:
		return ''


def getBoxUptime():
	try:
		f = open("/proc/uptime", "rb")
		seconds = int(f.readline().split('.')[0])
		f.close()
		return formatUptime(seconds)
	except:
		return ''


def formatUptime(seconds):
	out = ''
	if seconds > 86400:
		days = int(seconds / 86400)
		out += (_("1 day") if days == 1 else _("%d days") % days) + ", "
	if seconds > 3600:
		hours = int((seconds % 86400) / 3600)
		out += (_("1 hour") if hours == 1 else _("%d hours") % hours) + ", "
	if seconds > 60:
		minutes = int((seconds % 3600) / 60)
		out += (_("1 minute") if minutes == 1 else _("%d minutes") % minutes) + " "
	else:
		out += (_("1 second") if seconds == 1 else _("%d seconds") % seconds) + " "
	return out


# For modules that do "from About import about"
about = modules[__name__]
