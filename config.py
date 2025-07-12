# === Configurações Gerais ===
SSID = "Suryland"  # Nome da rede Wi-Fi
SENHA = "AvengersAssemble2020@@"  # Senha da rede Wi-Fi

# === Configurações do Servidor HTTP ===
HTTP_PORT = 80 # Porta padrão para HTTP
HTTP_MAX_PENDING_CONN = 5 # Número máximo de conexões pendentes no socket do servidor
HTTP_CLIENT_TIMEOUT_S = 10 # Timeout em segundos para operações de socket com o cliente (recv, send)
HTTP_MAX_REQUEST_SIZE = 1024 # Tamanho máximo em bytes da requisição HTTP a ser lida

# === Intervalos ===
# INTERVALO_LOOP_PRINCIPAL foi substituído pela lógica do servidor HTTP e INTERVALO_HEARTBEAT_MAIN
INTERVALO_HEARTBEAT_MAIN = 5 # Intervalo para o loop de manutenção em main.py (segundos)
INTERVALO_RECONEXAO_WIFI = 60 # Intervalo para tentar reconectar ao Wi-Fi se cair (segundos)

# Configurações de leitura por sensor (serão usadas pelos endpoints)
# Cada sensor terá: NUM_LEITURAS_X, INTERVALO_LEITURA_X_S
# Exemplo para temperatura:
NUM_LEITURAS_TEMP = 10
INTERVALO_LEITURA_TEMP_S = 1 # Intervalo entre as leituras individuais para compor uma medição final

NUM_LEITURAS_DIST = 10
INTERVALO_LEITURA_DIST_S = 1

NUM_LEITURAS_TURB = 10
INTERVALO_LEITURA_TURB_S = 1

NUM_LEITURAS_TDS = 10
INTERVALO_LEITURA_TDS_S = 1 # Intervalo entre as leituras individuais de TDS

# MAX_REENVIO_ZABBIX não é mais necessário

# === Limites de Outlier para Sensores ===
# Valores em percentual (ex: 0.10 para 10%)
# Estes podem ser globais ou por sensor, se necessário.
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
# ARQUIVO_CACHE_DADOS não é mais necessário com a remoção do Zabbix e sua lógica de cache

# === Debugging ===
DEBUG_MODE = True # Ativa/desativa mensagens de debug adicionais
# PC_MODE foi removido. O código agora assume que está rodando em hardware MicroPython.

print("Configurações carregadas de config.py")
# A lógica condicional para PC_MODE foi removida.
