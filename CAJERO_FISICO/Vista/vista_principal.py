# vista_principal.py
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BitCafé - Ventana Principal")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("☕ Bienvenido al Sistema de BitCafé")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        layout.addWidget(titulo)

        # Botón para ver pedidos entrantes
        btn_pedidos = QPushButton("📦 Ver pedidos entrantes")
        btn_pedidos.setObjectName("btn_pedidos")
        layout.addWidget(btn_pedidos)

        # Botón para ir a pantalla de pago
        btn_pagos = QPushButton("💳 Ir a pantalla de pago")
        btn_pagos.setObjectName("btn_pagos")
        layout.addWidget(btn_pagos)

        self.setLayout(layout)
