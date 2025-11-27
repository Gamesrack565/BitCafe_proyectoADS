#BITCAFE
#VERSION 1.0 (Punto de Venta Manual)
#By: Angel A. Higuera

#Librerías y modulos
#Importa componentes de interfaz grafica de PyQt6: QMessageBox, QApplication.
from PyQt6.QtWidgets import QMessageBox, QApplication
#Importa constantes del nucleo de PyQt6.
from PyQt6.QtCore import Qt
#Importa el cliente de API para realizar peticiones al backend.
from Modelo.api_client import api
#Importa el widget personalizado para representar un item en la lista de compra.
from Vista.vista_pedido_manual import ProductoItem

# --- IMPORTAMOS TUS VISTAS ---
#Importa el dialogo para seleccionar metodo de pago y monto.
from Vista.dialogo_pagar import DialogoPago
#Importa el dialogo que muestra el cambio y confirmacion de exito.
from Vista.dialogo_exito_pago import DialogoExitoPago
#Importa el dialogo personalizado para avisos (ej. carrito vacio).
from Vista.dialogo_carrito_vacio import DialogoAviso
#Importa el dialogo para mostrar el codigo QR de Mercado Pago.
from Vista.dialogo_qr import DialogoQR        

# --- IMPORTAMOS LA VARIABLE COMPARTIDA ---
#Bloque try-except para importar variables globales de manera segura.
try:
    #Intenta importar la cache del catalogo y el modulo completo.
    from Modelo.variables import cache_catalogo
    import Modelo.variables as store_module 
#Si falla la importacion.
except ImportError:
    #Imprime aviso en consola.
    print("AVISO: No se encontró Modelo/store.py")
    #Establece variables como None por defecto.
    cache_catalogo = None
    store_module = None

class ControladorPedidoManual:
    def __init__(self, vista):
        #Guarda referencia a la vista principal del punto de venta.
        self.vista = vista
        #Inicializa la lista para almacenar el catalogo completo de productos.
        self.catalogo_completo = [] 
        #Inicializa la variable para el monto total de la orden.
        self.total_orden = 0.0
        
        # 1. Cargar catálogo
        #Llama al metodo para cargar los productos (desde cache o API).
        self.cargar_catalogo()
        
        # 2. Conectar señales
        #Conecta la senal de seleccion del buscador al metodo de agregar producto.
        self.vista.producto_seleccionado.connect(self.agregar_producto_a_orden)
        
        # 3. Inicializar folio
        #Establece un texto placeholder en el campo de folio.
        self.vista.input_folio.setText("NUEVA-VENTA")

        # 4. CONEXIÓN DEL BOTÓN PAGAR
        #Conecta el evento click del boton pagar al metodo de apertura del dialogo.
        self.vista.btn_pagar.clicked.connect(self.abrir_dialogo_pago)

    def cargar_catalogo(self):
        #Imprime mensaje de depuracion.
        print("Caja: Iniciando carga de catálogo...")
        #Intenta obtener los datos del catalogo desde el modulo de variables globales.
        datos_en_memoria = getattr(store_module, 'cache_catalogo', None)

        #Si existen datos en la memoria cache.
        if datos_en_memoria:
            #Imprime confirmacion de uso de cache.
            print("Caja: Usando caché.")
            #Asigna los datos de memoria a la variable local.
            self.catalogo_completo = datos_en_memoria
        #Si no hay datos en cache.
        else:
            #Imprime aviso de descarga.
            print("Caja: Descargando de API...")
            #Cambia el cursor a espera.
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            #Realiza la peticion a la API para obtener productos.
            productos_api = api.obtener_productos()
            #Restaura el cursor normal.
            QApplication.restoreOverrideCursor()
            
            #Si la API devolvio una lista de productos.
            if productos_api:
                #Guarda la lista en la variable local.
                self.catalogo_completo = productos_api
                #Si el modulo global esta disponible.
                if store_module:
                    #Actualiza la cache global con los datos descargados.
                    store_module.cache_catalogo = productos_api
            #Si la API fallo o devolvio vacio.
            else:
                #Inicializa la lista como vacia.
                self.catalogo_completo = []

        #Crea una lista con solo los nombres de los productos para el autocompletado.
        nombres = [p.get("nombre", "") for p in self.catalogo_completo]
        #Asigna la lista de nombres al modelo del autocompletador de la vista.
        self.vista.completer.model().setStringList(nombres)

    def agregar_producto_a_orden(self, nombre_seleccionado):
        #Limpia el campo de texto del buscador.
        self.vista.input_buscar.clear()
        
        #Busca el objeto producto completo en la lista usando el nombre seleccionado.
        producto_encontrado = next((p for p in self.catalogo_completo if p.get("nombre") == nombre_seleccionado), None)
        
        #Si se encontro el producto correspondiente.
        if producto_encontrado:
            #Obtiene el ID del producto.
            p_id = producto_encontrado.get("id_producto")
            #Obtiene el nombre del producto.
            nombre = producto_encontrado.get("nombre")
            #Obtiene y convierte el precio a flotante.
            precio = float(producto_encontrado.get("precio", 0.0))
            
            #Obtiene el ID de categoria.
            cat_id = producto_encontrado.get("id_categoria", 4)
            #Mapea el ID de categoria a un nombre legible.
            mapa_cat = {1: "Bebidas", 2: "Alimentos", 3: "Postres", 4: "General"}
            #Obtiene el nombre de la categoria.
            cat_nombre = mapa_cat.get(cat_id, "General")

            #Crea una instancia del widget visual del producto (fila de la lista).
            item = ProductoItem(p_id, nombre, cat_nombre, precio)
            #Conecta la senal de cambio de cantidad al metodo de recalculo.
            item.cantidad_cambiada.connect(self.recalcular_total)
            #Conecta la senal de eliminar item al metodo de eliminar fila.
            item.eliminar_item.connect(self.eliminar_fila)
            
            #Inserta el nuevo widget en la parte superior de la lista visual.
            self.vista.layout_lista_productos.insertWidget(0, item)
            #Recalcula el total de la orden.
            self.recalcular_total()

    def eliminar_fila(self, item_widget):
        #Remueve el widget del layout visual.
        self.vista.layout_lista_productos.removeWidget(item_widget)
        #Programa la eliminacion del objeto widget de la memoria.
        item_widget.deleteLater()
        #Recalcula el total tras la eliminacion.
        self.recalcular_total() 

    def recalcular_total(self):
        #Inicializa el acumulador del total.
        total = 0.0
        #Obtiene referencia al layout que contiene los productos.
        layout = self.vista.layout_lista_productos
        
        #Itera sobre todos los elementos en el layout.
        for i in range(layout.count()):
            #Obtiene el item del layout en el indice i.
            item = layout.itemAt(i)
            #Si el item es valido.
            if item:
                #Obtiene el widget contenido en el item.
                widget = item.widget()
                #Si es un widget valido y es instancia de ProductoItem.
                if widget and isinstance(widget, ProductoItem):
                    #Calcula el subtotal (precio * cantidad) del widget actual.
                    subtotal = widget.precio_unitario * widget.cantidad_actual
                    #Suma el subtotal al total general.
                    total += subtotal
        
        #Actualiza la variable miembro con el nuevo total.
        self.total_orden = total
        #Actualiza la etiqueta visual del total.
        self.actualizar_label_total()

    def actualizar_label_total(self):
        #Formatea el texto del label con el total a dos decimales.
        self.vista.lbl_total_valor.setText(f"${self.total_orden:.2f}")

    # =======================================================
    # LÓGICA DE PAGO (CORREGIDA Y UNIFICADA)
    # =======================================================

    def abrir_dialogo_pago(self):
        """
        Paso 1: Solo abre la ventana para preguntar método y monto.
        """
        # Validación: No cobrar si está vacío
        #Verifica si el total es menor o igual a cero.
        if self.total_orden <= 0:
            #Instancia el dialogo personalizado de aviso enviando el mensaje y el padre.
            aviso = DialogoAviso("No hay productos para cobrar.", self.vista)
            #Muestra el dialogo y espera a que el usuario lo cierre.
            aviso.exec()
            #Detiene la ejecucion del metodo.
            return

        # Abrimos el diálogo pasándole el total actual (self.total_orden)
        #Instancia el dialogo de pago.
        dialogo = DialogoPago(self.total_orden)
        
        #Si el usuario confirma el dialogo (click en Cobrar/QR).
        if dialogo.exec():
            # Si el usuario da click en COBRAR o GENERAR QR, obtenemos los datos
            #Extrae metodo, monto recibido y referencia del dialogo.
            metodo, monto_recibido, referencia = dialogo.obtener_datos()
            
            # Calculamos el cambio visualmente para pasarlo al dialogo de éxito
            #Inicializa variable cambio.
            cambio = 0.0
            #Si el metodo es efectivo, calcula la diferencia.
            if metodo == "efectivo":
                cambio = monto_recibido - self.total_orden

            # Pasamos la estafeta a la función que habla con la API
            #Llama al metodo encargado de procesar la transaccion con la API.
            self.enviar_pedido_a_api(metodo, referencia, cambio)

    def enviar_pedido_a_api(self, metodo, referencia, cambio_visual):
        """
        Paso 2: Enviar al Backend y Manejar Flujo (Efectivo vs QR)
        """
        # Recolectamos items directamente de la vista (Widgets)
        #Inicializa lista para formatear los items para la API.
        items_api = []
        #Obtiene el layout de productos.
        layout = self.vista.layout_lista_productos
        
        #Itera sobre los widgets para extraer datos.
        for i in range(layout.count()):
            #Obtiene el widget.
            widget = layout.itemAt(i).widget()
            #Si es un widget de producto valido.
            if widget and isinstance(widget, ProductoItem):
                #Agrega diccionario con ID y cantidad a la lista.
                items_api.append({
                    "id_producto": widget.p_id,
                    "cantidad": widget.cantidad_actual,
                    "notas": "" 
                })

        #Pone cursor de espera.
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        # 1. CREAR EL PEDIDO EN EL SERVIDOR
        # Usamos la versión que retorna DATOS (JSON) para obtener el ID
        #Llama a la API para crear el pedido y espera la respuesta con los datos creados.
        respuesta_pedido = api.crear_pedido_manual_retorna_datos(
            lista_items=items_api,
            total=self.total_orden,
            metodo_pago=metodo,
            referencia=referencia
        )
        
        #Restaura cursor.
        QApplication.restoreOverrideCursor()

        #Si no hubo respuesta valida de la API.
        if not respuesta_pedido:
            #Muestra error critico.
            QMessageBox.critical(self.vista, "Error", "No se pudo registrar la venta en la base de datos.")
            #Sale de la funcion.
            return

        #Obtiene el ID del pedido recien creado desde la respuesta.
        pedido_id = respuesta_pedido.get("id_pedido") # Asegúrate que tu API retorna 'id_pedido' o 'id'

        # 2. DECIDIR FLUJO SEGÚN MÉTODO
        #Evalua si el metodo de pago es efectivo.
        if metodo == "efectivo":
            # Flujo Rápido: Ya está pagado
            #Crea el dialogo de exito mostrando el cambio calculado.
            dialogo_exito = DialogoExitoPago(cambio_visual, metodo, self.vista)
            #Muestra el dialogo.
            dialogo_exito.exec()
            #Limpia la interfaz para una nueva venta.
            self.limpiar_orden_completa()
            
        #Evalua si el metodo de pago es transferencia (QR).
        elif metodo == "transferencia":
            # Flujo Mercado Pago
            #Imprime log de generacion de QR.
            print(f"Generando QR para pedido {pedido_id}...")
            
            #Pone cursor de espera.
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            #Solicita a la API el link de pago de Mercado Pago para el pedido.
            link_pago = api.obtener_link_mercadopago(pedido_id)
            #Restaura cursor.
            QApplication.restoreOverrideCursor()
            
            #Si se obtuvo un link de pago valido.
            if link_pago:
                # Mostrar Ventana QR
                #Instancia el dialogo QR con el link y el total.
                dialogo_qr = DialogoQR(link_pago, self.total_orden, self.vista)
                
                #Ejecuta el dialogo y espera el resultado (Aceptar/Cancelar).
                if dialogo_qr.exec(): 
                    # Si el cajero confirma el pago visualmente
                    #Llama a la API para confirmar el pago del pedido en la BD.
                    api.confirmar_pago_pedido(pedido_id)
                    
                    # Mostramos éxito (Cambio 0 en transferencia)
                    #Muestra dialogo de exito.
                    dialogo_exito = DialogoExitoPago(0, "transferencia", self.vista)
                    dialogo_exito.exec()
                    #Limpia la orden.
                    self.limpiar_orden_completa()
                #Si el usuario cierra el dialogo QR sin confirmar pago.
                else:
                    # Si cierra el QR sin confirmar
                    #Informa que el pedido quedo pendiente.
                    QMessageBox.information(self.vista, "Pendiente", "El pedido se guardó PENDIENTE de pago.")
                    #Limpia la orden de la pantalla.
                    self.limpiar_orden_completa()
            #Si fallo la obtencion del link.
            else:
                #Muestra error.
                QMessageBox.warning(self.vista, "Error", "Se creó el pedido pero falló la generación del QR.")
                # Opcional: limpiar o dejar el pedido ahí
                #Limpia la orden.
                self.limpiar_orden_completa()

    def limpiar_orden_completa(self):
        """Resetea la pantalla"""
        #Obtiene referencia al layout.
        layout = self.vista.layout_lista_productos
        # Borrar widgets de forma segura
        #Itera mientras haya elementos en el layout.
        while layout.count():
            #Toma el primer elemento.
            item = layout.takeAt(0)
            #Si tiene un widget asociado.
            if item.widget(): 
                #Elimina el widget de memoria.
                item.widget().deleteLater()
            
        #Resetea la variable de total.
        self.total_orden = 0.0
        #Limpia el buscador.
        self.vista.input_buscar.clear()
        #Actualiza la etiqueta de total a cero.
        self.actualizar_label_total()
        #Resetea el folio.
        self.vista.input_folio.setText("NUEVA-VENTA")