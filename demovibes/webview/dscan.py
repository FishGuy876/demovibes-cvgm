from django.conf import settings
import os
import subprocess
import re, sys
import logging

L = logging.getLogger('dscan')
fsenc = sys.getfilesystemencoding()
program = getattr(settings, 'DEMOSAUCE_SCAN', False)

L.debug("Filesystem enc = %s" % fsenc)

def is_configured():
    if program:
        return True
    else:
        return False

class ScanFile(object):
    file = ''
    bitrate = 0
    length = 0
    samplerate = 0
    loopiness = 0
    readable = False
    __replaygain = None
    
    def __init__(self, file):
        #some checks to catch bad configuration/wrong handling
        try:
            if not is_configured():
                L.error("ScanFile got called without being enabled in configuration")
                return
            if not os.path.isfile(program):
                L.error("ScanFile can't find scan tool at %s. check your config" % program)
                return
            if not file: 
                L.error("ScanFile got called with no file which indicates a bug in our code")
                return
            if not os.path.isfile(file):
                L.error("ScanFile can't find %s. this is likely our fault" % str(file)) 
                return
                
            self.file = file.encode(fsenc)
            path = os.path.dirname(program)
            p = subprocess.Popen([program, '--no-replaygain', self.file], stdout = subprocess.PIPE, cwd = path)
            output = p.communicate()[0]
            if p.returncode != 0:
                L.warn("scan doesn't like %s" % self.file)
                return 
            
            bitrate = re.compile(r'bitrate:(\d*\.?\d+)')
            length = re.compile(r'length:(\d*\.?\d+)')
            samplerate = re.compile(r'samplerate:(\d*\.?\d+)')
            loopiness = re.compile(r'loopiness:(\d*\.?\d+)')
            
            self.length = float(length.search(output).group(1))

            samplerate_match = samplerate.search(output)
            if samplerate_match:
                self.samplerate = float(samplerate_match.group(1))

            bitrate_match = bitrate.search(output)
            if bitrate_match:
                self.bitrate = float(bitrate_match.group(1))

            loop_match = loopiness.search(output)
            if loop_match:
                self.loopiness = float(loop_match.group(1))
                
            self.readable = True
        except:
            import traceback
            trace = traceback.format_exc()
            L.error("Error occurred. Printing traceback.\n%s" % trace)
        
    def replaygain(self):
        if not self.readable:
            return 0

        if not self.__replaygain:
            try:
                path = os.path.dirname(program)
                p = subprocess.Popen([program, self.file], stdout = subprocess.PIPE, cwd = path)
                output = p.communicate()[0]
                repgain = re.compile(r'replaygain:(-?\d*\.?\d+)')
                self.__replaygain = float(repgain.search(output).group(1))
            except:
                import traceback
                trace = traceback.format_exc()
                L.error("Error occurred. Printing traceback.\n%s" % trace)
        
        return self.__replaygain
        
