from PyQt6.QtWidgets import QApplication, QStackedWidget, QPushButton
from Vista.vista_pago import VentanaPago
from Vista.vista_pedidos import VentanaPedidos
from Vista.vista_principal import VentanaPrincipal
import sys

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.principal_view = VentanaPrincipal()
        self.pago_view = VentanaPago()
        self.pedidos_view = VentanaPedidos()

        self.addWidget(self.principal_view)
        self.addWidget(self.pago_view)
        self.addWidget(self.pedidos_view)

        # Navegación entre pantallas
        self.principal_view.body.itemAt(1).widget().clicked.connect(self.ir_a_pedidos)
        self.principal_view.body.itemAt(2).widget().clicked.connect(self.ir_a_pago)
        self.pedidos_view.btn_actualizar.clicked.connect(self.ir_a_principal)
        self.pago_view.btn_pagar.clicked.connect(self.ir_a_principal)

        self.setFixedSize(900, 600)
        self.setWindowTitle("BitCafé - Interfaz Cajero")
        self.show()

    def ir_a_principal(self): self.setCurrentIndex(0)
    def ir_a_pago(self): self.setCurrentIndex(1)
    def ir_a_pedidos(self): self.setCurrentIndex(2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainApp()
    sys.exit(app.exec())
