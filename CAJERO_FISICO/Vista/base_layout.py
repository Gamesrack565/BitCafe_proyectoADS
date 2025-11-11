from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import os

class BaseLayout(QWidget):
    def __init__(self, titulo=""):
        super().__init__()

        # Layout principal (horizontal)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------- PANEL IZQUIERDO -------------
        panel_izq = QFrame()
        panel_izq.setStyleSheet("""
            QFrame {
                background-color: #D6301D;
                color: white;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 15px;
                padding: 10px 20px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
            QLabel {
                color: white;
            }
        """)
        panel_izq.setFixedWidth(220)

        vbox_menu = QVBoxLayout(panel_izq)
        vbox_menu.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---------- LOGO IMAGEN DE TAZA ----------
        ruta_imagen = os.path.join(os.path.dirname(__file__), "assets", "taza.png")
        if os.path.exists(ruta_imagen):
            logo_img = QLabel()
            pixmap = QPixmap(ruta_imagen)
            pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_img.setPixmap(pixmap)
            logo_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox_menu.addWidget(logo_img)
        else:
            print(f"⚠️ No se encontró la imagen en: {ruta_imagen}")

        # ---------- TÍTULO PRINCIPAL ----------
        logo_text = QLabel("BitCafé")
        logo_text.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_text.setStyleSheet("margin: 10px 0;")
        vbox_menu.addWidget(logo_text)

        # ---------- BOTONES DE MENÚ ----------
        botones = ["Dashboard", "Pedido Manual", "Pedidos", "Menú", "Ajustes", "Cerrar Sesión"]
        self.menu_botones = {}
        for texto in botones:
            btn = QPushButton(texto)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            vbox_menu.addWidget(btn)
            self.menu_botones[texto] = btn

        vbox_menu.addStretch()

        # ----------- CONTENIDO DERECHA -------------
        self.contenido = QFrame()
        self.contenido.setStyleSheet("background-color: white;")
        contenido_layout = QVBoxLayout(self.contenido)
        contenido_layout.setContentsMargins(20, 20, 20, 20)
        contenido_layout.setSpacing(10)

        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        contenido_layout.addWidget(titulo_label)

        self.body = QVBoxLayout()
        self.body.setAlignment(Qt.AlignmentFlag.AlignTop)
        contenido_layout.addLayout(self.body)

        # Agregar ambos paneles al layout principal
        main_layout.addWidget(panel_izq)
        main_layout.addWidget(self.contenido)
