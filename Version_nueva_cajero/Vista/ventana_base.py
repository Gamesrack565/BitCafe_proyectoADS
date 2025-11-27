#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QDateTime, QLocale 
from PyQt6.QtGui import QPixmap, QFont

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

        # --- Logo ---
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            lbl_logo.setPixmap(pixmap.scaled(84, 84, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_logo.setText("☕")
            lbl_logo.setStyleSheet("color: white; font-size: 40px;")

        layout_lateral.addWidget(lbl_logo)

        # --- Título App ---
        lbl_titulo = QLabel("BitCafe")
        # Le quitamos el margen inferior grande para pegar el reloj
        lbl_titulo.setStyleSheet("color: white; font-size: 20px; font-weight: 600; margin-bottom: 5px;") 
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_lateral.addWidget(lbl_titulo)

        # --- NUEVO: RELOJ Y FECHA ---
        self.lbl_reloj = QLabel("Cargando...")
        self.lbl_reloj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_reloj.setStyleSheet("""
            color: #FFD1C9;  
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        layout_lateral.addWidget(self.lbl_reloj)

        # Iniciamos el Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_reloj)
        self.timer.start(1000) # Actualizar cada 1000ms (1 segundo)
        self.actualizar_reloj() # Primera llamada inmediata

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

        # ==========================================
        #           AREA DE CONTENIDO
        # ==========================================
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

    # --- LÓGICA DEL RELOJ ---
    def actualizar_reloj(self):
        # Obtenemos fecha actual
        ahora = QDateTime.currentDateTime()
        
        # Formato: "Vie 21 Nov | 10:30 AM"
        # Usamos QLocale Spanish para asegurar que salga "Vie" y no "Fri"
        locale = QLocale(QLocale.Language.Spanish, QLocale.Country.Mexico)
        fecha = locale.toString(ahora, "ddd d MMM") 
        hora = locale.toString(ahora, "hh:mm AP")
        
        texto_final = f"{fecha} | {hora}"
        self.lbl_reloj.setText(texto_final.upper()) # UPPER para que se vea: VIE 21 NOV