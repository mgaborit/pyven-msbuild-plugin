import zipfile, os
import msbuild_plugin.constants

def zip_pvn():
    if not os.path.isdir(os.path.join(os.environ.get('PVN_HOME'), 'plugins')):
        os.makedirs(os.path.join(os.environ.get('PVN_HOME'), 'plugins'))
    zf = zipfile.ZipFile(os.path.join(os.environ.get('PVN_HOME'), 'plugins', 'msbuild-plugin_' + msbuild_plugin.constants.VERSION + '.zip'), mode='w')
    
    zf.write('__init__.py')
    
    zf.write('msbuild_plugin/__init__.py')
    zf.write('msbuild_plugin/constants.py')
    zf.write('msbuild_plugin/parser.py')
    zf.write('msbuild_plugin/msbuild.py')
    
if __name__ == '__main__':
    zip_pvn()
