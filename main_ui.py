from PyQt5 import QtCore, QtGui, QtWidgets
class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        self.setupUi(MainWindow)

    def _text(self, text, name=None, size=11, bold=False, color=None):
        label = QtWidgets.QLabel(text)
        if name:
            label.setObjectName(name)
        font = QtGui.QFont('Segoe UI', size)
        font.setBold(bold)
        label.setFont(font)
        if color:
            label.setStyleSheet('color: %s; background: transparent;' % color)
        return label

    def _card(self):
            w = QtWidgets.QFrame()
            w.setObjectName('card')
            w.setFrameShape(QtWidgets.QFrame.NoFrame)
            return w
    
    def _value(self, name, height=58):
            widget = self._text('Không nhận dạng được', name, 12, True)
            widget.setMinimumHeight(height)
            widget.setAlignment(QtCore.Qt.AlignCenter)
            widget.setWordWrap(True)
            widget.setProperty('field', 'true')
            return widget
    
    def setupUi(self, MainWindow):
            MainWindow.setObjectName('MainWindow')
            MainWindow.setWindowTitle('Quản lý bãi xe thông minh')
            MainWindow.resize(1390, 870)
            MainWindow.setMinimumSize(1100, 740)
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            self.centralwidget.setObjectName('centralwidget')
            MainWindow.setCentralWidget(self.centralwidget)
            self.centralwidget.setStyleSheet('''
                QWidget#centralwidget { background: #F2F5FA; color: #17263E; font-family: 'Segoe UI'; }
                QFrame#card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; }
                QLabel[field="true"] { background: #F5F8FD; border: 1px solid #E5EAF2;
                    border-radius: 10px; color: #1C3554; padding: 7px; }
                QLabel#label_main, QLabel#label_in, QLabel#label_plate {
                    background: #EAF0F7; border: 1px solid #DDE6F0; border-radius: 12px;
                    color: #70829A; }
                QPushButton { font-family: 'Segoe UI'; font-size: 12pt; font-weight: 600;
                    border: 0; border-radius: 11px; min-height: 48px; padding: 4px 10px; }
                QPushButton#button_check_in { color: white; background: #2563EB; }
                QPushButton#button_check_in:hover { background: #1D4ED8; }
                QPushButton#button_check_in:pressed { background: #1E40AF; }
                QPushButton#button_check_out { color: #C24135; background: #FFF1EF;
                    border: 1px solid #F5CBC6; }
                QPushButton#button_check_out:hover { background: #FFE0DC; }
                QPushButton#button_check_out:pressed { background: #FFCCC6; }
                QTextBrowser#textBrowser { background: #F5F8FD; border: 1px solid #E5EAF2;
                    border-radius: 10px; padding: 8px; color: #33455D; }
                QStatusBar { background: #FFFFFF; color: #63748B; border-top: 1px solid #E2E8F0; }
            ''')
    
            root = QtWidgets.QVBoxLayout(self.centralwidget)
            root.setContentsMargins(28, 23, 28, 20)
            root.setSpacing(18)
    
            # App header
            header = QtWidgets.QHBoxLayout()
            header.setSpacing(12)
            brand = self._text('P', 'brandMark', 23, True, '#FFFFFF')
            brand.setAlignment(QtCore.Qt.AlignCenter)
            brand.setFixedSize(52, 52)
            brand.setStyleSheet('background:#2563EB;color:white;border-radius:14px;')
            header.addWidget(brand)
            brand_titles = QtWidgets.QVBoxLayout()
            brand_titles.setSpacing(2)
            self.text_header = self._text('PARKING VISION', 'text_header', 20, True, '#142C4B')
            brand_titles.addWidget(self.text_header)
            brand_titles.addWidget(self._text('Hệ thống quản lý và nhận diện biển số xe', size=10, color='#697D95'))
            header.addLayout(brand_titles)
            header.addStretch(1)
            self.top_badge = self._text('●  NHẬN DIỆN AI', size=10, bold=True, color='#136B50')
            self.top_badge.setStyleSheet('background:#DDF8EB;color:#136B50;padding:10px 14px;border-radius:12px;')
            header.addWidget(self.top_badge)
            root.addLayout(header)
    
            body = QtWidgets.QHBoxLayout()
            body.setSpacing(18)
            root.addLayout(body, 1)
    
            # Left: live video + saved-entry photo
            left = QtWidgets.QVBoxLayout()
            left.setSpacing(18)
            body.addLayout(left, 7)
            video_card = self._card()
            video_layout = QtWidgets.QVBoxLayout(video_card)
            video_layout.setContentsMargins(20, 16, 20, 20)
            video_layout.setSpacing(12)
            video_head = QtWidgets.QHBoxLayout()
            video_head.addWidget(self._text('CAMERA NHẬN DIỆN', size=12, bold=True, color='#1C3554'))
            video_head.addStretch(1)
            video_head.addWidget(self._text('● LIVE / VIDEO', size=9, bold=True, color='#16805A'))
            video_layout.addLayout(video_head)
            self.label_main = self._text('Đang chờ khung hình...', 'label_main', 12, False, '#71839D')
            self.label_main.setAlignment(QtCore.Qt.AlignCenter)
            self.label_main.setMinimumSize(480, 300)
            self.label_main.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            video_layout.addWidget(self.label_main, 1)
            left.addWidget(video_card, 7)
    
            capture_card = self._card()
            capture_layout = QtWidgets.QVBoxLayout(capture_card)
            capture_layout.setContentsMargins(20, 15, 20, 16)
            capture_layout.setSpacing(10)
            self.label_6 = self._text('ẢNH XE KHI VÀO BÃI', 'label_6', 12, True, '#1C3554')
            capture_layout.addWidget(self.label_6)
            self.label_in = self._text('Chưa có ảnh xe', 'label_in', 11, False, '#71839D')
            self.label_in.setMinimumHeight(150)
            self.label_in.setAlignment(QtCore.Qt.AlignCenter)
            self.label_in.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            capture_layout.addWidget(self.label_in)
            left.addWidget(capture_card, 4)
    
            # Right: OCR and parking actions
            right = QtWidgets.QVBoxLayout()
            right.setSpacing(18)
            body.addLayout(right, 5)
            result_card = self._card()
            result_layout = QtWidgets.QVBoxLayout(result_card)
            result_layout.setContentsMargins(22, 18, 22, 20)
            result_layout.setSpacing(10)
            result_layout.addWidget(self._text('THÔNG TIN PHƯƠNG TIỆN', size=12, bold=True, color='#1C3554'))
            self.label = self._text('Ảnh biển số', 'label', 10, True, '#64758C')
            result_layout.addWidget(self.label)
            self.label_plate = self._text('Chưa có ảnh biển số', 'label_plate', 11, False, '#71839D')
            self.label_plate.setAlignment(QtCore.Qt.AlignCenter)
            self.label_plate.setMinimumHeight(95)
            result_layout.addWidget(self.label_plate)
    
            self.label_2 = self._text('BIỂN SỐ ĐỌC ĐƯỢC', 'label_2', 10, True, '#64758C')
            result_layout.addWidget(self.label_2)
            self.label_digits = self._value('label_digits', 56)
            self.label_digits.setFont(QtGui.QFont('Segoe UI', 17, QtGui.QFont.Bold))
            result_layout.addWidget(self.label_digits)
    
            self.label_5 = self._text('TRẠNG THÁI', 'label_5', 10, True, '#64758C')
            result_layout.addWidget(self.label_5)
            self.label_status = self._value('label_status', 50)
            result_layout.addWidget(self.label_status)
    
            row = QtWidgets.QHBoxLayout()
            row.setSpacing(12)
            time_col = QtWidgets.QVBoxLayout()
            time_col.setSpacing(8)
            self.label_3 = self._text('THỜI GIAN VÀO', 'label_3', 10, True, '#64758C')
            self.label_time = self._value('label_time', 50)
            time_col.addWidget(self.label_3)
            time_col.addWidget(self.label_time)
            price_col = QtWidgets.QVBoxLayout()
            price_col.setSpacing(8)
            self.label_4 = self._text('GIÁ VÉ', 'label_4', 10, True, '#64758C')
            self.label_price = self._value('label_price', 50)
            price_col.addWidget(self.label_4)
            price_col.addWidget(self.label_price)
            row.addLayout(time_col, 3)
            row.addLayout(price_col, 2)
            result_layout.addLayout(row)
            right.addWidget(result_card, 1)
    
            action_card = self._card()
            action_layout = QtWidgets.QVBoxLayout(action_card)
            action_layout.setContentsMargins(22, 17, 22, 19)
            action_layout.setSpacing(10)
            action_layout.addWidget(self._text('THAO TÁC BÃI XE', size=12, bold=True, color='#1C3554'))
            btn_row = QtWidgets.QHBoxLayout()
            btn_row.setSpacing(12)
            self.button_check_in = QtWidgets.QPushButton('↳  XÁC NHẬN VÀO')
            self.button_check_in.setObjectName('button_check_in')
            self.button_check_out = QtWidgets.QPushButton('↗  XÁC NHẬN RA')
            self.button_check_out.setObjectName('button_check_out')
            btn_row.addWidget(self.button_check_in)
            btn_row.addWidget(self.button_check_out)
            action_layout.addLayout(btn_row)
            action_layout.addWidget(self._text('Chỉ xác nhận khi biển số đã được nhận diện chính xác.', size=9, color='#7A8BA1'))
            right.addWidget(action_card)
    
            fee_card = self._card()
            fee_layout = QtWidgets.QVBoxLayout(fee_card)
            fee_layout.setContentsMargins(22, 14, 22, 14)
            fee_layout.setSpacing(6)
            fee_layout.addWidget(self._text('BẢNG GIÁ THAM KHẢO', size=11, bold=True, color='#1C3554'))
            self.textBrowser = QtWidgets.QTextBrowser()
            self.textBrowser.setObjectName('textBrowser')
            self.textBrowser.setFixedHeight(66)
            self.textBrowser.setHtml('<div style="font-family:Segoe UI;font-size:11pt;line-height:1.6;">'
                                     '<b>Ban ngày:</b> 3.000 VND &nbsp;&nbsp;&nbsp; '
                                     '<b>Ban đêm:</b> 5.000 VND</div>')
            fee_layout.addWidget(self.textBrowser)
            right.addWidget(fee_card)
    
            self.menubar = QtWidgets.QMenuBar(MainWindow)
            self.menubar.setVisible(False)
            MainWindow.setMenuBar(self.menubar)
            self.statusbar = QtWidgets.QStatusBar(MainWindow)
            self.statusbar.showMessage('Parking Vision  •  Sẵn sàng kiểm tra phương tiện')
            MainWindow.setStatusBar(self.statusbar)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)