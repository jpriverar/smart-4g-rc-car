import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QGridLayout, QSpinBox, QStackedWidget
from PyQt5.QtWidgets import QDesktopWidget, QHBoxLayout, QWidget, QSizePolicy, QGroupBox, QLabel, QComboBox, QLineEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def showConfigWidget(self):
        self.stacked_widget.setCurrentIndex(1)

    def hideConfigWidget(self):
        # Ocultar el widget de configuración y volver al widget anterior
        self.stacked_widget.setCurrentIndex(0)

    def initUI(self):
        self.setWindowTitle("Mi Ventana Principal")
        self.resize(1024, 600)  # resolucion de pixeles

        # Crear QStackedWidget para alternar entre las ventanas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Agregar el botón de configuración en la barra de herramientas
        config_button = QPushButton("Config", self)
        config_button.clicked.connect(self.showConfigWidget)
        self.toolbar = self.addToolBar("Configuración")

        # Agregar espacio elástico a la derecha del botón Config
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(config_button)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.hideConfigWidget)
        self.toolbar.addWidget(close_button)

        # Crear widget de configuración
        config_widget = QWidget()
        layout = QGridLayout()

        # Agregar widgets a la izquierda con entradas de texto
        MAX_label = QLabel("MAX POWER:", config_widget)
        COL_label = QLabel("COLISION DISTANCE:", config_widget)
        IMAGE_label = QLabel("IMAGE RESOLUTION:", config_widget)
        MAX_edit = QLineEdit(config_widget)
        COL_edit = QLineEdit(config_widget)
        IMAGE_edit = QLineEdit(config_widget)
        MAX_edit.setMaximumWidth(100)
        COL_edit.setMaximumWidth(100)
        IMAGE_edit.setMaximumWidth(100)

        layout.addWidget(MAX_label, 0, 0)
        layout.addWidget(MAX_edit, 0, 1)
        layout.addWidget(COL_label, 1, 0)
        layout.addWidget(COL_edit, 1, 1)
        layout.addWidget(IMAGE_label, 2, 0)
        layout.addWidget(IMAGE_edit, 2, 1)

        # Agregar widgets a la derecha con dropbox
        left_gauge_label = QLabel("LEFT GAUGE:")
        left_gauge_combo = QComboBox()
        left_gauge_combo.addItems(["RPM", "Km/h", "Acc"])
        right_gauge_label = QLabel("RIGHT GAUGE:")
        right_gauge_combo = QComboBox()
        right_gauge_combo.addItems(["RPM", "Km/h", "Acc"])

        layout.addWidget(left_gauge_label, 0, 2)
        layout.addWidget(left_gauge_combo, 0, 3)
        layout.addWidget(right_gauge_label, 1, 2)
        layout.addWidget(right_gauge_combo, 1, 3)

        # Ajustar espaciado entre widgets
        layout.setColumnStretch(4, 1)  # agregar espacio al final de la cuadrícula
        layout.setHorizontalSpacing(20)  # aumentar el espacio horizontal
        layout.setVerticalSpacing(10)  # aumentar el espacio vertical

        # Agregar layout al widget de configuración
        config_widget.setLayout(layout)

        # Agregar widget de configuración al QStackedWidget
        self.stacked_widget.addWidget(QWidget())
        self.stacked_widget.addWidget(config_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_window = MainWindow()
    my_window.show()
    sys.exit(app.exec_())