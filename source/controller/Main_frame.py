import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

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
        slider1 = str(event)
        print(slider1)

    # Metodos para leer los radio buttons
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

    # Metodos para leer las spinBox
    #Steering
    def spinS_MAX_valueChange(self):
        value_S_MAX = self.spinBox_S_MAX.value()
        print('El valor del Steering MAX es:',value_S_MAX)

    def spinS_CENTER_valueChange(self):
        value_S_CENTER = self.spinBox_S_CENTER.value()
        print('El valor del Steering CENTER es:',value_S_CENTER)

    def spinS_MIN_valueChange(self):
        value_S_MIN = self.spinBox_S_MIN.value()
        print('El valor del Steering MIN es:',value_S_MIN)

    #Ultrasonic sensor
    def spinFCOLLD_valueChange(self):
        value_FCOLLD = self.spinBox_FCOLLD.value()
        print('El valor del Front Collision Sensor es:',value_FCOLLD)

    def spinBCOLLD_valueChange(self):
        value_BCOLLD = self.spinBox_BCOLLD.value()
        print('El valor del Back Collision Sensor es:', value_BCOLLD)

    #PAN camera
    def spinPAN_MAX_valueChange(self):
        value_PAN_MAX = self.spinBox_PAN_MAX.value()
        print('El valor del PAN MAX es:', value_PAN_MAX)

    def spinPAN_CENTER_valueChange(self):
        value_PAN_CENTER = self.spinBox_PAN_CENTER.value()
        print('El valor del PAN CENTER es:', value_PAN_CENTER)

    def spinPAN_MIN_valueChange(self):
        value_PAN_MIN = self.spinBox_PAN_MIN.value()
        print('El valor del PAN MIN es:', value_PAN_MIN)

    #TILT camera
    def spinTILT_MAX_valueChange(self):
        value_TILT_MAX = self.spinBox_TILT_MAX.value()
        print('El valor del TILT MAX es:', value_TILT_MAX)

    def spinTILT_CENTER_valueChange(self):
        value_TILT_CENTER = self.spinBox_TILT_CENTER.value()
        print('El valor del TILT CENTER es:', value_TILT_CENTER)

    def spinTILT_MIN_valueChange(self):
        value_TILT_MIN = self.spinBox_TILT_MIN.value()
        print('El valor del TILT MIN es:', value_TILT_MIN)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_window = VentanaPrincipal()
    my_window.show()
    sys.exit(app.exec_())

