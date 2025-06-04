from PyQt5.QtCore import QObject, pyqtSignal

class UIEvents(QObject):
    add_candidated_pressed : pyqtSignal = pyqtSignal(str)
    """Passed Parameters: name_of_candidate : str | Fired when a user presses submit on the add_candidate page."""

    load_candidate_credentials_from_file : pyqtSignal = pyqtSignal()
    """Passed Parameters: None | Fired when user presses load credentails prompting the server to load the credentials from a file"""

    load_electors_from_file : pyqtSignal = pyqtSignal()

    submit_vote : pyqtSignal = pyqtSignal(int)
    """Passed Parameters: vote_choice : int | Fired when a user presses submit votes."""

    add_validator_pressed : pyqtSignal = pyqtSignal(str)
    """Passed Parameters: node_id : str"""