# vista_pago.py
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton
from .base_layout import BaseLayout
import requests, webbrowser

class VentanaPago(BaseLayout):
    def __init__(self):
        super().__init__("Pantalla de Pago")

        label = QLabel("💳 Pago con Mercado Pago")
        label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        self.body.addWidget(label)

        self.input_total = QLineEdit()
        self.input_total.setPlaceholderText("Ingrese el monto total")
        self.body.addWidget(self.input_total)

        self.btn_pagar = QPushButton("Pagar con Mercado Pago")
        self.body.addWidget(self.btn_pagar)

    def realizar_pago(self):
        total = self.input_total.text()
        if not total:
            return
        try:
            response = requests.post("http://127.0.0.1:8000/pagos/crear", json={"total": float(total)})
            if response.status_code == 200:
                data = response.json()
                webbrowser.open(data["init_point"])
        except Exception as e:
            print("Error de conexión:", e)
