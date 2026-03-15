import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QHeaderView, QProgressBar, QLabel,
                             QSpinBox, QApplication)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSlot
from config import AppConfig
from views.components.switch import Switch
from workers.checker_worker import CheckerWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.accounts = []
        self.worker = None
        self.is_dark_mode = False # Default based on config.py
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(AppConfig.APP_NAME)
        self.setMinimumSize(AppConfig.WINDOW_MIN_WIDTH, AppConfig.WINDOW_MIN_HEIGHT)
        self.setWindowIcon(QIcon(AppConfig.APP_ICON_PATH))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Toolbar/Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.btn_import = QPushButton("Import Accounts")
        self.btn_import.clicked.connect(self.import_accounts)
        
        button_layout.addWidget(self.btn_import)

        # Thread count
        button_layout.addWidget(QLabel("Threads:"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 100)
        self.spin_threads.setValue(5)
        button_layout.addWidget(self.spin_threads)

        self.btn_start = QPushButton("Start Check")
        self.btn_start.setObjectName("primary_btn")
        self.btn_start.clicked.connect(self.start_check)
        self.btn_start.setEnabled(False)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setObjectName("danger_btn")
        self.btn_stop.clicked.connect(self.stop_check)
        self.btn_stop.setEnabled(False)

        self.btn_export = QPushButton("Export Live")
        self.btn_export.clicked.connect(self.export_live)
        self.btn_export.setEnabled(False)

        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.btn_export)
        
        button_layout.addStretch()
        
        # Theme toggle with switch
        button_layout.addWidget(QLabel("Dark Mode:"))
        self.switch_theme = Switch()
        self.switch_theme.toggled.connect(self.toggle_theme)
        button_layout.addWidget(self.switch_theme)
        
        layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Email", "Password", "Refresh Token", "Client ID", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Sleeker look
        layout.addWidget(self.table)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Stats
        self.lbl_stats = QLabel("Loaded: 0 | Live: 0 | Die: 0")
        self.lbl_stats.setObjectName("stats_label")
        layout.addWidget(self.lbl_stats)

    @pyqtSlot(bool)
    def toggle_theme(self, checked):
        self.is_dark_mode = checked
        theme_path = AppConfig.DARK_THEME_PATH if self.is_dark_mode else AppConfig.LIGHT_THEME_PATH
        
        if os.path.exists(theme_path):
            with open(theme_path, "r", encoding="utf-8") as f:
                QApplication.instance().setStyleSheet(f.read())
        
        # Force redraw of custom components if needed
        self.switch_theme.update()
        
    @pyqtSlot()
    def import_accounts(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Account File", "", "Text Files (*.txt)")
        if file_path:
            self.accounts = []
            self.table.setRowCount(0)
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 4:
                        self.accounts.append(parts)
                        row = self.table.rowCount()
                        self.table.insertRow(row)
                        for i, part in enumerate(parts):
                            self.table.setItem(row, i, QTableWidgetItem(part))
                        self.table.setItem(row, 4, QTableWidgetItem("Ready"))
            
            self.btn_start.setEnabled(len(self.accounts) > 0)
            self._update_stats()

    def _update_stats(self):
        live = 0
        die = 0
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 4)
            if status_item:
                status = status_item.text()
                if status == "Live": live += 1
                elif status == "Die": die += 1
        self.lbl_stats.setText(f"Loaded: {len(self.accounts)} | Live: {live} | Die: {die}")
        self.btn_export.setEnabled(live > 0)

    @pyqtSlot()
    def start_check(self):
        if not self.accounts:
            return
        
        self.btn_start.setEnabled(False)
        self.btn_import.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.progress_bar.setValue(0)

        # Reset status in table
        for row in range(self.table.rowCount()):
            self.table.setItem(row, 4, QTableWidgetItem("Wait..."))

        self.worker = CheckerWorker(self.accounts, thread_count=self.spin_threads.value())
        self.worker.account_checked.connect(self.on_account_checked)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    @pyqtSlot(int, str, str)
    def on_account_checked(self, index, status, message):
        item = QTableWidgetItem(status)
        if status == "Live":
            item.setForeground(Qt.green)
        elif status == "Die":
            item.setForeground(Qt.red)
        
        self.table.setItem(index, 4, item)
        # self.table.scrollToItem(item) # Might be too jittery with many threads
        self._update_stats()

    @pyqtSlot()
    def stop_check(self):
        if self.worker:
            self.worker.stop()
            self.btn_stop.setEnabled(False)

    @pyqtSlot()
    def on_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_import.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self._update_stats()
        self.worker = None

    @pyqtSlot()
    def export_live(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Live Accounts", "live_accounts.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                for row in range(self.table.rowCount()):
                    if self.table.item(row, 4).text() == "Live":
                        line_parts = []
                        for col in range(4):
                            line_parts.append(self.table.item(row, col).text())
                        f.write('|'.join(line_parts) + '\n')
