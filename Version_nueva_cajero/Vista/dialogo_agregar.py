#BITCAFE
#VERSION 1.0 (Formulario de Creación de Producto)
#By: Angel A. Higuera

#Librerías y modulos
#Importa los widgets necesarios de PyQt6 para construir la interfaz.
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QDoubleSpinBox, QComboBox, QPushButton, QFileDialog,
                             QRadioButton, QButtonGroup, QGraphicsDropShadowEffect)
#Importa constantes del nucleo de Qt (alineacion, cursores, etc).
from PyQt6.QtCore import Qt
#Importa clases para manejo de colores y paletas visuales.
from PyQt6.QtGui import QColor, QPalette

#Define la clase DialogoProducto que hereda de QDialog (ventana modal).
class DialogoProducto(QDialog):
    def __init__(self, parent=None, producto_data=None):
        #Inicializa la clase padre QDialog.
        super().__init__(parent)
        #Establece el titulo de la ventana.
        self.setWindowTitle("Gestión de Producto")
        #Fija el tamano de la ventana para que no sea redimensionable.
        self.setFixedSize(450, 750)
        #Establece el color de fondo blanco.
        self.setStyleSheet("background-color: #FFFFFF;")
        
        #Variable para almacenar la ruta de la imagen seleccionada por el usuario.
        self.ruta_imagen_seleccionada = None 

        # Layout Principal
        #Crea un layout vertical para organizar los elementos de arriba a abajo.
        self.layout = QVBoxLayout(self)
        #Establece margenes internos (izquierda, arriba, derecha, abajo).
        self.layout.setContentsMargins(30, 30, 30, 30)
        #Establece el espaciado entre widgets.
        self.layout.setSpacing(12) # Espacio un poco más ajustado

        # --- ESTILOS CSS ---
        #Define el estilo CSS comun para las etiquetas (labels).
        self.estilo_label = "color: #333; font-weight: 500; font-size: 14px; margin-bottom: 2px;"
        #Define el estilo CSS para los campos de entrada (inputs).
        self.estilo_input = """
            background-color: #FFFFFF;
            border: 1px solid #AAAAAA;
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 14px;
            color: #333;
            selection-background-color: #D22A00; 
            selection-color: #FFFFFF;
        """

        # 1. Nombre
        #Agrega la etiqueta visual para el campo Nombre.
        self.agregar_campo_texto("Nombre")
        #Crea el input de texto para el nombre.
        self.inp_nombre = self.crear_input()
        #Aplica la correccion de color de seleccion.
        self.fix_selection_color(self.inp_nombre)
        #Anade el input al layout principal.
        self.layout.addWidget(self.inp_nombre)

        # 2. Descripción (Ahora es una línea simple como en la imagen)
        #Agrega la etiqueta para Descripcion.
        self.agregar_campo_texto("Descripción")
        #Crea el input de texto.
        self.inp_desc = self.crear_input()
        #Aplica correccion de color.
        self.fix_selection_color(self.inp_desc)
        #Anade el input al layout.
        self.layout.addWidget(self.inp_desc)

        # 3. Precio
        #Agrega la etiqueta para Precio.
        self.agregar_campo_texto("Precio")
        #Crea un widget de entrada numerica con decimales.
        self.inp_precio = QDoubleSpinBox()
        #Establece el rango permitido (0 a 10000).
        self.inp_precio.setRange(0, 10000)
        #Oculta los botones de flechas (spin buttons) para un look mas limpio.
        self.inp_precio.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        #Aplica el estilo CSS de input.
        self.inp_precio.setStyleSheet(self.estilo_input)
        #Aplica correccion de color.
        self.fix_selection_color(self.inp_precio)
        #Anade el widget al layout.
        self.layout.addWidget(self.inp_precio)

        # 4. ¿Está disponible? (Radio Buttons)
        #Agrega etiqueta de pregunta.
        self.agregar_campo_texto("¿Está disponible?")
        #Crea un grupo de botones para manejo exclusivo (solo uno seleccionado).
        self.group_disp = QButtonGroup(self)
        #Crea un layout horizontal para poner los radios lado a lado.
        layout_disp = QHBoxLayout()
        #Establece espaciado entre radios.
        layout_disp.setSpacing(40)
        #Alinea los radios a la izquierda.
        layout_disp.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        #Crea el radio button "Si".
        self.rb_disp_si = QRadioButton("Sí")
        #Crea el radio button "No".
        self.rb_disp_no = QRadioButton("No")
        #Estiliza ambos botones.
        self.estilizar_radio(self.rb_disp_si); self.estilizar_radio(self.rb_disp_no)
        
        #Anade los botones al grupo logico.
        self.group_disp.addButton(self.rb_disp_si)
        self.group_disp.addButton(self.rb_disp_no)
        #Marca "Si" por defecto.
        self.rb_disp_si.setChecked(True) 

        #Anade los widgets visuales al layout horizontal.
        layout_disp.addWidget(self.rb_disp_si)
        layout_disp.addWidget(self.rb_disp_no)
        #Anade el layout horizontal al layout principal vertical.
        self.layout.addLayout(layout_disp)

        # 5. ID de la categoría (ComboBox estilizado)
        #Agrega etiqueta para Categoria.
        self.agregar_campo_texto("ID de la categoría")
        #Crea el combobox (lista desplegable).
        self.inp_categoria = QComboBox()
        #Define un diccionario para mapear Nombres a IDs.
        self.mapa_categorias = {"Bebidas": 1, "Alimentos": 2, "Postres": 3, "General": 4}
        #Anade las llaves (nombres) al combobox.
        self.inp_categoria.addItems(self.mapa_categorias.keys())
        
        #Aplica estilo CSS avanzado para personalizar el combobox y su desplegable.
        self.inp_categoria.setStyleSheet("""
            QComboBox { 
                background-color: #FFFFFF; border: 1px solid #AAAAAA; 
                border-radius: 8px; padding: 8px; color: #555;
                selection-background-color: #D22A00;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF; color: #333;
                selection-background-color: #D22A00; selection-color: #FFFFFF;
            }
        """)
        #Aplica correccion de color.
        self.fix_selection_color(self.inp_categoria)
        #Anade al layout.
        self.layout.addWidget(self.inp_categoria)

        # 6. ¿Maneja stock? (Radio Buttons)
        #Agrega etiqueta para manejo de stock.
        self.agregar_campo_texto("¿Maneja stock?")
        #Crea grupo logico.
        self.group_stock = QButtonGroup(self)
        #Crea layout horizontal.
        layout_stock = QHBoxLayout()
        #Establece espaciado.
        layout_stock.setSpacing(40)
        #Alinea a la izquierda.
        layout_stock.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        #Crea radio buttons.
        self.rb_stock_si = QRadioButton("Sí")
        self.rb_stock_no = QRadioButton("No")
        #Estiliza radio buttons.
        self.estilizar_radio(self.rb_stock_si); self.estilizar_radio(self.rb_stock_no)
        
        #Anade a grupo logico.
        self.group_stock.addButton(self.rb_stock_si)
        self.group_stock.addButton(self.rb_stock_no)
        #Marca "No" por defecto.
        self.rb_stock_no.setChecked(True)

        #Anade widgets al layout horizontal.
        layout_stock.addWidget(self.rb_stock_si)
        layout_stock.addWidget(self.rb_stock_no)
        #Anade layout horizontal al principal.
        self.layout.addLayout(layout_stock)

        #Conecta el evento de clic del grupo para habilitar/deshabilitar el input de cantidad.
        self.group_stock.buttonClicked.connect(self.toggle_stock_input)

        # 7. Cantidad
        #Agrega etiqueta para cantidad.
        self.agregar_campo_texto("Cantidad")
        #Crea input numerico.
        self.inp_stock = QDoubleSpinBox()
        #Configura para no usar decimales (enteros).
        self.inp_stock.setDecimals(0)
        #Establece rango.
        self.inp_stock.setRange(0, 9999)
        #Quita botones de flecha.
        self.inp_stock.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        #Aplica estilo base.
        self.inp_stock.setStyleSheet(self.estilo_input)
        #Deshabilita por defecto (ya que "No maneja stock" es el default).
        self.inp_stock.setEnabled(False)
        #Aplica correccion de color.
        self.fix_selection_color(self.inp_stock)
        #Anade al layout.
        self.layout.addWidget(self.inp_stock)

        # 8. Imagen (Botón "Subir archivo")
        #Agrega etiqueta para imagen.
        self.agregar_campo_texto("Imagen")
        #Crea un boton para subir archivo.
        self.btn_img = QPushButton("Subir archivo")
        #Cambia el cursor a mano al pasar por encima.
        self.btn_img.setCursor(Qt.CursorShape.PointingHandCursor)
        #Fija altura del boton.
        self.btn_img.setFixedHeight(35)
        #Conecta el clic a la funcion de seleccion de archivo.
        self.btn_img.clicked.connect(self.seleccionar_imagen)
        # Aplica estilo: Borde Rojo, Fondo Blanco (Outline).
        self.btn_img.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D22A00;
                color: #D22A00;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #FFF5F0; }
        """)
        #Anade al layout.
        self.layout.addWidget(self.btn_img)
        
        # Etiqueta pequeña para ver qué archivo se seleccionó
        #Crea etiqueta vacia para mostrar nombre de archivo.
        self.lbl_nombre_img = QLabel("")
        #Estiliza la etiqueta con color gris y letra pequena.
        self.lbl_nombre_img.setStyleSheet("color: #888; font-size: 11px; margin-left: 5px;")
        #Anade al layout.
        self.layout.addWidget(self.lbl_nombre_img)

        #Agrega un espacio flexible para empujar el boton de aceptar al final.
        self.layout.addStretch()

        # --- BOTÓN ACEPTAR ---
        #Crea el boton principal de accion.
        self.btn_aceptar = QPushButton("Aceptar")
        #Cambia cursor a mano.
        self.btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        #Fija altura grande para facil clic.
        self.btn_aceptar.setFixedHeight(45)
        #Conecta al metodo accept de QDialog (cierra retornando True).
        self.btn_aceptar.clicked.connect(self.accept)
        # Aplica estilo: Fondo Rojo Sólido.
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
        #Crea efecto de sombra.
        shadow = QGraphicsDropShadowEffect()
        #Configura radio de difusion.
        shadow.setBlurRadius(15)
        #Configura color de sombra con transparencia.
        shadow.setColor(QColor(0, 0, 0, 40))
        #Configura desplazamiento vertical.
        shadow.setOffset(0, 4)
        #Aplica el efecto al boton.
        self.btn_aceptar.setGraphicsEffect(shadow)

        #Anade el boton al layout.
        self.layout.addWidget(self.btn_aceptar)

    # =====================
    #  CORRECCIÓN DE COLOR (PALETA)
    # =====================
    def fix_selection_color(self, widget):
        #Obtiene la paleta actual del widget.
        palette = widget.palette()
        #Define color rojo de marca.
        rojo_bitcafe = QColor("#D22A00")
        #Define color blanco.
        blanco = QColor("#FFFFFF")
        #Establece el color de fondo de seleccion (Highlight).
        palette.setColor(QPalette.ColorRole.Highlight, rojo_bitcafe)
        #Establece el color de texto seleccionado.
        palette.setColor(QPalette.ColorRole.HighlightedText, blanco)
        #Aplica la paleta modificada al widget.
        widget.setPalette(palette)

    # =====================
    # HELPERS
    # =====================
    def agregar_campo_texto(self, texto):
        #Crea una etiqueta con el texto dado.
        lbl = QLabel(texto)
        #Aplica el estilo predefinido.
        lbl.setStyleSheet(self.estilo_label)
        #Anade al layout principal.
        self.layout.addWidget(lbl)

    def crear_input(self):
        #Crea un QLineEdit.
        inp = QLineEdit()
        #Aplica estilo.
        inp.setStyleSheet(self.estilo_input)
        #Pone texto placeholder.
        inp.setPlaceholderText("Value")
        #Retorna el widget creado.
        return inp

    def estilizar_radio(self, radio):
        #Aplica hoja de estilos especifica para personalizar el indicador del radio button.
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
        #Verifica si el radio button "Si" esta marcado.
        habilitar = self.rb_stock_si.isChecked()
        #Habilita o deshabilita el input numerico segun el estado.
        self.inp_stock.setEnabled(habilitar)
        #Si se deshabilita (No maneja stock).
        if not habilitar:
            #Resetea el valor a 0.
            self.inp_stock.setValue(0)
            #Cambia el color del texto a gris para indicar inactividad visualmente.
            self.inp_stock.setStyleSheet(self.estilo_input + "color: #AAA;")
        #Si se habilita.
        else:
            #Restaura el color normal.
            self.inp_stock.setStyleSheet(self.estilo_input + "color: #333;")

    # =====================
    # LÓGICA
    # =====================
    def seleccionar_imagen(self):
        #Abre un dialogo del sistema para seleccionar archivo.
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        #Si se selecciono un archivo.
        if archivo:
            #Guarda la ruta completa.
            self.ruta_imagen_seleccionada = archivo
            #Extrae solo el nombre del archivo.
            nombre_archivo = archivo.split("/")[-1]
            #Actualiza el texto del boton.
            self.btn_img.setText(f"Archivo seleccionado: {nombre_archivo}")
            #Actualiza la etiqueta auxiliar.
            self.lbl_nombre_img.setText(nombre_archivo)

    def obtener_datos_formulario(self):
        #Obtiene el texto seleccionado en el combobox.
        nombre_cat = self.inp_categoria.currentText()
        #Busca el ID correspondiente en el mapa.
        id_cat = self.mapa_categorias.get(nombre_cat, 4)

        #Construye el diccionario con todos los datos recolectados.
        datos = {
            "nombre": self.inp_nombre.text(),
            "descripcion": self.inp_desc.text(), # Ahora es QLineEdit
            "precio": self.inp_precio.value(),
            "esta_disponible": self.rb_disp_si.isChecked(),
            "id_categoria": id_cat,
            "maneja_stock": self.rb_stock_si.isChecked(),
            "cantidad_stock": int(self.inp_stock.value())
        }
        
        # Aquí SÍ devolvemos la ruta de la imagen porque es para CREAR
        #Retorna el diccionario de datos y la ruta de la imagen como tupla.
        return datos, self.ruta_imagen_seleccionada