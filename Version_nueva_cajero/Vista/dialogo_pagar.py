#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QHBoxLayout, QTabWidget, QWidget, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

class DialogoPago(QDialog):
    def __init__(self, total_a_pagar_float, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesar Pago")
        self.setFixedSize(420, 500) 
        self.total_real = total_a_pagar_float
        self.metodo_seleccionado = "efectivo" 

        # --- 1. CREAR EL BOTÓN PRIMERO (Para evitar el error de crash) ---
        self.btn_finalizar = QPushButton("COBRAR")
        self.btn_finalizar.setFixedSize(150, 50) # Botón más grande
        self.btn_finalizar.setEnabled(False) 
        self.btn_finalizar.setCursor(Qt.CursorShape.PointingHandCursor)
        # Estilo del botón COBRAR
        self.btn_finalizar.setStyleSheet("""
            QPushButton { 
                background-color: #D22A00; 
                color: white; 
                border-radius: 10px; 
                font-weight: bold; 
                font-size: 16px; 
                border: none;
            }
            QPushButton:disabled { background-color: #FFCCCC; color: #E0E0E0; }
            QPushButton:hover { background-color: #B22400; }
        """)

        # --- 2. ESTILOS GENERALES MEJORADOS ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("""
            QDialog { 
                background-color: white; 
                border: 2px solid #D22A00; 
                border-radius: 15px; 
            }
            /* Pestañas */
            QTabWidget::pane { border: none; margin-top: 10px; }
            QTabBar::tab {
                background: #F0F0F0; 
                color: #555; 
                padding: 12px 30px;
                border-top-left-radius: 8px; 
                border-top-right-radius: 8px;
                font-weight: bold; 
                font-size: 14px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { 
                background: #D22A00; 
                color: white; 
            }
            
            /* Inputs (Cajas de texto) */
            QLineEdit { 
                background-color: #FAFAFA;
                border: 1px solid #AAAAAA; 
                border-radius: 8px; 
                padding: 10px; 
                font-size: 18px; /* Letra grande al escribir */
                color: #000000;  /* NEGRO PURO */
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #D22A00;
                background-color: #FFFFFF;
            }

            /* Etiquetas */
            QLabel { 
                font-size: 15px; 
                color: #222222; /* Gris muy oscuro casi negro */
                font-weight: 600; 
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        # Título y Total
        lbl_titulo = QLabel(f"Total a Cobrar: ${self.total_real:.2f}")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Forzamos estilo inline para asegurar que este título sea gigante y rojo
        lbl_titulo.setStyleSheet("font-size: 26px; font-weight: 900; color: #D22A00; margin-bottom: 15px;")
        layout.addWidget(lbl_titulo)

        # Pestañas
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- TAB 1: EFECTIVO ---
        tab_efectivo = QWidget()
        l_efectivo = QVBoxLayout(tab_efectivo)
        l_efectivo.setSpacing(15)
        l_efectivo.setContentsMargins(20, 25, 20, 20)

        l_efectivo.addWidget(QLabel("Monto Recibido:"))
        
        self.input_pago = QLineEdit()
        self.input_pago.setPlaceholderText("$ 0.00")
        self.input_pago.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Validador doble
        self.input_pago.setValidator(QDoubleValidator(0.0, 99999.0, 2))
        l_efectivo.addWidget(self.input_pago)

        l_efectivo.addWidget(QLabel("Cambio a Entregar:"))
        
        self.input_cambio = QLineEdit("---")
        self.input_cambio.setEnabled(False) # Solo lectura
        self.input_cambio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Estilo específico para el cambio (Letra Roja Grande)
        self.input_cambio.setStyleSheet("""
            QLineEdit {
                color: #D22A00; 
                font-weight: 900; 
                font-size: 20px; 
                background-color: #FFF5F5;
                border: 1px solid #FFCCCC;
            }
        """)
        l_efectivo.addWidget(self.input_cambio)
        
        l_efectivo.addStretch()
        self.tabs.addTab(tab_efectivo, "Efectivo")

        # --- TAB 2: TRANSFERENCIA ---
        tab_transf = QWidget()
        l_transf = QVBoxLayout(tab_transf)
        l_transf.setSpacing(15)
        l_transf.setContentsMargins(20, 25, 20, 20)

        lbl_inst = QLabel("1. Solicita la transferencia al cliente.\n2. Verifica en tu app del banco.\n3. Ingresa referencia (opcional).")
        lbl_inst.setStyleSheet("color: #444; font-size: 14px; font-weight: normal;")
        lbl_inst.setWordWrap(True)
        l_transf.addWidget(lbl_inst)

        l_transf.addWidget(QLabel("Referencia / Folio:"))
        self.input_ref = QLineEdit()
        self.input_ref.setPlaceholderText("Ej: 4589")
        l_transf.addWidget(self.input_ref)

        l_transf.addStretch()
        self.tabs.addTab(tab_transf, "Transferencia")

        # --- BOTONES ---
        layout_btns = QHBoxLayout()
        layout_btns.setSpacing(15)
        
        # Botón Cancelar (Arreglado para que se vea)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedSize(120, 50)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet("""
            QPushButton { 
                background-color: #FFFFFF; 
                color: #555555; 
                border: 2px solid #CCCCCC; 
                border-radius: 10px; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover { 
                background-color: #F0F0F0; 
                border: 2px solid #999999;
                color: #000000;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        # Conectamos el botón Finalizar que creamos al principio
        self.btn_finalizar.clicked.connect(self.accept)

        layout_btns.addStretch()
        layout_btns.addWidget(btn_cancelar)
        layout_btns.addWidget(self.btn_finalizar)
        layout.addLayout(layout_btns)

        # --- CONEXIONES LOGICAS ---
        self.input_pago.textChanged.connect(self.calcular_cambio)
        self.tabs.currentChanged.connect(self.cambiar_metodo)

    # En DialogoPago...

    def cambiar_metodo(self, index):
        if index == 0:
            self.metodo_seleccionado = "efectivo"
            self.btn_finalizar.setText("COBRAR") # Texto normal
            self.btn_finalizar.setStyleSheet("""
                QPushButton { background-color: #D22A00; color: white; border-radius: 10px; font-weight: bold; font-size: 16px; border: none;}
                QPushButton:disabled { background-color: #FFCCCC; color: #E0E0E0; }
                QPushButton:hover { background-color: #B22400; }
            """)
            self.calcular_cambio(self.input_pago.text()) 
        else:
            self.metodo_seleccionado = "transferencia"
            # Cambiamos el estilo para indicar que vamos al siguiente paso (QR)
            self.btn_finalizar.setText("GENERAR QR >") 
            self.btn_finalizar.setStyleSheet("""
                QPushButton { background-color: #009EE3; color: white; border-radius: 10px; font-weight: bold; font-size: 16px; border: none;}
                QPushButton:hover { background-color: #007EB5; }
            """)
            self.btn_finalizar.setEnabled(True)

    def calcular_cambio(self, texto):
        if self.metodo_seleccionado != "efectivo": return
        try:
            texto = texto.replace(',', '.')
            if not texto:
                # Si borran todo, reseteamos
                self.input_cambio.setText("---")
                self.btn_finalizar.setEnabled(False)
                return

            pago = float(texto)
            cambio = pago - self.total_real
            
            if cambio >= -0.01: 
                self.input_cambio.setText(f"${cambio:.2f}")
                self.btn_finalizar.setEnabled(True)
            else:
                faltante = abs(cambio)
                self.input_cambio.setText(f"Falta ${faltante:.2f}")
                self.btn_finalizar.setEnabled(False)
        except ValueError:
            self.input_cambio.setText("---")
            self.btn_finalizar.setEnabled(False)

    def obtener_datos(self):
        monto = 0.0
        ref = ""
        if self.metodo_seleccionado == "efectivo":
            try: 
                texto = self.input_pago.text().replace(',', '.')
                monto = float(texto)
            except: pass
        else:
            monto = self.total_real 
            ref = self.input_ref.text()
            
        return self.metodo_seleccionado, monto, ref