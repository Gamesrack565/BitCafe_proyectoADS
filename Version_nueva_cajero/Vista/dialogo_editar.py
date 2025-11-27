#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QDoubleSpinBox, QComboBox, QPushButton, 
                             QRadioButton, QButtonGroup, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class DialogoProducto(QDialog):
    def __init__(self, parent=None, producto_data=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Producto")
        self.setFixedSize(450, 680) 
        self.setStyleSheet("background-color: #FFFFFF;")
        
        # Layout Principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)

        # --- ESTILOS CSS ---
        self.estilo_label = "color: #333; font-weight: 500; font-size: 14px; margin-bottom: 2px;"
        self.estilo_input = """
            background-color: #FFFFFF;
            border: 1px solid #AAAAAA;
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 14px;
            color: #333;
        """

        # 1. Nombre
        self.agregar_campo_texto("Nombre")
        self.inp_nombre = self.crear_input()
        self.layout.addWidget(self.inp_nombre)

        # 2. Descripción
        self.agregar_campo_texto("Descripción")
        self.inp_desc = self.crear_input()
        self.layout.addWidget(self.inp_desc)

        # 3. Precio
        self.agregar_campo_texto("Precio")
        self.inp_precio = QDoubleSpinBox()
        self.inp_precio.setRange(0, 10000)
        self.inp_precio.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.inp_precio.setStyleSheet(self.estilo_input)
        self.layout.addWidget(self.inp_precio)

        # 4. ¿Está disponible? (Radio Buttons)
        self.agregar_campo_texto("¿Está disponible?")
        self.group_disp = QButtonGroup(self)
        layout_disp = QHBoxLayout()
        layout_disp.setSpacing(40)
        layout_disp.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.rb_disp_si = QRadioButton("Sí")
        self.rb_disp_no = QRadioButton("No")
        self.estilizar_radio(self.rb_disp_si); self.estilizar_radio(self.rb_disp_no)
        
        self.group_disp.addButton(self.rb_disp_si)
        self.group_disp.addButton(self.rb_disp_no)
        self.rb_disp_si.setChecked(True) 

        layout_disp.addWidget(self.rb_disp_si)
        layout_disp.addWidget(self.rb_disp_no)
        self.layout.addLayout(layout_disp)

        # 5. Categoría
        self.agregar_campo_texto("ID de la categoría")
        self.inp_categoria = QComboBox()
        self.mapa_categorias = {"Bebidas": 1, "Alimentos": 2, "Postres": 3, "General": 4}
        self.inp_categoria.addItems(self.mapa_categorias.keys())
        
        # --- ESTILO CORREGIDO (TEXTO VISIBLE) ---
        self.inp_categoria.setStyleSheet("""
            /* Estilo del botón cerrado */
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #AAAAAA;
                border-radius: 8px;
                padding: 5px 10px;
                color: #333333; /* Color del texto seleccionado arriba */
                font-size: 14px;
            }
            
            /* Flecha */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #AAAAAA;
                border-left-style: solid;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background: #F0F0F0;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #555;
                margin-top: 2px;
            }

            /* LA LISTA DESPLEGABLE */
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;  /* Fondo blanco */
                color: #333333;             /* <--- ESTA LÍNEA ES LA SOLUCIÓN (Texto Negro) */
                border: 1px solid #AAAAAA;
                selection-background-color: #D22A00; 
                selection-color: #FFFFFF;   /* Texto blanco solo al pasar el mouse */
                outline: none;
            }
        """)
        
        self.layout.addWidget(self.inp_categoria)

        # 6. ¿Maneja stock? (Radio Buttons)
        self.agregar_campo_texto("¿Maneja stock?")
        self.group_stock = QButtonGroup(self)
        layout_stock = QHBoxLayout()
        layout_stock.setSpacing(40)
        layout_stock.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.rb_stock_si = QRadioButton("Sí")
        self.rb_stock_no = QRadioButton("No")
        self.estilizar_radio(self.rb_stock_si); self.estilizar_radio(self.rb_stock_no)
        
        self.group_stock.addButton(self.rb_stock_si)
        self.group_stock.addButton(self.rb_stock_no)
        self.rb_stock_no.setChecked(True)

        layout_stock.addWidget(self.rb_stock_si)
        layout_stock.addWidget(self.rb_stock_no)
        self.layout.addLayout(layout_stock)

        self.group_stock.buttonClicked.connect(self.toggle_stock_input)

        # 7. Cantidad
        self.agregar_campo_texto("Cantidad")
        self.inp_stock = QDoubleSpinBox()
        self.inp_stock.setDecimals(0)
        self.inp_stock.setRange(0, 9999)
        self.inp_stock.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.inp_stock.setStyleSheet(self.estilo_input)
        self.inp_stock.setEnabled(False)
        self.layout.addWidget(self.inp_stock)

        self.layout.addStretch()

        # --- BOTÓN ACEPTAR ---
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aceptar.setFixedHeight(45)
        self.btn_aceptar.clicked.connect(self.accept)
        # Estilo Fondo Rojo, Texto Blanco
        self.btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover { background-color: #B02200; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.btn_aceptar.setGraphicsEffect(shadow)

        self.layout.addWidget(self.btn_aceptar)

        # --- CARGAR DATOS SI ES EDICIÓN ---
        if producto_data:
            self.cargar_datos_existentes(producto_data)

    # =====================
    # HELPERS DE DISEÑO
    # =====================
    def agregar_campo_texto(self, texto):
        lbl = QLabel(texto)
        lbl.setStyleSheet(self.estilo_label)
        self.layout.addWidget(lbl)

    def crear_input(self):
        inp = QLineEdit()
        inp.setStyleSheet(self.estilo_input)
        inp.setPlaceholderText("Value")
        return inp

    def estilizar_radio(self, radio):
        radio.setStyleSheet("""
            QRadioButton { font-size: 14px; color: #333; spacing: 8px; }
            QRadioButton::indicator { width: 16px; height: 16px; }
            QRadioButton::indicator:checked { 
                background-color: #D22A00; border: 2px solid #D22A00; border-radius: 8px; 
                image: url(none);
            }
            QRadioButton::indicator:unchecked { 
                background-color: #CCC; border-radius: 8px; 
            }
        """)

    def toggle_stock_input(self):
        habilitar = self.rb_stock_si.isChecked()
        self.inp_stock.setEnabled(habilitar)
        if not habilitar:
            self.inp_stock.setValue(0)
            self.inp_stock.setStyleSheet(self.estilo_input + "color: #AAA;")
        else:
            self.inp_stock.setStyleSheet(self.estilo_input + "color: #333;")

    # =====================
    # LÓGICA
    # =====================
    def cargar_datos_existentes(self, data):
        self.inp_nombre.setText(data.get("nombre", ""))
        self.inp_desc.setText(data.get("descripcion", "") or "")
        self.inp_precio.setValue(float(data.get("precio", 0.0)))
        
        cat_data = data.get("categoria")
        cat_nombre = "General"
        
        if isinstance(cat_data, dict):
            cat_nombre = cat_data.get("nombre", "General")
        elif isinstance(cat_data, str):
            cat_nombre = cat_data
            
        index = self.inp_categoria.findText(cat_nombre)
        if index >= 0: self.inp_categoria.setCurrentIndex(index)

        if data.get("esta_disponible", True):
            self.rb_disp_si.setChecked(True)
        else:
            self.rb_disp_no.setChecked(True)

        if data.get("maneja_stock", False):
            self.rb_stock_si.setChecked(True)
            self.inp_stock.setEnabled(True)
            self.inp_stock.setValue(int(data.get("cantidad_stock", 0)))
        else:
            self.rb_stock_no.setChecked(True)
            self.inp_stock.setEnabled(False)

    def obtener_datos_formulario(self):
        nombre_cat = self.inp_categoria.currentText()
        id_cat = self.mapa_categorias.get(nombre_cat, 4)

        datos = {
            "nombre": self.inp_nombre.text(),
            "descripcion": self.inp_desc.text(),
            "precio": self.inp_precio.value(),
            "esta_disponible": self.rb_disp_si.isChecked(),
            "id_categoria": id_cat,
            "maneja_stock": self.rb_stock_si.isChecked(),
            "cantidad_stock": int(self.inp_stock.value())
        }
        
        # Retornamos None en el segundo valor (imagen) para no romper el controlador
        return datos, None