import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import threading
from remote_controller import RemoteController
from video_receiver import UDPVideoThread

sys.path.append("../common")
from socket_relay_client import RelayClientUDP


class VentanaPrincipal(QMainWindow):
    def __init__(self, command_sender):
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

        # Actualizar el texto de los gauges respecto a las combobox
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

        #Leer el valor de la spinbox
        #Steering
        self.spinBox_S_MAX.valueChanged.connect(self.spinS_MAX_valueChange)
        self.spinBox_S_CENTER.valueChanged.connect(self.spinS_CENTER_valueChange)
        self.spinBox_S_MIN.valueChanged.connect(self.spinS_MIN_valueChange)

        #Ultrasonic sensor
        self.spinBox_FCOLLD.valueChanged.connect(self.spinFCOLLD_valueChange)
        self.spinBox_BCOLLD.valueChanged.connect(self.spinBCOLLD_valueChange)

        #PAN Camera
        self.spinBox_PAN_MAX.valueChanged.connect(self.spinPAN_MAX_valueChange)
        self.spinBox_PAN_CENTER.valueChanged.connect(self.spinPAN_CENTER_valueChange)
        self.spinBox_PAN_MIN.valueChanged.connect(self.spinPAN_MIN_valueChange)

        #Tilt Camera
        self.spinBox_TILT_MAX.valueChanged.connect(self.spinTILT_MAX_valueChange)
        self.spinBox_TILT_CENTER.valueChanged.connect(self.spinTILT_CENTER_valueChange)
        self.spinBox_TILT_MIN.valueChanged.connect(self.spinTILT_MIN_valueChange)

        self.send_command = command_sender

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
            self.label_GUI_text_1.setText("ACC")

        if Right_Gauge_text == "RPM":
            self.label_GUI_text_2.setText("RPM")
        elif Right_Gauge_text == "Km/h":
            self.label_GUI_text_2.setText("Km/h")
        elif Right_Gauge_text == "Acc":
            self.label_GUI_text_2.setText("ACC")

    # Metodo para leer el slider
    def slider_one(self,event):
        self.hSlider_MAX_P.setValue(event)
        self.label_MAX_P.setText(str(event))
        value = str(event)

        # Changing power percentage to 8-bit integer representation
        value = int(int(value)*255/100)
        self.send_command(f"DM{value}\n".encode())

    # Metodos para leer los radio buttons
    def control_radio1(self):
        if self.radioButton_FCOLLD.isChecked()==True:
            self.send_command(f"FE000\n".encode())
        else:
            self.send_command(f"FD000\n".encode())

    def control_radio2(self):
        if self.radioButton_BCOLLD.isChecked()==True:
            self.send_command(f"BE000\n".encode())
        else:
            self.send_command(f"BD000\n".encode())

    # Metodos para leer las spinBox
    #Steering
    def spinS_MAX_valueChange(self):
        value = self.spinBox_S_MAX.value()
        self.send_command(f"SM{value}\n".encode())

    def spinS_CENTER_valueChange(self):
        value = self.spinBox_S_CENTER.value()
        self.send_command(f"Sc{value}\n".encode())

    def spinS_MIN_valueChange(self):
        value = self.spinBox_S_MIN.value()
        self.send_command(f"Sm{value}\n".encode())

    #Ultrasonic sensor
    def spinFCOLLD_valueChange(self):
        value = self.spinBox_FCOLLD.value()
        self.send_command(f"F!{value}\n".encode())

    def spinBCOLLD_valueChange(self):
        value = self.spinBox_BCOLLD.value()
        self.send_command(f"B!{value}\n".encode())

    #PAN camera
    def spinPAN_MAX_valueChange(self):
        value = self.spinBox_PAN_MAX.value()
        self.send_command(f"PM{value}\n".encode())

    def spinPAN_CENTER_valueChange(self):
        value = self.spinBox_PAN_CENTER.value()
        self.send_command(f"Pc{value}\n".encode())

    def spinPAN_MIN_valueChange(self):
        value = self.spinBox_PAN_MIN.value()
        self.send_command(f"Pm{value}\n".encode())

    #TILT camera
    def spinTILT_MAX_valueChange(self):
        value = self.spinBox_TILT_MAX.value()
        self.send_command(f"TM{value}\n".encode())

    def spinTILT_CENTER_valueChange(self):
        value = self.spinBox_TILT_CENTER.value()
        self.send_command(f"Tc{value}\n".encode())

    def spinTILT_MIN_valueChange(self):
        value = self.spinBox_TILT_MIN.value()
        self.send_command(f"Tm{value}\n".encode())
        
    def start_video_stream(self, host, port):
        # Create the video thread and connect its signal to the update_image slot
        self.thread = UDPVideoThread(host, port)
        self.thread.change_pixmap.connect(self.update_image)
        self.thread.start()

    def update_image(self, qImg):
        # Update the label_video with the new image
        pixmap = QPixmap.fromImage(qImg)
        scaled_pixmap = pixmap.scaled(self.label_video.size(), QtCore.Qt.IgnoreAspectRatio)
        self.label_video.setPixmap(scaled_pixmap)

if __name__ == '__main__':

    HOST = "3.134.62.14"
    CONTROL_PORT = 8486
    VIDEO_PORT = 8488

    control_client = RelayClientUDP(HOST, CONTROL_PORT)
    control_client.sendto("OK".encode())

    controller = RemoteController(dev_path="auto", command_sender=control_client.sendto)
    controller_thread = threading.Thread(target=controller.read_loop, daemon=True)
    controller_thread.start()

    app = QApplication(sys.argv)
    my_window = VentanaPrincipal(command_sender=control_client.sendto)
    my_window.show()
    my_window.start_video_stream(HOST, VIDEO_PORT)
    sys.exit(app.exec_())

