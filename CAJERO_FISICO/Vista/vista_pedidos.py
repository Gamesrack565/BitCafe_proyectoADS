# vista_pedidos.py
from PyQt6.QtWidgets import QLabel, QListWidget, QPushButton
import requests
from .base_layout import BaseLayout

class VentanaPedidos(BaseLayout):
    def __init__(self):
        super().__init__("Pedidos")

        self.lista_pedidos = QListWidget()
        self.body.addWidget(self.lista_pedidos)

        self.btn_actualizar = QPushButton("🔄 Actualizar pedidos")
        self.body.addWidget(self.btn_actualizar)

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
