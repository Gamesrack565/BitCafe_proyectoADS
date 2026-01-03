# BITCAFE
# VERSION 1.1 - Soporte para Ejecutable (.exe)
# By: Angel A. Higuera

import os
import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QDateTime, QLocale 
from PyQt6.QtGui import QPixmap, QFont

def resource_path(relative_path):
    """ Obtiene la ruta absoluta para recursos, compatible con PyInstaller """
    if not relative_path:
        return None
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class VentanaBase(QWidget):
    def __init__(self, logo_path=None, sidebar_color="#D22A00"):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión - BitCafe")
        self.resize(1200, 820)
        self.setStyleSheet("background-color: #FFFFFF;")

        # --- Layout Principal ---
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.panel_lateral = QFrame()
        self.panel_lateral.setFixedWidth(220)
        self.panel_lateral.setStyleSheet(f"""
            QFrame {{
                background-color: {sidebar_color};
            }}
            QPushButton {{
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
                text-align: left;
                padding: 14px 24px;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.08);
                font-weight: 600;
            }}
        """)

        layout_lateral = QVBoxLayout(self.panel_lateral)
        layout_lateral.setContentsMargins(0, 28, 0, 28)
        layout_lateral.setSpacing(6)

        # --- Logo (CON RESOURCE_PATH) ---
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Aplicamos resource_path a la ruta que recibimos
        ruta_final_logo = resource_path(logo_path)

        if ruta_final_logo and os.path.exists(ruta_final_logo):
            pixmap = QPixmap(ruta_final_logo)
            lbl_logo.setPixmap(pixmap.scaled(84, 84, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_logo.setText("☕")
            lbl_logo.setStyleSheet("color: white; font-size: 40px; background: transparent;")

        layout_lateral.addWidget(lbl_logo)

        # --- Título App ---
        lbl_titulo = QLabel("BitCafe")
        lbl_titulo.setStyleSheet("color: white; font-size: 20px; font-weight: 600; margin-bottom: 5px; background: transparent;") 
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_lateral.addWidget(lbl_titulo)

        # --- Reloj y Fecha ---
        self.lbl_reloj = QLabel("Cargando...")
        self.lbl_reloj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_reloj.setStyleSheet("""
            color: #FFD1C9;  
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 20px;
            background: transparent;
        """)
        layout_lateral.addWidget(self.lbl_reloj)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_reloj)
        self.timer.start(1000)
        self.actualizar_reloj()

        # --- Botones del Menú ---
        self.botones_menu = {}
        opciones = ["Dashboard", "Pedido Manual", "Pedidos", "Menú", "Ajustes", "Cerrar Sesión"]

        for opcion in opciones:
            btn = QPushButton(opcion)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout_lateral.addWidget(btn)
            self.botones_menu[opcion] = btn
            
            if opcion == "Ajustes":
                layout_lateral.addStretch()

        self.main_layout.addWidget(self.panel_lateral)

        # Area de Contenido
        self.contenido_frame = QFrame()
        self.contenido_frame.setStyleSheet("background-color: #FFFFFF;")
        self.contenido_layout = QVBoxLayout(self.contenido_frame)
        self.contenido_layout.setContentsMargins(36, 22, 36, 36)
        self.contenido_layout.setSpacing(16)

        self.main_layout.addWidget(self.contenido_frame)

    def set_titulo_contenido(self, titulo):
        lbl = QLabel(titulo)
        lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        lbl.setStyleSheet("color: black; border-bottom: 1px solid #E6E6E6; padding-bottom: 18px;")
        self.contenido_layout.addWidget(lbl)

    def actualizar_reloj(self):
        ahora = QDateTime.currentDateTime()
        locale = QLocale(QLocale.Language.Spanish, QLocale.Country.Mexico)
        fecha = locale.toString(ahora, "ddd d MMM") 
        hora = locale.toString(ahora, "hh:mm AP")
        texto_final = f"{fecha} | {hora}"
        self.lbl_reloj.setText(texto_final.upper())