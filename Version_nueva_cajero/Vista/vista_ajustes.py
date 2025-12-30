# BITCAFE - VERSION 1.9 (DISEÑO CENTRADO PROFESIONAL - CÓDIGO TOTAL)
# By: Angel A. Higuera & Gemini Partner

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGraphicsDropShadowEffect,
                             QAbstractButton, QGridLayout, QScrollArea, QInputDialog, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QBrush
from .ventana_base import VentanaBase

class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(60, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg_color = QColor("#D22A00") if self.isChecked() else QColor("#CCCCCC")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        x_pos = self.width() - 28 if self.isChecked() else 4
        painter.drawEllipse(x_pos, 4, 24, 24)
        painter.end()

class VistaAjustes(VentanaBase):
    def __init__(self, logo_path=None):
        super().__init__(logo_path=logo_path, sidebar_color="#D22A00")
        self.set_titulo_contenido("Configuración del Sistema")

        # --- CONTENEDOR CON SCROLL PARA ASEGURAR VISIBILIDAD TOTAL ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        container_scroll = QWidget()
        container_scroll.setStyleSheet("background: transparent;")
        self.layout_principal = QVBoxLayout(container_scroll)
        self.layout_principal.setContentsMargins(40, 20, 40, 40)
        self.layout_principal.setSpacing(30)
        self.layout_principal.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        scroll.setWidget(container_scroll)
        self.contenido_layout.addWidget(scroll)

        # --- BLOQUE 1: ESTADO DE LA TIENDA (CARD CENTRADA) ---
        self.card_estado = QFrame()
        self.card_estado.setFixedSize(550, 110)
        self.card_estado.setStyleSheet("background-color: white; border-radius: 20px; border: 1px solid #EEE;")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30); shadow.setColor(QColor(0,0,0, 35)); shadow.setOffset(0, 10)
        self.card_estado.setGraphicsEffect(shadow)

        layout_card = QHBoxLayout(self.card_estado)
        layout_card.setContentsMargins(40, 0, 40, 0)
        
        lbl_aceptando = QLabel("¿Aceptando Pedidos?")
        lbl_aceptando.setStyleSheet("font-weight: bold; font-size: 20px; color: #333; border: none;")
        
        self.switch_tienda = ToggleSwitch()
        layout_card.addWidget(lbl_aceptando)
        layout_card.addStretch()
        layout_card.addWidget(self.switch_tienda)

        self.layout_principal.addWidget(self.card_estado, alignment=Qt.AlignmentFlag.AlignHCenter)

        # --- BLOQUE 2: HORARIOS DE OPERACIÓN ---
        lbl_tit_horarios = QLabel("Horarios de Operación")
        lbl_tit_horarios.setStyleSheet("font-weight: bold; font-size: 18px; color: #444;")
        self.layout_principal.addWidget(lbl_tit_horarios, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.frame_horarios = QFrame()
        self.grid_horarios = QGridLayout(self.frame_horarios)
        self.grid_horarios.setVerticalSpacing(15)
        self.grid_horarios.setHorizontalSpacing(30)

        self.nombres_dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
        self.botones_inicio = []
        self.botones_fin = []

        for i, dia in enumerate(self.nombres_dias):
            lbl_dia = QLabel(dia)
            lbl_dia.setStyleSheet("font-weight: bold; font-size: 15px; color: #222;")
            
            btn_ini = self.crear_boton_tiempo("09:00")
            btn_fin = self.crear_boton_tiempo("18:00")
            
            self.botones_inicio.append(btn_ini)
            self.botones_fin.append(btn_fin)

            self.grid_horarios.addWidget(lbl_dia, i, 0)
            self.grid_horarios.addWidget(btn_ini, i, 1)
            self.grid_horarios.addWidget(QLabel("-"), i, 2)
            self.grid_horarios.addWidget(btn_fin, i, 3)

        self.layout_principal.addWidget(self.frame_horarios, alignment=Qt.AlignmentFlag.AlignHCenter)

        # --- BLOQUE 3: GESTIÓN DE PERFIL (CAMPOS OCULTOS PARA EL CONTROLADOR) ---
        # El controlador busca inp_pass_nueva e inp_pass_confirm para no fallar
        self.inp_pass_actual = QLineEdit(); self.inp_pass_actual.setPlaceholderText("Pass actual"); self.inp_pass_actual.hide()
        self.inp_pass_nueva = QLineEdit(); self.inp_pass_nueva.setPlaceholderText("Nueva pass"); self.inp_pass_nueva.hide()
        self.inp_pass_confirm = QLineEdit(); self.inp_pass_confirm.setPlaceholderText("Confirmar pass"); self.inp_pass_confirm.hide()
        
        self.layout_principal.addWidget(self.inp_pass_actual)
        self.layout_principal.addWidget(self.inp_pass_nueva)
        self.layout_principal.addWidget(self.inp_pass_confirm)

        # --- BLOQUE 4: BOTONES DE ACCIÓN (GARANTIZADOS ABAJO) ---
        container_btns = QFrame()
        layout_btns = QHBoxLayout(container_btns)
        layout_btns.setSpacing(20)
        layout_btns.setContentsMargins(0, 20, 0, 10)

        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.setFixedSize(220, 50)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00; color: white; font-weight: bold;
                border-radius: 15px; font-size: 15px;
            }
            QPushButton:hover { background-color: #B02200; }
        """)

        self.btn_desactivar = QPushButton("Cerrar Sesión")
        self.btn_desactivar.setFixedSize(140, 50)
        self.btn_desactivar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_desactivar.setStyleSheet("""
            QPushButton {
                background-color: #666; color: white; font-weight: bold;
                border-radius: 15px; font-size: 14px;
            }
            QPushButton:hover { background-color: #444; }
        """)

        layout_btns.addWidget(self.btn_guardar)
        layout_btns.addWidget(self.btn_desactivar)
        
        self.layout_principal.addWidget(container_btns, alignment=Qt.AlignmentFlag.AlignHCenter)

    def crear_boton_tiempo(self, texto):
        btn = QPushButton(texto)
        btn.setFixedSize(120, 40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #F8F8F8; border-radius: 10px;
                border: 1px solid #DDD; font-weight: bold; color: #333;
            }
            QPushButton:hover { border: 1px solid #D22A00; color: #D22A00; }
        """)
        return btn

    def cargar_datos_iniciales(self, api_client):
        """Sincronización inicial requerida por el flujo de la app."""
        try:
            horarios = api_client.obtener_horarios()
            estado = api_client.obtener_estado_tienda()
            
            self.switch_tienda.blockSignals(True)
            self.switch_tienda.setChecked(estado)
            self.switch_tienda.blockSignals(False)
            
            for i, dia in enumerate(self.nombres_dias):
                if dia in horarios:
                    config = horarios[dia]
                    self.botones_inicio[i].setText(config.get("inicio", "09:00"))
                    self.botones_fin[i].setText(config.get("fin", "18:00"))
        except Exception as e:
            print(f"Error sincronizando datos: {e}")

    def cambiar_monto_cargo(self):
        """Método de soporte para el controlador."""
        num, ok = QInputDialog.getDouble(self, "Modificar Cargo", "Nuevo monto:", 2.00, 0, 100, 2)
        return num if ok else None