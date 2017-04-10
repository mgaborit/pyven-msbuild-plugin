import os, subprocess, time
import pyven.constants

from pyven.plugins.plugin_api.process import Process

from pyven.results.line_logs_parser import LineLogsParser

from pyven.logging.logger import Logger
from pyven.exceptions.exception import PyvenException

class MSBuild(Process):

    def __init__(self, cwd, name, configuration, architecture, project, options):
        super(MSBuild, self).__init__(cwd, name)
        self.duration = 0
        self.type = 'msbuild'
        self.configuration = configuration
        self.architecture = architecture
        self.project = project
        self.options = options
        self.parser = LineLogsParser(error_patterns=['error', 'Error', 'erreur', 'Erreur'],\
                                    error_exceptions=['Erreur interne'],\
                                    warning_patterns=['warning', 'Warning', 'avertissement', 'Avertissement'],\
                                    warning_exceptions=[])
    
    @Process.error_checks
    def process(self, verbose=False, warning_as_error=False):
        Logger.get().info('Building : ' + self.type + ':' + self.name)
        self.duration, out, err, returncode = self._call_command(self._format_call())
        
        if verbose:
            for line in out.splitlines():
                Logger.get().info('[' + self.type + ']' + line)
            for line in err.splitlines():
                Logger.get().info('[' + self.type + ']' + line)
        
        self.parser.parse(out.splitlines())
        warnings = self.parser.warnings
        for w in warnings:
            self.warnings.append([w[0].replace(w[0].split()[-1], '')])
        
        if returncode != 0:
            self.status = pyven.constants.STATUS[1]
            errors = self.parser.errors
            for e in errors:
                if e[0].split()[-1].startswith('[') and e[0].split()[-1].endswith(']'):
                    self.errors.append([e[0].replace(e[0].split()[-1], '')])
                else:
                    self.errors.append([e[0]])
            Logger.get().error('Build failed : ' + self.type + ':' + self.name)
        elif warning_as_error and len(self.warnings) > 0:
            self.status = pyven.constants.STATUS[1]
            Logger.get().error('Build failed : ' + self.type + ':' + self.name)
        else:
            self.status = pyven.constants.STATUS[0]
        return returncode == 0 and (not warning_as_error or len(self.warnings) == 0)
    
    @Process.error_checks
    def clean(self, verbose=False, warning_as_error=False):
        Logger.get().info('Cleaning : ' + self.type + ':' + self.name)
        if os.path.isfile(os.path.join(self.cwd, self.project)):
            self.duration, out, err, returncode = self._call_command(self._format_call(clean=True))
            
            if verbose:
                for line in out.splitlines():
                    Logger.get().info('[' + self.type + ']' + line)
                for line in err.splitlines():
                    Logger.get().info('[' + self.type + ']' + line)
                    
            if returncode != 0:
                Logger.get().error('Clean failed : ' + self.type + ':' + self.name)
            return returncode == 0
        Logger.get().info('No project to be cleaned : ' + self.project)
        self.status = pyven.constants.STATUS[0]
        return True
        
    def report_summary(self):
        return self.report_title() + ' : ' + os.path.basename(self.project)
    
    def report_title(self):
        return self.name
        
    def report_properties(self):
        properties = []
        properties.append(('Project', os.path.basename(self.project)))
        properties.append(('Configuration', self.configuration))
        properties.append(('Platform', self.architecture))
        properties.append(('Duration', str(self.duration) + ' seconds'))
        return properties
        
    def _call_command(self, command):
        tic = time.time()
        out = ''
        err = ''
        try:
            
            sp = subprocess.Popen(command,\
                                  stdin=subprocess.PIPE,\
                                  stdout=subprocess.PIPE,\
                                  stderr=subprocess.PIPE,\
                                  universal_newlines=True,\
                                  cwd=self.cwd,\
                                  shell=pyven.constants.PLATFORM == pyven.constants.PLATFORMS[1])
            out, err = sp.communicate(input='\n')
            returncode = sp.returncode
        except FileNotFoundError as e:
            returncode = 1
            self.errors.append(['Unknown command'])
        toc = time.time()
        return round(toc - tic, 3), out, err, returncode
        
    def _format_call(self, clean=False):
        call = ['msbuild.exe', self.project]
        call.append('/consoleLoggerParameters:NoSummary;ErrorsOnly;WarningsOnly')
        if self.project.endswith('.sln'):
            call.append('/property:Configuration='+self.configuration)
            call.append('/property:Platform='+self.architecture)
            if clean:
                call.append('/t:clean')
        elif self.project.endswith('.dproj'):
            call.append('/p:config='+self.configuration)
            call.append('/p:platform='+self.architecture)
            if clean:
                call.append('/t:clean')
            else:
                call.append('/t:build')
        else:
            raise PyvenException('Project format not supported : ' + self.project, 'Supported formats : *.sln, *.dproj')
        for option in self.options:
            call.append(option)
            
        Logger.get().info(' '.join(call))
        return call
        