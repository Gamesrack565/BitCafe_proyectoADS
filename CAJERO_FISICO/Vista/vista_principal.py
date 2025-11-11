# vista_principal.py
from PyQt6.QtWidgets import QLabel, QPushButton
from .base_layout import BaseLayout

class VentanaPrincipal(BaseLayout):
    def __init__(self):
        super().__init__("Dashboard")

        label = QLabel("Bienvenido al sistema de Bit Café ☕")
        label.setStyleSheet("font-size: 16px; margin-top: 30px;")
        self.body.addWidget(label)

        btn_pedidos = QPushButton("📦 Ver pedidos entrantes")
        btn_pedidos.setObjectName("btn_pedidos")
        btn_pagos = QPushButton("💳 Ir a pantalla de pago")
        btn_pagos.setObjectName("btn_pagos")

        self.body.addWidget(btn_pedidos)
        self.body.addWidget(btn_pagos)
