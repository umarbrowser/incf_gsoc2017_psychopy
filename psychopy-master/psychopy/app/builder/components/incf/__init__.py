from os import path
from .._base import BaseComponent, Param, getInitVals, _translate


thisFolder = path.abspath(path.dirname(__name__))
iconFile = path.join(thisFolder, '#created icon name')
tooltip = _translate('Incf experimental tools')


