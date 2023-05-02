import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import cv2
import numpy as np
import socket

class VideoThread(QThread):
    change_pixmap = pyqtSignal(QImage)

    def run(self):
        HOST = "192.168.100.18"
        PORT = 8486

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        while True:
            # Getting the size of the image
            size_data = client_socket.recv(4)
            size = int.from_bytes(size_data, byteorder="big")

            # Waiting to get the whole image
            data = b""
            while len(data) < size:
                data += client_socket.recv(size - len(data))

            # Decoding the image
            frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Convert the image to QImage and emit the signal
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            self.change_pixmap.emit(qImg)

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super(VentanaPrincipal,self).__init__()
        loadUi('GUI-4G-CAR-DEF.ui',self)

        # Conexion entre botones
        self.btn_config.clicked.connect(lambda: self.stacked_BarraConfig.setCurrentWidget(self.page_settings))
        self.btn_CAR_S.clicked.connect(lambda: self.stacked_Contenido.setCurrentWidget(self.page_car))
        self.btn_GUI_S.clicked.connect(lambda: self.stacked_Contenido.setCurrentWidget(self.page_GUI))
        self.btn_CAMERA_S.clicked.connect(lambda: self.stacked_Contenido.setCurrentWidget(self.page_CAMERA))
        self.btn_CLOSE_S.clicked.connect(lambda: self.stacked_Contenido.setCurrentWidget(self.page_video))
        self.btn_CLOSE_S.clicked.connect(lambda: self.stacked_BarraConfig.setCurrentWidget(self.page_config))

        # Conectar la señal currentTextChanged del QComboBox a la función actualizar_texto
        self.comboBox_LGauge.currentTextChanged.connect(self.actualizar_texto)
        self.comboBox_RGauge.currentTextChanged.connect(self.actualizar_texto)

        # Establecer el valor del QLabel al valor inicial del QComboBox
        self.label_GUI_text_1.setText(self.comboBox_LGauge.itemText(1))
        self.label_GUI_text_2.setText(self.comboBox_RGauge.itemText(0))

        # Actualizar el texto de los gauges
        self.comboBox_LGauge.currentTextChanged.connect(self.actualizar_texto)
        self.comboBox_RGauge.currentTextChanged.connect(self.actualizar_texto)

        # Establecemos las posiciones de los combobox en la GUI
        self.comboBox_LGauge.setCurrentIndex(1)
        self.comboBox_RGauge.setCurrentIndex(0)

        # Leer el valor del slider
        self.hSlider_MAX_P.valueChanged.connect(self.slider_one)

        # Leer el estado del radio button
        self.radioButton_FCOLLD.toggled.connect(self.control_radio1)
        self.radioButton_BCOLLD.toggled.connect(self.control_radio2)

    # Metodo para actualizar ambos textos de las combobox
    def actualizar_texto(self, texto):
        # Obtener el texto seleccionado del QComboBox
        Left_Gauge_text = self.comboBox_LGauge.currentText()
        Right_Gauge_text = self.comboBox_RGauge.currentText()

        # Actualizamos el texto dependiendo de la opcion seleccionada
        if Left_Gauge_text == "RPM":
            self.label_GUI_text_1.setText("RPM")
        elif Left_Gauge_text == "Km/h":
            self.label_GUI_text_1.setText("Km/h")
        elif Left_Gauge_text == "Acc":
            self.label_GUI_text_1.setText("Acc")

        if Right_Gauge_text == "RPM":
            self.label_GUI_text_2.setText("RPM")
        elif Right_Gauge_text == "Km/h":
            self.label_GUI_text_2.setText("Km/h")
        elif Right_Gauge_text == "Acc":
            self.label_GUI_text_2.setText("Acc")

    # Metodo para el slider
    def slider_one(self,event):
        self.hSlider_MAX_P.setValue(event)
        self.label_MAX_P.setText(str(event))

    # Metodos para los radio buttons
    def control_radio1(self):
        if self.radioButton_FCOLLD.isChecked()==True:
            print("Front Collision Detection ON")
        else:
            print("Front Collision Detection OFF")

    def control_radio2(self):
        if self.radioButton_BCOLLD.isChecked()==True:
            print("Back Collision Detection ON")
        else:
            print("Back Collision Detection OFF")

    def start_video_stream(self):
        # Create the video thread and connect its signal to the update_image slot
        self.thread = VideoThread()
        self.thread.change_pixmap.connect(self.update_image)
        self.thread.start()

    def update_image(self, qImg):
        # Update the label_video with the new image
        pixmap = QPixmap.fromImage(qImg)
        scaled_pixmap = pixmap.scaled(self.label_video.size(), QtCore.Qt.IgnoreAspectRatio)
        self.label_video.setPixmap(scaled_pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_window = VentanaPrincipal()
    my_window.show()
    my_window.start_video_stream()
    sys.exit(app.exec_())