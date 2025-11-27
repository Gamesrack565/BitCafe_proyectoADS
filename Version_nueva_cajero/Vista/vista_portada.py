#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QColor

class VistaPortada(QWidget):
    # Señales
    solicitar_conexion = pyqtSignal()
    entrar_sistema = pyqtSignal()

    def __init__(self, logo_path=None):
        super().__init__()
        
        # Configuración de fondo
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #FFEFEA;") # Fondo Crema

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20) # Espacio entre elementos

        # --- 1. LOGO ---
        lbl_logo = QLabel(self)
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("background-color: transparent;") 
        
        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            lbl_logo.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_logo.setText("☕")
            lbl_logo.setStyleSheet("font-size: 100px; background-color: transparent;")

        layout.addWidget(lbl_logo, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- 2. TEXTOS (Título) ---
        lbl_titulo = QLabel("Bit Cafe")
        lbl_titulo.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #D22A00; margin-top: 10px; background-color: transparent;") 
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        lbl_subtitulo = QLabel("Bienvenido")
        lbl_subtitulo.setFont(QFont("Arial", 20))
        lbl_subtitulo.setStyleSheet("color: #D22A00; margin-bottom: 20px; background-color: transparent;")
        lbl_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_subtitulo)

        # --- 3. BOTÓN "ENTRAR" ---
        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.setFixedSize(300, 50)
        self.btn_entrar.setEnabled(False) # Deshabilitado al inicio mientras carga
        
        self.btn_entrar.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #D22A00;
                font-weight: bold;
                font-size: 18px;
                border: 2px solid #D22A00;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #D22A00;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                color: #FFCDD2; /* Rojo muy pálido */
                border: 2px solid #FFCDD2;
                background-color: #FFFFFF;
            }
        """)
        self.btn_entrar.clicked.connect(self.manejar_clic)
        
        # Sombra suave para el botón
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(210, 42, 0, 50)) # Sombra rojiza
        shadow.setOffset(0, 4)
        self.btn_entrar.setGraphicsEffect(shadow)

        layout.addWidget(self.btn_entrar, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- 4. ETIQUETA DE ESTADO (Abajo del botón) ---
        self.lbl_estado = QLabel("Iniciando sistema...")
        self.lbl_estado.setStyleSheet("color: #E57373; font-size: 13px; background-color: transparent; font-style: italic;")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_estado)

        # --- Auto-Inicio ---
        QTimer.singleShot(1000, lambda: self.solicitar_conexion.emit())

    def manejar_clic(self):
        texto = self.btn_entrar.text()
        if texto == "Entrar":
            self.entrar_sistema.emit()
        else:
            # Caso de Reintentar
            self.lbl_estado.setText("Reconectando...")
            self.btn_entrar.setEnabled(False)
            self.solicitar_conexion.emit()

    # --- MÉTODOS PARA EL CONTROLADOR (MAIN) ---
    
    def mostrar_mensaje(self, texto):
        """Actualiza solo el texto chiquito de abajo"""
        self.lbl_estado.setText(texto)

    def habilitar_entrada(self):
        """Login exitoso: Activa el botón y avisa"""
        self.lbl_estado.setText("Sistema conectado correctamente.")
        self.lbl_estado.setStyleSheet("color: #2E7D32; font-size: 13px; background-color: transparent; font-weight: bold;") # Verde
        
        self.btn_entrar.setText("Entrar")
        self.btn_entrar.setEnabled(True)
        self.btn_entrar.setFocus()

    def mostrar_error(self, texto_error):
        """Fallo: Muestra error abajo y cambia botón a Reintentar"""
        self.lbl_estado.setText(f"Error: {texto_error}")
        self.lbl_estado.setStyleSheet("color: #D32F2F; font-size: 13px; background-color: transparent; font-weight: bold;") # Rojo fuerte
        
        self.btn_entrar.setText("Reintentar Conexión")
        self.btn_entrar.setEnabled(True)