# BITCAFE - VERSION 2.0 (Sincronización Reforzada + Horarios Automáticos - REACTIVA)
# By: Angel A. Higuera & Gemini Partner

from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap 
from Modelo.api_client import api
from Vista.vista_pedido_manual import ProductoItem

# --- IMPORTACIÓN DE VISTAS ---
from Vista.dialogo_pagar import DialogoPago
from Vista.dialogo_exito_pago import DialogoExitoPago
from Vista.dialogo_carrito_vacio import DialogoAviso
from Vista.dialogo_ticket import DialogoTicket

import qrcode
from io import BytesIO
from datetime import datetime, time

class ControladorPedidoManual:
    def __init__(self, modelo_api, vista_manual):
        self.api = modelo_api
        self.vista = vista_manual
        self.catalogo_completo = []
        self.total_orden = 0.0
        self.horarios_cache = None # Guardamos los horarios para no saturar la API

        # 1. Carga inicial
        self.refrescar_todo()

        # 2. CONEXIONES DE SEÑALES
        self.vista.producto_seleccionado.connect(self.agregar_producto_a_orden)
        self.vista.input_folio.setText("NUEVA-VENTA")
        self.vista.btn_pagar.clicked.connect(self.abrir_dialogo_pago)
        self.vista.btn_imprimir.clicked.connect(self.previsualizar_ticket_actual)

        # --- REVALIDACIÓN DINÁMICA ---
        # Verificamos al escribir para que el usuario sienta el desbloqueo inmediato
        self.vista.input_buscar.textChanged.connect(self.verificar_estado_tienda_visual)
        
        # Timer para verificar cada 30 segundos
        self.timer_auto_bloqueo = QTimer()
        self.timer_auto_bloqueo.timeout.connect(self.verificar_estado_tienda_visual)
        self.timer_auto_bloqueo.start(30000) 

    def verificar_estado_tienda_visual(self):
        """Bloquea o desbloquea la interfaz basándose en Switch y Horario."""
        try:
            # A) Obtener estados
            estado_manual = self.api.obtener_estado_tienda()
            esta_en_horario = self.validar_horario_operacion()
            
            estado_final_abierto = estado_manual and esta_en_horario
            
            self.vista.input_buscar.blockSignals(True)
            
            # Actualizamos UI
            self.vista.input_buscar.setEnabled(estado_final_abierto)
            self.vista.btn_pagar.setEnabled(estado_final_abierto)
            
            if not estado_final_abierto:
                if not estado_manual:
                    motivo = "🚫 TIENDA CERRADA (Manual)"
                else:
                    motivo = "🚫 FUERA DE HORARIO"
                
                self.vista.input_buscar.setPlaceholderText(motivo)
                self.vista.btn_pagar.setStyleSheet("background-color: #888888; color: #CCCCCC; border-radius: 12px;")
                if self.vista.input_buscar.text():
                    self.vista.input_buscar.clear()
            else:
                self.vista.input_buscar.setPlaceholderText("Buscar producto...")
                self.vista.btn_pagar.setStyleSheet("background-color: #D22A00; color: white; border-radius: 12px; font-weight: bold;")
            
            self.vista.input_buscar.blockSignals(False)
            return estado_final_abierto

        except Exception as e:
            print(f"Error verificando estado visual: {e}")
            return True 

    def validar_horario_operacion(self):
        """Versión robusta: usa índices numéricos para evitar errores de idioma/acentos."""
        try:
            # Sincronización fresca de horarios
            res_horarios = self.api.obtener_horarios()
            if res_horarios and "error" not in res_horarios:
                self.horarios_cache = res_horarios
            
            if not self.horarios_cache: return True 
            
            ahora = datetime.now()
            # Mapeo universal basado en el índice de la semana de Python (0=Lunes, 6=Domingo)
            dias_index = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
            dia_hoy = dias_index[ahora.weekday()]
            
            if dia_hoy not in self.horarios_cache: 
                return True 
            
            config = self.horarios_cache[dia_hoy]
            if config.get("cerrado", False): return False
            
            h_actual = ahora.time()
            formato = "%H:%M"
            
            # Convertir strings "HH:MM" asegurando limpieza de espacios
            hora_inicio = datetime.strptime(config["inicio"].strip(), formato).time()
            hora_fin = datetime.strptime(config["fin"].strip(), formato).time()
            
            return hora_inicio <= h_actual <= hora_fin
            
        except Exception as e:
            print(f"Error crítico en validación de horario: {e}")
            return True

    def cargar_catalogo(self, mostrar_todo=True):
        """Descarga productos y normaliza flags de disponibilidad."""
        try:
            productos_api = self.api.obtener_productos()
            if productos_api:
                for p in productos_api:
                    estado = p.get("esta_disponible", p.get("disponible", True))
                    p["disponible"] = estado
                    p["esta_disponible"] = estado
                self.catalogo_completo = productos_api
            else:
                self.catalogo_completo = []

            nombres = [p.get("nombre", "") for p in self.catalogo_completo]
            self.vista.completer.model().setStringList(nombres)
        except:
            print("Error al cargar catálogo.")

    def agregar_producto_a_orden(self, nombre_seleccionado):
        """Añade item al carrito validando tienda y stock actual."""
        if not self.verificar_estado_tienda_visual():
            self.vista.input_buscar.clear()
            DialogoAviso("🚫 OPERACIÓN DENEGADA\n\nLa tienda está cerrada o fuera de horario.", self.vista).exec()
            return

        self.vista.input_buscar.clear()
        producto = next((p for p in self.catalogo_completo if p.get("nombre") == nombre_seleccionado), None)

        if producto:
            disponible = str(producto.get("disponible")).lower() in ["true", "1", "t"]
            
            if not disponible:
                self.cargar_catalogo()
                DialogoAviso(f"🚫 PRODUCTO NO DISPONIBLE\n\n'{nombre_seleccionado}' se ha desactivado.", self.vista).exec()
                return 
            
            p_id = producto.get("id_producto")
            precio = float(producto.get("precio", 0.0))
            url_img = producto.get("imagen") or producto.get("url_imagen") or ""
            
            item = ProductoItem(p_id, producto.get("nombre"), "General", precio, url_imagen=url_img)
            item.cantidad_cambiada.connect(self.recalcular_total)
            item.eliminar_item.connect(self.eliminar_fila)

            self.vista.layout_lista_productos.insertWidget(0, item)
            self.recalcular_total()

    def abrir_dialogo_pago(self):
        """Inicia el flujo de cobro con validación de seguridad final."""
        if not self.verificar_estado_tienda_visual():
            DialogoAviso("🚫 TIENDA CERRADA\n\nNo se pueden procesar pagos.", self.vista).exec()
            return

        if self.total_orden <= 0:
            DialogoAviso("⚠️ Carrito vacío.", self.vista).exec()
            return

        self.ejecutar_flujo_pago()

    def ejecutar_flujo_pago(self):
        """Maneja la lógica de QR y métodos de pago."""
        items_api, items_ticket = [], []
        layout = self.vista.layout_lista_productos
        
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ProductoItem):
                items_api.append({"id_producto": widget.p_id, "cantidad": widget.cantidad_actual, "notas": ""})
                items_ticket.append({"nombre": widget.nombre, "cantidad": widget.cantidad_actual, "precio": widget.precio_unitario})

        dialogo = DialogoPago(self.total_orden, self.vista)
        
        def cargar_qr(index):
            if index == 1: 
                try:
                    res = self.api.crear_pedido_manual_retorna_datos(items_api, self.total_orden, "transferencia", "PENDIENTE_QR")
                    if res and "id_pedido" in res:
                        id_real = res.get("id_pedido")
                        link = self.api.obtener_link_mercadopago(id_real)
                        if link:
                            qr = qrcode.QRCode(box_size=10, border=2)
                            qr.add_data(str(link))
                            buffer = BytesIO()
                            qr.make_image(fill_color="black", back_color="white").save(buffer, format="PNG")
                            pixmap = QPixmap()
                            pixmap.loadFromData(buffer.getvalue())
                            dialogo.mostrar_qr(pixmap)
                            dialogo.id_pedido_actual = id_real 
                except Exception as e:
                    print(f"Error generando QR: {e}")

        dialogo.tabs.currentChanged.connect(cargar_qr)

        if dialogo.exec():
            metodo, monto, *ref = dialogo.obtener_datos()
            referencia = ref[0] if ref else ""
            
            if metodo == "transferencia":
                id_f = getattr(dialogo, 'id_pedido_actual', "N/A")
                DialogoTicket({"id_pedido": id_f, "total": self.total_orden, "items": items_ticket, "metodo_pago": "TRANSFERENCIA"}, self.vista).exec()
                DialogoExitoPago(0.0, metodo, self.vista).exec()
                self.limpiar_orden_completa()
            else:
                self.enviar_pedido_a_api(metodo, referencia, monto - self.total_orden)

    def enviar_pedido_a_api(self, metodo, referencia, cambio_visual):
        items_api, items_ticket = [], []
        layout = self.vista.layout_lista_productos
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ProductoItem):
                items_ticket.append({"nombre": widget.nombre, "cantidad": widget.cantidad_actual, "precio": widget.precio_unitario})
                items_api.append({"id_producto": widget.p_id, "cantidad": widget.cantidad_actual, "notas": ""})

        res = self.api.crear_pedido_manual_retorna_datos(items_api, self.total_orden, metodo, referencia)
        if res:
            DialogoTicket({"id_pedido": res.get("id_pedido", "N/A"), "total": self.total_orden, "items": items_ticket, "metodo_pago": metodo}, self.vista).exec()
            DialogoExitoPago(cambio_visual, metodo, self.vista).exec()
            self.limpiar_orden_completa()
        else:
            QMessageBox.critical(self.vista, "Error", "No se pudo registrar la venta.")

    def recalcular_total(self):
        total = 0.0
        layout = self.vista.layout_lista_productos
        for i in range(layout.count()):
            item = layout.itemAt(i).widget()
            if isinstance(item, ProductoItem):
                total += (item.precio_unitario * item.cantidad_actual)
        self.total_orden = total
        self.vista.lbl_total_valor.setText(f"${self.total_orden:.2f}")

    def eliminar_fila(self, item_widget):
        self.vista.layout_lista_productos.removeWidget(item_widget)
        item_widget.deleteLater()
        QTimer.singleShot(10, self.recalcular_total)

    def limpiar_orden_completa(self):
        layout = self.vista.layout_lista_productos
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.total_orden = 0.0
        self.vista.lbl_total_valor.setText("$0.00")
        self.vista.input_folio.setText("NUEVA-VENTA")

    def previsualizar_ticket_actual(self):
        if self.total_orden <= 0: return
        items = []
        layout = self.vista.layout_lista_productos
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ProductoItem):
                items.append({"nombre": widget.nombre, "cantidad": widget.cantidad_actual, "precio": widget.precio_unitario})
        DialogoTicket({"id_pedido": "PREVIA", "total": self.total_orden, "items": items, "metodo_pago": "PREVIA"}, self.vista).exec()

    def refrescar_todo(self):
        """Fuerza la recarga total."""
        self.cargar_catalogo()
        self.verificar_estado_tienda_visual()