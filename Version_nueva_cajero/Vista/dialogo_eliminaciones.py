#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

class DialogoBase(QDialog):
    """Clase base para compartir el estilo de 'tarjeta flotante'"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(420, 220)

        # Layout principal (transparente)
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(10, 10, 10, 10)

        # Tarjeta Blanca (El fondo real)
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        # Sombra 
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.frame.setGraphicsEffect(shadow)

        self.layout_main.addWidget(self.frame)
        
        # Layout interno de la tarjeta
        self.layout_card = QVBoxLayout(self.frame)
        self.layout_card.setContentsMargins(25, 20, 25, 25)
        self.layout_card.setSpacing(15)

        # Botón Cerrar (X) en la esquina superior derecha
        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.setStyleSheet("""
            QPushButton { color: #D22A00; border: none; font-size: 18px; font-weight: bold; }
            QPushButton:hover { color: #B02200; background-color: #FFF0F0; border-radius: 15px; }
        """)
        
        # Header layout para la X
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        header_layout.addWidget(self.btn_close)
        self.layout_card.addLayout(header_layout)


class DialogoConfirmarEliminar(DialogoBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Texto Pregunta
        lbl_msg = QLabel("¿Está seguro que desea borrar el\nproducto?")
        lbl_msg.setWordWrap(True)
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lbl_msg.setStyleSheet("color: #D22A00; font-size: 20px; font-weight: bold;")
        self.layout_card.addWidget(lbl_msg)

        self.layout_card.addStretch()

        # Botones
        layout_btns = QHBoxLayout()
        layout_btns.setSpacing(15)
        layout_btns.setAlignment(Qt.AlignmentFlag.AlignRight)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setFixedSize(100, 38)
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #D22A00;
                border: 2px solid #D22A00;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #FFF5F0; }
        """)

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aceptar.setFixedSize(100, 38)
        btn_aceptar.clicked.connect(self.accept)
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #B02200; }
        """)

        layout_btns.addWidget(btn_cancelar)
        layout_btns.addWidget(btn_aceptar)
        self.layout_card.addLayout(layout_btns)


class DialogoExitoEliminar(DialogoBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Texto Éxito
        lbl_msg = QLabel("Se ha eliminado el producto con\néxito.")
        lbl_msg.setWordWrap(True)
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lbl_msg.setStyleSheet("color: #D22A00; font-size: 20px; font-weight: bold;")
        self.layout_card.addWidget(lbl_msg)

        self.layout_card.addStretch()

        # Botón Solo Aceptar
        layout_btns = QHBoxLayout()
        layout_btns.setAlignment(Qt.AlignmentFlag.AlignRight)

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aceptar.setFixedSize(100, 38)
        btn_aceptar.clicked.connect(self.accept)
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #B02200; }
        """)

        layout_btns.addWidget(btn_aceptar)
        self.layout_card.addLayout(layout_btns)