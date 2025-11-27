#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from .ventana_base import VentanaBase 


class MensajeVacio(QFrame):
    def __init__(self, texto, color_fondo, color_texto):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color_fondo};
                border-radius: 12px;
                border: none;
            }}
        """)
        self.setFixedHeight(120) 
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl = QLabel(texto)
        lbl.setStyleSheet(f"color: {color_texto}; font-weight: bold; font-size: 14px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(lbl)



class TarjetaPedidoKanban(QFrame):
    # Señal personalizada: Devuelve (id_pedido, accion_solicitada)
    accion_clicked = pyqtSignal(object, str)

    def __init__(self, id_pedido, folio, hora, items, total, estado, tiempo_estimado_str=None):
        super().__init__()
        self.id_pedido = id_pedido
        self.estado = estado
        
        # Colores visuales según estado
        colores = {
            "nuevo": ("#E8FBEA", "#C5E8C7"),       # Verde
            "preparacion": ("#FFF8F5", "#F5D9B8"), # Naranja/Blanco
            "listo": ("#FDF2F2", "#F5C2C2")        # Rojo
        }
        fondo, borde = colores.get(estado, ("#FFFFFF", "#E8E8E8"))

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {fondo};
                border: 1px solid {borde};
                border-radius: 12px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12) 
        layout.setSpacing(8)

        # --- 1. HEADER: HORA Y TIEMPO RESTANTE ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)

        lbl_hora = QLabel(f"Hora de Pedido: {hora}")
        lbl_hora.setStyleSheet("color: #D22A00; font-weight: 700; font-size: 12px;")
        header_layout.addWidget(lbl_hora)

        # Lógica de Tiempo Restante
        if tiempo_estimado_str and estado == "preparacion":
            texto_tiempo, color_tiempo = self.calcular_tiempo_restante(tiempo_estimado_str)
            lbl_tiempo = QLabel(texto_tiempo)
            lbl_tiempo.setStyleSheet(f"color: {color_tiempo}; font-size: 11px; font-weight: normal;")
            header_layout.addWidget(lbl_tiempo)
        
        layout.addLayout(header_layout)

        # --- 2. FOLIO Y DETALLES ---
        lbl_folio = QLabel(f"Folio: {folio}")
        lbl_folio.setStyleSheet("color: #555555; font-size: 12px;")
        layout.addWidget(lbl_folio)

        # Items
        if isinstance(items, list):
            items_texto = "\n".join(items)
        else:
            items_texto = str(items)
            
        lbl_items = QLabel(items_texto)
        lbl_items.setWordWrap(True)
        lbl_items.setStyleSheet("color: #000000; font-weight: 600; font-size: 13px;")
        layout.addWidget(lbl_items)

        # --- 3. TOTAL Y BOTÓN DE ACCIÓN ---
        fila_bottom = QHBoxLayout()
        fila_bottom.setContentsMargins(0, 8, 0, 0)
        
        lbl_total = QLabel(f"${total}")
        lbl_total.setStyleSheet("color: #D22A00; font-weight: 800; font-size: 15px;")
        
        fila_bottom.addStretch()
        fila_bottom.addWidget(lbl_total)
        
        layout.addLayout(fila_bottom)

        # --- 4. BOTONES ---
        if estado == "preparacion":
            btn_listo = QPushButton("Listo")
            btn_listo.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_listo.setFixedHeight(30)
            btn_listo.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #D22A00;
                    border-radius: 8px;
                    color: #D22A00;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 0 15px;
                }
                QPushButton:hover { background-color: #FFF5F5; }
            """)
            btn_listo.clicked.connect(lambda: self.accion_clicked.emit(self.id_pedido, "marcar_listo"))
            layout.addWidget(btn_listo, alignment=Qt.AlignmentFlag.AlignRight)

        elif estado == "listo":
            btn_entregado = QPushButton("Entregado")
            btn_entregado.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_entregado.setFixedHeight(30)
            btn_entregado.setStyleSheet("""
                QPushButton {
                    background-color: #D22A00;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 0 15px;
                }
                QPushButton:hover { background-color: #B22400; }
            """)
            btn_entregado.clicked.connect(lambda: self.accion_clicked.emit(self.id_pedido, "marcar_entregado"))
            layout.addWidget(btn_entregado, alignment=Qt.AlignmentFlag.AlignRight)

        elif estado == "nuevo":
            lbl_estado = QLabel("Preparando") 
            lbl_estado.setStyleSheet("background-color: #C9FFB5; color: #005500; border-radius: 4px; padding: 4px; font-size: 10px; font-weight: bold;")
            pass

    def calcular_tiempo_restante(self, fecha_iso):
        try:
            fecha_limpia = fecha_iso.split(".")[0].replace("Z", "")
            dt_estimado = datetime.fromisoformat(fecha_limpia)
            dt_ahora = datetime.now()
            
            diferencia = dt_estimado - dt_ahora
            minutos = int(diferencia.total_seconds() / 60)
            
            if minutos > 0:
                return f"Tiempo restante: {minutos} min", "#D22A00" 
            else:
                return f"Retrasado: {abs(minutos)} min", "#FF0000" 
        except Exception as e:
            return "Tiempo: --", "#999999"


class VistaPedidos(VentanaBase):
    solicitud_cambio_estado = pyqtSignal(object, str)

    def __init__(self, logo_path=None):
        super().__init__(logo_path=logo_path, sidebar_color="#D22A00")
        self.set_titulo_contenido("Pedidos")

        # Layout principal
        layout_columnas = QHBoxLayout()
        layout_columnas.setSpacing(20) 
        self.contenido_layout.addLayout(layout_columnas)

        # --- Crear columnas ---
        self.layout_nuevos = self.crear_columna(layout_columnas, "Nuevos", "#C9FFB5", "#000000")
        self.layout_preparacion = self.crear_columna(layout_columnas, "En preparación", "#FFFFFF", "#D22A00", "2px solid #D22A00")
        self.layout_listos = self.crear_columna(layout_columnas, "Listos", "#D22A00", "#FFFFFF")

    def crear_columna(self, layout_padre, titulo, header_bg, header_color, header_border="none"):
        columna_container = QWidget()
        col_layout = QVBoxLayout(columna_container)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(12)

        lbl_header = QLabel(titulo)
        lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_header.setFixedHeight(50)
        lbl_header.setStyleSheet(f"""
            background-color: {header_bg}; color: {header_color};
            font-weight: 700; font-size: 15px;
            border: {header_border}; border-radius: 12px; padding: 8px;
        """)
        
        col_layout.addWidget(lbl_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # --- AQUÍ ESTÁ EL CAMBIO: APLICAMOS EL ESTILO DEL DASHBOARD AL SCROLL ---
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #F0F0F0; width: 8px; margin: 0px; border-radius: 4px; }
            QScrollBar::handle:vertical { background-color: #C1C1C1; min-height: 30px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background-color: #D22A00; }
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { border: none; background: none; height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        # ------------------------------------------------------------------------
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        layout_tarjetas = QVBoxLayout(content_widget)
        layout_tarjetas.setContentsMargins(0, 6, 5, 6) # Margen derecho 5px para no tapar el slider
        layout_tarjetas.setSpacing(10)
        layout_tarjetas.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(content_widget)
        col_layout.addWidget(scroll)
        layout_padre.addWidget(columna_container)

        return layout_tarjetas

    def eliminar_tarjeta_visual(self, id_pedido):
        """Busca y elimina visualmente una tarjeta por su ID inmediatamente"""
        layouts = [self.layout_nuevos, self.layout_preparacion, self.layout_listos]
            
        encontrado = False
        for layout in layouts:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget and isinstance(widget, TarjetaPedidoKanban):
                        if widget.id_pedido == id_pedido:
                            widget.deleteLater()
                            encontrado = True
                            break 
            if encontrado:
                break    

    def limpiar_tablero(self):
        for layout in [self.layout_nuevos, self.layout_preparacion, self.layout_listos]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

    def agregar_tarjeta(self, estado, id_pedido, folio, hora, items, total, tiempo_estimado=None):
        tarjeta = TarjetaPedidoKanban(id_pedido, folio, hora, items, total, estado, tiempo_estimado)
        tarjeta.accion_clicked.connect(self.propagar_senal)

        if estado == "nuevo":
            self.layout_nuevos.insertWidget(0, tarjeta)
        elif estado == "preparacion":
            self.layout_preparacion.insertWidget(0, tarjeta)
        elif estado == "listo":
            self.layout_listos.insertWidget(0, tarjeta)

    def propagar_senal(self, id_pedido, accion):
        print(f"Vista: Usuario quiere {accion} en pedido {id_pedido}")
        self.solicitud_cambio_estado.emit(id_pedido, accion)

    def actualizar_pedidos(self, lista_nuevos, lista_prep, lista_listos):
        self.limpiar_tablero()
        
        def procesar_lista(lista, estado, layout_obj, msg_vacio):
            if lista:
                for p in reversed(lista):
                    self.agregar_tarjeta(
                        estado, 
                        p.get('id'), p.get('folio'), p.get('hora'), 
                        p.get('items'), p.get('total'), p.get('tiempo_estimado')
                    )
            else:
                layout_obj.addWidget(msg_vacio)

        msg_nuevos = MensajeVacio("No hay pedidos nuevos", "#F0FDF4", "#4C8B56")
        procesar_lista(lista_nuevos, "nuevo", self.layout_nuevos, msg_nuevos)

        msg_prep = MensajeVacio("Nada en cocina", "#FFFBF8", "#CC9A86")
        procesar_lista(lista_prep, "preparacion", self.layout_preparacion, msg_prep)

        msg_listos = MensajeVacio("Nada por entregar", "#FEF2F2", "#E57373")
        procesar_lista(lista_listos, "listo", self.layout_listos, msg_listos)