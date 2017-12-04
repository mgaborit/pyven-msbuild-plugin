from pyven.exceptions.parser_exception import ParserException
from pyven.plugins.plugin_api.parser import Parser

from msbuild_plugin.msbuild import MSBuild

class MSBuildParser(Parser):
    COUNT = 0
    SINGLETON = None
    
    def __init__(self, cwd):
        MSBuildParser.COUNT += 1
        super(MSBuildParser, self).__init__(cwd)
    
    def parse(self, node, project):
        objects = []
        members = self.parse_process(node)
        errors = []
        config_node = node.find('configuration')
        if config_node is None:
            errors.append('Missing MSBuild configuration')
        elif config_node.text is None:
            errors.append('Missing MSBuild configuration')
        else:
            configuration = config_node.text
        archi_node = node.find('architecture')
        if archi_node is None:
            errors.append('Missing MSBuild platform')
        elif archi_node.text is None:
            errors.append('Missing MSBuild platform')
        else:
            architecture = archi_node.text
        dot_net_version = None
        dot_net_node = node.find('dot_net')
        if dot_net_node is not None and dot_net_node.text is not None:
            dot_net_version = dot_net_node.text
        project_nodes = node.xpath('projects/project')
        projects = []
        if len(project_nodes) == 0:
            errors.append('Missing projects informations')
        else:
            for project_node in project_nodes:
                projects.append(project_node.text)
        options = []
        for option_node in node.xpath('options/option'):
            options.append(option_node.text)
        if len(errors) > 0:
            e = ParserException('')
            e.args = tuple(errors)
            raise e
        
        for project in projects:
            objects.append(MSBuild(self.cwd, members[0], configuration, architecture, project, options, dot_net_version))
        return objects
        
def get(cwd):
    if MSBuildParser.COUNT <= 0 or MSBuildParser.SINGLETON is None:
        MSBuildParser.SINGLETON = MSBuildParser(cwd)
    MSBuildParser.SINGLETON.cwd = cwd
    return MSBuildParser.SINGLETON