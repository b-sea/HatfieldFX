
# HFX imports
import HFX

# Package imports
import blur_function
import blur_talks

# python imports
import inspect
import traceback


def applicationName(data):
    """
    Return the applications name
    :param data:
    :return:
    """
    if data != 'APP':
        return
    return HFX.currentEnvironment()

blur_talks.registerBlurStatement('APP', applicationName)


def blurFunctionNetwork(data):
    """
    return a string version of the blur function network
    :param data:
    :return:
    """
    if data != 'BLUR_FUNCTIONS':
        return

    # grab all data
    callbacks = blur_function.CALLBACKS
    originalFunctions = blur_function.BLUR_FUNCTION_DATA
    blurredFunctions = blur_function.BLUR_FUNCTIONS

    # prepare data package
    package = {}

    # grab all blurred functions
    for function in blurredFunctions:
        package[str(function)] = {
            'blur': HFX.getBlurId(blurredFunctions[function]),
            'original': HFX.getBlurId(originalFunctions[function]),
            'callbacks': []
        }

        # loop through and append all callbacks
        for callback in callbacks[function]:
            package[str(function)]['callbacks'].append(HFX.getBlurId(callback))

    return str(package)


blur_talks.registerBlurStatement('BLUR_FUNCTIONS', blurFunctionNetwork)


def pythonNetwork(data):
    """
    Return the mapped python function/class framework
    :param data:
    :return:
    """
    if data != 'PYTHON_FRAMEWORK':
        return
    package = {}
    for i in blur_function.PYTHON_FRAMEWORK:
        package[i] = str(blur_function.PYTHON_FRAMEWORK[i].__module__ + '.' +
                         blur_function.PYTHON_FRAMEWORK[i].__name__)
    return str(package)


blur_talks.registerBlurStatement('PYTHON_FRAMEWORK', pythonNetwork)


def classNetwork(data):
    """
    Return the mapped python function/class framework
    :param data:
    :return:
    """
    if data != 'CLASS_FRAMEWORK':
        return
    package = []
    for i in blur_function.PYTHON_CLASSES:
        package.append(i)
    return str(package)


blur_talks.registerBlurStatement('CLASS_FRAMEWORK', classNetwork)


def classMembers(data):
    """
    Request a classes members list
    :param data:
    :return:
    """
    if not data.startswith('CLASS_MEMBERS:'):
        return

    data = data.split(':')[1]
    targetClass = blur_function.PYTHON_CLASSES[data]

    package = {
        'name': targetClass['path'],
        'funcs': targetClass['functions']
    }

    return str(package)


blur_talks.registerBlurStatement('CLASS_MEMBERS:', classMembers)


def shell(data):
    """
    Interactive shell
    :param data:
    :return:
    """
    if data.split(':')[0] != 'SHELL':
        return
    try:
        exec data.split(':')[1]
        try:
            return str(ret)
        except NameError:
            pass
    except Exception, e:
        return e

blur_talks.registerBlurStatement('SHELL:', shell)


def getCode(data):
    """
    Get the raw code for a function
    :param data:
    :return:
    """
    if not data.startswith('CODE'):
        return

    functionID = data.split(':')[1]

    if data.endswith(':CLASS'):
        function = None
        exec "import %s" % functionID.rsplit('.', 2)[0]
        exec "function = eval('%s')" % functionID
        try:
            raw = inspect.getsource(function)
            f = ''

            for i in raw.split('\n'):
                try:
                    new = i.split('    ', 1)[1]
                    f += new + '\n'
                except:
                    f += '\n'
            return f
        except TypeError:
            return ''
    else:
        function = blur_function.PYTHON_FRAMEWORK[functionID]
        return inspect.getsource(function)


blur_talks.registerBlurStatement('CODE:', getCode)


def updateFunction(data):
    """
    Update a function with new code.
    :param data:
    :return:
    """
    if data.split('|')[0] != 'UPDATE':
        return

    # extract data
    functionID = data.split('|')[1]
    newCode = data.split('|')[2]
    functionName = newCode.split(':')[0].split('(')[0].replace('def ', '')

    command = ''

    print 'HFX {BLUR:SERVER}: Updating function.\n\tPlease wait...'

    # execute changes and register in proper name spaces
    try:
        # grab original function
        if functionID in blur_function.PYTHON_FRAMEWORK:
            targetFunction = blur_function.PYTHON_FRAMEWORK[functionID]
            module = targetFunction.__module__
            function = targetFunction.__name__

            blurred = False
            if targetFunction in blur_function.BLUR_FUNCTIONS.values():
                blurred = True

            # execute code replacement
            dirs = []

            command += 'import %s\n' % module
            command += 'dirs = dir(%s)\n' % module
            command += 'sys.path.append(os.path.dirname(inspect.getabsfile(%s)))\n' % functionID.rsplit('.', 2)[0]

            exec 'import %s\n' % module
            exec 'dirs = dir(%s)\n' % module
            exec 'sys.path.append(os.path.dirname(inspect.getabsfile(%s)))\n' % functionID.rsplit('.', 2)[0]

            imports = ''

            print '\tCollecting imports...'

            for i in dirs:
                try:
                    exec "import %s\n" % i
                    imports += "    import %s\n" % i
                except ImportError:
                    continue

            newCode = newCode.replace(newCode.split('\n', 1)[0], newCode.split('\n', 1)[0] + '\n' + imports)

            command += newCode + '\n'
            command += 'newFunc = %s\n' % functionName
            command += '%s.%s = newFunc\n' % (module, function)

            exec command

            blur_function.PYTHON_FRAMEWORK[HFX.getBlurId(newFunc)] = newFunc

            if blurred:
                for blur in blur_function.BLUR_FUNCTIONS:
                    if blur_function.BLUR_FUNCTIONS[blur] is targetFunction:
                        blur_function.BLUR_FUNCTIONS[blur] = newFunc
        else:
            # execute code replacement
            dirs = []

            command += 'import %s\n' % functionID.rsplit('.', 2)[0]
            command += 'sys.path.append(os.path.dirname(inspect.getabsfile(%s)))\n' % functionID.rsplit('.', 2)[0]

            exec 'import %s' % functionID.rsplit('.', 2)[0]
            exec 'dirs = dir(%s)' % functionID.rsplit('.', 2)[0]
            exec 'sys.path.append(os.path.dirname(inspect.getabsfile(%s)))' % functionID.rsplit('.', 2)[0]

            imports = ''

            print '\tCollecting imports...'

            for i in dirs:
                try:
                    exec "import %s" % i
                    imports += "    import %s\n" % i
                except ImportError:
                    continue

            newCode = newCode.replace(newCode.split('\n', 1)[0], newCode.split('\n', 1)[0] + '\n' + imports)

            command += newCode + '\n'
            command += 'newFunc = %s\n' % functionName

            # Find the class name
            className = functionID.rsplit('.', 1)[0]
            classNickName = className.rsplit('.', 1)[1]

            print '\tUpdataing all running instances'

            # loop over all open instances and replace
            for Class in blur_function.BLUR_CLASSES:
                if Class.__name__ == classNickName:
                    for instance in blur_function.BLUR_CLASSES[Class]:
                        instanceCommand = command
                        try:
                            instanceCommand += 'newFunc = partial(newFunc, instance)\n'
                            instanceCommand += 'instance.%s = newFunc\n' % functionID.rsplit('.', 1)[1]
                            if functionID.rsplit('.', 1)[1] == 'blurSandbox':
                                instanceCommand += 'instance.%s(instance)' % functionID.rsplit('.', 1)[1]
                            exec instanceCommand
                            print '\t\tInstance update: ' + str(instance) + '.' + functionID.rsplit('.', 1)[1]
                        except Exception, e:
                            print e
                            traceback.print_exc()
                    break

            command += '%s = newFunc' % functionID
            exec command

            blur_function.PYTHON_FRAMEWORK[HFX.getBlurId(newFunc)] = newFunc

    except Exception:
        traceback.print_exc()

    print 'HFX {BLUR:SERVER}: %s updated.' % functionID


blur_talks.registerBlurStatement('UPDATE|', updateFunction)
