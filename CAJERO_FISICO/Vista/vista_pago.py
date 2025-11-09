# vista_pago.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import requests, webbrowser

class VentanaPago(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pantalla de Pago - BitCafé")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("💳 Pago con Mercado Pago")
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.label)

        self.input_total = QLineEdit()
        self.input_total.setPlaceholderText("Ingrese el monto total")
        layout.addWidget(self.input_total)

        # Cambiado a atributo de clase
        self.btn_pagar = QPushButton("Pagar con Mercado Pago")
        self.btn_pagar.clicked.connect(self.realizar_pago)
        layout.addWidget(self.btn_pagar)

        self.setLayout(layout)

    def realizar_pago(self):
        total = self.input_total.text()
        if not total:
            self.label.setText("⚠️ Ingrese un monto válido.")
            return

        try:
            response = requests.post("http://127.0.0.1:8000/pagos/crear", json={"total": float(total)})
            if response.status_code == 200:
                data = response.json()
                webbrowser.open(data["init_point"])
                self.label.setText("✅ Redirigiendo a Mercado Pago...")
            else:
                self.label.setText("❌ Error al generar pago.")
        except Exception as e:
            self.label.setText(f"Error de conexión: {e}")
