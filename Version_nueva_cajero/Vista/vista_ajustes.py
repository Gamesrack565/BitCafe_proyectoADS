#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QCheckBox, QGraphicsDropShadowEffect,
                             QLineEdit, QInputDialog, QAbstractButton, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QBrush
from .ventana_base import VentanaBase


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor("#D22A00") if self.isChecked() else QColor("#CCCCCC")
        circle_color = Qt.GlobalColor.white

        rect = self.rect()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, rect.width(), rect.height(), 14, 14)

        painter.setBrush(QBrush(circle_color))
        radius = 11
        y_pos = 3
        x_pos = rect.width() - (radius * 2) - 3 if self.isChecked() else 3
        painter.drawEllipse(x_pos, y_pos, radius * 2, radius * 2)
        painter.end()


class VistaAjustes(VentanaBase):
    def __init__(self, logo_path=None):
        super().__init__(logo_path=logo_path, sidebar_color="#D22A00")
        self.set_titulo_contenido("Ajustes")

        # Layout Principal
        main_layout = QHBoxLayout()
        main_layout.setSpacing(300) 
        main_layout.setContentsMargins(40, 30, 40, 30)
        self.contenido_layout.addLayout(main_layout)


        col_izq = QVBoxLayout()
        col_izq.setAlignment(Qt.AlignmentFlag.AlignTop)
        col_izq.setSpacing(30)
        main_layout.addLayout(col_izq, stretch=0)

        # --- SECCIÓN 1: ESTADO DE LA TIENDA ---
        lbl_estado = QLabel("Estado de la Tienda")
        lbl_estado.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000;")
        col_izq.addWidget(lbl_estado)

        # Tarjeta Blanca
        card_estado = QFrame()
        card_estado.setFixedSize(380, 120)
        card_estado.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #EEE;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0,0,0, 40))
        shadow.setOffset(0, 5)
        card_estado.setGraphicsEffect(shadow)

        layout_card = QHBoxLayout(card_estado)
        layout_card.setContentsMargins(40, 0, 40, 0)
        
        lbl_aceptando = QLabel("Aceptando Pedidos")
        lbl_aceptando.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; border: none;")
        
        self.switch_tienda = ToggleSwitch()
        self.switch_tienda.setChecked(True)

        layout_card.addWidget(lbl_aceptando)
        layout_card.addStretch()
        layout_card.addWidget(self.switch_tienda)

        col_izq.addWidget(card_estado)
        
        # --- SECCIÓN 2: MI PERFIL Y SEGURIDAD ---
        col_izq.addSpacing(10)
        lbl_perfil = QLabel("Mi Perfil y Seguridad")
        lbl_perfil.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000;")
        col_izq.addWidget(lbl_perfil)
        
        input_style = """
            QLineEdit {
                background-color: #E0E0E0;
                border-radius: 18px;
                padding: 10px 20px;
                font-weight: bold;
                color: #333333;
                font-size: 14px;
                border: none;
            }
        """
        
        self.inp_pass_actual = QLineEdit()
        self.inp_pass_actual.setPlaceholderText("Contraseña Actual")
        self.inp_pass_actual.setStyleSheet(input_style)
        self.inp_pass_actual.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass_actual.setFixedHeight(45)
        
        self.inp_pass_nueva = QLineEdit()
        self.inp_pass_nueva.setPlaceholderText("Contraseña Nueva")
        self.inp_pass_nueva.setStyleSheet(input_style)
        self.inp_pass_nueva.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass_nueva.setFixedHeight(45)

        self.inp_pass_confirm = QLineEdit()
        self.inp_pass_confirm.setPlaceholderText("Confirmar Contraseña Nueva")
        self.inp_pass_confirm.setStyleSheet(input_style)
        self.inp_pass_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass_confirm.setFixedHeight(45)

        col_izq.addWidget(self.inp_pass_actual)
        col_izq.addWidget(self.inp_pass_nueva)
        col_izq.addWidget(self.inp_pass_confirm)

        col_izq.addSpacing(10)

        # Botón Guardar
        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setFixedHeight(45)
        self.btn_guardar.setFixedWidth(180)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00;
                color: white;
                font-weight: bold;
                border-radius: 12px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #B02200; }
        """)
        shadow_btn = QGraphicsDropShadowEffect()
        shadow_btn.setBlurRadius(15)
        shadow_btn.setColor(QColor(0,0,0, 50))
        shadow_btn.setOffset(0, 4)
        self.btn_guardar.setGraphicsEffect(shadow_btn)
        
        col_izq.addWidget(self.btn_guardar)
        col_izq.addStretch() 

        col_der = QVBoxLayout()
        col_der.setAlignment(Qt.AlignmentFlag.AlignTop)
        col_der.setSpacing(25)
        main_layout.addLayout(col_der, stretch=55)

        # --- SECCIÓN 3: REGLAS DE NEGOCIO ---
        lbl_reglas = QLabel("Reglas de Negocio")
        lbl_reglas.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000;")
        col_der.addWidget(lbl_reglas)

        lbl_costos = QLabel("Costos y Cargos")
        lbl_costos.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333;")
        col_der.addWidget(lbl_costos)

        self.btn_cargo = QPushButton("Cargo por servicio")
        self.btn_cargo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cargo.setFixedSize(200, 35)
        self.btn_cargo.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border-radius: 10px;
                font-weight: bold;
                color: #000000;
            }
            QPushButton:hover { background-color: #D0D0D0; }
        """)
        self.btn_cargo.clicked.connect(self.cambiar_monto_cargo)
        col_der.addWidget(self.btn_cargo)

        self.lbl_monto = QLabel("$2.00")
        self.lbl_monto.setStyleSheet("font-weight: bold; font-size: 18px; color: #000000; margin-top: 5px;")
        col_der.addWidget(self.lbl_monto)

        col_der.addSpacing(10)
        lbl_horarios = QLabel("Horarios de Operación")
        lbl_horarios.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333;")
        col_der.addWidget(lbl_horarios)

        # Grid de Horarios
        grid_horarios = QGridLayout()
        grid_horarios.setVerticalSpacing(15)
        # Reducimos el espaciado horizontal para que estén más pegados
        grid_horarios.setHorizontalSpacing(10) 

        dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
        self.checkboxes_dias = []

        for i, dia in enumerate(dias):
            lbl_dia = QLabel(dia)
            lbl_dia.setStyleSheet("font-weight: bold; font-size: 14px; color: #000000;")
            
            btn_inicio = QPushButton("Hora de inicio")
            btn_inicio.setFixedSize(120, 32)
            btn_inicio.setStyleSheet("""
                QPushButton { background-color: #E0E0E0; border-radius: 10px; font-weight: bold; color: #333333; border: 1px solid #CCC; }
            """)
            
            btn_fin = QPushButton("Fin")
            btn_fin.setFixedSize(60, 32)
            btn_fin.setStyleSheet("""
                QPushButton { background-color: #E0E0E0; border-radius: 10px; font-weight: bold; color: #333333; border: 1px solid #CCC; }
            """)
            
            chk_cerrado = QCheckBox("Cerrado")
            chk_cerrado.setCursor(Qt.CursorShape.PointingHandCursor)
            chk_cerrado.setStyleSheet(f"""
                QCheckBox {{ font-weight: bold; font-size: 13px; spacing: 8px; color: #000000; }}
                QCheckBox::indicator {{
                    width: 18px; height: 18px;
                    border-radius: 4px;
                    border: 1px solid #999;
                    background-color: white;
                }}
                QCheckBox::indicator:checked {{
                    background-color: #D22A00;
                    border: 1px solid #D22A00;
                    image: url(none);
                }}
            """)
            self.checkboxes_dias.append(chk_cerrado)

            grid_horarios.addWidget(lbl_dia, i, 0)
            grid_horarios.addWidget(btn_inicio, i, 1)
            grid_horarios.addWidget(btn_fin, i, 2)
            grid_horarios.addWidget(chk_cerrado, i, 3)

        # CORRECCIÓN CLAVE: Agregamos una columna elástica al final (índice 4)
        # Esto empujará las columnas 0, 1, 2, 3 hacia la izquierda.
        grid_horarios.setColumnStretch(4, 1)

        col_der.addLayout(grid_horarios)
        col_der.addStretch()

        self.btn_desactivar = QPushButton("Desactivar Aplicación")
        self.btn_desactivar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_desactivar.setFixedSize(200, 45)
        self.btn_desactivar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00; color: white;
                font-weight: bold; border-radius: 12px; font-size: 14px;
            }
            QPushButton:hover { background-color: #B02200; }
        """)
        shadow_des = QGraphicsDropShadowEffect()
        shadow_des.setBlurRadius(15)
        shadow_des.setColor(QColor(0,0,0, 50))
        shadow_des.setOffset(0, 4)
        self.btn_desactivar.setGraphicsEffect(shadow_des)

        col_der.addWidget(self.btn_desactivar, alignment=Qt.AlignmentFlag.AlignRight)

    def cambiar_monto_cargo(self):
        num, ok = QInputDialog.getDouble(self, "Modificar Cargo", 
                                         "Ingrese nuevo cargo por servicio:", 
                                         2.00, 0, 100, 2)
        if ok:
            self.lbl_monto.setText(f"${num:.2f}")