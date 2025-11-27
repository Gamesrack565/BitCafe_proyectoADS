#BITCAFE
#VERSION 1.0 (Monitor de Cocina)
#By: Angel A. Higuera

#Librerías y modulos
#Importa clases para manejo de hilos y temporizadores en Qt.
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
#Importa la clase datetime para manipulación de fechas y horas.
from datetime import datetime
#Importa el modulo para ejecución concurrente (hilos paralelos).
import concurrent.futures # <--- IMPORTANTE: Librería para el paralelismo
#Importa el cliente de API para realizar peticiones al backend.
from Modelo.api_client import api

# --- HILO 1: DESCARGA PARALELA (TURBO) ---
#Clase que maneja la sincronización de datos en segundo plano.
class HiloSincronizacion(QThread):
    #Define una señal que emitirá la lista combinada de pedidos.
    datos_listos = pyqtSignal(list)

    def run(self):
        #Inicia bloque de manejo de errores.
        try:
            # Usamos un Executor para lanzar peticiones simultáneas
            # Esto reduce el tiempo de espera a la mitad
            #Inicia el gestor de contexto para un pool de hilos.
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Lanzamos las dos "cañas de pescar" al mismo tiempo
                #Envía la tarea de obtener pedidos pendientes al ejecutor.
                future_pendientes = executor.submit(api.obtener_pedidos_pendientes)
                #Envía la tarea de obtener pedidos listos al ejecutor simultáneamente.
                future_listos = executor.submit(api.obtener_pedidos_listos)

                # Esperamos a que ambas terminen y recogemos resultados
                #Obtiene el resultado de pendientes, bloqueando hasta que termine.
                raw_pendientes = future_pendientes.result() or []
                #Obtiene el resultado de listos, bloqueando hasta que termine.
                raw_listos = future_listos.result() or []

            # --- Filtro Anti-Fantasma ---
            # (Tu lógica original para evitar duplicados si cambia de estado justo ahora)
            #Crea un conjunto con los IDs de los pedidos que ya están listos.
            ids_en_listos = {p.get('id_pedido') for p in raw_listos if p.get('id_pedido')}
            
            #Filtra la lista de pendientes para excluir los que ya aparecieron en listos.
            pendientes_reales = [
                p for p in raw_pendientes 
                if p.get('id_pedido') not in ids_en_listos
            ]
            
            #Combina ambas listas filtradas en una sola.
            total_pedidos = pendientes_reales + raw_listos
            #Emite la señal con la lista total de pedidos procesados.
            self.datos_listos.emit(total_pedidos)
            
        #Captura cualquier excepción durante la sincronización.
        except Exception as e:
            #Imprime el error en la consola.
            print(f"Error en hilo sync paralelo: {e}")
            #Emite una lista vacía para no romper la UI.
            self.datos_listos.emit([])

# --- HILO 2: ACCIONES (PATCH) ---
#Clase para ejecutar actualizaciones de estado sin bloquear la UI.
class HiloAccion(QThread):
    #Señal que indica si la acción terminó con éxito o no.
    accion_terminada = pyqtSignal(bool)

    def __init__(self, id_pedido, nuevo_estado):
        #Inicializa la clase padre QThread.
        super().__init__()
        #Guarda el ID del pedido a modificar.
        self.id_pedido = id_pedido
        #Guarda el nuevo estado deseado.
        self.nuevo_estado = nuevo_estado

    def run(self):
        #Inicia bloque try-except.
        try:
            # La api ya usa 'session', así que esto es rápido
            #Llama a la API para actualizar el estado del pedido.
            exito = api.actualizar_estado_pedido(self.id_pedido, self.nuevo_estado)
            #Emite el resultado de la operación (True/False).
            self.accion_terminada.emit(exito)
        #Si ocurre un error en la petición.
        except Exception as e:
            #Imprime el error.
            print(f"Error en hilo acción: {e}")
            #Emite falso indicando fallo.
            self.accion_terminada.emit(False)

# --- CONTROLADOR PRINCIPAL ---
class ControladorPedidos:
    def __init__(self, vista_pedidos):
        #Guarda la referencia a la vista del monitor de cocina.
        self.vista = vista_pedidos
        #Inicializa la variable para comparar datos anteriores y evitar repintados.
        self.datos_anteriores = None
        
        # Referencias a hilos
        #Inicializa la referencia al hilo de sincronización.
        self.hilo_sync = None
        #Inicializa la referencia al hilo de acciones.
        self.hilo_accion = None
        
        # Timer: Dispara el hilo cada 4 segundos
        #Crea una instancia de QTimer.
        self.timer = QTimer()
        #Conecta la señal timeout al método de descarga.
        self.timer.timeout.connect(self.iniciar_descarga_segundo_plano)
        #Inicia el temporizador con intervalo de 4000ms.
        self.timer.start(4000) 

        # Conexión botones
        #Conecta la señal personalizada de la vista al procesador de acciones.
        self.vista.solicitud_cambio_estado.connect(self.procesar_accion_usuario)

        # Carga inicial
        #Fuerza una primera descarga inmediata.
        self.iniciar_descarga_segundo_plano()

    def iniciar_descarga_segundo_plano(self):
        # --- FIX CRASH: Evitamos solapar hilos ---
        #Verifica si el hilo de sincronización ya existe y está corriendo.
        if self.hilo_sync is not None and self.hilo_sync.isRunning():
            #Si está ocupado, sale de la función para no saturar.
            return

        #Crea una nueva instancia del hilo de sincronización.
        self.hilo_sync = HiloSincronizacion()
        #Conecta la señal de datos listos al procesador de datos.
        self.hilo_sync.datos_listos.connect(self.procesar_datos)
        #Inicia la ejecución del hilo.
        self.hilo_sync.start()

    def procesar_accion_usuario(self, id_pedido, accion):
        """
        Maneja el clic del usuario con UI OPTIMISTA
        """
        #Imprime log de la acción solicitada.
        print(f"Controlador: Usuario pide {accion} en pedido {id_pedido}")
        
        #Inicializa la variable para el estado API.
        nuevo_estado = ""
        #Evalúa qué acción solicitó el usuario.
        if accion == "marcar_listo":
            nuevo_estado = "listo"
        elif accion == "marcar_entregado":
            nuevo_estado = "entregado"
        #Si la acción no es reconocida.
        else:
            return

        # 1. UI OPTIMISTA: Eliminamos tarjeta visualmente YA.
        #Llama a la vista para eliminar la tarjeta inmediatamente, dando sensación de rapidez.
        self.vista.eliminar_tarjeta_visual(id_pedido)
        
        # 2. ENVIAR A API (Segundo plano)
        # Si había una acción previa corriendo, dejamos que termine y lanzamos la nueva
        # (Idealmente usaríamos una cola, pero para uso normal esto basta)
        
        #Instancia el hilo de acción con los datos necesarios.
        self.hilo_accion = HiloAccion(id_pedido, nuevo_estado)
        #Conecta la señal de terminación al callback.
        self.hilo_accion.accion_terminada.connect(self.al_terminar_accion)
        #Inicia el hilo.
        self.hilo_accion.start()

    def al_terminar_accion(self, exito):
        #Si la acción fue exitosa en el servidor.
        if exito:
            #Confirma en consola.
            print("API confirmó actualización.")
            # Invalidamos caché para forzar que la próxima descarga 
            # refresque la pantalla con la verdad absoluta del servidor
            
            #Borra los datos anteriores para asegurar el repintado.
            self.datos_anteriores = None 
            #Fuerza una sincronización inmediata para actualizar el estado real.
            self.iniciar_descarga_segundo_plano()
        #Si hubo error en el servidor.
        else:
            #Imprime error.
            print("Error API. El pedido reaparecerá en la siguiente sincronización.")

    def procesar_datos(self, pedidos_raw):
        # Anti-Lag: Si nada cambió, no repintamos la UI
        #Compara los datos crudos actuales con los de la iteración anterior.
        if pedidos_raw == self.datos_anteriores:
            #Si son idénticos, no hace nada para ahorrar recursos.
            return 
        
        #Actualiza la caché de datos anteriores.
        self.datos_anteriores = pedidos_raw
        
        #Si la lista de pedidos está vacía.
        if not pedidos_raw:
            #Limpia la vista enviando listas vacías.
            self.vista.actualizar_pedidos([], [], [])
            return

        #Inicializa listas para clasificar pedidos.
        lista_nuevos = []
        lista_preparacion = []
        lista_listos = []

        #Itera sobre cada pedido crudo recibido.
        for p in pedidos_raw:
            # Extracción segura de datos
            #Obtiene folio o usa el ID como fallback.
            folio = p.get("num_orden") or str(p.get("id_pedido", "---"))
            #Obtiene el ID del pedido.
            id_pedido = p.get("id_pedido")
            #Obtiene el tiempo estimado de entrega.
            tiempo_estimado = p.get("tiempo_estimado")
            #Obtiene la cadena de fecha de creación.
            fecha_str = p.get("fecha_creacion", "")
            
            # Formateo de Hora
            #Inicializa la hora formateada con el string original por defecto.
            hora_formateada = fecha_str
            #Intenta parsear y formatear la fecha.
            try:
                if fecha_str:
                    #Limpia milisegundos y zona horaria para formato simple.
                    clean_date = fecha_str.split(".")[0].replace("Z", "")
                    #Convierte string a objeto datetime.
                    dt = datetime.fromisoformat(clean_date)
                    #Formatea a hora AM/PM.
                    hora_formateada = dt.strftime("%I:%M %p")
            except: pass

            # Formateo de Items
            #Inicializa lista de descripciones.
            items_desc = []
            #Itera sobre los items del pedido.
            for item in p.get("items", []):
                #Obtiene cantidad.
                cant = item.get("cantidad", 1)
                #Obtiene nombre del producto.
                nombre = item.get("producto", {}).get("nombre", "Prod")
                #Agrega string formateado a la lista.
                items_desc.append(f"{cant}x {nombre}")
            #Si no hay items, agrega texto placeholder.
            if not items_desc: items_desc.append("Sin items")

            #Obtiene total.
            total = p.get("total_pedido", "0.00")
            #Obtiene estado normalizado a minúsculas.
            estado = str(p.get("estado_pedido", "pendiente")).lower().strip()

            #Construye el diccionario "tarjeta" para la vista.
            tarjeta = {
                'id': id_pedido,
                'folio': folio, 
                'hora': hora_formateada,
                'items': items_desc, 
                'total': total,
                'tiempo_estimado': tiempo_estimado
            }

            # Clasificación
            #Si el estado es listo o terminado.
            if estado in ["listo", "terminado"]:
                lista_listos.append(tarjeta)
            #Si el estado es preparación o cocinando.
            elif estado in ["preparacion", "cocinando", "en_proceso"]:
                lista_preparacion.append(tarjeta)
            #Para cualquier otro estado (asume nuevo).
            else:
                lista_nuevos.append(tarjeta)

        #Envía las listas clasificadas a la vista para actualizar la UI.
        self.vista.actualizar_pedidos(lista_nuevos, lista_preparacion, lista_listos)