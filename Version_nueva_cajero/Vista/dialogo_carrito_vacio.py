#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QGraphicsDropShadowEffect, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QCursor

class DialogoAviso(QDialog):
    def __init__(self, mensaje, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 200) # Tamaño compacto

        # --- CONTENEDOR PRINCIPAL ---
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 380, 180)
        self.container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(25, 20, 25, 25)

        # --- BOTÓN CERRAR (X) ---
        # Layout superior para la X
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.setStyleSheet("""
            QPushButton {
                color: #D22A00;
                font-weight: bold;
                border: none;
                background: transparent;
                font-size: 16px;
            }
            QPushButton:hover { color: #FF0000; }
        """)
        btn_close.clicked.connect(self.reject)
        top_layout.addWidget(btn_close)
        
        layout.addLayout(top_layout)

        # --- MENSAJE ---
        self.lbl_mensaje = QLabel(mensaje)
        self.lbl_mensaje.setWordWrap(True)
        # Estilo idéntico a tu imagen: Rojo y Negrita
        self.lbl_mensaje.setStyleSheet("""
            color: #D22A00; 
            font-size: 20px; 
            font-weight: bold; 
            border: none;
        """)
        layout.addWidget(self.lbl_mensaje)
        
        layout.addStretch()

        # --- BOTÓN ACEPTAR ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch() # Empuja el botón a la derecha
        
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_aceptar.setFixedSize(100, 38)
        self.btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00;
                color: white;
                font-weight: 500;
                font-size: 14px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background-color: #B22400; }
        """)
        self.btn_aceptar.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_aceptar)
        layout.addLayout(btn_layout)