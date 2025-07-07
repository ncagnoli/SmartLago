import time
import config
import utils

# Tenta importar 'machine' para hardware real, se falhar, estamos provavelmente no PC
try:
    import machine
    # Se 'machine' importou, não estamos em PC_MODE forçado por falta de 'machine'
except ImportError:
    if not config.PC_MODE:
        print(f"[{utils.agora()}] ATENÇÃO: Módulo 'machine' não encontrado. Forçando PC_MODE.")
        config.PC_MODE = True # Força PC_MODE se machine não existe e não estava já setado

# Importar urandom para simulação, ou random como fallback para PC
try:
    import urandom
except ImportError:
    import random as urandom # usa random do python padrão se urandom não existir

# --- Inicialização dos Sensores (apenas se não estiver em PC_MODE) ---
ds_sensor = None
roms = []
hcsr04_sensor_pins = None
adc_turbidez = None
adc_tds = None

if not config.PC_MODE:
    # Sensor de Temperatura DS18B20
    try:
        import onewire
        import ds18x20
        ow_pin = machine.Pin(config.PIN_DS18B20)
        ow_bus = onewire.OneWire(ow_pin)
        ds_sensor = ds18x20.DS18X20(ow_bus)
        roms = ds_sensor.scan()
        if not roms:
            print(f"[{utils.agora()}] Nenhum sensor DS18B20 encontrado no pino {config.PIN_DS18B20}.")
            ds_sensor = None # Marca como não disponível
        else:
            print(f"[{utils.agora()}] Sensor DS18B20 encontrado: {roms}")
    except ImportError:
        print(f"[{utils.agora()}] Micropython-onewire ou ds18x20 não instalado. Sensor de temperatura desabilitado.")
        ds_sensor = None
    except Exception as e: # Captura machine.Pin() error se o pino for inválido
        print(f"[{utils.agora()}] Erro ao inicializar sensor DS18B20: {e}")
        ds_sensor = None

    # Sensor de Distância HC-SR04
    try:
        trigger_pin = machine.Pin(config.PIN_HCSR04_TRIGGER, machine.Pin.OUT)
        echo_pin = machine.Pin(config.PIN_HCSR04_ECHO, machine.Pin.IN)
        hcsr04_sensor_pins = {"trigger": trigger_pin, "echo": echo_pin}
        print(f"[{utils.agora()}] Sensor HC-SR04 inicializado (Trigger: {config.PIN_HCSR04_TRIGGER}, Echo: {config.PIN_HCSR04_ECHO}).")
    except Exception as e:
        print(f"[{utils.agora()}] Erro ao inicializar sensor HC-SR04: {e}")
        hcsr04_sensor_pins = None

    # Sensor de Turbidez (ADC)
    try:
        adc_turbidez = machine.ADC(machine.Pin(config.PIN_TURBIDEZ_ADC))
        print(f"[{utils.agora()}] Sensor de Turbidez ADC inicializado no pino {config.PIN_TURBIDEZ_ADC}.")
    except Exception as e:
        print(f"[{utils.agora()}] Erro ao inicializar ADC para Turbidez: {e}")
        adc_turbidez = None

    # Sensor de TDS (ADC)
    try:
        adc_tds = machine.ADC(machine.Pin(config.PIN_TDS_ADC))
        print(f"[{utils.agora()}] Sensor de TDS ADC inicializado no pino {config.PIN_TDS_ADC}.")
    except Exception as e:
        print(f"[{utils.agora()}] Erro ao inicializar ADC para TDS: {e}")
        adc_tds = None
else:
    print(f"[{utils.agora()}] [PC_MODE] Inicialização de hardware dos sensores pulada.")

# --- Funções de Leitura Individual dos Sensores ---

def _simular_leitura(min_val, max_val, decimals=2):
    """Gera um valor aleatório para simulação."""
    val = urandom.uniform(min_val, max_val)
    return round(val, decimals)

# --- Funções de Cálculo Estatístico ---

def _calcular_moda(leituras: list, округление_до_casas_decimais=None):
    """
    Calcula a moda de uma lista de leituras.
    Se houver múltiplas modas, retorna a menor delas.
    Se todas as leituras forem únicas (e houver mais que uma), ou a lista estiver vazia, retorna None.
    'округление_до_casas_decimais': opcionalmente arredonda as leituras antes de calcular a moda
                                   para agrupar valores próximos.
    """
    if not leituras:
        return None

    if округление_до_casas_decimais is not None:
        leituras_processadas = [round(l, округление_до_casas_decimais) for l in leituras]
    else:
        leituras_processadas = list(leituras) # Copia para não modificar a original se não arredondar

    if not leituras_processadas: # Caso raro, se todas as leituras originais fossem None e isso não foi filtrado antes
        return None

    contagens = {}
    for valor in leituras_processadas:
        contagens[valor] = contagens.get(valor, 0) + 1

    if not contagens: # Deve ser impossível se leituras_processadas não estiver vazio
        return None

    max_contagem = 0
    for valor in contagens:
        if contagens[valor] > max_contagem:
            max_contagem = contagens[valor]

    # Se todas as contagens forem 1 (todos os valores únicos) e houver mais de um valor, não há moda clara.
    # Ou se a contagem máxima for 1 e houver mais de um item, também não há moda clara.
    if max_contagem == 1 and len(leituras_processadas) > 1:
         # Se todos os valores são únicos, não há uma moda clara.
         # Poderíamos retornar a média como fallback, ou None.
         # print(f"[{utils.agora()}] [Moda] Todos os valores são únicos, sem moda clara. Retornando a média como fallback.")
         # return sum(leituras_processadas) / len(leituras_processadas)
        return None


    modas = []
    for valor, contagem in contagens.items():
        if contagem == max_contagem:
            modas.append(valor)

    if not modas: # Impossível se max_contagem > 0
        return None

    # Retorna a menor das modas se houver empate, para consistência.
    # Ou poderia ser a primeira encontrada: return modas[0]
    return min(modas)


def ler_temperatura_ds18b20():
    """Lê a temperatura do sensor DS18B20 ou simula se PC_MODE=True."""
    if config.PC_MODE:
        sim_temp = _simular_leitura(15.0, 30.0)
        #print(f"[{utils.agora()}] [PC_MODE] Temperatura simulada: {sim_temp:.2f} °C")
        return sim_temp

    if not ds_sensor or not roms:
        return None
    try:
        ds_sensor.convert_temp()
        time.sleep_ms(750)
        temp = ds_sensor.read_temp(roms[0])
        return temp
    except Exception as e:
        print(f"[{utils.agora()}] Erro ao ler temperatura DS18B20: {e}")
        return None

def ler_distancia_hcsr04():
    """Lê a distância do sensor HC-SR04 ou simula se PC_MODE=True."""
    if config.PC_MODE:
        sim_dist = _simular_leitura(10.0, 200.0)
        #print(f"[{utils.agora()}] [PC_MODE] Distância simulada: {sim_dist:.2f} cm")
        return sim_dist

    if not hcsr04_sensor_pins:
        return None
    trigger = hcsr04_sensor_pins["trigger"]
    echo = hcsr04_sensor_pins["echo"]
    try:
        trigger.value(0); time.sleep_us(2)
        trigger.value(1); time.sleep_us(10)
        trigger.value(0)
        duracao_pulso = machine.time_pulse_us(echo, 1, 30000)
        if duracao_pulso < 0: return None
        distancia_cm = (duracao_pulso / 2) / 29.1
        return distancia_cm
    except OSError: # Timeout geralmente
        return None
    except Exception as e:
        print(f"[{utils.agora()}] Erro inesperado ao ler HC-SR04: {e}")
        return None

def ler_turbidez_adc():
    """Lê o valor bruto do ADC para turbidez ou simula se PC_MODE=True."""
    if config.PC_MODE:
        sim_turb = _simular_leitura(0, 4000) # ADC raw (0-65535, mas faixa típica)
        #print(f"[{utils.agora()}] [PC_MODE] Turbidez ADC simulada: {sim_turb}")
        return sim_turb

    if not adc_turbidez:
        return None
    try:
        return adc_turbidez.read_u16()
    except Exception as e:
        print(f"[{utils.agora()}] Erro ao ler ADC de turbidez: {e}")
        return None

def ler_tds_adc():
    """Lê o valor bruto do ADC para TDS ou simula se PC_MODE=True."""
    if config.PC_MODE:
        sim_tds = _simular_leitura(0, 2000) # ADC raw (0-65535, mas faixa típica)
        #print(f"[{utils.agora()}] [PC_MODE] TDS ADC simulado: {sim_tds}")
        return sim_tds

    if not adc_tds:
        return None
    try:
        return adc_tds.read_u16()
    except Exception as e:
        print(f"[{utils.agora()}] Erro ao ler ADC de TDS: {e}")
        return None

# --- Função de Processamento de Leituras e Filtragem ---

def _processar_leituras_sensor(leituras_func, nome_sensor, num_leituras, intervalo_leitura_s, limite_outlier_percent, casas_decimais_moda=None):
    """
    Coleta várias leituras de um sensor, filtra outliers e calcula a MODA.
    Retorna a moda ou None se não houver leituras válidas ou moda clara.
    'casas_decimais_moda': número de casas decimais para arredondar antes de calcular a moda.
                           Sensores como temperatura podem se beneficiar disso. ADC não.
    """
    if not callable(leituras_func):
        print(f"[{utils.agora()}] {nome_sensor}: Função de leitura não é chamável.")
        return None

    leituras_coletadas = []
    if config.DEBUG_MODE:
        print(f"[{utils.agora()}] {nome_sensor}: Iniciando {num_leituras} leituras com intervalo de {intervalo_leitura_s}s...")

    for i in range(num_leituras):
        valor = leituras_func()
        if valor is not None:
            leituras_coletadas.append(valor)
            if config.DEBUG_MODE and config.PC_MODE: # Log mais verboso para simulação
                 print(f"[{utils.agora()}] {nome_sensor} [PC_MODE] Leitura {i+1}/{num_leituras}: {valor}")
            elif config.DEBUG_MODE:
                 print(f"[{utils.agora()}] {nome_sensor} Leitura {i+1}/{num_leituras}: {valor:.2f}" if isinstance(valor, float) else f"{valor}")
        else:
            if config.DEBUG_MODE:
                print(f"[{utils.agora()}] {nome_sensor} Leitura {i+1}/{num_leituras}: Falha")

        # Mesmo em PC_MODE, o intervalo de leitura pode ser útil para simular o tempo real
        time.sleep(intervalo_leitura_s if not config.PC_MODE else 0.01) # Intervalo menor em PC_MODE para acelerar

    if not leituras_coletadas:
        print(f"[{utils.agora()}] {nome_sensor}: Nenhuma leitura bem-sucedida.")
        return None

    # Filtragem de outliers (baseada na média bruta, como antes)
    media_bruta = sum(leituras_coletadas) / len(leituras_coletadas)
    leituras_filtradas = []

    if limite_outlier_percent > 0:
        for v in leituras_coletadas:
            # A lógica de outlier pode precisar de refinamento, especialmente para valores zero.
            # Se a média bruta for muito pequena (próxima de zero), a divisão pode ser instável.
            is_outlier = False
            if abs(media_bruta) > 1e-6: # Evita divisão por zero ou instabilidade
                if abs(v - media_bruta) / media_bruta > limite_outlier_percent:
                    is_outlier = True
            elif v != 0 and abs(v) > limite_outlier_percent * 1: # Fallback se media_bruta é zero, compara com uma unidade
                 # Se media_bruta é zero, um valor não-zero pode ser um outlier se for grande o suficiente.
                 # Esta parte é mais heurística.
                 pass # Depende do que se espera quando a média é zero.

            if is_outlier:
                if config.DEBUG_MODE:
                    print(f"[{utils.agora()}] {nome_sensor}: valor {v} descartado como outlier (média bruta {media_bruta:.2f}).")
            else:
                leituras_filtradas.append(v)
    else: # Sem filtragem de outlier
        leituras_filtradas = list(leituras_coletadas)

    if not leituras_filtradas:
        print(f"[{utils.agora()}] {nome_sensor}: Todas as leituras foram descartadas como outliers.")
        # Fallback: talvez retornar a média bruta das leituras originais? Ou None?
        # Por enquanto, None, indicando que a filtragem removeu tudo.
        return None

    # Cálculo da MODA sobre as leituras filtradas
    valor_final_sensor = _calcular_moda(leituras_filtradas, округление_до_casas_decimais=casas_decimais_moda)

    if valor_final_sensor is None:
        if config.DEBUG_MODE:
            print(f"[{utils.agora()}] {nome_sensor}: Nenhuma moda clara encontrada nas leituras filtradas. Usando média como fallback.")
        # Fallback para média se a moda não for clara
        if leituras_filtradas: # Garante que há algo para calcular a média
             valor_final_sensor = sum(leituras_filtradas) / len(leituras_filtradas)
        else: # Isso não deveria acontecer se a verificação anterior de not leituras_filtradas funcionou
             return None


    if config.DEBUG_MODE:
        print(f"[{utils.agora()}] {nome_sensor}: Leituras originais ({len(leituras_coletadas)}): {leituras_coletadas}")
        print(f"[{utils.agora()}] {nome_sensor}: Média bruta: {media_bruta:.2f}")
        print(f"[{utils.agora()}] {nome_sensor}: Leituras filtradas ({len(leituras_filtradas)}): {leituras_filtradas}")
        if isinstance(valor_final_sensor, float):
            print(f"[{utils.agora()}] {nome_sensor}: Valor final (Moda/Média fallback): {valor_final_sensor:.2f}")
        else:
            print(f"[{utils.agora()}] {nome_sensor}: Valor final (Moda/Média fallback): {valor_final_sensor}")


    return valor_final_sensor

# --- Função Principal de Leitura dos Sensores ---

def ler_todos_sensores():
    """
    Lê todos os sensores configurados, aplicando filtragem e cálculo de moda.
    Retorna um dicionário com os dados dos sensores.
    """
    # Tenta importar led_signals dinamicamente para evitar dependência cíclica ou erro na inicialização
    try:
        import led_signals
        if hasattr(led_signals, 'sinal_leitura_sensores_em_andamento'):
            led_signals.sinal_leitura_sensores_em_andamento()
    except ImportError:
        pass # led_signals não disponível, continua sem ele

    print(f"[{utils.agora()}] Iniciando leitura de todos os sensores...")
    dados = {}

    # Temperatura
    # Para temperatura, arredondar para 1 casa decimal antes da moda pode ser útil
    if ds_sensor or config.PC_MODE: # Inclui PC_MODE para que a simulação ocorra
        dados["temperatura"] = _processar_leituras_sensor(
            leituras_func=ler_temperatura_ds18b20,
            nome_sensor="Temperatura",
            num_leituras=config.NUM_LEITURAS,
            intervalo_leitura_s=config.INTERVALO_LEITURA_TEMP,
            limite_outlier_percent=config.LIMITE_OUTLIER_TEMP,
            casas_decimais_moda=1 # Arredonda temps para 1 decimal (ex: 23.5, 23.6)
        )
    else:
        dados["temperatura"] = None

    # Distância
    # Para distância, talvez 0 ou 1 casa decimal.
    if hcsr04_sensor_pins or config.PC_MODE:
        dados["distancia"] = _processar_leituras_sensor(
            leituras_func=ler_distancia_hcsr04,
            nome_sensor="Distancia",
            num_leituras=config.NUM_LEITURAS,
            intervalo_leitura_s=config.INTERVALO_LEITURA_DIST,
            limite_outlier_percent=config.LIMITE_OUTLIER_DIST,
            casas_decimais_moda=0 # Arredonda para inteiro mais próximo
        )
    else:
        dados["distancia"] = None

    # Turbidez (valores ADC, geralmente inteiros)
    if adc_turbidez or config.PC_MODE:
        dados["turbidez"] = _processar_leituras_sensor(
            leituras_func=ler_turbidez_adc,
            nome_sensor="Turbidez",
            num_leituras=config.NUM_LEITURAS,
            intervalo_leitura_s=config.INTERVALO_LEITURA_TURB,
            limite_outlier_percent=config.LIMITE_OUTLIER_TURB,
            casas_decimais_moda=None # ADC são inteiros, não arredondar
        )
    else:
        dados["turbidez"] = None

    # TDS (valores ADC, geralmente inteiros)
    if adc_tds or config.PC_MODE:
        dados["tds"] = _processar_leituras_sensor(
            leituras_func=ler_tds_adc,
            nome_sensor="TDS",
            num_leituras=config.NUM_LEITURAS,
            intervalo_leitura_s=config.INTERVALO_LEITURA_TDS,
            limite_outlier_percent=config.LIMITE_OUTLIER_TDS,
            casas_decimais_moda=None # ADC são inteiros, não arredondar
        )
    else:
        dados["tds"] = None

    print(f"[{utils.agora()}] Dados finais dos sensores (Moda/Média): {dados}")
    return dados

if __name__ == '__main__':
    # Para testar este módulo, certifique-se que config.py e utils.py estão acessíveis
    # e que os pinos em config.py correspondem ao seu hardware.
    print("Testando módulo sensor_manager...")

    # Opcional: Importar led_signals para teste visual se estiver usando
    try:
        import led_signals
        print("led_signals importado para teste visual.")
    except ImportError:
        print("led_signals não encontrado, teste será apenas por print.")
        led_signals = None # Garante que não dê erro se não existir

    # Teste de leitura de todos os sensores
    resultados = ler_todos_sensores()

    print("\n--- Resultados Finais do Teste ---")
    if resultados:
        for sensor, valor in resultados.items():
            if valor is not None:
                print(f"Sensor {sensor}: {valor:.2f}")
            else:
                print(f"Sensor {sensor}: Falha na leitura ou não disponível")
    else:
        print("Nenhum dado de sensor foi retornado.")

    # Testes individuais (descomente para testar funções específicas)
    # print("\nTestando leitura individual de temperatura...")
    # temp = ler_temperatura_ds18b20()
    # if temp is not None:
    #     print(f"Temperatura individual: {temp:.2f} C")
    # else:
    #     print("Falha ao ler temperatura individual ou sensor não disponível.")

    # print("\nTestando leitura individual de distância...")
    # dist = ler_distancia_hcsr04()
    # if dist is not None:
    #     print(f"Distância individual: {dist:.2f} cm")
    # else:
    #     print("Falha ao ler distância individual ou sensor não disponível.")

    # print("\nTestando leitura individual de turbidez (ADC raw)...")
    # turb = ler_turbidez_adc()
    # if turb is not None:
    #     print(f"Turbidez individual (ADC): {turb}")
    # else:
    #     print("Falha ao ler turbidez individual ou sensor não disponível.")

    # print("\nTestando leitura individual de TDS (ADC raw)...")
    # tds_val = ler_tds_adc()
    # if tds_val is not None:
    #     print(f"TDS individual (ADC): {tds_val}")
    # else:
    #     print("Falha ao ler TDS individual ou sensor não disponível.")

    print("\nFim do teste do sensor_manager.")
