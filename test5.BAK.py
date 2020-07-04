import sys

import serial
from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtWidgets import *
from coordinate7 import Ui_MainWindow
from sympy import *
import math
from scipy.optimize import fsolve


class Demo(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Demo, self).__init__()
        self.setupUi(self)

        self.list_positon = []
        self.length1=150####
        self.length2=150####
        self.ser = 0
        self.previous = [0, 0, 0, 0]

        self.doubleSpinBox_x_init()
        self.doubleSpinBox_y_init()
        self.doubleSpinBox_z_init()
        self.doubleSpinBox_r_init()
        self.doubleSpinBox_j1_init()
        self.doubleSpinBox_j2_init()
        self.doubleSpinBox_j3_init()
        self.doubleSpinBox_j4_init()

        self.dateTimeEdit_init()

        self.pushButton_run_coordinate.clicked.connect(lambda: self.run_func(self.pushButton_run_coordinate))
        self.pushButton_run_joint.clicked.connect(lambda: self.run_func(self.pushButton_run_joint))

        self.pushButton_connection.clicked.connect(self.connection_func)  # 连接
        self.pushButton_resetzero.clicked.connect(self.resetzero_func)  # 归零
        self.pushButton_replace.clicked.connect(self.replace_func)  # 复位
        self.pushButton_stop.clicked.connect(self.stop_func)

        self.pushButton_speedsetting_coordinate.clicked.connect(
            lambda: self.speedsetting_func(self.pushButton_speedsetting_coordinate))  # 速度设置
        self.pushButton_speedsetting_joint.clicked.connect(
            lambda: self.speedsetting_func(self.pushButton_speedsetting_joint))

        self.slider_Speed_coordinate.valueChanged.connect(
            lambda :self.changeValue_func(self.slider_Speed_coordinate))  #速度滑块
        self.slider_Speed_joint.valueChanged.connect(
            lambda :self.changeValue_func(self.slider_Speed_joint))


        self.tabWidget_CJ.currentChanged['int'].connect(self.tabCJ_func)  # 绑定标签点击时的信号与槽函数



    def dateTimeEdit_init(self):
        timer = QTimer(self)
        timer.timeout.connect(self.showtime)
        timer.start()

    def showtime(self):
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

    #加个急停
    def stop_func(self):
        if self.ser != 0:
            result = self.ser.write("M112 \n".encode("gbk"))
            print("M112 \n")
        else:
            print("未连接！")

    def tabCJ_func(self, index):
        if (index == 0):
            #####################下面为坐标界面数值设定：
            alpha=self.doubleSpinBox_j1.value()
            beta=self.doubleSpinBox_j2.value()
            self.doubleSpinBox_x.setValue( self.length1*math.cos(alpha*math.pi/180)+ self.length2*math.cos((alpha+beta)*math.pi/180))
            self.doubleSpinBox_y.setValue(self.length1 * math.sin(alpha*math.pi/180) + self.length2 * math.sin((alpha+beta)*math.pi/180))
            # self.run_func(self.pushButton_run_joint)
            # sendNOW = "G92 X%0.1f Y%0.1f Z%0.1f \n" % (self.doubleSpinBox_x.value(), self.doubleSpinBox_y.value(),self.doubleSpinBox_z.value())
            # if self.ser != 0:
            #     result = self.ser.write(sendNOW.encode("gbk"))
            # else:
            #     print("未连接！")
            # print("G92",self.doubleSpinBox_x.value(), self.doubleSpinBox_y.value(),self.doubleSpinBox_z.value())
            #####################
        else:
            #####################下面为关节界面数值设定：
            x=self.doubleSpinBox_x.value()
            y=self.doubleSpinBox_y.value()
            #sympy求解速度过慢
            # j1= symbols('j1')
            # j2= symbols('j2')
            # result=solve([-x+self.length1*cos(j1)+self.length2*cos(j1+j2), -y+self.length1*sin(j1)+self.length2*sin(j1+j2)], [j1, j2])

            def func(i):
                j1,j2=i[0],i[1]
                return [-x+self.length1*math.cos(j1)+self.length2*math.cos(j1+j2), -y+self.length1*math.sin(j1)+self.length2*math.sin(j1+j2)]
            result = fsolve(func, [0, 0])
            (j1_r,j2_r)=result

            # for (i1,i2) in result:
            #     # if i1<0:
            #     #     i1=i1+2*math.pi
            #     # if i2<0:
            #     #     i2=i2+2*math.pi
            #     if i1>=0 and i2>=0:
            #         j1_r=i1
            #         j2_r=i2
            self.doubleSpinBox_j1.setValue( 180*float(j1_r)/float(pi))
            self.doubleSpinBox_j2.setValue(180 * float(j2_r) / float(pi))
            #####################


    def connection_func(self):
        # 端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
        portx = "COM3"
        # 波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
        bps = 250000
        # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
        timex = 3
        # 打开串口，并得到串口对象
        self.ser = serial.Serial(portx, bps, timeout=timex)
        print("连接成功")


    def resetzero_func(self):
        self.doubleSpinBox_x.setValue(0)
        self.doubleSpinBox_y.setValue(0)
        self.doubleSpinBox_z.setValue(0)
        self.doubleSpinBox_r.setValue(0)

        self.doubleSpinBox_j1.setValue(0)
        self.doubleSpinBox_j2.setValue(0)
        self.doubleSpinBox_j3.setValue(0)
        self.doubleSpinBox_j4.setValue(0)

    def replace_func(self):
        if self.ser!=0:
            result = self.ser.write("G28 \n".encode("gbk"))
        else:
            print("未连接！")


    def run_func(self, pushButton_run):
        if pushButton_run == self.pushButton_run_coordinate:
            self.list_positon.clear()
            self.list_positon.extend([self.doubleSpinBox_x.value(), self.doubleSpinBox_y.value()
                                         , self.doubleSpinBox_z.value(), self.doubleSpinBox_r.value()])
            sendangle = "G1 X%0.1f Y%0.1f \n" % (self.list_positon[0], self.list_positon[1])
            if self.ser != 0:
                if self.list_positon[0] ** 2 + self.list_positon[1] ** 2 <= 300 ** 2:
                    result = self.ser.write(sendangle.encode("gbk"))

                    #########保持坐标一致############：
                    x = self.doubleSpinBox_x.value()
                    y = self.doubleSpinBox_y.value()
                    def func(i):
                        j1, j2 = i[0], i[1]
                        return [-x + self.length1 * math.cos(j1) + self.length2 * math.cos(j1 + j2),
                                -y + self.length1 * math.sin(j1) + self.length2 * math.sin(j1 + j2)]
                    result = fsolve(func, [0, 0])
                    (j1_r, j2_r) = result

                    self.previous[0]=180 * float(j1_r) / float(pi)
                    self.previous[1]=180 * float(j2_r) / float(pi)
                    ####################
                else:
                    print("out of range!")
            else:
                print("未连接！")

            print(self.list_positon)

        else:
            self.list_positon.clear()
            self.list_positon.extend([self.doubleSpinBox_j1.value(), self.doubleSpinBox_j2.value()
                                         , self.doubleSpinBox_j3.value(), self.doubleSpinBox_j4.value()])
            deltax = self.list_positon[0] - self.previous[0]
            deltay = self.list_positon[1] - self.previous[1]
            print(deltax, deltay)
            sendangle = "G888 X%0.1f Y%0.1f \n" % (deltax, deltay)
            if self.ser != 0:
                result = self.ser.write(sendangle.encode("gbk"))
            else:
                print("未连接！")
            print(self.list_positon)
            self.previous = self.list_positon.copy()


    def changeValue_func(self,slider_Speed):
        if slider_Speed == self.slider_Speed_coordinate:
            self.slider_value = self.slider_Speed_coordinate.value()
            self.label_Speed_num_coordinate.setText(str(self.slider_value))
            self.slider_Speed_joint.setValue(self.slider_Speed_coordinate.value())
        else:
            self.slider_value = self.slider_Speed_joint.value()
            self.label_Speed_num_joint.setText(str(self.slider_value))
            self.slider_Speed_coordinate.setValue(self.slider_Speed_joint.value())


    def speedsetting_func(self,pushButton_Speedsetting):
        if pushButton_Speedsetting == self.pushButton_speedsetting_coordinate:
            if self.ser != 0:
                result = self.ser.write(("M220 S%d \n" % (self.slider_Speed_coordinate.value())).encode("gbk"))
            else:
                print("未连接！")
            print("M220 %d \n" % (self.slider_Speed_coordinate.value()))
        else:
            if self.ser != 0:
                result = self.ser.write(("M220 S%d \n" % (self.slider_Speed_joint.value())).encode("gbk"))
            else:
                print("未连接！")
            print("M220 S%d \n" % (self.slider_Speed_joint.value()))

    # x初始化及加减
    def doubleSpinBox_x_init(self):
        self.doubleSpinBox_x.setValue(0)
        self.doubleSpinBox_x.setRange(-999, 999)
        self.doubleSpinBox_x.setValue(self.doubleSpinBox_j1.value() * 2 + self.doubleSpinBox_j2.value()
                                      + self.doubleSpinBox_j3.value() + self.doubleSpinBox_j4.value())
        self.pushButton_xup.clicked.connect(self.xup_func)
        self.pushButton_xdown.clicked.connect(self.xdown_func)

    def xup_func(self):
        self.doubleSpinBox_x.setValue(self.doubleSpinBox_x.value() + self.doubleSpinBox_step_coordinate.value())
        self.run_func(self.pushButton_run_coordinate)

    def xdown_func(self):
        self.doubleSpinBox_x.setValue(self.doubleSpinBox_x.value() - self.doubleSpinBox_step_coordinate.value())
        self.run_func(self.pushButton_run_coordinate)

    # y初始化及加减
    def doubleSpinBox_y_init(self):
        self.doubleSpinBox_y.setValue(0)
        self.doubleSpinBox_y.setRange(-999, 999)
        self.pushButton_yup.clicked.connect(self.yup_func)
        self.pushButton_ydown.clicked.connect(self.ydown_func)

    def yup_func(self):
        self.doubleSpinBox_y.setValue(self.doubleSpinBox_y.value() + self.doubleSpinBox_step_coordinate.value())
        self.run_func(self.pushButton_run_coordinate)

    def ydown_func(self):
        self.doubleSpinBox_y.setValue(self.doubleSpinBox_y.value() - self.doubleSpinBox_step_coordinate.value())
        self.run_func(self.pushButton_run_coordinate)

    # z初始化及加减
    def doubleSpinBox_z_init(self):
        self.doubleSpinBox_z.setValue(0)
        self.doubleSpinBox_z.setRange(-999, 999)
        self.pushButton_zup.clicked.connect(self.zup_func)
        self.pushButton_zdown.clicked.connect(self.zdown_func)

    def zup_func(self):
        self.doubleSpinBox_z.setValue(self.doubleSpinBox_z.value() + self.doubleSpinBox_step_coordinate.value())
        self.run_func(self.pushButton_run_coordinate)

    def zdown_func(self):
        self.doubleSpinBox_z.setValue(self.doubleSpinBox_z.value() - self.doubleSpinBox_step_coordinate.value())
        self.run_func(self.pushButton_run_coordinate)

    # r初始化及加减
    def doubleSpinBox_r_init(self):
        self.doubleSpinBox_r.setValue(0)
        self.doubleSpinBox_r.setRange(-999, 999)
        self.pushButton_rup.clicked.connect(self.rup_func)
        self.pushButton_rdown.clicked.connect(self.rdown_func)

    def rup_func(self):
        self.doubleSpinBox_r.setValue(self.doubleSpinBox_r.value() + self.doubleSpinBox_step_coordinate.value())
        self.run_func(self.pushButton_run_coordinate)

    def rdown_func(self):
        self.doubleSpinBox_r.setValue(self.doubleSpinBox_r.value() - self.doubleSpinBox_step_coordinate.value())
        self.run_func(self.pushButton_run_coordinate)

    # J1初始化及加减
    def doubleSpinBox_j1_init(self):
        self.doubleSpinBox_j1.setValue(0)
        self.doubleSpinBox_j1.setRange(-999, 999)
        self.pushButton_J1up.clicked.connect(self.j1up_func)
        self.pushButton_J1down.clicked.connect(self.j1down_func)

    def j1up_func(self):
        self.doubleSpinBox_j1.setValue(self.doubleSpinBox_j1.value() + self.doubleSpinBox_step_joint.value())
        self.run_func(self.pushButton_run_joint)

    def j1down_func(self):
        self.doubleSpinBox_j1.setValue(self.doubleSpinBox_j1.value() - self.doubleSpinBox_step_joint.value())
        self.run_func(self.pushButton_run_joint)



    # J2初始化及加减
    def doubleSpinBox_j2_init(self):
        self.doubleSpinBox_j2.setValue(0)
        self.doubleSpinBox_j2.setRange(-999, 999)
        self.pushButton_J2up.clicked.connect(self.j2up_func)
        self.pushButton_J2down.clicked.connect(self.j2down_func)

    def j2up_func(self):
        self.doubleSpinBox_j2.setValue(self.doubleSpinBox_j2.value() + self.doubleSpinBox_step_joint.value())
        self.run_func(self.pushButton_run_joint)

    def j2down_func(self):
        self.doubleSpinBox_j2.setValue(self.doubleSpinBox_j2.value() - self.doubleSpinBox_step_joint.value())
        self.run_func(self.pushButton_run_joint)



    # J3初始化及加减
    def doubleSpinBox_j3_init(self):
        self.doubleSpinBox_j3.setValue(0)
        self.doubleSpinBox_j3.setRange(-999, 999)
        self.pushButton_J3up.clicked.connect(self.j3up_func)
        self.pushButton_J3down.clicked.connect(self.j3down_func)

    def j3up_func(self):
        self.doubleSpinBox_j3.setValue(self.doubleSpinBox_j3.value() + self.doubleSpinBox_step_joint.value())
        self.run_func(self.pushButton_run_joint)

    def j3down_func(self):
        self.doubleSpinBox_j3.setValue(self.doubleSpinBox_j3.value() - self.doubleSpinBox_step_joint.value())
        self.run_func(self.pushButton_run_joint)



    # J4初始化及加减
    def doubleSpinBox_j4_init(self):
        self.doubleSpinBox_j4.setValue(0)
        self.doubleSpinBox_j4.setRange(-999, 999)
        self.pushButton_J4up.clicked.connect(self.j4up_func)
        self.pushButton_J4down.clicked.connect(self.j4down_func)

    def j4up_func(self):
        self.doubleSpinBox_j4.setValue(self.doubleSpinBox_j4.value() + self.doubleSpinBox_step_joint.value())
        self.run_func(self.pushButton_run_joint)

    def j4down_func(self):
        self.doubleSpinBox_j4.setValue(self.doubleSpinBox_j4.value() - self.doubleSpinBox_step_joint.value())
        self.run_func(self.pushButton_run_joint)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())