# BITCAFE - DASHBOARD VIEW V1.6 (ELIPSIS CORREGIDA)
# By: Angel A. Higuera & Gemini Partner

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QPushButton, QGraphicsDropShadowEffect, QSizePolicy, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPainter, QFontMetrics

from .ventana_base import VentanaBase


class LabelElipsado(QLabel):
    """
    QLabel que corta el texto con (...) dinámicamente.
    Override de minimumSizeHint para permitir que el layout lo encoja
    y el precio no se desplace hacia afuera.
    """
    def __init__(self, texto):
        super().__init__(texto)
        self.texto_real = texto
        # Permitir que el label se encoja tanto como sea necesario
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(50) 

    def minimumSizeHint(self):
        # Le dice al layout que este widget puede medir casi nada de ancho
        return QSize(50, self.fontMetrics().height())

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = self.fontMetrics()
        # Calculamos el texto con elipsis según el ancho actual real del widget
        texto_cortado = metrics.elidedText(self.texto_real, Qt.TextElideMode.ElideRight, self.width())
        
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.setFont(self.font())
        # Alineación izquierda y centrada verticalmente
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, texto_cortado)


class MensajeVacioDashboard(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #EAEAEA;
            }
        """)
        
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setColor(QColor(0, 0, 0, 30))
        sombra.setOffset(0, 5)
        self.setGraphicsEffect(sombra)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_texto = QLabel("No hay pedidos por ahora")
        lbl_texto.setStyleSheet("color: #999999; font-size: 16px; font-weight: bold; border: none;")
        lbl_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(lbl_texto)


class TarjetaPedido(QFrame):
    def __init__(self, folio, descripcion, precio):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #ECECEC;
                border-radius: 14px;
            }
            QLabel { font-size: 13px; border: none; }
        """)
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(14)

        # 1. Badge "Nuevo"
        lbl_badge = QLabel("Nuevo")
        lbl_badge.setStyleSheet("""
            background-color: #DFF7DF; color: #2E7D32;
            padding: 4px 10px; border-radius: 10px;
            font-size: 11px; font-weight: 700;
        """)
        lbl_badge.setFixedSize(65, 26)
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 2. Folio (Ancho fijo pero razonable)
        lbl_folio = QLabel(f"Folio {folio}")
        lbl_folio.setStyleSheet("font-weight: 700; color: #333333;")
        lbl_folio.setFixedWidth(160) 

        # 3. Descripción (El que se acorta)
        lbl_desc = LabelElipsado(descripcion)
        lbl_desc.setStyleSheet("color: #666666;") 
        
        # 4. Precio (Alineado a la derecha)
        lbl_precio = QLabel(f"${precio}")
        lbl_precio.setStyleSheet("font-weight: 800; color: #000000; font-size: 14px;")
        lbl_precio.setFixedWidth(100)
        lbl_precio.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Añadir al layout
        layout.addWidget(lbl_badge)
        layout.addWidget(lbl_folio)
        # lbl_desc tiene stretch 1 por defecto al ser Ignored/Expanding, ocupará el espacio sobrante
        layout.addWidget(lbl_desc, 1) 
        layout.addWidget(lbl_precio)


class TarjetaEstadistica(QFrame):
    def __init__(self, titulo, valor_inicial="0"):
        super().__init__()
        self.setFixedSize(200, 120)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #F2F2F2;
            }
            QLabel { border: none; }
        """)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(18)
        sombra.setColor(QColor(0, 0, 0, 20))
        sombra.setOffset(0, 6)
        self.setGraphicsEffect(sombra)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setStyleSheet("color: #666666; font-size: 13px;")
        self.lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_num = QLabel(str(valor_inicial))
        self.lbl_num.setStyleSheet("font-size: 30px; font-weight: 800; color: #111111;")
        self.lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_num)

    def actualizar_valor(self, nuevo_valor):
        self.lbl_num.setText(str(nuevo_valor))


class VistaDashboard(VentanaBase):
    def __init__(self, logo_path=None):
        super().__init__(logo_path=logo_path, sidebar_color="#D22A00")
        self.set_titulo_contenido("Dashboard")

        self.layout_dashboard = QVBoxLayout()
        self.layout_dashboard.setSpacing(18)
        self.contenido_layout.addLayout(self.layout_dashboard)

        # Título sección
        lbl_subtitulo = QLabel("Últimos pedidos")
        lbl_subtitulo.setStyleSheet("font-size: 13px; font-weight: 600; color: #555555;")
        lbl_subtitulo.setContentsMargins(4, 8, 4, 8)
        self.layout_dashboard.addWidget(lbl_subtitulo)

        # Scroll Area Configurada
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(250) 
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #F0F0F0; width: 8px; margin: 0px; border-radius: 4px; }
            QScrollBar::handle:vertical { background-color: #C1C1C1; min-height: 30px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background-color: #D22A00; }
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { border: none; background: none; height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)

        self.contenedor_items_pedidos = QWidget()
        self.contenedor_items_pedidos.setStyleSheet("background: transparent;")
        
        self.layout_lista_pedidos = QVBoxLayout(self.contenedor_items_pedidos)
        self.layout_lista_pedidos.setSpacing(12)
        self.layout_lista_pedidos.setContentsMargins(0, 0, 10, 0)
        self.layout_lista_pedidos.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.contenedor_items_pedidos)
        self.layout_dashboard.addWidget(self.scroll_area)

        # Estadísticas
        fila_stats = QHBoxLayout()
        fila_stats.setSpacing(36)
        fila_stats.setContentsMargins(30, 10, 30, 10)

        self.card_nuevos = TarjetaEstadistica("Pedidos Nuevos")
        self.card_preparacion = TarjetaEstadistica("Pedidos en preparación")
        self.card_ventas = TarjetaEstadistica("Ventas del Día")

        fila_stats.addStretch()
        fila_stats.addWidget(self.card_nuevos)
        fila_stats.addWidget(self.card_preparacion)
        fila_stats.addWidget(self.card_ventas)
        fila_stats.addStretch()

        self.layout_dashboard.addLayout(fila_stats)

        # Botones inferiores
        fila_botones = QHBoxLayout()
        fila_botones.setSpacing(40)
        fila_botones.setAlignment(Qt.AlignmentFlag.AlignCenter)

        estilo_btn = """
            QPushButton {
                background-color: #D22A00; color: white; font-weight: 700;
                border-radius: 14px; padding: 12px 24px; font-size: 14px;
            }
            QPushButton:hover { background-color: #B81E00; }
        """

        self.btn_add = QPushButton("Añadir Producto")
        self.btn_add.setStyleSheet(estilo_btn)
        self.btn_add.setMinimumWidth(180)

        self.btn_ver = QPushButton("Ver Pedidos")
        self.btn_ver.setStyleSheet(estilo_btn)
        self.btn_ver.setMinimumWidth(180)

        fila_botones.addWidget(self.btn_add)
        fila_botones.addWidget(self.btn_ver)

        self.layout_dashboard.addLayout(fila_botones)
        self.layout_dashboard.addSpacing(20)

    def actualizar_estadisticas(self, nuevos, preparacion, ventas):
        self.card_nuevos.actualizar_valor(nuevos)
        self.card_preparacion.actualizar_valor(preparacion)
        self.card_ventas.actualizar_valor(f"${ventas}")

    def actualizar_lista_pedidos(self, lista_datos_pedidos):
        while self.layout_lista_pedidos.count():
            item = self.layout_lista_pedidos.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not lista_datos_pedidos:
            msg_vacio = MensajeVacioDashboard()
            self.layout_lista_pedidos.addWidget(msg_vacio)
            return

        for p in lista_datos_pedidos:
            tarjeta = TarjetaPedido(p['folio'], p['desc'], p['total'])
            self.layout_lista_pedidos.addWidget(tarjeta)