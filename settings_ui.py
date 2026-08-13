import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QUrl
from PyQt6.QtGui import QIcon

import config

class ConfigBridge(QObject):
    configChanged = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.cfg = config.load_config()
        
    @pyqtSlot(result='QVariantMap')
    def getConfig(self):
        return self.cfg
        
    @pyqtSlot('QVariantMap')
    def saveConfig(self, new_cfg):
        config.save_config(new_cfg)
        self.cfg = new_cfg
        self.configChanged.emit()
        
    @pyqtSlot(result=str)
    def browseIcon(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(None, "Select Icon Image", "", "Images (*.png *.jpg *.jpeg *.svg *.xpm)")
        return path or ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setDesktopFileName('neurokrunner')
    app.setWindowIcon(QIcon.fromTheme("preferences-system"))
    
    engine = QQmlApplicationEngine()
    bridge = ConfigBridge()
    engine.rootContext().setContextProperty("backend", bridge)
    
    qml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())
