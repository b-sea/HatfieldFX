"""
HFX Blur
"""

# HFX import
import HFX

# python imports
import sys
import inspect


__all__ = [
    'findBlurFunction',
    'blur',
    'blurLink',
    'registerMembers',
    'PYTHON_FRAMEWORK',
    'PYTHON_CLASSES',
    'addCallback',
    'getBlurId',
    'blurClass',
    'registerBlurPlugin',
    'blurPlugins'
]

BLUR_FUNCTIONS = {}
BLUR_FUNCTION_DATA = {}

CALLBACKS = {}

PYTHON_CLASSES = {}
PYTHON_FRAMEWORK = {}

BLUR_CLASSES = {}
BLUR_CLASS_INSTANCES = {}

BLUR_PLUGINS = []
BLUR_INIT_PLUGINS = []


def blurSandbox(self):
    """
    Empty blur function for classes. This function is called automatically when updated from blur.
    :param self:
    :return:
    """
    pass


def blurClass(cls):
    """
    Define a class to be blur capable.
    :param cls:
    :return:
    """
    global BLUR_CLASSES

    # create the class instance if not present
    if cls.__class__ not in BLUR_CLASSES:
        BLUR_CLASSES[cls.__class__] = []

    BLUR_CLASSES[cls.__class__].append(cls)

    # add the sandbox to the instance
    cls.blurSandbox = blurSandbox

    return cls


def _idGenerator(function):
    function = str(function).split(' ')
    function.reverse()
    return function[0].replace('>', '')


def registerMembers(module):
    global PYTHON_FRAMEWORK
    global PYTHON_CLASSES

    for name, obj in inspect.getmembers(sys.modules[module]):
        # Register functions
        if inspect.isfunction(obj):
            PYTHON_FRAMEWORK[_idGenerator(obj)] = obj

        # Register classes
        if inspect.isclass(obj):
            # exclude PySide
            if obj.__name__.startswith('Q'):
                continue

            path = obj.__module__ + '.' + obj.__name__
            PYTHON_CLASSES[obj.__name__] = {
                'functions': [],
                'class': obj,
                'path': path
            }

            # add functions but exclude all base members
            baseFunctions = dir(obj.__base__)
            for func in dir(obj):
                if func in baseFunctions:
                    continue
                PYTHON_CLASSES[obj.__name__]['functions'].append(func)


def getBlurId(function):
    """
    Extract the id number from the function.
    :param function:
    :return:
    """
    function = str(function).split(' ')
    function.reverse()
    return function[0].replace('>', '')


def getFunction(id_):
    return PYTHON_FRAMEWORK[id_]


def findBlurFunction(blurredFunction):
    """
    Find a blurred function in environments.
    :param blurredFunction:
    :return:
    """
    environments = []
    for i in BLUR_FUNCTIONS:
        if blurredFunction in BLUR_FUNCTIONS[i]:
            environments.append(i)

    return BLUR_FUNCTION_DATA, environments


def blur(function):
    """
    Make a function or class blur able and linked to an HFX environment to maintain uniform namespaces between software.
    :param function:
    :param environment:
    :return:
    """
    if HFX.currentEnvironment() is None:
        return

    if inspect.isclass(function):
        global BLUR_CLASSES

        # create the class instance if not present
        if function.__class__ not in BLUR_CLASSES:
            BLUR_CLASSES[function.__class__] = []

        function.blurSandbox = blurSandbox

        registerMembers(function.__module__)
        return

    global BLUR_FUNCTIONS
    global BLUR_FUNCTION_DATA
    global CALLBACKS

    def blurredFunction(*args, **kwargs):
        if HFX.currentEnvironment() is None:
            return function(*args, **kwargs)

        linkedFunction = BLUR_FUNCTIONS[blurredFunction]

        for call in CALLBACKS[blurredFunction]:
            call()

        if linkedFunction is None:
            return function(*args, **kwargs)

        else:
            return linkedFunction(*args, **kwargs)

    CALLBACKS[blurredFunction] = []
    BLUR_FUNCTIONS[blurredFunction] = None
    BLUR_FUNCTION_DATA[blurredFunction] = function

    registerMembers(function.__module__)

    return blurredFunction


def blurLink(blurredFunction, environmentFunction):
    """
    Link the blurredFunction to the environment function:
    :param blurredFunction:
    :param environmentFunction:
    :param envirnonment:
    :return:
    """
    global BLUR_FUNCTIONS
    global BLUR_FUNCTION_DATA

    BLUR_FUNCTIONS[blurredFunction] = environmentFunction

    registerMembers(environmentFunction.__module__)


def addCallback(blurredFunction, callback):
    global CALLBACKS
    global BLUR_FUNCTION_DATA

    CALLBACKS[blurredFunction].append(callback)

    registerMembers(callback.__module__)


def registerBlurPlugin(plugin, init=None):
    """
    Register a plug for blur.
    :param plugin:
    :return:
    """
    global BLUR_PLUGINS
    global BLUR_INIT_PLUGINS

    if init and plugin not in BLUR_INIT_PLUGINS:
        BLUR_INIT_PLUGINS.append(plugin)
        blur(plugin)
        return

    if plugin not in BLUR_PLUGINS and not init:
        BLUR_PLUGINS.append(plugin)
        blur(plugin)


def blurPlugins(classes=None, functions=None, inits=None):
    """
    Return all registered plugins.
    """
    if inits:
        return BLUR_INIT_PLUGINS
    package = []
    for i in BLUR_PLUGINS:
        if classes:
            if inspect.isclass(i):
                package.append(i)
        elif functions:
            if inspect.isfunction(i):
                package.append(i)
        else:
            return BLUR_PLUGINS

    return package
