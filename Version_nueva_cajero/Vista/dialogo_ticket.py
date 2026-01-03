# BITCAFE - Actividad C: Previsualización de Ticket (FIX VISUALIZACIÓN)
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
        ticket_layout.setContentsMargins(10, 10, 10, 10) # Margen interno para que no se pegue al borde

        # Texto del Ticket (Simulado fuente térmica)
        self.txt_ticket = QTextEdit()
        self.txt_ticket.setReadOnly(True)
        
        # --- CORRECCIÓN AQUÍ: Forzamos color negro (#000000) ---
        self.txt_ticket.setStyleSheet("""
            QTextEdit {
                border: none; 
                font-family: 'Courier New', monospace; 
                font-size: 13px;
                color: #000000;  
                background-color: white;
            }
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
        self.btn_cerrar.setStyleSheet("""
            QPushButton { background-color: #BDC3C7; color: #333; font-weight: bold; border-radius: 10px; }
            QPushButton:hover { background-color: #A6ACAF; }
        """)
        self.btn_cerrar.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_cerrar)
        btn_layout.addWidget(self.btn_imprimir)
        layout.addLayout(btn_layout)

    def generar_formato_ticket(self, datos):
        """Versión BITCAFE - Detección Forzada de Transferencia"""
        # 1. Extraer datos (con manejo de errores si vienen vacíos)
        folio = str(datos.get("num_orden") or datos.get("id_pedido") or "N/A")
        total = float(datos.get("total_pedido") or datos.get("total") or 0.0)
        items = datos.get("items", [])
        cliente_id = datos.get("id_usuario") or "1"
        
        # 2. LÓGICA DETECTIVE DE PAGO
        metodo_raw = str(datos.get("metodo_pago", "")).upper()
        
        if any(x in metodo_raw for x in ["TRANS", "QR", "MP", "STRIPE", "PAGADO"]):
            metodo_pago = "TRANSFERENCIA"
        elif len(folio) > 10 or datos.get("init_point") or "BITCAFE-" in folio:
            metodo_pago = "TRANSFERENCIA"
        elif "EFECTIVO" in metodo_raw:
            metodo_pago = "EFECTIVO"
        else:
            metodo_pago = "TRANSFERENCIA" if "preference_id" in datos else "EFECTIVO"

        # 3. Fecha
        fecha_raw = datos.get("fecha_creacion") or datetime.now().strftime('%Y-%m-%d %H:%M')
        fecha_str = str(fecha_raw).replace("T", " ")[:16]

        # --- DISEÑO ---
        ticket =  "\n"
        ticket += "            BITCAFE            \n"
        ticket += "      Café & Tecnología      \n\n"
        ticket += f"Folio: {folio}\n"
        ticket += f"Fecha: {fecha_str}\n"
        ticket += f"Cliente ID: {cliente_id}\n"
        ticket += f"Pago: {metodo_pago}\n"
        ticket += "-"*33 + "\n"
        ticket += "CANT   PRODUCTO           TOTAL\n"
        ticket += "-"*33 + "\n"
        
        for item in items:
            # Manejo flexible de llaves de diccionario según venga de API o Local
            if "producto" in item and isinstance(item["producto"], dict):
                p_info = item["producto"]
                n_prod = p_info.get("nombre", "Producto")
            else:
                n_prod = item.get("nombre", "Producto")

            cant = item.get("cantidad", 1)
            
            # Obtener precio unitario
            if "precio_unitario_compra" in item:
                p_uni = float(item["precio_unitario_compra"])
            elif "precio" in item:
                p_uni = float(item["precio"])
            else:
                p_uni = 0.0

            sub = cant * p_uni
            
            # Formateo de columnas para que se vea alineado
            # Cortamos el nombre a 15 caracteres
            nombre_fmt = n_prod[:15]
            
            linea = f"{str(cant).ljust(4)} {nombre_fmt.ljust(16)} {f'${sub:.2f}'.rjust(10)}\n"
            ticket += linea
            
            if item.get("notas"):
                ticket += f"       ({item.get('notas')})\n"
            
        ticket += "-"*33 + "\n\n"
        ticket += f"TOTAL: ${total:.2f}".rjust(32) + "\n\n\n"
        ticket += "      ¡Gracias por su compra!    \n"
        ticket += "          Vuelva Pronto          "
        
        return ticket