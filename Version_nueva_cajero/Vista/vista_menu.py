#BITCAFE
#VERSION 1.0 
#By: Angel A. Higuera

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QLineEdit,
                             QGraphicsDropShadowEffect, QAbstractButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen
from .ventana_base import VentanaBase


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor("#D22A00") if self.isChecked() else QColor("#CCCCCC")
        circle_color = Qt.GlobalColor.white

        rect = self.rect()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, rect.width(), rect.height(), 14, 14)

        painter.setBrush(QBrush(circle_color))
        radius = 11
        y_pos = 3
        x_pos = rect.width() - (radius * 2) - 3 if self.isChecked() else 3
            
        painter.drawEllipse(x_pos, y_pos, radius * 2, radius * 2)
        painter.end()

# Configuración de anchos
COL_ANCHO_CAT = 140
COL_ANCHO_PRECIO = 100
COL_ANCHO_DISP = 120
COL_ANCHO_ACCIONES = 100



class ProductoAdminItem(QFrame):
    def __init__(self, nombre, categoria, precio, activo):
        super().__init__()
        self.nombre_texto = nombre 
        
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #F0F0F0;
            }
            QLabel { border: none; background: transparent; color: #333; font-size: 13px;}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        # Imagen
        img = QLabel()
        img.setFixedSize(48, 48)
        img.setStyleSheet("background-color: #E0E0E0; border-radius: 8px;")
        layout.addWidget(img)
        layout.addSpacing(10)

        # Datos
        lbl_nombre = QLabel(nombre)
        lbl_nombre.setStyleSheet("font-weight: bold; font-size: 14px; color: #111;")
        layout.addWidget(lbl_nombre, stretch=1)

        lbl_cat = QLabel(categoria)
        lbl_cat.setFixedWidth(COL_ANCHO_CAT)
        lbl_cat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_cat)

        lbl_precio = QLabel(f"${precio}")
        lbl_precio.setFixedWidth(COL_ANCHO_PRECIO)
        lbl_precio.setStyleSheet("font-weight: bold; color: #333;")
        lbl_precio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_precio)

        # Switch
        container_switch = QWidget()
        container_switch.setFixedWidth(COL_ANCHO_DISP)
        layout_switch = QVBoxLayout(container_switch)
        layout_switch.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_switch.setContentsMargins(0,0,0,0)

        # IMPORTANTE: Guardamos con self para que el controlador lo vea
        self.switch = ToggleSwitch()
        self.switch.setChecked(activo)
        
        layout_switch.addWidget(self.switch)
        layout.addWidget(container_switch)

        # Acciones
        container_actions = QWidget()
        container_actions.setFixedWidth(COL_ANCHO_ACCIONES)
        layout_actions = QHBoxLayout(container_actions)
        layout_actions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_actions.setContentsMargins(0,0,0,0)
        layout_actions.setSpacing(15)

        # IMPORTANTE: Guardamos con self.btn_edit
        self.btn_edit = QPushButton("✏️") 
        self.btn_edit.setFixedSize(30, 30)
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setStyleSheet("QPushButton { border: none; font-size: 18px; } QPushButton:hover { background-color: #F5F5F5; border-radius: 5px; }")
        
        # IMPORTANTE: Guardamos con self.btn_del
        self.btn_del = QPushButton("🗑️") 
        self.btn_del.setFixedSize(30, 30)
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.setStyleSheet("QPushButton { border: none; font-size: 18px; } QPushButton:hover { background-color: #FFF0F0; border-radius: 5px; }")

        layout_actions.addWidget(self.btn_edit)
        layout_actions.addWidget(self.btn_del)
        layout.addWidget(container_actions)



class VistaMenu(VentanaBase):
    def __init__(self, logo_path=None):
        super().__init__(logo_path=logo_path, sidebar_color="#D22A00")
        self.set_titulo_contenido("Menú")

        self.layout_principal = QVBoxLayout()
        self.layout_principal.setSpacing(15)
        self.contenido_layout.addLayout(self.layout_principal)

        # --- Buscador ---
        container_busqueda = QWidget()
        layout_busqueda = QHBoxLayout(container_busqueda)
        layout_busqueda.setContentsMargins(20, 0, 20, 10)
        
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("🔍 Buscar producto por nombre...")
        self.input_buscar.setFixedHeight(45)
        self.input_buscar.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 1px solid #DDD;
                border-radius: 12px; padding: 5px 15px; font-size: 14px; color: #333;
            }
            QLineEdit:focus { border: 1px solid #D22A00; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        self.input_buscar.setGraphicsEffect(shadow)
        self.input_buscar.textChanged.connect(self.filtrar_lista)

        layout_busqueda.addWidget(self.input_buscar)
        self.layout_principal.addWidget(container_busqueda)

        # --- Encabezados ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0) 
        header_layout.setSpacing(10)
        style_header = "color: #D22A00; font-weight: bold; font-size: 15px;"

        lbl_ph = QLabel(""); lbl_ph.setFixedSize(48, 10)
        header_layout.addWidget(lbl_ph); header_layout.addSpacing(10)

        lbl_nom = QLabel("Nombre del Producto"); lbl_nom.setStyleSheet(style_header)
        header_layout.addWidget(lbl_nom, stretch=1)

        for txt, w in [("Categoría", COL_ANCHO_CAT), ("Precio", COL_ANCHO_PRECIO), ("Disponibilidad", COL_ANCHO_DISP), ("Acciones", COL_ANCHO_ACCIONES)]:
            l = QLabel(txt); l.setStyleSheet(style_header); l.setFixedWidth(w); l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(l)

        self.layout_principal.addWidget(header_widget)

        # --- Lista Scroll ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #F0F0F0; width: 10px; margin: 0; border-radius: 5px; }
            QScrollBar::handle:vertical { background-color: #C1C1C1; min-height: 30px; border-radius: 5px; }
            QScrollBar::handle:vertical:hover { background-color: #D22A00; }
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { border: none; background: none; height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        
        self.contenedor_items = QWidget()
        self.contenedor_items.setStyleSheet("background: transparent;")
        self.layout_items = QVBoxLayout(self.contenedor_items)
        self.layout_items.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_items.setSpacing(12) 

        self.scroll_area.setWidget(self.contenedor_items)
        self.layout_principal.addWidget(self.scroll_area)

        # --- Botón Añadir ---
        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_add = QPushButton("Añadir Producto")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setFixedSize(320, 50)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #D22A00; color: white; font-weight: bold; font-size: 15px; border-radius: 25px;
            }
            QPushButton:hover { background-color: #B02200; }
        """)
        shadow_add = QGraphicsDropShadowEffect()
        shadow_add.setBlurRadius(20)
        shadow_add.setColor(QColor(0, 0, 0, 50))
        shadow_add.setOffset(0, 5)
        self.btn_add.setGraphicsEffect(shadow_add)

        footer_layout.addWidget(self.btn_add)
        self.layout_principal.addLayout(footer_layout)
        self.layout_principal.addSpacing(10)



    def filtrar_lista(self, texto_busqueda):
        texto_busqueda = texto_busqueda.lower().strip()
        for i in range(self.layout_items.count()):
            item = self.layout_items.itemAt(i)
            widget = item.widget()
            if widget and isinstance(widget, ProductoAdminItem):
                if not texto_busqueda or texto_busqueda in widget.nombre_texto.lower():
                    widget.setVisible(True)
                else:
                    widget.setVisible(False)


    def limpiar_lista(self):
        """Elimina todos los items visuales antes de recargar"""
        while self.layout_items.count():
            item = self.layout_items.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()