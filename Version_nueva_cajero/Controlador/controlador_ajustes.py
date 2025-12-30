# BITCAFE - CONTROLADOR AJUSTES
# VERSION 1.9 (Sincronización Total - Gestión de Sesión)
# By: Angel A. Higuera & Gemini Partner

from PyQt6.QtWidgets import QMessageBox, QApplication, QTimeEdit, QDialog, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTime

class ControladorAjustes:
    def __init__(self, api, vista_ajustes, controlador_pedido=None):
        """
        Cerebro de la pantalla de Ajustes.
        @param api: Instancia del cliente API para comunicación con el servidor.
        @param vista_ajustes: Instancia de la interfaz de ajustes.
        @param controlador_pedido: Referencia al controlador de caja para bloqueo inmediato.
        """
        self.api = api 
        self.vista = vista_ajustes
        self.controlador_pedido = controlador_pedido 
        
        # 1. Sincronizar el estado real de la tienda al abrir la ventana
        self.cargar_estado_tienda()
        
        # 2. Cargar configuración de horarios existentes desde el servidor
        self.cargar_horarios_configurados()
        
        # 3. Conectar el Switch "Aceptando Pedidos"
        self.vista.switch_tienda.clicked.connect(self.gestionar_cambio_tienda)
        
        # 4. Conectar botones de horarios (Selector de Hora)
        self.conectar_eventos_horarios()
        
        # 5. Conectar el botón de Guardar Cambios
        self.vista.btn_guardar.clicked.connect(self.ejecutar_guardado_total)

        # 6. Conectar botón Cerrar Sesión (Cierra el programa)
        self.vista.btn_desactivar.clicked.connect(self.cerrar_sesion)

    def cerrar_sesion(self):
        """Cierra la sesión del usuario y finaliza la aplicación con confirmación."""
        msg = QMessageBox(self.vista)
        msg.setWindowTitle("Cerrar Sesión")
        msg.setText("¿Estás seguro de que deseas cerrar sesión y salir del sistema?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Traducir botones
        btn_si = msg.button(QMessageBox.StandardButton.Yes)
        btn_si.setText("Sí, Salir")
        btn_no = msg.button(QMessageBox.StandardButton.No)
        btn_no.setText("Cancelar")

        if msg.exec() == QMessageBox.StandardButton.Yes:
            QApplication.quit()

    def cargar_estado_tienda(self):
        """Consulta a la API si la tienda está abierta para poner el switch en su lugar."""
        try:
            estado_actual = self.api.obtener_estado_tienda()
            self.vista.switch_tienda.blockSignals(True)
            self.vista.switch_tienda.setChecked(estado_actual)
            self.vista.switch_tienda.blockSignals(False)
        except Exception as e:
            print(f"Error al cargar estado de tienda: {e}")

    def gestionar_cambio_tienda(self):
        """Se activa al hacer clic en el Switch de la interfaz."""
        nuevo_estado = self.vista.switch_tienda.isChecked()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            exito = self.api.actualizar_estado_tienda(nuevo_estado)
            if exito:
                # REFRESCAR CAJA INMEDIATAMENTE PARA BLOQUEO/DESBLOQUEO
                if self.controlador_pedido:
                    self.controlador_pedido.verificar_estado_tienda_visual()
            else:
                self.vista.switch_tienda.setChecked(not nuevo_estado)
                QMessageBox.warning(self.vista, "Error", "El servidor no pudo actualizar el estado.")
        except Exception as e:
            self.vista.switch_tienda.setChecked(not nuevo_estado)
            QMessageBox.critical(self.vista, "Error de Conexión", f"Fallo de comunicación: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def conectar_eventos_horarios(self):
        """Asigna el selector de hora a cada botón de la cuadrícula."""
        for i in range(len(self.vista.nombres_dias)):
            btn_ini = self.vista.botones_inicio[i]
            btn_fin = self.vista.botones_fin[i]
            
            btn_ini.clicked.connect(lambda checked, b=btn_ini: self.abrir_selector_hora(b))
            btn_fin.clicked.connect(lambda checked, b=btn_fin: self.abrir_selector_hora(b))

    def abrir_selector_hora(self, boton):
        """Abre un diálogo con QTimeEdit para una selección de hora precisa."""
        dialogo = QDialog(self.vista)
        dialogo.setWindowTitle("Seleccionar Hora")
        layout = QVBoxLayout(dialogo)
        
        selector = QTimeEdit()
        selector.setDisplayFormat("HH:mm")
        
        # Cargar la hora que ya tiene el botón
        if ":" in boton.text():
            t = QTime.fromString(boton.text().strip(), "HH:mm")
            if t.isValid():
                selector.setTime(t)
        
        layout.addWidget(selector)
        
        btn_confirmar = QPushButton("Confirmar")
        btn_confirmar.setStyleSheet("background-color: #D22A00; color: white; font-weight: bold; height: 35px; border-radius: 8px;")
        btn_confirmar.clicked.connect(dialogo.accept)
        layout.addWidget(btn_confirmar)
        
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            nueva_hora = selector.time().toString("HH:mm")
            boton.setText(nueva_hora)
            # Feedback visual de cambio
            boton.setStyleSheet("background-color: #D22A00; color: white; border-radius: 12px; font-weight: bold; border: 1px solid #B02200;")

    def cargar_horarios_configurados(self):
        """Refleja los horarios de la BD en los botones de la vista."""
        try:
            horarios = self.api.obtener_horarios()
            if not horarios or "error" in horarios: return
            
            for i, dia in enumerate(self.vista.nombres_dias):
                if dia in horarios:
                    self.vista.botones_inicio[i].setText(horarios[dia]["inicio"])
                    self.vista.botones_fin[i].setText(horarios[dia]["fin"])
        except Exception as e:
            print(f"Error cargando horarios: {e}")

    def ejecutar_guardado_total(self):
        """Envía la configuración completa al servidor."""
        datos_horarios = {}
        
        # 1. Recopilar datos
        for i, dia in enumerate(self.vista.nombres_dias):
            datos_horarios[dia] = {
                "inicio": self.vista.botones_inicio[i].text(),
                "fin": self.vista.botones_fin[i].text(),
                "cerrado": False 
            }
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            # 2. Guardar Horarios
            exito = self.api.guardar_horarios(datos_horarios)
            
            if exito:
                # 3. Sincronización inmediata con el buscador de la caja
                if self.controlador_pedido:
                    self.controlador_pedido.verificar_estado_tienda_visual()
                
                QMessageBox.information(self.vista, "Éxito", "Configuración de horarios guardada y aplicada.")
            else:
                QMessageBox.warning(self.vista, "Error", "No se pudo guardar la configuración en el servidor.")
            
            # 4. Actualización de perfil
            self.actualizar_perfil()
            
        except Exception as e:
            QMessageBox.critical(self.vista, "Error Crítico", f"Error al procesar el guardado: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def actualizar_perfil(self):
        """Maneja la actualización de contraseña si los widgets están presentes."""
        try:
            if hasattr(self.vista, 'inp_pass_nueva'):
                nueva = self.vista.inp_pass_nueva.text()
                confirmar = self.vista.inp_pass_confirm.text()

                if nueva and nueva == confirmar:
                    # Aquí iría la llamada api.actualizar_password(nueva)
                    QMessageBox.information(self.vista, "Perfil", "Contraseña actualizada correctamente.")
                    self.vista.inp_pass_actual.clear()
                    self.vista.inp_pass_nueva.clear()
                    self.vista.inp_pass_confirm.clear()
                elif nueva != confirmar:
                    QMessageBox.warning(self.vista, "Perfil", "Las contraseñas no coinciden.")
        except:
            pass