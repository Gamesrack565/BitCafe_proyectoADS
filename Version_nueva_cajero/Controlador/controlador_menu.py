#BITCAFE
#VERSION 1.0 (Gestión de Menú y Productos)
#By: Angel A. Higuera

#Librerías y modulos
#Importa componentes de interfaz grafica de PyQt6: QMessageBox, QApplication.
from PyQt6.QtWidgets import QMessageBox, QApplication
#Importa componentes del nucleo de PyQt6: constantes Qt, QThread, pyqtSignal.
from PyQt6.QtCore import Qt, QThread, pyqtSignal
#Importa el cliente de API para realizar peticiones al backend.
from Modelo.api_client import api
#Importa el widget personalizado para representar un producto en la lista.
from Vista.vista_menu import ProductoAdminItem
#Importa el dialogo para crear nuevos productos.
from Vista.dialogo_agregar import DialogoProducto as DialogoCrear
#Importa el dialogo para editar productos existentes.
from Vista.dialogo_editar import DialogoProducto as DialogoEditar 
#Importa los dialogos de confirmacion y exito para eliminaciones.
from Vista.dialogo_eliminaciones import DialogoConfirmarEliminar, DialogoExitoEliminar

# --- VARIABLE COMPARTIDA (CACHE GLOBAL) ---
#Intenta importar el modulo de variables globales.
try:
    import Modelo.variables as store_module
#Si falla la importacion (ej. ejecutando solo este archivo).
except ImportError:
    #Define la variable como None por seguridad (fallback).
    store_module = None 

# --- HILO CARGAR MENU ---
#Clase que maneja la carga de productos en un hilo separado para no congelar la UI.
class HiloCargarMenu(QThread):
    #Senal que emite una lista de productos cuando la carga finaliza.
    datos_cargados = pyqtSignal(list)

    def run(self):
        #Inicia bloque de manejo de errores.
        try:
            #Imprime mensaje de depuracion en consola.
            print("Hilo Menu: Descargando productos...")
            #Llama a la API para obtener la lista de productos.
            productos = api.obtener_productos()
            #Emite la senal con los productos obtenidos (o lista vacia si es None).
            self.datos_cargados.emit(productos if productos else [])
        #Captura cualquier excepcion durante la descarga.
        except Exception as e:
            #Imprime el error especifico.
            print(f"Error en hilo menú: {e}")
            #Emite una lista vacia para evitar errores en la UI.
            self.datos_cargados.emit([])

# --- CONTROLADOR PRINCIPAL ---
class ControladorMenu:
    def __init__(self, vista_menu):
        #Guarda referencia a la vista principal del menu.
        self.vista = vista_menu
        #Inicializa la lista local de productos (copia maestra).
        self.productos_locales = [] 
        
        #Conecta el evento click del boton 'Agregar' al metodo de apertura.
        self.vista.btn_add.clicked.connect(self.abrir_crear_producto)
        #Inicia la carga inicial de datos.
        self.iniciar_carga_tabla()

    def iniciar_carga_tabla(self):
        """Descarga inicial completa desde API"""
        #Imprime log de inicio.
        print("Controlador: Iniciando carga de red...")
        #Cambia el cursor a 'reloj de arena' para indicar espera.
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        #Deshabilita el boton de agregar para evitar acciones simultaneas.
        self.vista.btn_add.setEnabled(False)

        #Instancia el hilo de carga.
        self.hilo = HiloCargarMenu()
        #Conecta la senal de datos cargados al metodo receptor.
        self.hilo.datos_cargados.connect(self.recibir_datos_api) 
        #Conecta la senal de finalizacion para restaurar la UI.
        self.hilo.finished.connect(self.finalizar_carga) 
        #Inicia la ejecucion del hilo.
        self.hilo.start()

    def finalizar_carga(self):
        #Restaura el cursor normal.
        QApplication.restoreOverrideCursor()
        #Rehabilita el boton de agregar.
        self.vista.btn_add.setEnabled(True)

    def recibir_datos_api(self, productos):
        """Callback cuando llega data de la RED"""
        #Guarda los productos recibidos en la variable local.
        self.productos_locales = productos
        
        #Si el modulo de almacenamiento global esta disponible.
        if store_module:
            #Actualiza la cache global con los nuevos datos (util para Caja).
            store_module.cache_catalogo = productos
            
        #Llama al metodo para dibujar la tabla con los datos recibidos.
        self.renderizar_tabla(self.productos_locales)

    def renderizar_tabla(self, lista_productos):
        """Dibuja la UI basado en una lista (sin descargar nada)"""
        #Imprime log de renderizado.
        print(f"Controlador: Renderizando {len(lista_productos)} productos.")
        #Limpia los items actuales de la vista.
        self.vista.limpiar_lista()
        
        #Si la lista esta vacia, termina la funcion.
        if not lista_productos: return

        #Itera sobre cada producto de la lista.
        for p in lista_productos:
            #Obtiene el ID del producto de forma segura.
            p_id = p.get("id_producto")
            #Si no tiene ID, salta al siguiente ciclo.
            if p_id is None: continue 

            #Obtiene el nombre o usa guiones por defecto.
            nombre = p.get("nombre", "---")
            #Obtiene el ID de categoria, por defecto 4 (General).
            cat_id = p.get("id_categoria", 4)
            #Diccionario de mapeo simple para nombres de categorias.
            mapa_cat = {1: "Bebidas", 2: "Alimentos", 3: "Postres", 4: "General"}
            #Obtiene el nombre de la categoria segun el ID.
            cat_nombre = mapa_cat.get(cat_id, "General")
            
            #Obtiene el precio del producto.
            precio = p.get("precio", 0.0)
            #Obtiene el estado de disponibilidad.
            activo = p.get("esta_disponible", True)

            #Crea el widget visual del item pasando los datos.
            item = ProductoAdminItem(nombre, cat_nombre, precio, activo)
            
            # Conexiones con lambdas
            #Conecta el switch de disponibilidad pasando el ID y el objeto item.
            item.switch.clicked.connect(lambda chk, pid=p_id, it=item: self.cambiar_disponibilidad(pid, it))
            #Conecta el boton de editar pasando el ID y la data completa.
            item.btn_edit.clicked.connect(lambda chk, pid=p_id, data=p: self.abrir_editar_producto(pid, data))
            #Conecta el boton de eliminar pasando solo el ID.
            item.btn_del.clicked.connect(lambda chk, pid=p_id: self.eliminar_producto(pid))

            #Agrega el widget creado al layout de la vista.
            self.vista.layout_items.addWidget(item)


    def actualizar_cache_local(self, p_id, datos_nuevos):
        """
        Busca el producto en la lista local y actualiza sus campos.
        Esto evita tener que volver a llamar a la API para ver los cambios.
        """
        #Itera sobre la lista local con indice.
        for i, prod in enumerate(self.productos_locales):
            #Si encuentra el producto con el ID buscado.
            if prod.get("id_producto") == p_id:
                #Actualiza el diccionario existente con los nuevos valores.
                self.productos_locales[i].update(datos_nuevos)
                #Rompe el ciclo una vez encontrado.
                break
        
        #Verifica si existe el modulo global.
        if store_module:
            #Sincroniza la cache global con la lista local actualizada.
            store_module.cache_catalogo = self.productos_locales

    def cambiar_disponibilidad(self, p_id, item_widget):
        #Obtiene el nuevo estado (booleano) del switch visual.
        nuevo_estado = item_widget.switch.isChecked()
        
        # 1. Llamada API (Rápida gracias a Session)
        #Llama a la API para actualizar solo el campo 'esta_disponible'.
        exito = api.actualizar_producto(p_id, {"esta_disponible": nuevo_estado})

        #Si la actualizacion en el servidor fue exitosa.
        if exito:
            # 2. OPTIMIZACIÓN: Solo actualizamos memoria, no recargamos tabla
            #Actualiza el estado en la lista local.
            self.actualizar_cache_local(p_id, {"esta_disponible": nuevo_estado})
            #Confirma en consola.
            print(f"Estado producto {p_id} actualizado en memoria.")
        #Si hubo error en la API.
        else:
            #Revertir switch visualmente a su estado anterior.
            item_widget.switch.setChecked(not nuevo_estado)
            #Muestra mensaje de advertencia al usuario.
            QMessageBox.warning(self.vista, "Error", "No se pudo actualizar.")

    def abrir_editar_producto(self, p_id, data_actual):
        #Crea e instancia el dialogo de edicion con los datos actuales.
        dialogo = DialogoEditar(self.vista, producto_data=data_actual)
        #Ejecuta el dialogo y espera respuesta (modal).
        if dialogo.exec():
            #Obtiene los datos del formulario si el usuario acepto.
            datos, _ = dialogo.obtener_datos_formulario()
            
            #Pone cursor de espera.
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            #Llama a la API para actualizar el producto.
            exito = api.actualizar_producto(p_id, datos)
            #Restaura cursor.
            QApplication.restoreOverrideCursor()
            
            #Si la actualizacion fue exitosa.
            if exito:
                # 1. Actualizamos memoria local con los nuevos datos.
                self.actualizar_cache_local(p_id, datos)
                # 2. Re-renderizamos tabla usando memoria local (INSTANTÁNEO).
                self.renderizar_tabla(self.productos_locales)
            #Si fallo la actualizacion.
            else:
                #Muestra error critico.
                QMessageBox.critical(self.vista, "Error", "Fallo al actualizar producto.")

    def abrir_crear_producto(self):
        #Crea e instancia el dialogo de creacion.
        dialogo = DialogoCrear(self.vista)
        #Ejecuta el dialogo.
        if dialogo.exec():
            #Obtiene datos y ruta de imagen del formulario.
            datos, ruta_img = dialogo.obtener_datos_formulario()
            
            #Pone cursor de espera.
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            #Llama a la API para crear el producto.
            exito = api.crear_producto(datos, ruta_img)
            #Restaura cursor.
            QApplication.restoreOverrideCursor()
            
            #Si la creacion fue exitosa.
            if exito:
                #Aquí sí recargamos todo porque necesitamos el ID nuevo que genera la DB.
                self.iniciar_carga_tabla()
            #Si fallo.
            else:
                #Muestra error critico.
                QMessageBox.critical(self.vista, "Error", "Fallo al crear producto.")

    def eliminar_producto(self, p_id):
        #Crea dialogo de confirmacion de eliminacion.
        dialogo_conf = DialogoConfirmarEliminar(self.vista)
        #Si el usuario confirma la accion.
        if dialogo_conf.exec():
            #Pone cursor de espera.
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            #Llama a la API para eliminar el producto.
            exito = api.eliminar_producto(p_id)
            #Restaura cursor.
            QApplication.restoreOverrideCursor()
            
            #Si la eliminacion fue exitosa.
            if exito:
                # OPTIMIZACIÓN: Eliminar de local y repintar (Más rápido que descargar)
                #Filtra la lista local quitando el producto eliminado.
                self.productos_locales = [p for p in self.productos_locales if p.get("id_producto") != p_id]
                
                #Si existe el modulo global.
                if store_module:
                    #Actualiza la cache global.
                    store_module.cache_catalogo = self.productos_locales
                
                #Vuelve a dibujar la tabla con la lista filtrada.
                self.renderizar_tabla(self.productos_locales)
                
                # Feedback
                #Muestra dialogo de exito.
                DialogoExitoEliminar(self.vista).exec()
            #Si fallo la eliminacion.
            else:
                #Muestra mensaje de advertencia.
                QMessageBox.warning(self.vista, "Error", "No se pudo eliminar.")