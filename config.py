# === Configurações Gerais ===
SSID = "Suryland"  # Nome da rede Wi-Fi
SENHA = "AvengersAssemble2020@@"  # Senha da rede Wi-Fi
#SENHA = "paodebatata" # Outra senha de exemplo

# === API/Zabbix ===
# API_URL = "http://149.28.230.181/adapter/resources/95d80ef9-3670-4f50-a386-bbf6a9329de4/data"  # URL da API (antigo)
ZABBIX_SERVER = "endereco_do_servidor_zabbix"  # IP ou hostname do servidor Zabbix
ZABBIX_PORT = 10051  # Porta padrão do Zabbix sender
ZABBIX_HOST = "PicoW_SensorStation" # Nome do host no Zabbix para este dispositivo

# === Intervalos ===
INTERVALO_LOOP_PRINCIPAL = 30  # Tempo entre ciclos de leitura/envio (segundos)
INTERVALO_LEITURA_TEMP = 1  # Intervalo entre leituras de temperatura (segundos)
INTERVALO_LEITURA_DIST = 1  # Intervalo entre leituras de distância (segundos)
INTERVALO_LEITURA_TURB = 1  # Intervalo entre leituras de turbidez (segundos)
INTERVALO_LEITURA_TDS = 1   # Intervalo entre leituras de TDS (segundos) - Adicionado

# === Parâmetros de Leitura e Envio ===
NUM_LEITURAS = 10  # Número de leituras por sensor para média
MAX_REENVIO_ZABBIX = 5  # Tentativas de reenvio dos dados para o Zabbix

# === Limites de Outlier para Sensores ===
# Valores em percentual (ex: 0.10 para 10%)
LIMITE_OUTLIER_TEMP = 0.10
LIMITE_OUTLIER_DIST = 0.50
LIMITE_OUTLIER_TURB = 0.20
LIMITE_OUTLIER_TDS = 0.20 # Exemplo, ajustar conforme necessidade

# === Pinos dos Sensores ===
# Estes serão usados pelos módulos específicos dos sensores
PIN_LED_ONBOARD = "LED" # Pino do LED da placa Pico W

# Pinos para o sensor de temperatura DS18B20
PIN_DS18B20 = 18

# Pinos para o sensor de distância HC-SR04
PIN_HCSR04_TRIGGER = 20
PIN_HCSR04_ECHO = 19

# Pino para o sensor de turbidez (ADC)
PIN_TURBIDEZ_ADC = 26 # ADC0

# Pino para o sensor TDS (ADC) - Exemplo, verificar pino correto
PIN_TDS_ADC = 27 # ADC1 - Exemplo, ajustar se necessário

# === Arquivos de Log/Cache ===
ARQUIVO_FALHAS_LOG = "falhas.log"
ARQUIVO_CACHE_DADOS = "cache_zabbix.db" # Nome alterado para refletir Zabbix

# === Debugging ===
DEBUG_MODE = True # Ativa/desativa mensagens de debug adicionais
PC_MODE = False  # True para simular leituras de sensor no PC (sem hardware real)

print("Configurações carregadas de config.py")
# Se PC_MODE for True, pode ser útil ajustar outros valores para teste rápido,
# como INTERVALO_LOOP_PRINCIPAL.
if PC_MODE:
    print("!!! ATENÇÃO: MODO PC ATIVADO - SENSORES SERÃO SIMULADOS !!!")
    # Exemplo: reduzir intervalo para testes mais rápidos no PC
    # INTERVALO_LOOP_PRINCIPAL = 5
    # NUM_LEITURAS = 3 # Menos leituras para simulação rápida
    pass
