# python imports
import traceback

# globals
requests = {}


def registerBlurStatement(statement, func):
    """
    Register a new statement for the blur language.
        NOTE: The statement will only be passed the raw string sent from the client, you need to handle the parsing.
    :param statement:
    :param func:
    :return:
    """
    global requests

    requests[statement] = func


def parse(request):
    """
    --private--
        Parses all calls sent to the server.
    :param request:
    :return:
    """
    for call in requests:
        try:
            result = requests[call](request)
            if result:
                print "HFX {BLUR:SERVER}: " + str(result)
                return result
        except:
            print "HFX {BLUR:SERVER:TALKS}: Call failed to execute. " + str(call)
            traceback.print_exc()


def commands():
    """
    Get all commands for blur
    :return:
    """
    return requests.keys()
