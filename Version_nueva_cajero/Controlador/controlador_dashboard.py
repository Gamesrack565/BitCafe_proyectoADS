#BITCAFE
#VERSION 2
#By: Angel A. Higuera

#Librerías y modulos
#Importa las clases de PyQt6: QTimer, QThread y pyqtSignal para concurrencia.
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
#Importa el objeto 'api' del modulo de cliente para peticiones HTTP.
from Modelo.api_client import api

# --- HILO OBRERO INTELIGENTE ---
#Define la clase HiloDashboard que hereda de QThread para ejecucion en segundo plano.
class HiloDashboard(QThread):
    #Define una senal que enviara un diccionario cuando los datos esten listos.
    datos_actualizados = pyqtSignal(dict)

    def __init__(self, pedir_resumen=False):
        #Inicializa la clase padre (QThread).
        super().__init__()
        #Flag para saber si debemos molestar a la base de datos con el resumen financiero.
        self.pedir_resumen = pedir_resumen

    def run(self):
        #Inicia un bloque try para manejar posibles errores de conexion o logica.
        try:
            # 1. Pedidos (Siempre necesario, es ligero)
            #Llama a la API para obtener la lista de pedidos pendientes.
            pedidos = api.obtener_pedidos_pendientes() or []
            
            # 2. Resumen (Solo si se solicita explícitamente)
            #Inicializa la variable resumen como None.
            resumen = None
            #Si la bandera 'pedir_resumen' es verdadera.
            if self.pedir_resumen:
                #Llama a la API para obtener el resumen de ventas del dia.
                resumen = api.obtener_resumen_dia() or {}

            # Empaquetamos respuesta
            #Crea un diccionario con los resultados obtenidos y la bandera de estado.
            resultado = {
                "pedidos": pedidos,
                "resumen": resumen, 
                "trae_resumen": self.pedir_resumen
            }
            #Emite la senal enviando el diccionario de resultados al hilo principal.
            self.datos_actualizados.emit(resultado)
        #Captura cualquier excepcion que ocurra durante la ejecucion.
        except Exception as e:
            #Imprime el error en la consola para depuracion.
            print(f"Error en hilo dashboard: {e}")

class ControladorDashboard:
    def __init__(self, vista_dashboard):
        #Guarda la referencia a la vista del dashboard para manipular la UI.
        self.vista = vista_dashboard
        
        # --- Caché para evitar parpadeos ---
        #Inicializa la cache de pedidos en None para la primera comparacion.
        self.cache_pedidos = None
        
        # --- Contador para optimización ---
        #Inicializa el contador de ciclos de actualizacion.
        self.contador_ciclos = 0 

        # Timer: 5 segundos
        #Crea una instancia de QTimer.
        self.timer = QTimer()
        #Conecta la senal 'timeout' del timer a la funcion de actualizacion.
        self.timer.timeout.connect(self.iniciar_actualizacion_segundo_plano)
        #Inicia el timer con un intervalo de 5000 milisegundos (5 segundos).
        self.timer.start(5000) 

        # Carga inicial (Forzamos resumen la primera vez)
        #Ejecuta la actualizacion inmediatamente forzando la carga del resumen.
        self.iniciar_actualizacion_segundo_plano(forzar_resumen=True)

    def iniciar_actualizacion_segundo_plano(self, forzar_resumen=False):
        #Determina si se debe pedir el resumen basandose en el contador o el argumento forzado.
        pedir_resumen = forzar_resumen or (self.contador_ciclos % 12 == 0)
        
        #Crea una nueva instancia del hilo obrero pasando la bandera de decision.
        self.hilo = HiloDashboard(pedir_resumen)
        #Conecta la senal del hilo a la funcion que procesara los datos en la UI.
        self.hilo.datos_actualizados.connect(self.procesar_datos)
        #Inicia la ejecucion del hilo.
        self.hilo.start()
        
        #Incrementa el contador de ciclos.
        self.contador_ciclos += 1

    def procesar_datos(self, datos_dict):
        #Extrae la lista de pedidos del diccionario recibido.
        pedidos_api = datos_dict.get("pedidos", [])
        #Extrae la bandera que indica si el resumen fue solicitado.
        trae_resumen = datos_dict.get("trae_resumen", False)
        #Extrae los datos del resumen financiero.
        resumen = datos_dict.get("resumen", {})
        
        #Compara si los pedidos recibidos son diferentes a los guardados en cache.
        if pedidos_api != self.cache_pedidos:
            #Actualiza la cache con los nuevos pedidos.
            self.cache_pedidos = pedidos_api 
            #Imprime un mensaje en consola indicando actualizacion de UI.
            print("Dashboard: Cambios detectados, actualizando UI...")
            
            #Inicializa la lista de datos formateados para la vista.
            datos_para_vista = []
            #Inicializa el contador para pedidos nuevos.
            count_nuevos = 0
            #Inicializa el contador para pedidos en preparacion.
            count_preparacion = 0
            
            #Verifica si la lista de pedidos existe y es valida.
            if pedidos_api and isinstance(pedidos_api, list):
                #Itera sobre cada pedido obtenido.
                for p in pedidos_api:
                    # Clasificación
                    #Obtiene el estado del pedido y lo convierte a minusculas.
                    estado = str(p.get("estado_pedido", "")).lower()
                    #Verifica si el estado corresponde a procesos de cocina.
                    if estado in ["preparacion", "cocinando", "en_proceso"]:
                        #Incrementa el contador de preparacion.
                        count_preparacion += 1
                    #Si no esta en preparacion (se asume nuevo/pendiente).
                    else:
                        #Incrementa el contador de nuevos.
                        count_nuevos += 1

                    # Descripción visual items
                    #Obtiene la lista de items del pedido.
                    items = p.get("items", [])
                    #Si hay items en el pedido.
                    if items:
                        #Inicializa lista para descripciones breves.
                        lista_desc = []
                        #Itera sobre cada item.
                        for item in items:
                            #Obtiene la cantidad del item, por defecto 1.
                            cant = item.get("cantidad", 1)
                            #Obtiene el nombre del producto de forma segura.
                            nom = item.get("producto", {}).get("nombre", "Desc.")
                            #Formatea la cadena "Cantidad x Nombre".
                            lista_desc.append(f"{cant}x {nom}")
                        #Une todas las descripciones con comas.
                        descripcion_final = ", ".join(lista_desc)
                    #Si no hay items.
                    else:
                        #Asigna un texto por defecto.
                        descripcion_final = "Sin detalles"

                    # Datos fila
                    #Agrega un diccionario formateado a la lista de la vista.
                    datos_para_vista.append({
                        'folio': str(p.get("num_orden", "---")),
                        'desc': descripcion_final,
                        'total': str(p.get("total_pedido", "0.00"))
                    })
            
            # Actualizamos la tabla y contadores de pedidos
            #Llama al metodo de la vista para actualizar la tabla de pedidos.
            self.vista.actualizar_lista_pedidos(datos_para_vista)
            #Actualiza la tarjeta de pedidos nuevos con el contador.
            self.vista.card_nuevos.actualizar_valor(str(count_nuevos))
            #Actualiza la tarjeta de pedidos en preparacion con el contador.
            self.vista.card_preparacion.actualizar_valor(str(count_preparacion))

        #Si se solicito el resumen y la respuesta contiene datos.
        if trae_resumen and resumen:
            #Obtiene el conteo de pedidos pagados del resumen.
            pagados = resumen.get("pedidos_pagados_hoy", 0)
            #Actualiza la tarjeta de ventas con el valor obtenido.
            self.vista.card_ventas.actualizar_valor(str(pagados))
        #Si se solicito resumen pero llego vacio o fallo.
        elif trae_resumen and not resumen:
             # Si intentamos pedir resumen y falló/vino vacío
             #Muestra un guion indicando falta de datos.
             self.vista.card_ventas.actualizar_valor("-")