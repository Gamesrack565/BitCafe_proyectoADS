# BITCAFE
# VERSION 1.1 - Imagenes Dinamicas y UI Limpia
# By: Angel A. Higuera & Gemini Partner

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                             QLineEdit, QPushButton, QScrollArea, QFrame, 
                             QGraphicsDropShadowEffect, QSizePolicy, QCompleter)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap
import requests
from io import BytesIO
from .ventana_base import VentanaBase

# --- WIDGET PERSONALIZADO: FILA DE PRODUCTO ---
class ProductoItem(QFrame):
    # Señales para el Controlador
    cantidad_cambiada = pyqtSignal(object, int) 
    eliminar_item = pyqtSignal(object)          

    def __init__(self, p_id, nombre, categoria, precio, url_imagen=None):
        super().__init__()
        self.p_id = p_id
        self.nombre = nombre
        self.precio_unitario = float(precio)
        self.cantidad_actual = 1

        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #EAEAEA;
            }
            QLabel { border: none; background: transparent; }
        """)
        self.setFixedHeight(80) 
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # --- LÓGICA DE IMAGEN REAL ---
        self.lbl_foto = QLabel()
        self.lbl_foto.setFixedSize(52, 52)
        self.lbl_foto.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; border: 1px solid #DDD;")
        self.lbl_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cargar_imagen_desde_url(url_imagen)
        layout.addWidget(self.lbl_foto)
        
        layout.addSpacing(12)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        lbl_nombre = QLabel(nombre)
        lbl_nombre.setStyleSheet("font-weight: bold; font-size: 14px; color: #222;")
        
        lbl_detalles = QLabel(f"{categoria}   |   ${self.precio_unitario:.2f}")
        lbl_detalles.setStyleSheet("color: #666; font-size: 12px;")
        
        info_layout.addWidget(lbl_nombre)
        info_layout.addWidget(lbl_detalles)
        layout.addLayout(info_layout)
        
        layout.addStretch() 
        
        # Botones +/-
        self.btn_menos = QPushButton("−")
        self.btn_menos.setFixedSize(32, 32)
        self.btn_menos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menos.clicked.connect(self.restar)
        
        self.lbl_cantidad = QLabel("1")
        self.lbl_cantidad.setFixedSize(30, 32)
        self.lbl_cantidad.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cantidad.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        
        self.btn_mas = QPushButton("+")
        self.btn_mas.setFixedSize(32, 32)
        self.btn_mas.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mas.clicked.connect(self.sumar)
        
        estilo_btn_qty = """
            QPushButton {
                background-color: #E0E0E0; border: 1px solid #AAAAAA; 
                border-radius: 6px; font-weight: 900; font-size: 16px; color: #000;
            }
            QPushButton:hover { background-color: #D0D0D0; border: 1px solid #888; }
            QPushButton:pressed { background-color: #BBBBBB; }
        """
        self.btn_menos.setStyleSheet(estilo_btn_qty)
        self.btn_mas.setStyleSheet(estilo_btn_qty)
        
        layout.addWidget(self.btn_menos)
        layout.addWidget(self.lbl_cantidad)
        layout.addWidget(self.btn_mas)

    def cargar_imagen_desde_url(self, url):
        """Descarga la imagen asegurando el formato correcto de la URL"""
        if not url or str(url).lower() == "none" or url == "":
            self.lbl_foto.setText("☕")
            return
        
        # 1. LIMPIEZA: Quitar espacios y asegurar que la URL sea string
        url = str(url).strip().replace(" ", "%20")
        
        # 2. CONSTRUCCIÓN SEGURA:
        # Si la URL no empieza con http, la construimos
        if not url.startswith("http"):
            # Si el pedazo de URL no empieza con /, se lo ponemos nosotros
            prefix = "/" if not url.startswith("/") else ""
            url = f"http://127.0.0.1:8000{prefix}{url}"
        else:
            # Si ya trae http, verificamos si por error se pegó al puerto 
            # (Caso: http://127.0.0.1:8000static...)
            if "8000static" in url:
                url = url.replace("8000static", "8000/static")

        try:
            # 3. DESCARGA
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                if not pixmap.isNull():
                    self.lbl_foto.setPixmap(pixmap.scaled(
                        52, 52, 
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                        Qt.TransformationMode.SmoothTransformation
                    ))
                    self.lbl_foto.setText("")
                else:
                    self.lbl_foto.setText("?")
            else:
                # Si el servidor responde 404 u otro error
                print(f"Error de servidor {response.status_code} en URL: {url}")
                self.lbl_foto.setText("404")
        except Exception as e:
            # Aquí es donde salía el "!"
            print(f"Error crítico en ProductoItem: {e} | URL intentada: {url}")
            self.lbl_foto.setText("!")

    def sumar(self):
        self.cantidad_actual += 1
        self.lbl_cantidad.setText(str(self.cantidad_actual))
        self.cantidad_cambiada.emit(self, self.cantidad_actual)

    def restar(self):
        if self.cantidad_actual > 1:
            self.cantidad_actual -= 1
            self.lbl_cantidad.setText(str(self.cantidad_actual))
            self.cantidad_cambiada.emit(self, self.cantidad_actual)
        else:
            self.eliminar_item.emit(self)


# --- VISTA PRINCIPAL PEDIDO MANUAL ---
class VistaPedidoManual(VentanaBase):
    producto_seleccionado = pyqtSignal(str)

    def __init__(self, logo_path=None):
        super().__init__(logo_path=logo_path, sidebar_color="#D22A00")
        self.set_titulo_contenido("Pedido Manual")
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 20, 20, 0)
        self.grid_layout.setHorizontalSpacing(40)
        self.grid_layout.setVerticalSpacing(10)
        
        self.grid_layout.setColumnStretch(0, 65)
        self.grid_layout.setColumnStretch(1, 35)
        
        self.contenido_layout.addLayout(self.grid_layout)
        
        # --- Fila 0: Buscador y Folio ---
        panel_superior_izq = QWidget()
        layout_sup = QVBoxLayout(panel_superior_izq)
        layout_sup.setContentsMargins(0, 0, 0, 0)
        layout_sup.setSpacing(10)
        
        # Folio oculto por requerimiento
        self.lbl_folio_texto = QLabel("Folio:")
        self.lbl_folio_texto.setStyleSheet("font-weight: bold; font-size: 15px; color: #111;")
        layout_sup.addWidget(self.lbl_folio_texto)
        
        self.input_folio = QLineEdit("Generando...") 
        self.input_folio.setReadOnly(True)
        self.input_folio.setFixedWidth(240)
        self.input_folio.setStyleSheet("background-color: #EEE; border: 1px solid #CCC; border-radius: 8px; padding: 6px 12px; font-weight: bold;")
        layout_sup.addWidget(self.input_folio)
        
        # OCULTAR FOLIO:
        self.lbl_folio_texto.hide()
        self.input_folio.hide()
        
        lbl_buscar = QLabel("¿Qué va a ordenar?")
        lbl_buscar.setStyleSheet("font-weight: bold; font-size: 15px; color: #111;")
        layout_sup.addWidget(lbl_buscar)
        
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Busca tu producto...")
        self.input_buscar.setFixedHeight(45)
        self.input_buscar.setStyleSheet("background-color: white; border: 1px solid #EEE; color: #333; border-radius: 12px; padding: 5px 15px; font-size: 14px;")
        self.input_buscar.setGraphicsEffect(self._crear_sombra_suave())
        layout_sup.addWidget(self.input_buscar)
        
        self.grid_layout.addWidget(panel_superior_izq, 0, 0)
        
        # --- Fila 1 ---
        lbl_orden = QLabel("Orden"); lbl_orden.setStyleSheet("font-weight: bold; font-size: 16px; color: #111; margin-top: 20px;")
        self.grid_layout.addWidget(lbl_orden, 1, 0)
        
        lbl_ticket = QLabel("Acciones"); lbl_ticket.setStyleSheet("font-weight: bold; font-size: 16px; color: #111; margin-top: 20px;")
        self.grid_layout.addWidget(lbl_ticket, 1, 1)

        # --- Fila 2: Contenido ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        
        self.contenedor_productos = QWidget()
        self.contenedor_productos.setStyleSheet("background: transparent;")
        self.layout_lista_productos = QVBoxLayout(self.contenedor_productos)
        self.layout_lista_productos.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_lista_productos.setSpacing(12)
        self.layout_lista_productos.setContentsMargins(5, 5, 5, 5)
        
        scroll_area.setWidget(self.contenedor_productos)
        self.grid_layout.addWidget(scroll_area, 2, 0)
        
        # Panel Derecho
        panel_acciones = QWidget()
        layout_acciones = QVBoxLayout(panel_acciones)
        layout_acciones.setContentsMargins(0, 0, 0, 0)
        layout_acciones.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_acciones.setSpacing(15) 
        
        self.btn_imprimir = QPushButton("Imprimir Ticket")
        self.btn_imprimir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_imprimir.setFixedSize(200, 45) 
        self.btn_imprimir.setStyleSheet("background-color: #D22A00; color: white; font-weight: bold; border-radius: 10px; border: none;")
        self.btn_imprimir.setGraphicsEffect(self._crear_sombra_suave())
        layout_acciones.addWidget(self.btn_imprimir)
        
        self.btn_pagar = QPushButton("Pagar")
        self.btn_pagar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pagar.setFixedSize(200, 45)
        self.btn_pagar.setStyleSheet("background-color: white; color: #D22A00; font-weight: bold; border-radius: 10px; border: 2px solid #D22A00;")
        self.btn_pagar.setGraphicsEffect(self._crear_sombra_suave())
        layout_acciones.addWidget(self.btn_pagar)
        
        layout_acciones.addStretch()
        
        layout_total = QVBoxLayout()
        lbl_total_titulo = QLabel("Total a Pagar:"); lbl_total_titulo.setStyleSheet("font-weight: bold; font-size: 14px; color: #555;")
        layout_total.addWidget(lbl_total_titulo)
        
        self.lbl_total_valor = QLabel("$ 0.00") 
        self.lbl_total_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total_valor.setFixedSize(200, 60)
        self.lbl_total_valor.setStyleSheet("background-color: #F8F8F8; border: 2px solid #D22A00; border-radius: 12px; font-size: 24px; font-weight: 900; color: #D22A00;")
        layout_total.addWidget(self.lbl_total_valor)
        
        layout_acciones.addLayout(layout_total)
        self.grid_layout.addWidget(panel_acciones, 2, 1)

        # Buscador
        self.completer = QCompleter([])
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.popup().setStyleSheet("QListView { background: white; color: #333; border: 1px solid #CCC; } QListView::item:selected { background: #D22A00; color: white; }")
        self.input_buscar.setCompleter(self.completer)
        self.completer.activated.connect(self.producto_seleccionado.emit)

    def _crear_sombra_suave(self):
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setColor(QColor(0, 0, 0, 25))
        sombra.setOffset(0, 4)
        return sombra