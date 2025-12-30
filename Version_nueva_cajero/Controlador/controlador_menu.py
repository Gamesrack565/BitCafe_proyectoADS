# BITCAFE
# VERSION 1.2 (Gestión de Menú - Sincronización en Tiempo Real)
# By: Angel A. Higuera y Gemini Partner

from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from Modelo.api_client import api
from Vista.vista_menu import ProductoAdminItem
from Vista.dialogo_agregar import DialogoProducto as DialogoCrear
from Vista.dialogo_editar import DialogoProducto as DialogoEditar 
from Vista.dialogo_eliminaciones import DialogoConfirmarEliminar, DialogoExitoEliminar

# --- VARIABLE COMPARTIDA (CACHE GLOBAL) ---
try:
    import Modelo.variables as store_module
except ImportError:
    store_module = None 

# --- HILO CARGAR MENU ---
class HiloCargarMenu(QThread):
    datos_cargados = pyqtSignal(list)

    def run(self):
        try:
            print("Hilo Menu: Descargando productos...")
            productos = api.obtener_productos()
            self.datos_cargados.emit(productos if productos else [])
        except Exception as e:
            print(f"Error en hilo menú: {e}")
            self.datos_cargados.emit([])

# --- CONTROLADOR PRINCIPAL ---
class ControladorMenu:
    def __init__(self, modelo_api, vista_menu):
        self.modelo_api = modelo_api
        self.vista = vista_menu
        self.productos_locales = [] 
        
        self.vista.btn_add.clicked.connect(self.abrir_crear_producto)
        self.iniciar_carga_tabla()
    
    def _generar_url_imagen(self, nombre_producto, imagen_path_relativo):
        path_str = str(imagen_path_relativo).strip() if imagen_path_relativo is not None else ''
        if not path_str or path_str.lower() == 'none':
            return None

        URL_BASE = api.BASE_URL
        base_limpia = URL_BASE.rstrip('/')
        path_limpio = path_str.lstrip('/')
        
        if not path_limpio.startswith("static_images/"):
            path_limpio = f"static_images/{path_limpio}"
            
        return f"{base_limpia}/{path_limpio}"

    def iniciar_carga_tabla(self):
        print("Controlador: Iniciando carga de red...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.vista.btn_add.setEnabled(False)

        self.hilo = HiloCargarMenu()
        self.hilo.datos_cargados.connect(self.recibir_datos_api) 
        self.hilo.finished.connect(self.finalizar_carga) 
        self.hilo.start()

    def finalizar_carga(self):
        QApplication.restoreOverrideCursor()
        self.vista.btn_add.setEnabled(True)

    def recibir_datos_api(self, productos):
        self.productos_locales = productos
        if store_module:
            store_module.cache_catalogo = productos
        self.renderizar_tabla(self.productos_locales)

    def renderizar_nuevo_producto(self, p_data):
        p_id = p_data.get("id_producto")
        if p_id is None: return 

        nombre = p_data.get("nombre", "---")
        cat_id = p_data.get("id_categoria", 4)
        mapa_cat = {1: "Bebidas", 2: "Alimentos", 3: "Postres", 4: "General"}
        cat_nombre = mapa_cat.get(cat_id, "General")
        precio = p_data.get("precio", 0.0)
        activo = p_data.get("esta_disponible", True)

        imagen_path_relativo = p_data.get("ruta_imagen") 
        imagen_url_completa = self._generar_url_imagen(nombre, imagen_path_relativo)
        
        item = ProductoAdminItem(nombre, cat_nombre, precio, activo, imagen_url=imagen_url_completa)
        
        item.switch.clicked.connect(lambda chk, pid=p_id, it=item: self.cambiar_disponibilidad(pid, it))
        item.btn_edit.clicked.connect(lambda chk, pid=p_id, data=p_data: self.abrir_editar_producto(pid, data))
        item.btn_del.clicked.connect(lambda chk, pid=p_id: self.eliminar_producto(pid))
        item.status_changed.connect(self.vista.filtrar_lista)

        self.vista.layout_items.insertWidget(0, item)

    def renderizar_tabla(self, lista_productos):
        self.vista.limpiar_lista()
        if not lista_productos: return

        for p in lista_productos:
            p_id = p.get("id_producto")
            if p_id is None: continue 

            nombre = p.get("nombre", "---")
            cat_id = p.get("id_categoria", 4)
            mapa_cat = {1: "Bebidas", 2: "Alimentos", 3: "Postres", 4: "General"}
            cat_nombre = mapa_cat.get(cat_id, "General")
            precio = p.get("precio", 0.0)
            activo = p.get("esta_disponible", True)
            imagen_path_relativo = p.get("ruta_imagen") 
            imagen_url_completa = self._generar_url_imagen(nombre, imagen_path_relativo)
            
            item = ProductoAdminItem(nombre, cat_nombre, precio, activo, imagen_url=imagen_url_completa)
            item.switch.clicked.connect(lambda chk, pid=p_id, it=item: self.cambiar_disponibilidad(pid, it))
            item.btn_edit.clicked.connect(lambda chk, pid=p_id, data=p: self.abrir_editar_producto(pid, data))
            item.btn_del.clicked.connect(lambda chk, pid=p_id: self.eliminar_producto(pid))
            item.status_changed.connect(self.vista.filtrar_lista)

            self.vista.layout_items.addWidget(item)

    def actualizar_cache_local(self, p_id, datos_nuevos):
        """Sincroniza el cambio tanto en la lista local como en la global para la Caja."""
        for i, prod in enumerate(self.productos_locales):
            if prod.get("id_producto") == p_id:
                # Actualizamos los campos necesarios (disponible vs esta_disponible)
                if "esta_disponible" in datos_nuevos:
                    # Sincronizamos ambos nombres de variable por seguridad entre vistas
                    datos_nuevos["disponible"] = datos_nuevos["esta_disponible"]
                
                self.productos_locales[i].update(datos_nuevos)
                break
        
        if store_module:
            store_module.cache_catalogo = self.productos_locales

    def cambiar_disponibilidad(self, p_id, item_widget):
        nuevo_estado = item_widget.switch.isChecked()
        resultado = api.actualizar_producto(p_id, {"esta_disponible": nuevo_estado})

        if resultado:
            # Sincronización total: Local y Global
            self.actualizar_cache_local(p_id, {"esta_disponible": nuevo_estado})
            
            item_widget.switch.setChecked(nuevo_estado)
            self.vista.filtrar_lista()
            
            # Forzamos persistencia visual
            item_widget.show()
            item_widget.setVisible(True)
            item_widget.setEnabled(True)
            
            print(f"Sync: Producto {p_id} ahora disponible={nuevo_estado} en todo el sistema.")
        else:
            item_widget.switch.setChecked(not nuevo_estado)
            QMessageBox.warning(self.vista, "Error", "No se pudo actualizar en el servidor.")

    def abrir_editar_producto(self, p_id, data_actual):
        dialogo = DialogoEditar(self.vista, producto_data=data_actual)
        if dialogo.exec():
            datos, ruta_img = dialogo.obtener_datos_formulario()
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            resultado = api.actualizar_producto(p_id, datos, ruta_img)
            QApplication.restoreOverrideCursor()

            if isinstance(resultado, dict) and 'status_code' not in resultado:
                self.actualizar_cache_local(p_id, resultado)
                self.renderizar_tabla(self.productos_locales)
                QMessageBox.information(self.vista, "Éxito", "Producto actualizado exitosamente.")
            else:
                QMessageBox.critical(self.vista, "Error", "Fallo al actualizar.")

    def abrir_crear_producto(self):
        dialogo = DialogoCrear(self.vista)
        if dialogo.exec():
            datos, ruta_img = dialogo.obtener_datos_formulario()
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            resultado = api.crear_producto(datos, ruta_img) 
            QApplication.restoreOverrideCursor()
            
            if isinstance(resultado, dict) and 'status_code' not in resultado:
                self.productos_locales.insert(0, resultado)
                if store_module:
                    store_module.cache_catalogo = self.productos_locales
                self.renderizar_nuevo_producto(resultado)
                QMessageBox.information(self.vista, "Éxito", "Producto creado exitosamente.")
            else:
                QMessageBox.critical(self.vista, "Error", "Fallo al crear.")

    def eliminar_producto(self, p_id):
        dialogo_conf = DialogoConfirmarEliminar(self.vista)
        if dialogo_conf.exec():
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            exito = api.eliminar_producto(p_id)
            QApplication.restoreOverrideCursor()
            
            if exito:
                self.productos_locales = [p for p in self.productos_locales if p.get("id_producto") != p_id]
                if store_module:
                    store_module.cache_catalogo = self.productos_locales
                self.renderizar_tabla(self.productos_locales)
                DialogoExitoEliminar(self.vista).exec()
            else:
                QMessageBox.warning(self.vista, "Error", "No se pudo eliminar.")