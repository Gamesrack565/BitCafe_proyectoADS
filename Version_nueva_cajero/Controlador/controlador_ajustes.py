# BITCAFE - CONTROLADOR AJUSTES
# VERSION 2.2 (SIN CERRAR SESIÓN - CLASE INTEGRADA)
# By: Angel A. Higuera & Gemini Partner

from PyQt6.QtWidgets import (QMessageBox, QApplication, QTimeEdit, QDialog, 
                             QVBoxLayout, QPushButton, QFrame, QHBoxLayout, 
                             QLabel, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QColor, QCursor

# ============================================================================
# CLASE DIALOGO EXITO (INTEGRADA AQUÍ PARA EVITAR ERRORES DE IMPORTACIÓN)
# ============================================================================
class DialogoExito(QDialog):
    def __init__(self, mensaje="Cambios guardados correctamente", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 200) 

        # --- CONTENEDOR PRINCIPAL ---
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 380, 180)
        self.container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(25, 20, 25, 25)

        # --- BOTÓN CERRAR (X) ---
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # ESTILO ROJO (Aviso)
        btn_close.setStyleSheet("""
            QPushButton {
                color: #D22A00; 
                font-weight: bold;
                border: none;
                background: transparent;
                font-size: 16px;
            }
            QPushButton:hover { color: #FF0000; }
        """)
        btn_close.clicked.connect(self.accept) 
        top_layout.addWidget(btn_close)
        
        layout.addLayout(top_layout)

        # --- MENSAJE ---
        self.lbl_mensaje = QLabel(mensaje)
        self.lbl_mensaje.setWordWrap(True)
        
        # ESTILO ROJO
        self.lbl_mensaje.setStyleSheet("""
            color: #D22A00; 
            font-size: 20px; 
            font-weight: bold; 
            border: none;
        """)
        self.lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        layout.addWidget(self.lbl_mensaje)
        
        layout.addStretch()

        # --- BOTÓN ACEPTAR ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch() 
        
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_aceptar.setFixedSize(100, 38)
        
        # ESTILO ROJO
        self.btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #D22A00;
                color: white;
                font-weight: 500;
                font-size: 14px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background-color: #B22400; }
        """)
        self.btn_aceptar.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_aceptar)
        layout.addLayout(btn_layout)


# ============================================================================
# CONTROLADOR AJUSTES
# ============================================================================
class ControladorAjustes:
    def __init__(self, api, vista_ajustes, controlador_pedido=None):
        self.api = api 
        self.vista = vista_ajustes
        self.controlador_pedido = controlador_pedido 
        
        # 1. Sincronizar datos
        self.cargar_estado_tienda()
        self.cargar_horarios_configurados()
        
        # 2. Conectar eventos
        self.vista.switch_tienda.clicked.connect(self.gestionar_cambio_tienda)
        self.conectar_eventos_horarios()
        
        # 3. Guardar Cambios
        self.vista.btn_guardar.clicked.connect(self.ejecutar_guardado_total)
        
        # (SE ELIMINÓ LA CONEXIÓN AL BOTÓN DESACTIVAR/CERRAR SESIÓN)

    def cargar_estado_tienda(self):
        try:
            estado_actual = self.api.obtener_estado_tienda()
            self.vista.switch_tienda.blockSignals(True)
            self.vista.switch_tienda.setChecked(estado_actual)
            self.vista.switch_tienda.blockSignals(False)
        except Exception as e:
            print(f"Error al cargar estado de tienda: {e}")

    def gestionar_cambio_tienda(self):
        nuevo_estado = self.vista.switch_tienda.isChecked()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            exito = self.api.actualizar_estado_tienda(nuevo_estado)
            if exito:
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
        for i in range(len(self.vista.nombres_dias)):
            btn_ini = self.vista.botones_inicio[i]
            btn_fin = self.vista.botones_fin[i]
            btn_ini.clicked.connect(lambda checked, b=btn_ini: self.abrir_selector_hora(b))
            btn_fin.clicked.connect(lambda checked, b=btn_fin: self.abrir_selector_hora(b))

    def abrir_selector_hora(self, boton):
        dialogo = QDialog(self.vista)
        dialogo.setWindowTitle("Seleccionar Hora")
        layout = QVBoxLayout(dialogo)
        
        selector = QTimeEdit()
        selector.setDisplayFormat("HH:mm")
        
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
            boton.setStyleSheet("background-color: #D22A00; color: white; border-radius: 12px; font-weight: bold; border: 1px solid #B02200;")

    def cargar_horarios_configurados(self):
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
        datos_horarios = {}
        for i, dia in enumerate(self.vista.nombres_dias):
            datos_horarios[dia] = {
                "inicio": self.vista.botones_inicio[i].text(),
                "fin": self.vista.botones_fin[i].text(),
                "cerrado": False 
            }
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            exito = self.api.guardar_horarios(datos_horarios)
            
            if exito:
                if self.controlador_pedido:
                    self.controlador_pedido.verificar_estado_tienda_visual()
                
                # USO DE LA CLASE INTEGRADA (ROJA)
                dialogo = DialogoExito("Configuración guardada correctamente.", self.vista)
                dialogo.exec()
                
            else:
                QMessageBox.warning(self.vista, "Error", "No se pudo guardar la configuración.")
            
            self.actualizar_perfil()
            
        except Exception as e:
            QMessageBox.critical(self.vista, "Error Crítico", f"Error al procesar el guardado: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def actualizar_perfil(self):
        try:
            if hasattr(self.vista, 'inp_pass_nueva'):
                nueva = self.vista.inp_pass_nueva.text()
                confirmar = self.vista.inp_pass_confirm.text()

                if nueva and nueva == confirmar:
                    # USO DE LA CLASE INTEGRADA (ROJA)
                    dialogo = DialogoExito("Contraseña actualizada correctamente.", self.vista)
                    dialogo.exec()
                    
                    self.vista.inp_pass_actual.clear()
                    self.vista.inp_pass_nueva.clear()
                    self.vista.inp_pass_confirm.clear()
                elif nueva != confirmar:
                    QMessageBox.warning(self.vista, "Perfil", "Las contraseñas no coinciden.")
        except:
            pass