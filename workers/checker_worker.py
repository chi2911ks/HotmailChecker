from PyQt5.QtCore import QThread, pyqtSignal
from services.microsoft_service import MicrosoftService
from concurrent.futures import ThreadPoolExecutor

class CheckerWorker(QThread):
    account_checked = pyqtSignal(int, str, str)  # index, status, message
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, accounts, thread_count=5, parent=None):
        super().__init__(parent)
        self.accounts = accounts
        self.thread_count = thread_count
        self.is_running = True
        self.checked_count = 0

    def check_account(self, index, acc):
        if not self.is_running:
            return

        try:
            mail, password, refresh_token, client_id = acc
            success, result = MicrosoftService.check_refresh_token(client_id, refresh_token)
            
            if success:
                self.account_checked.emit(index, "Live", "Token is valid")
            else:
                self.account_checked.emit(index, "Die", result)
        except Exception as e:
            self.account_checked.emit(index, "Error", f"Invalid format: {str(e)}")
        
        self.checked_count += 1
        total = len(self.accounts)
        self.progress.emit(int((self.checked_count) / total * 100))

    def run(self):
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            for i, acc in enumerate(self.accounts):
                if not self.is_running:
                    break
                executor.submit(self.check_account, i, acc)
        
        self.finished.emit()

    def stop(self):
        self.is_running = False
