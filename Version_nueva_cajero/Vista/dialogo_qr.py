#BITCAFE - VERSION 1.1 (Rediseño de Pago QR)
#By: Angel A. Higuera / Gemini Partner

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QGraphicsDropShadowEffect, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap, QImage
import qrcode
from qrcode.constants import ERROR_CORRECT_H
import io

class DialogoQR(QDialog):
    def __init__(self, url_pago, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pago por Transferencia")
        
        # Configuración de ventana (Sin bordes de Windows)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 620)

        # Contenedor Principal con estilo BitCafe
        self.container = QFrame(self)
        self.container.setGeometry(15, 15, 420, 590)
        self.container.setStyleSheet("""
            QFrame { 
                background-color: white; 
                border-radius: 25px; 
                border: 2px solid #F0F0F0; 
            }
        """)
        
        # Sombra elegante
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(30)
        sombra.setYOffset(10)
        sombra.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(sombra)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(10)

        # Header: Logo o Nombre del Sistema
        lbl_titulo = QLabel("BITCAFÉ")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #888; border: none; letter-spacing: 2px;") 
        layout.addWidget(lbl_titulo)

        lbl_subtitulo = QLabel("Escanea y Paga")
        lbl_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_subtitulo.setStyleSheet("font-size: 26px; font-weight: 900; color: #009EE3; border: none;") 
        layout.addWidget(lbl_subtitulo)

        layout.addSpacing(10)

        # QR Frame (Contenedor para resaltar el QR)
        self.lbl_qr = QLabel()
        self.lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qr.setFixedSize(280, 280)
        self.lbl_qr.setStyleSheet("border: 2px solid #009EE3; border-radius: 10px; background-color: #FAFAFA;")
        
        self.generar_qr(url_pago)
        layout.addWidget(self.lbl_qr, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Monto a pagar destacado
        lbl_total_text = QLabel("TOTAL A PAGAR")
        lbl_total_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_total_text.setStyleSheet("color: #999; font-size: 12px; font-weight: bold; border: none; margin-top: 15px;")
        layout.addWidget(lbl_total_text)

        lbl_monto = QLabel(f"${total:.2f}")
        lbl_monto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_monto.setStyleSheet("color: #222; font-size: 34px; font-weight: bold; border: none;")
        layout.addWidget(lbl_monto)

        layout.addStretch()

        # Botón de Confirmación Principal
        self.btn_confirmar = QPushButton("CONFIRMAR PAGO")
        self.btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirmar.setFixedHeight(60)
        self.btn_confirmar.setStyleSheet("""
            QPushButton { 
                background-color: #009EE3; 
                color: white; 
                font-weight: bold; 
                font-size: 18px; 
                border-radius: 15px; 
                border: none; 
            }
            QPushButton:hover { background-color: #007EB5; }
            QPushButton:pressed { background-color: #005F8A; }
        """)
        self.btn_confirmar.clicked.connect(self.accept) 
        layout.addWidget(self.btn_confirmar)

        # Botón Cancelar discreto
        btn_cancelar = QPushButton("Regresar")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setFixedHeight(30)
        btn_cancelar.setStyleSheet("""
            QPushButton { background-color: transparent; color: #BBB; font-weight: bold; font-size: 13px; border: none; }
            QPushButton:hover { color: #E74C3C; }
        """)
        btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(btn_cancelar)

    def generar_qr(self, url):
        if not url: return
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=ERROR_CORRECT_H,
                box_size=10,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img_pil = qr.make_image(fill_color="#000000", back_color="#FAFAFA").convert("RGB")
            buffer = io.BytesIO()
            img_pil.save(buffer, format="PNG")
            
            q_img = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(q_img)
            
            pixmap_escalado = pixmap.scaled(
                260, 260,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation 
            )
            self.lbl_qr.setPixmap(pixmap_escalado)
            
        except Exception as e:
            self.lbl_qr.setText("Error QR")
            print(f"Error: {e}")