
# abstract class imports
from abstract import *
from util import palette, styleSheet

# HFX imports
import HFX

# PySide imports
from PySide import QtGui, QtCore


__all__ = [
    'IntValue',
    'FloatValue',
    'Slider',
    'OptionBox',
    'ShortTextInput',
    'LongTextInput',
    'Toggle',
    'EnvironmentInput',
    'MultiToggle',
    'Button',
    'Label',
    'ProgressBar'
]


class Label(Control):
    """
    Standard label type. Mimics PySide's QLabel
    """
    def __init__(self, label):
        """
        :param label:
        :return:
        """
        super(Label, self).__init__(label, label)

    def setText(self, text):
        self._subControlAction.setText(text)


class Button(Control):
    def __init__(self, name, *args, **kwargs):
        super(Button, self).__init__(name, *args, **kwargs)

        self._input = QtGui.QPushButton(name)
        self.addControl(self._input)

    def connect(self, *args, **kwargs):
        self._input.clicked.connect(*args, **kwargs)


class IntValue(Control):
    """
    Base class for Values
    """
    def __init__(self, name, default=0, **kwargs):
        """
        :param name:
        :param default:
        :param kwargs:
        :return:
        """
        super(IntValue, self).__init__(name, name, **kwargs)

        self._input = QtGui.QSpinBox()
        self._input.setValue(default)
        self._input.setRange(-9999999, 9999999)

        self.addControl(self._input)

    def connect(self, func):
        """
        Connect a function to this Controls event callback system.
            The event is triggered when EDITING FINISHED.
        :param func:
        :return:
        """
        self._input.valueChanged.connect(func)

    def setValue(self, value):
        """
        Set the value of this control
        :param value:
        :return:
        """
        self._input.setValue(value)

    def value(self):
        """
        Get the value of this control
        :return:
        """
        return self._input.value()


class FloatValue(Control):
    """
    Base class for floating point values
    """
    def __init__(self, name, default=0, **kwargs):
        """
        :param name:
        :param default:
        :param kwargs:
        :return:
        """
        super(FloatValue, self).__init__(name, name, **kwargs)

        self._input = QtGui.QDoubleSpinBox()
        self._input.setValue(default)
        self._input.setRange(-99999, 99999)

        self.addControl(self._input)

    def connect(self, func):
        """
        Connect a function to this Controls event callback system.
            The event is triggered when EDITING FINISHED.
        :param func:
        :return:
        """
        self._input.editingFinished.connect(func)

    def setValue(self, value):
        """
        Set the value of this control
        :param value:
        :return:
        """
        self._input.setValue(value)

    def value(self):
        """
        Get the value of this control
        :return:
        """
        return self._input.value()


class Slider(Control):
    """
    Base Sliders
    """
    def __init__(self, name, minVal, maxVal, default=0, vertical=False, **kwargs):
        """
        :param name:
        :param minVal:
        :param maxVal:
        :return:
        """
        super(Slider, self).__init__(name, name, **kwargs)

        self._valueEcho = QtGui.QLabel()
        self._valueEcho.setMinimumWidth(50)
        self._input = QtGui.QSlider()
        self._detailedInput = FloatValue('Exact')

        if not vertical:
            self._input.setOrientation(QtCore.Qt.Horizontal)

        self._input.setRange(minVal*100.0, maxVal*100.0)

        self.addSubControl(self._detailedInput)
        self.addControl(self._input)
        self.addControl(self._valueEcho)
        self.setValue(default)

        self._input.valueChanged.connect(self._sliderCallback)
        self._detailedInput.connect(self._detailEcho)

    def _sliderCallback(self):
        """
        --private--
        :return:
        """
        self._valueEcho.setText(str(self.value()))
        self._detailedInput.setValue(self.value())

    def _detailEcho(self):
        """
        --private--
        :return:
        """
        self.setValue(self._detailedInput.value())

    def connect(self, func):
        """
        Connect a function to this Controls event callback system.
            The event is triggered when VALUE CHANGED.
        :param func:
        :return:
        """
        self._input.valueChanged.connect(func)

    def setValue(self, value):
        """
        Set the value of this control
        :param value:
        :return:
        """
        self._input.setValue(value*100.0)

    def value(self):
        """
        Return the value of this control
        :return:
        """
        return self._input.value()/100.0


class Toggle(Control):
    """
    Base class for Toggles
    """
    def __init__(self, *args, **kwargs):
        super(Toggle, self).__init__(*args, **kwargs)

        self.input = QtGui.QCheckBox(args[0])
        self.addControl(self.input)

    def connect(self, func):
        """
        Connect a function to this Controls event callback system.
            The event is triggered when EDITING FINISHED.
        :param func:
        :return:
        """
        self.input.clicked.connect(func)

    def setValue(self, value):
        """
        Set the value of this control
        :param value:
        :return:
        """
        if value:
            self.input.setChecked(True)
        else:
            self.input.setChecked(False)

    def value(self):
        """
        Get the value of this control
        :return:
        """
        return self.input.isChecked()


class MultiToggle(Control):
    def __init__(self, label, options, default=0, **kwargs):
        super(MultiToggle, self).__init__(label=label, name=label.lower(), **kwargs)

        self._toggles = []

        for option in options:
            button = QtGui.QRadioButton(option)
            if options.index(option) == default:
                button.setChecked(True)
            self.addControl(button)
            self._toggles.append(button)

    def connect(self, f):
        for button in self._toggles:
            button.clicked.connect(f)

    def setValue(self, value):
        """
        :param value:
        :return:
        """
        for i in self._toggles:
            if str(i.text()) == value:
                i.setChecked(True)
                return

    def value(self):
        """
        :return:
        """
        for i in self._toggles:
            if i.isChecked():
                return i.text()


class OptionBox(Control):
    """
    Base class for simple options
    """
    def __init__(self, name, options, allowNone=False, width=None, searchable=False, **kwargs):
        """
        :param name:
        :param options:
        :param kwargs:
        :return:
        """
        super(OptionBox, self).__init__(name, name, width=width, **kwargs)

        self.allowNone = allowNone
        self.searchable = searchable

        if allowNone:
            options = [''] + options

        self.options = options
        self._input = QtGui.QComboBox()
        self._input.addItems(options)
        self._input.setStyleSheet(styleSheet)
        self._input.setPalette(palette)
        if width:
            self._input.setMinimumWidth(width)
        if searchable:
            lineEdit = QtGui.QLineEdit(self)
            lineEdit.setCompleter(QtGui.QCompleter(options))
            lineEdit.setPalette(palette)
            self._input.setLineEdit(lineEdit)

        self.addControl(self._input)

    def setItems(self, options):
        if self.allowNone:
            options = [''] + options

        self.options = options
        self._input.clear()
        if self.searchable:
            lineEdit = QtGui.QLineEdit(self)
            lineEdit.setCompleter(QtGui.QCompleter(options))
            lineEdit.setPalette(palette)
            self._input.setLineEdit(lineEdit)
        self._input.addItems(options)

    def connect(self, func, activatedInstead=False):
        """
        Connect a function to this Controls event callback system.
            The event is triggered when INDEX CHANGED.
        :param func:
        :return:
        """
        if not activatedInstead:
            self._input.currentIndexChanged.connect(func)
        else:
            self._input.activated.connect(func)

    def setValue(self, option):
        self._input.setCurrentIndex(self.options.index(option))

    def value(self):
        """
        Get the value of this control
        :return:
        """
        return self.options[self._input.currentIndex()]


class ShortTextInput(Control):
    """
    Base class from single line text input
    """
    def __init__(self, name, **kwargs):
        """
        :param name:
        :return:
        """
        super(ShortTextInput, self).__init__(name, name, **kwargs)

        self.setMaximumWidth(300)
        self._input = QtGui.QLineEdit()
        self.addControl(self._input)

    def setCompleter(self, words):
        r = QtGui.QCompleter(words)
        r.popup().setStyleSheet(styleSheet)
        r.popup().setPalette(palette)
        self._input.setCompleter(r)

    def connect(self, f, binding=None):
        if binding == 'textChanged':
            self._input.textChanged.connect(f)
        else:
            self._input.returnPressed.connect(f)

    def setValue(self, value):
        self._input.setText(value)

    def value(self):
        return str(self._input.text())


class LongTextInput(Widget):
    """
    Base class from single line text input
    """
    def __init__(self, name, syntaxHighlighter=False, readOnly=False, **kwargs):
        """
        :param name:
        :return:
        """
        super(LongTextInput, self).__init__(name, name, **kwargs)

        self._input = QtGui.QTextEdit()
        self._input.setReadOnly(readOnly)

        char_format = QtGui.QTextCharFormat()
        char_format.setFont(self._input.font())

        if syntaxHighlighter:
            PythonHighlighter(self._input.document())
            self._input.setFontPointSize(18)

        self.addControl(self._input)

    def setValue(self, text):
        """
        Set the value of this control.
        :param text:
        :return:
        """
        self._input.setText(text)

    def value(self):
        """
        Get the value of this control.
        :return:
        """
        return str(self._input.toPlainText())


class EnvironmentInput(Control):
    def __init__(self):
        super(EnvironmentInput, self).__init__(name='envs', label='Environments', inLineLabel=True)

        self.inputs = {}
        self._value = []
        self._connections = []

        self.refresh()

    def refresh(self):
        initialValues = self._value
        self.inputs = {}

        self.clearSubControls()

        appData = HFX.SETTINGS.value('apps')

        if appData is not None:
            for app in sorted(appData):
                self.inputs[app] = QtGui.QCheckBox(app)
                self.addSubControl(self.inputs[app])
                if app in initialValues:
                    self.inputs[app].setChecked(True)
                self.inputs[app].clicked.connect(self.sync)
                for launcher in sorted(appData[app]['launchers']):
                    variant = launcher[0]
                    key = app + '/' + variant
                    self.inputs[key] = QtGui.QCheckBox('    ' + variant)
                    if key in initialValues:
                        self.inputs[key].setChecked(True)
                    self.addSubControl(self.inputs[key])
                    self.inputs[key].clicked.connect(self.sync)

    def connect(self, f):
        self._connections.append(f)

    def sync(self):
        self._value = []
        for box in sorted(self.inputs):
            if self.inputs[box].checkState() is QtCore.Qt.CheckState.Checked:
                self._value.append(box)

        for call in self._connections:
            try:
                call(self.value())
            except:
                call()

    def setValue(self, value):
        """
        Set the value of this control. Must be a list.
        :param value:
        :return:
        """
        self._value = value
        self.refresh()
        self.sync()

    def value(self):
        return self._value


class ProgressBar(Control):
    """
    HFX progress bar
    """
    def __init__(self):
        super(ProgressBar, self).__init__('Progress', inLineLabel=True)
        self.input = QtGui.QProgressBar()
        self.addControl(self.input)

    def setValue(self, value):
        self.input.setValue(value)


# ----------- 3rd party ------------ #

def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('#CC6600', 'bold'),
    'operator': format('red'),
    'brace': format('darkGray'),
    'defclass': format('green', 'bold'),
    'string': format('darkMagenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'self': format('green', 'italic'),
    'numbers': format('brown'),
}


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python + numpy keywords
    python_keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False','linspace','array','arange','zeros']


    keywords=python_keywords
    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # syntax highlighting from this point onward
        self.tri_single = (QtCore.QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QtCore.QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                try:
                    length = text.length() - start + add
                except AttributeError:
                    pass
            try:
                # Apply formatting
                self.setFormat(start, length, style)
                # Look for the next match
                start = delimiter.indexIn(text, start + length)
            except:
                pass

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
