# BITCAFE - Actividad C: Previsualización de Ticket
# By: Angel A. Higuera & Gemini Partner

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QFrame, QTextEdit, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

class DialogoTicket(QDialog):
    def __init__(self, datos_ticket, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Previsualización de Ticket")
        self.setFixedSize(350, 600)
        self.setStyleSheet("background-color: #F8F9FA;")

        layout = QVBoxLayout(self)

        # Contenedor del "Papel" del ticket
        self.ticket_frame = QFrame()
        self.ticket_frame.setStyleSheet("""
            QFrame { 
                background-color: white; 
                border: 1px solid #DDD;
                border-radius: 5px;
            }
        """)
        ticket_layout = QVBoxLayout(self.ticket_frame)

        # Texto del Ticket (Simulado fuente térmica)
        self.txt_ticket = QTextEdit()
        self.txt_ticket.setReadOnly(True)
        self.txt_ticket.setStyleSheet("""
            border: none; 
            font-family: 'Courier New', monospace; 
            font-size: 13px;
        """)
        
        # Formatear el contenido del ticket
        contenido = self.generar_formato_ticket(datos_ticket)
        self.txt_ticket.setPlainText(contenido)
        
        ticket_layout.addWidget(self.txt_ticket)
        layout.addWidget(self.ticket_frame)

        # Botones de Acción
        btn_layout = QHBoxLayout()
        
        self.btn_imprimir = QPushButton("IMPRIMIR")
        self.btn_imprimir.setFixedHeight(45)
        self.btn_imprimir.setStyleSheet("""
            QPushButton { background-color: #E74C3C; color: white; font-weight: bold; border-radius: 10px; }
            QPushButton:hover { background-color: #C0392B; }
        """)
        self.btn_imprimir.clicked.connect(self.accept)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.setFixedHeight(45)
        self.btn_cerrar.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_cerrar)
        btn_layout.addWidget(self.btn_imprimir)
        layout.addLayout(btn_layout)

    def generar_formato_ticket(self, datos):
        """Versión BITCAFE - Detección Forzada de Transferencia"""
        # 1. Extraer datos
        folio = str(datos.get("num_orden") or datos.get("id_pedido") or "N/A")
        total = datos.get("total_pedido") or datos.get("total") or 0.0
        items = datos.get("items", [])
        cliente_id = datos.get("id_usuario") or "1"
        
        # 2. LÓGICA DETECTIVE DE PAGO (Aquí está la magia)
        # Obtenemos lo que diga el sistema originalmente
        metodo_raw = str(datos.get("metodo_pago", "")).upper()
        
        # FUERZA BRUTA: Si el folio empieza con "BITCAFE-", o si existe init_point,
        # o si el folio tiene más de 10 caracteres (típico de UUID), es Transferencia.
        if any(x in metodo_raw for x in ["TRANS", "QR", "MP", "STRIPE", "PAGADO"]):
            metodo_pago = "TRANSFERENCIA"
        elif len(folio) > 10 or datos.get("init_point") or "BITCAFE-" in folio:
            # Si el pedido ya tiene folio generado por la API de Mercado Pago
            metodo_pago = "TRANSFERENCIA"
        elif "EFECTIVO" in metodo_raw:
            metodo_pago = "EFECTIVO"
        else:
            # Por seguridad, si no estamos seguros, revisamos el total
            # Si hay datos de mercado pago en el diccionario 'datos', forzamos
            metodo_pago = "TRANSFERENCIA" if "preference_id" in datos else "EFECTIVO"

        # 3. Fecha
        fecha_raw = datos.get("fecha_creacion") or datetime.now().strftime('%Y-%m-%d %H:%M')
        fecha_str = str(fecha_raw).replace("T", " ")[:16]

        # --- DISEÑO IDÉNTICO A TU IMAGEN ---
        ticket =  "\n"
        ticket += "            BITCAFE            \n\n"
        ticket += f"Folio: {folio}\n"
        ticket += f"Fecha: {fecha_str}\n"
        ticket += f"Cliente ID: {cliente_id}\n"
        ticket += f"Pago: {metodo_pago}\n"
        ticket += "_________________________________\n\n"
        ticket += "CANT   PRODUCTO            TOTAL\n"
        
        for item in items:
            p_info = item.get("producto", {})
            n_prod = p_info.get("nombre") or item.get("nombre") or "Producto"
            cant = item.get("cantidad", 1)
            p_uni = item.get("precio_unitario_compra") or item.get("precio") or 0.0
            sub = cant * p_uni
            
            # Alineación de columnas
            linea = f"{str(cant).ljust(6)} {n_prod[:15].ljust(15)} {f'${sub:.2f}'.rjust(10)}\n"
            ticket += linea
            
            if item.get("notas"):
                ticket += f"       ({item.get('notas')})\n"
            
        ticket += "_________________________________\n\n"
        ticket += f"TOTAL: ${total:.2f}".rjust(32) + "\n\n\n"
        ticket += "      ¡Gracias por su compra!    "
        
        return ticket