import os

class AppState:
    def __init__(self):
        self.latest_file_path = None
        self._load_state()

    def _load_state(self):
        if not os.path.exists('latest_file_path.txt'):
            with open('latest_file_path.txt', 'w') as f:
                f.write('')
        else:
            with open('latest_file_path.txt', 'r') as f:
                self.latest_file_path = f.read().strip()

    def save_state(self):
        with open('latest_file_path.txt', 'w') as f:
            f.write(self.latest_file_path if self.latest_file_path else '')

state = AppState()