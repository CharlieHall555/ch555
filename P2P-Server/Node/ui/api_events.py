from PyQt5.QtCore import QObject, pyqtSignal

class APIEvents(QObject):
    api_started : pyqtSignal = pyqtSignal(int)
    """Passed Parameters: port : int""" 

    credentials_loaded : pyqtSignal = pyqtSignal(str , str)
    """Passed Parameters: priv_key : str , public_key : str""" 