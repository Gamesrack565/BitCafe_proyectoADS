#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QGraphicsDropShadowEffect, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class DialogoExitoPago(QDialog):
    def __init__(self, cambio_float, metodo_pago, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setFixedSize(400, 320)

        # --- CONTENEDOR PRINCIPAL (TARJETA BLANCA) ---
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 380, 300)
        self.container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        # Sombra suave
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(10)

        # --- ICONO de palomota
        lbl_icon = QLabel("✓")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("color: #28a745; font-size: 60px; font-weight: bold; border: none;")
        layout.addWidget(lbl_icon)

        # --- TITULO ---
        lbl_titulo = QLabel("¡Cobro Exitoso!")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("color: #D22A00; font-size: 24px; font-weight: bold; border: none;")
        layout.addWidget(lbl_titulo)

        # --- MENSAJE DE CAMBIO ---
        mensaje_detalle = ""
        if metodo_pago == "efectivo":
            mensaje_detalle = f"Entregar cambio:\n${cambio_float:.2f}"
        else:
            mensaje_detalle = "Pago por transferencia\nregistrado correctamente."

        lbl_mensaje = QLabel(mensaje_detalle)
        lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_mensaje.setWordWrap(True)
        # Aquí usamos un gris oscuro para texto normal y grande para el dinero
        lbl_mensaje.setStyleSheet("color: #444; font-size: 18px; font-weight: 500; border: none; margin-top: 10px;")
        layout.addWidget(lbl_mensaje)

        layout.addStretch()

        # --- BOTÓN ACEPTAR ---
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aceptar.setFixedHeight(45)
        self.btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover { background-color: #B22400; }
        """)
        self.btn_aceptar.clicked.connect(self.accept)
        
        layout.addWidget(self.btn_aceptar)