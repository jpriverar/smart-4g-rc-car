from mqtt_client import MQTT_Client
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import threading
from remote_controller import RemoteController
from video_receiver import UDPVideoThread

sys.path.append("../common")


class GUI(QMainWindow):
    mqtt_msg_signal = pyqtSignal(str, int)

    def __init__(self):
        super(GUI, self).__init__()
        loadUi('GUI-4G-CAR-DEF.ui', self)

        self.widget_setter_func = {"STEER_MAX": self.set_steering_max,
                                   "STEER_CENTER": self.set_steering_center,
                                   "STEER_MIN": self.set_steering_min,
                                   "PAN_MAX": self.set_pan_max,
                                   "PAN_CENTER": self.set_pan_center,
                                   "PAN_MIN": self.set_pan_min,
                                   "TILT_MAX": self.set_tilt_max,
                                   "TILT_CENTER": self.set_tilt_center,
                                   "TILT_MIN": self.set_tilt_min,
                                   "DRIVE_MAX_POWER": self.set_drive_max_power}

        # Create a new QLabel called label_video and set its parent to frame_Global
        self.label_video = QtWidgets.QLabel(self.frame_Global)
        self.label_video.setContentsMargins(0, 0, 0, 0)  # Set the margin to zero
        self.label_video.setStyleSheet("padding: 0px;")  # Set the padding to zero
        self.label_video.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        # Stack label_video under frame_BarraConfig
        self.label_video.stackUnder(self.frame_BarraConfig)
        # Stack label_video under frame_Contenido
        self.label_video.stackUnder(self.frame_Contenido)

        # Conexion entre botones
        self.btn_config.clicked.connect(
            lambda: self.stacked_BarraConfig.setCurrentWidget(self.page_settings))
        self.btn_CAR_S.clicked.connect(
            lambda: self.stacked_Contenido.setCurrentWidget(self.page_car))
        self.btn_GUI_S.clicked.connect(
            lambda: self.stacked_Contenido.setCurrentWidget(self.page_GUI))
        self.btn_CAMERA_S.clicked.connect(
            lambda: self.stacked_Contenido.setCurrentWidget(self.page_CAMERA))
        self.btn_CLOSE_S.clicked.connect(
            lambda: self.stacked_Contenido.setCurrentWidget(self.page_video))
        self.btn_CLOSE_S.clicked.connect(
            lambda: self.stacked_BarraConfig.setCurrentWidget(self.page_config))

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

        # Leer el valor de la spinbox
        # Steering
        self.spinBox_S_MAX.valueChanged.connect(self.spinS_MAX_valueChange)
        self.spinBox_S_CENTER.valueChanged.connect(self.spinS_CENTER_valueChange)
        self.spinBox_S_MIN.valueChanged.connect(self.spinS_MIN_valueChange)

        # Ultrasonic sensor
        self.spinBox_FCOLLD.valueChanged.connect(self.spinFCOLLD_valueChange)
        self.spinBox_BCOLLD.valueChanged.connect(self.spinBCOLLD_valueChange)

        # PAN Camera
        self.spinBox_PAN_MAX.valueChanged.connect(self.spinPAN_MAX_valueChange)
        self.spinBox_PAN_CENTER.valueChanged.connect(self.spinPAN_CENTER_valueChange)
        self.spinBox_PAN_MIN.valueChanged.connect(self.spinPAN_MIN_valueChange)

        # Tilt Camera
        self.spinBox_TILT_MAX.valueChanged.connect(self.spinTILT_MAX_valueChange)
        self.spinBox_TILT_CENTER.valueChanged.connect(self.spinTILT_CENTER_valueChange)
        self.spinBox_TILT_MIN.valueChanged.connect(self.spinTILT_MIN_valueChange)

        # To update wigets when a new mqtt message is received
        self.mqtt_msg_signal.connect(self.widget_setter)

        # leer spinbox y combobox de IMAGE
        self.spinBox_COMPRESSION.valueChanged.connect(self.spin_COMPRESSION_valueChange)
        self.comboBox_IMAGE.currentTextChanged.connect(self.update_resolution)

    def init_video_stream(self, host, port):
        # Create the video thread and connect its signal to the update_image slot
        self.thread = UDPVideoThread(host, port)
        self.thread.change_pixmap.connect(self.update_image)
        self.thread.start()

    def update_image(self, qImg):
        # Update the label_video with the new image
        pixmap = QPixmap.fromImage(qImg)
        # Set a fixed size for the label equal to frame_video's size
        self.label_video.setFixedSize(self.frame_Global.size())
        scaled_pixmap = pixmap.scaled(self.frame_Global.size(
        ), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_video.setPixmap(scaled_pixmap)

    def init_remote_control(self, remote_host, control_port):
        self.controller = RemoteController(
            remote_host, control_port, dev_path="auto", mqtt_publisher=self.mqtt_client.publish)
        self.controller.start()

    def init_MQTT(self, broker_address):
        self.mqtt_client = MQTT_Client()
        self.mqtt_client.msg_handler = self.mqtt_msg_handler
        self.mqtt_client.will_set(topic="CONTROLLER/STATUS", payload="OFF", qos=1, retain=True)
        self.mqtt_client.connect(broker_address)
        self.mqtt_client.loop_start()

        self.mqtt_client.subscribe("RCCAR/DATA/RPM")
        self.mqtt_client.subscribe("RCCAR/DATA/POS")
        self.mqtt_client.subscribe("RCCAR/CONFIG/STEER_MAX")
        self.mqtt_client.subscribe("RCCAR/CONFIG/STEER_CENTER")
        self.mqtt_client.subscribe("RCCAR/CONFIG/STEER_MIN")
        self.mqtt_client.subscribe("RCCAR/CONFIG/PAN_MAX")
        self.mqtt_client.subscribe("RCCAR/CONFIG/PAN_CENTER")
        self.mqtt_client.subscribe("RCCAR/CONFIG/PAN_MIN")
        self.mqtt_client.subscribe("RCCAR/CONFIG/TILT_MAX")
        self.mqtt_client.subscribe("RCCAR/CONFIG/TILT_CENTER")
        self.mqtt_client.subscribe("RCCAR/CONFIG/TILT_MIN")
        self.mqtt_client.subscribe("RCCAR/CONFIG/DRIVE_MAX_POWER")

        # Setting on the led in dashboard
        self.mqtt_client.publish(topic="CONTROLLER/STATUS", payload="ON", qos=1, retain=True)

    def mqtt_msg_handler(self, topic, msg):
        widget_type, widget_name = topic.split("/")[-2:]

        if widget_type == "DATA":
            #print("Not implemented:", widget_name)
            pass

        elif widget_type == "CONFIG":
            self.mqtt_msg_signal.emit(widget_name, int(msg))

    def widget_setter(self, widget_name, value):
        self.widget_setter_func[widget_name](value)

    def set_pan_max(self, value):
        self.spinBox_PAN_MAX.setValue(value)

    def set_pan_center(self, value):
        self.spinBox_PAN_CENTER.setValue(value)

    def set_pan_min(self, value):
        self.spinBox_PAN_MIN.setValue(value)

    def set_tilt_max(self, value):
        self.spinBox_TILT_MAX.setValue(value)

    def set_tilt_center(self, value):
        self.spinBox_TILT_CENTER.setValue(value)

    def set_tilt_min(self, value):
        self.spinBox_TILT_MIN.setValue(value)

    def set_steering_max(self, value):
        self.spinBox_S_MAX.setValue(value)

    def set_steering_center(self, value):
        self.spinBox_S_CENTER.setValue(value)

    def set_steering_min(self, value):
        self.spinBox_S_MIN.setValue(value)

    def set_drive_max_power(self, value):
        self.hSlider_MAX_P.setValue(value)
        self.label_MAX_P.setText(str(value))

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
    def slider_one(self, event):
        self.hSlider_MAX_P.setValue(event)
        self.label_MAX_P.setText(str(event))
        value = str(event)

        # Changing power percentage to 8-bit integer representation
        value = int(int(value)*255/100)
        self.controller.send_command(f"DM{value}\n".encode())

    # Metodos para leer los radio buttons
    def control_radio1(self):
        if self.radioButton_FCOLLD.isChecked() == True:
            self.controller.send_command(f"FE000\n".encode())
        else:
            self.controller.send_command(f"FD000\n".encode())

    def control_radio2(self):
        if self.radioButton_BCOLLD.isChecked() == True:
            self.controller.send_command(f"BE000\n".encode())
        else:
            self.controller.send_command(f"BD000\n".encode())

    # Metodos para leer las spinBox
    # Steering
    def spinS_MAX_valueChange(self):
        value = self.spinBox_S_MAX.value()
        self.controller.send_command(f"SM{value}\n".encode())

    def spinS_CENTER_valueChange(self):
        value = self.spinBox_S_CENTER.value()
        self.controller.send_command(f"Sc{value}\n".encode())

    def spinS_MIN_valueChange(self):
        value = self.spinBox_S_MIN.value()
        self.controller.send_command(f"Sm{value}\n".encode())

    # Ultrasonic sensor
    def spinFCOLLD_valueChange(self):
        value = self.spinBox_FCOLLD.value()
        self.controller.send_command(f"F!{value}\n".encode())

    def spinBCOLLD_valueChange(self):
        value = self.spinBox_BCOLLD.value()
        self.controller.send_command(f"B!{value}\n".encode())

    # PAN camera
    def spinPAN_MAX_valueChange(self):
        value = self.spinBox_PAN_MAX.value()
        self.controller.send_command(f"PM{value}\n".encode())

    def spinPAN_CENTER_valueChange(self):
        value = self.spinBox_PAN_CENTER.value()
        self.controller.send_command(f"Pc{value}\n".encode())

    def spinPAN_MIN_valueChange(self):
        value = self.spinBox_PAN_MIN.value()
        self.controller.send_command(f"Pm{value}\n".encode())

    # TILT camera
    def spinTILT_MAX_valueChange(self):
        value = self.spinBox_TILT_MAX.value()
        self.controller.send_command(f"TM{value}\n".encode())

    def spinTILT_CENTER_valueChange(self):
        value = self.spinBox_TILT_CENTER.value()
        self.controller.send_command(f"Tc{value}\n".encode())

    def spinTILT_MIN_valueChange(self):
        value = self.spinBox_TILT_MIN.value()
        self.controller.send_command(f"Tm{value}\n".encode())

    #Metodos imagen
    def spin_COMPRESSION_valueChange(self):
        value_COMPRESSION = self.spinBox_COMPRESSION.value()
        print('El valor del TILT MIN es:', value_COMPRESSION)

    # Metodos para hacer set al valor del Packet y de los FPS
    def Packet_size_valueChange(self, value):
        self.label_Packet_size_value.setValue(value)

    def FPS_valueChange(self, value):
        self.label_FPS_value.setValue(value)

    def update_resolution(self):
        resolution_text = self.comboBox_IMAGE.currentText()
        if resolution_text == "640x480":
            print("Resolution is 640x480")
        else:
            print("Resolution is 320x240")


if __name__ == '__main__':

    HOST = "3.134.62.14"
    CONTROL_PORT = 8486
    VIDEO_PORT = 8488

    app = QApplication(sys.argv)
    gui = GUI()
    gui.init_MQTT(HOST)
    gui.init_remote_control(HOST, CONTROL_PORT)
    gui.init_video_stream(HOST, VIDEO_PORT)
    gui.showMaximized()
    gui.show()
    sys.exit(app.exec_())
