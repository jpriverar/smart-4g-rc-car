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
from mqtt_client import MQTT_Client

class GUI(QMainWindow):
    mqtt_msg_signal = pyqtSignal(str, int)

    def __init__(self):
        super(GUI, self).__init__()
        loadUi('GUI-4G-CAR-DEF_#2.ui', self)

        self.widget_setter_func = {"STEER_MAX": self.set_steering_max,
                                   "STEER_CENTER": self.set_steering_center,
                                   "STEER_MIN": self.set_steering_min,
                                   "PAN_MAX": self.set_pan_max,
                                   "PAN_CENTER": self.set_pan_center,
                                   "PAN_MIN": self.set_pan_min,
                                   "TILT_MAX": self.set_tilt_max,
                                   "TILT_CENTER": self.set_tilt_center,
                                   "TILT_MIN": self.set_tilt_min,
                                   "DRIVE_MAX_POWER": self.set_drive_max_power,
                                   "FPS": self.set_fps,
                                   "PACKET_SIZE":self.set_packet_size}

        # Ejemplo de los valores que pueden llegar a los gauges
        self.RPM = 10
        self.Acc = 15
        self.Speed = 25

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
        self.config_button.clicked.connect(lambda: self.stacked_BarraConfig.setCurrentWidget(self.page_settings))
        self.car_settings_button.clicked.connect(lambda: self.stacked_Contenido.setCurrentWidget(self.page_car))
        self.gui_settings_button.clicked.connect(lambda: self.stacked_Contenido.setCurrentWidget(self.page_GUI))
        self.camera_settings_button.clicked.connect(lambda: self.stacked_Contenido.setCurrentWidget(self.page_CAMERA))
        self.close_settings_button.clicked.connect(lambda: self.stacked_Contenido.setCurrentWidget(self.page_video))
        self.close_settings_button.clicked.connect(lambda: self.stacked_BarraConfig.setCurrentWidget(self.page_config))

        # Conectar la señal currentTextChanged del QComboBox a la función actualizar_texto
        self.left_gauge_options.currentTextChanged.connect(self.left_gauge_option_changed)
        self.right_gauge_options.currentTextChanged.connect(self.right_gauge_option_changed)

        # Establecemos las posiciones de los combobox en la GUI
        self.left_gauge_options.setCurrentIndex(0)
        self.right_gauge_options.setCurrentIndex(1)
        self.left_gauge_option_changed()
        self.right_gauge_option_changed()

        # Leer el valor del slider
        self.max_power_slider.valueChanged.connect(self.slider_one)

        # Leer el estado del radio button
        self.front_collision_detection_button.toggled.connect(self.control_radio1)
        self.back_collision_detection_button.toggled.connect(self.control_radio2)

        # Leer el valor de la spinbox
        # Steering
        self.steering_max_spinbox.valueChanged.connect(self.spinS_MAX_valueChange)
        self.steering_center_spinbox.valueChanged.connect(self.spinS_CENTER_valueChange)
        self.steering_min_spinbox.valueChanged.connect(self.spinS_MIN_valueChange)

        # Ultrasonic sensor
        self.front_collision_distance_spinbox.valueChanged.connect(self.spinFCOLLD_valueChange)
        self.back_collision_distance_spinbox.valueChanged.connect(self.spinBCOLLD_valueChange)

        # PAN Camera
        self.pan_max_spinbox.valueChanged.connect(self.spinPAN_MAX_valueChange)
        self.pan_center_spinbox.valueChanged.connect(self.spinPAN_CENTER_valueChange)
        self.pan_min_spinbox.valueChanged.connect(self.spinPAN_MIN_valueChange)

        # Tilt Camera
        self.tilt_max_spinbox.valueChanged.connect(self.spinTILT_MAX_valueChange)
        self.tilt_center_spinbox.valueChanged.connect(self.spinTILT_CENTER_valueChange)
        self.tilt_min_spinbox.valueChanged.connect(self.spinTILT_MIN_valueChange)

        # To update wigets when a new mqtt message is received
        self.mqtt_msg_signal.connect(self.widget_setter)

        # leer spinbox y combobox de IMAGE
        self.compression_quality_spinbox.valueChanged.connect(self.spin_COMPRESSION_valueChange)
        self.image_resolution_options.currentTextChanged.connect(self.update_resolution)

        # NUEVO If para el estilo de los gauges sin necesidad de mover las combobox
        if self.RPM < 50:
            self.right_gauge_value_label.setStyleSheet("background-color: rgb(0, 206, 151); color: white;"
                                                       "border-radius: 50%;"
                                                       "font-family: Bahnschrift;"
                                                       "font-size: 25px; font-weight: 600;")
        elif self.RPM < 100:
            self.right_gauge_value_label.setStyleSheet("background-color: rgb(255, 165, 0); color: black;"
                                                       "border-radius: 50%;"
                                                       "font-family: Bahnschrift;"
                                                       "font-size: 25px; font-weight: 600;")
        else:
            self.right_gauge_value_label.setStyleSheet("background-color: rgb(128, 0, 0); color: white;"
                                                       "border-radius: 50%;"
                                                       "font-family: Bahnschrift;"
                                                       "font-size: 25px; font-weight: 600;")

        if self.Speed <= 50:
            self.left_gauge_value_label.setStyleSheet("background-color: rgb(0, 206, 151); color: white; "
                                                      "border-radius: 50%;"
                                                      "font-family: Bahnschrift;"
                                                      "font-size: 25px; font-weight: 600;")
        elif self.Speed <= 75:
            self.left_gauge_value_label.setStyleSheet("background-color: rgb(255, 165, 0); color: black; "
                                                      "border-radius: 50%;"
                                                      "font-family: Bahnschrift;"
                                                      "font-size: 25px; font-weight: 600;")
        else:
            self.left_gauge_value_label.setStyleSheet("background-color: rgb(128, 0, 0); color: white; "
                                                      "border-radius: 50%;"
                                                      "font-family: Bahnschrift;"
                                                      "font-size: 25px; font-weight: 600;")

    def init_video_stream(self, host, port):
        # Create the video thread and connect its signal to the update_image slot
        self.video_streamer = UDPVideoThread(host, port)
        self.video_streamer.change_pixmap.connect(self.update_image)
        self.video_streamer.start()

    def update_image(self, qImg):
        # Update the label_video with the new image
        pixmap = QPixmap.fromImage(qImg)

        # Set a fixed size for the label equal to frame_video's size
        self.label_video.setFixedSize(self.frame_Global.size())
        scaled_pixmap = pixmap.scaled(self.frame_Global.size(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label_video.setPixmap(scaled_pixmap)

        # Update tranmission data
        self.fps_value_label.setText(str(int(self.video_streamer.fps)))
        self.packet_size_value_label.setText(str(self.video_streamer.packet_size))

    def init_remote_control(self, remote_host, control_port):
        self.controller = RemoteController(remote_host, control_port, dev_path="/dev/input/event12", mqtt_publisher=self.mqtt_client.publish)
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
            if widget_name == "RPM":
                gear, rpm = msg.split(",")
                self.left_gauge_value_label.setText(rpm)

        elif widget_type == "CONFIG":
            self.mqtt_msg_signal.emit(widget_name, int(msg))

    def widget_setter(self, widget_name, value):
        self.widget_setter_func[widget_name](value)

    def set_pan_max(self, value):
        self.pan_max_spinbox.setValue(value)

    def set_pan_center(self, value):
        self.pan_center_spinbox.setValue(value)

    def set_pan_min(self, value):
        self.pan_min_spinbox.setValue(value)

    def set_tilt_max(self, value):
        self.tilt_max_spinbox.setValue(value)

    def set_tilt_center(self, value):
        self.tilt_center_spinbox.setValue(value)

    def set_tilt_min(self, value):
        self.tilt_min_spinbox.setValue(value)

    def set_steering_max(self, value):
        self.steering_max_spinbox.setValue(value)

    def set_steering_center(self, value):
        self.steering_center_spinbox.setValue(value)

    def set_steering_min(self, value):
        self.steering_min_spinbox.setValue(value)

    def set_drive_max_power(self, value):
        self.max_power_slider.setValue(value)
        self.max_power_value_label.setText(str(value))

    def set_fps(self, value):
        self.fps_value_label.setValue(value)

    def set_packet_size(self, value):
        self.packet_size_value_label.set_value(value)

    def left_gauge_option_changed(self):
        # Obtener el texto seleccionado del QComboBox
        left_gauge_option = self.left_gauge_options.currentText()

        if left_gauge_option == "RPM":
            units = "RPM"
            self.left_gauge_value_label.setText(str(self.RPM))
            if self.RPM < 50:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(0, 206, 151); color: white; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift; "
                                                          "font-size: 25px; font-weight: 600;")
            elif self.RPM < 100:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(255, 165, 0); color: black; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift; "
                                                          "font-size: 25px; font-weight: 600;")
            else:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(128, 0, 0); color: white; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift;"
                                                          "font-size: 25px; font-weight: 600;")
        elif left_gauge_option == "Speed":
            units = "Km/h"
            self.left_gauge_value_label.setText(str(self.Speed))
            if self.Speed < 50:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(0, 206, 151); color: white; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift; "
                                                          "font-size: 25px; font-weight: 600;")
            elif self.Speed < 100:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(255, 165, 0); color: black; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift; "
                                                          "font-size: 25px; font-weight: 600;")
            else:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(128, 0, 0); color: white; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift;"
                                                          "font-size: 25px; font-weight: 600;")
        elif left_gauge_option == "Acceleration":
            units = "m/s*s"
            self.left_gauge_value_label.setText(str(self.Acc))
            if self.Acc < 50:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(0, 206, 151); color: white; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift; "
                                                          "font-size: 25px; font-weight: 600;")
            elif self.Acc < 100:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(255, 165, 0); color: black; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift; "
                                                          "font-size: 25px; font-weight: 600;")
            else:
                self.left_gauge_value_label.setStyleSheet("background-color: rgb(128, 0, 0); color: white; "
                                                          "border-radius: 50%;"
                                                          "font-family: Bahnschrift;"
                                                          "font-size: 25px; font-weight: 600;")
        self.left_gauge_units_label.setText(units)
        
    def right_gauge_option_changed(self):
        right_gauge_option = self.right_gauge_options.currentText()
        if right_gauge_option == "RPM":
            units = "RPM"
            self.right_gauge_value_label.setText(str(self.RPM))
            if self.RPM < 50:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(0, 206, 151); color: white; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift; "
                                                           "font-size: 25px; font-weight: 600;")
            elif self.RPM < 100:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(255, 165, 0); color: black; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift; "
                                                           "font-size: 25px; font-weight: 600;")
            else:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(128, 0, 0); color: white; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift;"
                                                           "font-size: 25px; font-weight: 600;")
        elif right_gauge_option == "Speed":
            units = "Km/h"
            self.right_gauge_value_label.setText(str(self.Speed))
            if self.Speed < 50:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(0, 206, 151); color: white; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift; "
                                                           "font-size: 25px; font-weight: 600;")
            elif self.Speed < 100:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(255, 165, 0); color: black; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift; "
                                                           "font-size: 25px; font-weight: 600;")
            else:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(128, 0, 0); color: white; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift;"
                                                           "font-size: 25px; font-weight: 600;")
        elif right_gauge_option == "Acceleration":
            units = "m/s*s"
            self.right_gauge_value_label.setText(str(self.Acc))
            if self.Acc < 50:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(0, 206, 151); color: white; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift; "
                                                           "font-size: 25px; font-weight: 600;")
            elif self.Acc < 100:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(255, 165, 0); color: black; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift; "
                                                           "font-size: 25px; font-weight: 600;")
            else:
                self.right_gauge_value_label.setStyleSheet("background-color: rgb(128, 0, 0); color: white; "
                                                           "border-radius: 50%;"
                                                           "font-family: Bahnschrift;"
                                                           "font-size: 25px; font-weight: 600;")
        self.right_gauge_units_label.setText(units)

    # Metodo para leer el slider
    def slider_one(self, event):
        self.max_power_slider.setValue(event)
        self.max_power_value_label.setText(str(event))
        value = str(event)

        # Changing power percentage to 8-bit integer representation
        value = int(int(value)*255/100)
        print(value)
        self.controller.send_command(f"DM{value}\n".encode())

    # Metodos para leer los radio buttons
    def control_radio1(self):
        if self.front_collision_detection_button.isChecked() == True:
            self.controller.send_command(f"FE000\n".encode())
        else:
            self.controller.send_command(f"FD000\n".encode())

    def control_radio2(self):
        if self.back_collision_detection_button.isChecked() == True:
            self.controller.send_command(f"BE000\n".encode())
        else:
            self.controller.send_command(f"BD000\n".encode())

    # Metodos para leer las spinBox
    # Steering
    def spinS_MAX_valueChange(self):
        value = self.steering_max_spinbox.value()
        self.controller.send_command(f"SM{value}\n".encode())

    def spinS_CENTER_valueChange(self):
        value = self.steering_center_spinbox.value()
        self.controller.send_command(f"Sc{value}\n".encode())

    def spinS_MIN_valueChange(self):
        value = self.steering_min_spinbox.value()
        self.controller.send_command(f"Sm{value}\n".encode())

    # Ultrasonic sensor
    def spinFCOLLD_valueChange(self):
        value = self.front_collision_distance_spinbox.value()
        self.controller.send_command(f"F!{value}\n".encode())

    def spinBCOLLD_valueChange(self):
        value = self.back_collision_distance_spinbox.value()
        self.controller.send_command(f"B!{value}\n".encode())

    # PAN camera
    def spinPAN_MAX_valueChange(self):
        value = self.pan_max_spinbox.value()
        self.controller.send_command(f"PM{value}\n".encode())

    def spinPAN_CENTER_valueChange(self):
        value = self.pan_center_spinbox.value()
        self.controller.send_command(f"Pc{value}\n".encode())

    def spinPAN_MIN_valueChange(self):
        value = self.pan_min_spinbox.value()
        self.controller.send_command(f"Pm{value}\n".encode())

    # TILT camera
    def spinTILT_MAX_valueChange(self):
        value = self.tilt_max_spinbox.value()
        self.controller.send_command(f"TM{value}\n".encode())

    def spinTILT_CENTER_valueChange(self):
        value = self.tilt_center_spinbox.value()
        self.controller.send_command(f"Tc{value}\n".encode())

    def spinTILT_MIN_valueChange(self):
        value = self.tilt_min_spinbox.value()
        self.controller.send_command(f"Tm{value}\n".encode())

    #Metodos imagen
    def spin_COMPRESSION_valueChange(self):
        value = self.compression_quality_spinbox.value()
        print('El valor del TILT MIN es:', value)

    # Metodos para hacer set al valor del Packet y de los FPS
    def Packet_size_valueChange(self, value):
        self.packet_size_value_label.setValue(value)

    def FPS_valueChange(self, value):
        self.fps_value_label.setValue(value)

    def update_resolution(self):
        resolution_text = self.image_resolution_options.currentText()
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
    #gui.showMaximized()
    gui.show()
    sys.exit(app.exec_())
