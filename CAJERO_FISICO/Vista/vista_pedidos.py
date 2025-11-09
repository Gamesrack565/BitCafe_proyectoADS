# vista_pedidos.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton
import requests

class VentanaPedidos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pedidos Entrantes - BitCafé")
        self.setGeometry(200, 200, 500, 400)

        layout = QVBoxLayout()

        self.titulo = QLabel("📦 Pedidos nuevos")
        self.titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.titulo)

        self.lista_pedidos = QListWidget()
        layout.addWidget(self.lista_pedidos)

        # Cambiado a atributo de clase
        self.btn_actualizar = QPushButton("🔄 Actualizar pedidos")
        self.btn_actualizar.clicked.connect(self.cargar_pedidos)
        layout.addWidget(self.btn_actualizar)

        self.setLayout(layout)
        self.cargar_pedidos()

    def cargar_pedidos(self):
        self.lista_pedidos.clear()
        try:
            response = requests.get("http://127.0.0.1:8000/pedidos")
            if response.status_code == 200:
                pedidos = response.json()
                for pedido in pedidos:
                    texto = f"#{pedido['id']} - {pedido['estado']} - Total: ${pedido['total']}"
                    self.lista_pedidos.addItem(texto)
            else:
                self.lista_pedidos.addItem("Error al obtener pedidos.")
        except Exception as e:
            self.lista_pedidos.addItem(f"Error de conexión: {e}")
