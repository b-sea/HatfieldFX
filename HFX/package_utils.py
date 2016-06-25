
# python imports
import json
import os
import subprocess
import sys
import traceback

__all__ = [
    'environments',
    'environmentDirectory',
    'loadEnvironment',
    'executeHFX',
    'loadPipeline',
    'currentEnvironment',
    'python'
]


def environmentDirectory():
    """
    Get the path to the environment directory where the .env files are stored for HFX.
    :return:
    """
    return os.path.join(os.path.dirname(__file__), 'environments')


def environments():
    """
    Returns a list of all generated environments and the paths to those .env files.
    :return:
    """
    environments = {}

    for i in os.listdir(environmentDirectory()):
        if i.endswith('.env'):
            environments[i] = os.path.join(environmentDirectory(), i)

    return environments


def loadEnvironment(environment):
    """
    Load an application environment.
    :param environment:
    :return:
    """
    envs = environments()
    if environment not in envs:
        print "HFX {SYSTEM.ENVIRONMENTS}: " + environment + " is not a valid environment. Run HFX.modifySettings()\n" \
                                                            "\tto create new application environments for HFX."
        return None

    with open(envs[environment]) as environment_file:
        environmentData = json.load(environment_file)

        return environmentData


def executeHFX(withPython=False):
    """
    Execute HFX. Does exactly the same as subprocess.Popen('python pathToHFX')
    :return:
    """
    env = loadEnvironment(os.environ['HFX_APP'])

    executable = env['HFX_APP_PATH']
    args = env['HFX_APP_ARGS'].split(' ')

    call = []

    if withPython:
        call.append('python')

    call.append(executable)
    call += args

    subprocess.Popen(call)


def python(pathToFile):
    """
    Launch an app or file with python.
    :param pathToFile:
    :return:
    """
    arg = ['python', pathToFile]
    subprocess.Popen(arg)


def loadPipeline(environment):
    """
    Load a pipeline for an application. This constructs the applications sys path and also does auto imports based on
    the settings synced in the HFX.modifySettings() panel.
    :param environment:
    :return:
    """
    env = loadEnvironment(environment)

    # blur import
    import blur

    pipeCount = 1

    for path in env['pipeline']:
        path = str(path)

        # get the state of this path in the pipeline
        state = env['pipeline'][path]

        add = True
        # perform expression replace
        if '<' in path and '>' in path:
            add = False
            for head in path.split('<'):
                var = head.split('>')[0]
                try:
                    pathPart = os.environ[var]
                    path = path.replace('<%s>' % var, pathPart)
                    add = True
                except KeyError:
                    continue

        if not add:
            continue

        print 'HFX {SETTINGS:PIPELINE}: Adding ' + path.replace('\\', '/')

        if state == 'Disabled':
            print '\tPath is flagged as disabled. Skipping append.'
            continue

        elif state == 'Append':
            sys.path.append(path.replace('\\', '/'))

        elif state == 'Auto-Import':
            print '\tPath flagged for auto import. Attempting to execute imports...'
            sys.path.append(path)

            if not os.path.exists(path):
                print '\tPath doesnt exist, skipping.'
                continue

            for i in os.listdir(path):
                try:
                    module = os.path.splitext(i)[0]
                    __import__(module)
                    blur.registerMembers(module)
                except ImportError:
                    print '\t\tFailed to auto import ' + i
                    traceback.print_exc()
                    continue
        else:
            pass

        os.environ['HFX_PIPE%s' % pipeCount] = path
        pipeCount += 1


def currentEnvironment():
    """
    Return what the current HFX_APP environment you're using. If None, you are running in the os environment.
    :return:
    """
    if 'HFX_APP' not in os.environ:
        return None
    else:
        return os.environ['HFX_APP']
