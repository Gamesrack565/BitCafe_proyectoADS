#BITCAFE
#VERSION 0.1
#By: Angel A. Higuera

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
        self.setWindowTitle("Escanea para pagar")
        
        # --- DEBUG ---
        print(f"DEBUG QR: Generando código para: {url_pago}")

        # Configuración de ventana
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(420, 600)

        # Contenedor
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 400, 580)
        self.container.setStyleSheet("""
            QFrame { background-color: white; border-radius: 15px; border: 1px solid #E0E0E0; }
        """)
        
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(25)
        sombra.setYOffset(5)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.container.setGraphicsEffect(sombra)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Títulos
        lbl_titulo = QLabel("Mercado Pago")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: 900; color: #009EE3; border: none;") 
        layout.addWidget(lbl_titulo)

        lbl_instruccion = QLabel("Escanea para pagar:")
        lbl_instruccion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_instruccion.setStyleSheet("color: #666; font-size: 14px; border: none;")
        layout.addWidget(lbl_instruccion)
        
        lbl_monto = QLabel(f"${total:.2f}")
        lbl_monto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_monto.setStyleSheet("color: #333; font-size: 28px; font-weight: bold; border: none; margin-bottom: 10px;")
        layout.addWidget(lbl_monto)

        # --- LABEL DEL QR ---
        self.lbl_qr = QLabel()
        self.lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qr.setStyleSheet("border: none; background-color: white;") 
        self.lbl_qr.setFixedSize(280, 280)
        
        self.generar_qr(url_pago)
        
        # CORRECCIÓN DE CENTRADO: Añadimos alignment=AlignCenter
        layout.addWidget(self.lbl_qr, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()

        # Botones
        self.btn_confirmar = QPushButton("Ya se realizó el pago")
        self.btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirmar.setFixedHeight(50)
        self.btn_confirmar.setStyleSheet("""
            QPushButton { background-color: #009EE3; color: white; font-weight: bold; font-size: 16px; border-radius: 10px; border: none; }
            QPushButton:hover { background-color: #007EB5; }
        """)
        self.btn_confirmar.clicked.connect(self.accept) 
        layout.addWidget(self.btn_confirmar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setFixedHeight(40)
        btn_cancelar.setStyleSheet("""
            QPushButton { background-color: transparent; color: #888; font-weight: bold; font-size: 14px; border: none; }
            QPushButton:hover { color: #555; text-decoration: underline; }
        """)
        btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(btn_cancelar)

    def generar_qr(self, url):
        """
        Genera un QR de ALTA CALIDAD optimizado para lectura en pantallas.
        """
        if not url: return

        try:
            # 1. Configuración ROBUSTA del QR
            qr = qrcode.QRCode(
                version=None,
                error_correction=ERROR_CORRECT_H,
                box_size=10,
                border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # 2. Convertir a RGB
            img_pil = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            # 3. Guardar en memoria
            buffer = io.BytesIO()
            img_pil.save(buffer, format="PNG")
            buffer.seek(0)

            # 4. Cargar en Qt
            q_img = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(q_img)
            
            # 5. ESCALADO PIXEL-PERFECT
            pixmap_escalado = pixmap.scaled(
                280, 280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation 
            )
            
            self.lbl_qr.setPixmap(pixmap_escalado)
            
        except Exception as e:
            print(f"Error generando QR visual: {e}")
            self.lbl_qr.setText("Error al cargar QR")