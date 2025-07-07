import socket
import json
import time
import config
import utils

# Constantes do protocolo Zabbix Sender
ZABBIX_HEADER = b'ZBXD\x01'

def _criar_pacote_zabbix(dados_sensores, host_no_zabbix, clock_time=None):
    """
    Cria o payload JSON para o Zabbix Sender.
    'dados_sensores' é um dicionário como {"temperatura": 25.0, "distancia": 100.0}
    As chaves em 'dados_sensores' devem corresponder às chaves dos itens no Zabbix.
    """
    if clock_time is None:
        clock_time = int(time.time()) # Timestamp UNIX

    data_list = []
    for key, value in dados_sensores.items():
        if value is not None: # Envia apenas dados válidos
            data_list.append({
                "host": host_no_zabbix,
                "key": key, # Ex: "temperatura", "SmartLevelX"
                "value": str(value),
                "clock": clock_time
            })

    payload = {
        "request": "sender data",
        "data": data_list
    }
    return json.dumps(payload).encode('utf-8')

def _enviar_pacote_zabbix(pacote_json_bytes, server_ip, server_port, timeout_socket=10):
    """
    Envia o pacote de dados para o servidor Zabbix e retorna a resposta.
    """
    tamanho_dados = len(pacote_json_bytes).to_bytes(8, 'little')
    pacote_completo = ZABBIX_HEADER + tamanho_dados + pacote_json_bytes

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_socket) # Timeout para a conexão e operações de socket
        sock.connect((server_ip, server_port))

        if config.DEBUG_MODE:
            print(f"[{utils.agora()}] [Zabbix] Conectado a {server_ip}:{server_port}")
            # print(f"[{utils.agora()}] [Zabbix] Enviando pacote: {pacote_completo}") # Pode ser muito verboso

        sock.sendall(pacote_completo)

        # Espera pela resposta do Zabbix
        # A resposta também tem um header e um tamanho de dados
        resposta_header = sock.recv(5)
        if not resposta_header or resposta_header != ZABBIX_HEADER:
            print(f"[{utils.agora()}] [Zabbix] Resposta com header inválido: {resposta_header}")
            return None

        resposta_tamanho_bytes = sock.recv(8)
        if not resposta_tamanho_bytes or len(resposta_tamanho_bytes) < 8:
            print(f"[{utils.agora()}] [Zabbix] Resposta com tamanho de dados inválido ou incompleto.")
            return None

        resposta_tamanho = int.from_bytes(resposta_tamanho_bytes, 'little')

        resposta_json_bytes = sock.recv(resposta_tamanho)
        if not resposta_json_bytes:
            print(f"[{utils.agora()}] [Zabbix] Não recebeu payload de resposta.")
            return None

        resposta_json = json.loads(resposta_json_bytes.decode('utf-8'))
        if config.DEBUG_MODE:
            print(f"[{utils.agora()}] [Zabbix] Resposta recebida: {resposta_json}")
        return resposta_json

    except socket.timeout:
        print(f"[{utils.agora()}] [Zabbix] Timeout ao conectar ou enviar/receber dados de {server_ip}:{server_port}")
        return None
    except OSError as e: # Erros de rede, ex: Host não encontrado, rede inacessível
        print(f"[{utils.agora()}] [Zabbix] OSError ao comunicar com {server_ip}:{server_port}: {e}")
        return None
    except Exception as e:
        print(f"[{utils.agora()}] [Zabbix] Erro inesperado ao enviar dados: {e}")
        return None
    finally:
        if sock:
            sock.close()
            if config.DEBUG_MODE:
                print(f"[{utils.agora()}] [Zabbix] Socket fechado.")

def enviar_dados(dados_sensores, tentativas=None, clock_time=None):
    """
    Prepara e envia os dados dos sensores para o servidor Zabbix.
    Retorna True se o envio for bem-sucedido (conforme resposta do Zabbix), False caso contrário.
    """
    if not dados_sensores:
        print(f"[{utils.agora()}] [Zabbix] Nenhum dado de sensor para enviar.")
        return False

    _tentativas = tentativas if tentativas is not None else config.MAX_REENVIO_ZABBIX

    # Mapear nomes internos para chaves do Zabbix, se necessário.
    # Por enquanto, assume-se que as chaves em dados_sensores são as chaves do Zabbix.
    # Ex: Se config.ZABBIX_ITEM_KEY_TEMP = "pico.temp", então usaríamos:
    # dados_para_zabbix = {config.ZABBIX_ITEM_KEY_TEMP: dados_sensores["temperatura"]}
    # Mas para simplificar, vamos usar as chaves diretas.
    # É importante que os itens correspondentes existam no Zabbix Host.

    pacote_zabbix = _criar_pacote_zabbix(dados_sensores, config.ZABBIX_HOST, clock_time)
    if not json.loads(pacote_zabbix.decode('utf-8'))["data"]: # Verifica se há dados após a filtragem de None
        print(f"[{utils.agora()}] [Zabbix] Nenhum dado válido para enviar após a criação do pacote.")
        return False


    if config.DEBUG_MODE:
        print(f"[{utils.agora()}] [Zabbix] Pacote JSON a ser enviado: {pacote_zabbix.decode('utf-8')}")

    for tentativa in range(_tentativas):
        print(f"[{utils.agora()}] [Zabbix] Tentativa {tentativa + 1}/{_tentativas} de envio para {config.ZABBIX_SERVER}:{config.ZABBIX_PORT}")

        resposta = _enviar_pacote_zabbix(pacote_zabbix, config.ZABBIX_SERVER, config.ZABBIX_PORT)

        if resposta and 'response' in resposta and resposta['response'] == 'success':
            info = resposta.get('info', '') # Ex: "processed: 1; failed: 0; total: 1; seconds spent: 0.000123"
            # Verificar se houve falhas parciais, se necessário
            # Ex: if 'failed: 0' in info:
            print(f"[{utils.agora()}] [Zabbix] Dados enviados com sucesso. Info: {info}")

            # Limpar cache se o envio principal for bem-sucedido
            # (a lógica de cache será adicionada depois)
            # limpar_cache_principal()
            return True
        else:
            print(f"[{utils.agora()}] [Zabbix] Falha no envio ou resposta negativa do servidor na tentativa {tentativa + 1}.")
            if resposta:
                 print(f"[{utils.agora()}] [Zabbix] Detalhes da resposta: {resposta}")
            if tentativa < _tentativas - 1:
                print(f"[{utils.agora()}] [Zabbix] Aguardando antes da próxima tentativa...")
                time.sleep(2) # Pequena pausa entre tentativas

    print(f"[{utils.agora()}] [Zabbix] Falha ao enviar dados para o Zabbix após {_tentativas} tentativas.")
    # Salvar dados no cache se todas as tentativas falharem
    # (a lógica de cache será adicionada depois)
    # salvar_dados_em_cache(dados_sensores, clock_time if clock_time else int(time.time()))
    return False


# --- Lógica de Cache (a ser implementada/integrada futuramente) ---
# def salvar_dados_em_cache(dados, timestamp):
#     try:
#         with open(config.ARQUIVO_CACHE_DADOS, "a") as f:
#             # Formato do cache: timestamp;json_dos_dados
#             # Isso permite armazenar o conjunto completo de dados para um timestamp
#             linha_cache = f"{timestamp};{json.dumps(dados)}\n"
#             f.write(linha_cache)
#         print(f"[{utils.agora()}] [ZabbixCache] Dados salvos no cache: {linha_cache.strip()}")
#     except Exception as e:
#         print(f"[{utils.agora()}] [ZabbixCache] Erro ao salvar dados no cache: {e}")

# def processar_cache():
#     """ Tenta enviar dados do cache. Retorna True se o cache estiver vazio ou for processado com sucesso."""
#     linhas_mantidas = []
#     cache_processado_com_sucesso_total = True
#     try:
#         with open(config.ARQUIVO_CACHE_DADOS, "r") as f:
#             linhas_cache = f.readlines()

#         if not linhas_cache:
#             if config.DEBUG_MODE:
#                 print(f"[{utils.agora()}] [ZabbixCache] Cache está vazio.")
#             return True # Cache vazio é um sucesso

#         print(f"[{utils.agora()}] [ZabbixCache] {len(linhas_cache)} registros encontrados no cache. Tentando reenviar...")

#         for linha in linhas_cache:
#             linha = linha.strip()
#             if not linha:
#                 continue

#             try:
#                 timestamp_str, dados_json_str = linha.split(";", 1)
#                 ts = int(timestamp_str)
#                 dados_cached = json.loads(dados_json_str)

#                 print(f"[{utils.agora()}] [ZabbixCache] Tentando reenviar dados do cache (timestamp: {ts}): {dados_cached}")
#                 if enviar_dados(dados_cached, tentativas=1, clock_time=ts): # Tenta enviar apenas uma vez para cada item do cache
#                     print(f"[{utils.agora()}] [ZabbixCache] Dados do cache (timestamp: {ts}) enviados com sucesso.")
#                 else:
#                     print(f"[{utils.agora()}] [ZabbixCache] Falha ao reenviar dados do cache (timestamp: {ts}). Mantendo no cache.")
#                     linhas_mantidas.append(linha + "\n")
#                     cache_processado_com_sucesso_total = False
#             except Exception as e:
#                 print(f"[{utils.agora()}] [ZabbixCache] Erro ao processar linha do cache '{linha}': {e}. Mantendo no cache.")
#                 linhas_mantidas.append(linha + "\n")
#                 cache_processado_com_sucesso_total = False

#         # Reescreve o arquivo de cache apenas com as linhas que não puderam ser enviadas
#         with open(config.ARQUIVO_CACHE_DADOS, "w") as f:
#             for linha_mantida in linhas_mantidas:
#                 f.write(linha_mantida)

#         if cache_processado_com_sucesso_total:
#             print(f"[{utils.agora()}] [ZabbixCache] Todo o cache foi processado e enviado com sucesso ou estava vazio.")
#         elif not linhas_mantidas:
#              print(f"[{utils.agora()}] [ZabbixCache] Cache foi processado, e agora está vazio.")
#         else:
#             print(f"[{utils.agora()}] [ZabbixCache] {len(linhas_mantidas)} registros permanecem no cache após tentativa de reenvio.")

#         return cache_processado_com_sucesso_total

#     except OSError: # Arquivo de cache não existe
#         if config.DEBUG_MODE:
#             print(f"[{utils.agora()}] [ZabbixCache] Arquivo de cache não encontrado (normal se for a primeira execução).")
#         return True # Considera sucesso se não há cache para processar
#     except Exception as e:
#         print(f"[{utils.agora()}] [ZabbixCache] Erro ao processar o cache: {e}")
#         return False # Falha no processamento do cache

if __name__ == '__main__':
    print("Testando módulo zabbix_client...")

    # Certifique-se que config.py e utils.py estão acessíveis
    # E que ZABBIX_SERVER, ZABBIX_PORT e ZABBIX_HOST em config.py estão corretos.
    # Você precisará de um servidor Zabbix rodando e um Host configurado
    # com os itens correspondentes às chaves dos dados_teste.

    # Dados de teste simulados (como viriam do sensor_manager)
    dados_teste = {
        "temperatura": 23.5,
        "distancia": 150.2,
        "turbidez": 350, # Exemplo de valor ADC bruto
        "tds": 780,     # Exemplo de valor ADC bruto
        "item_inexistente_no_zabbix": 123 # Para testar o comportamento
    }

    # Remover um item para simular uma leitura falha
    # dados_teste["temperatura"] = None

    print(f"Enviando dados de teste: {dados_teste}")

    # Teste de envio direto
    sucesso = enviar_dados(dados_teste)
    if sucesso:
        print("Envio de dados de teste bem-sucedido!")
    else:
        print("Falha no envio dos dados de teste.")

    # Para testar o cache, você precisaria:
    # 1. Descomentar as funções de cache (salvar_dados_em_cache, processar_cache)
    # 2. Simular uma falha de rede (ex: ZABBIX_SERVER incorreto temporariamente) para que os dados sejam cacheados.
    # 3. Corrigir a rede e chamar processar_cache().

    # Exemplo de como poderia ser um teste de cache:
    # print("\nTestando funcionalidade de cache...")
    # config.ZABBIX_SERVER = "servidor.inexistente" # Força falha para cachear
    # print(f"Tentando enviar para servidor inválido ({config.ZABBIX_SERVER}) para testar cache...")
    # enviar_dados({"cache_test_item": time.time()}, clock_time=int(time.time())) # Salva no cache

    # # Restaurar servidor correto
    # config.ZABBIX_SERVER = "seu_servidor_zabbix_real" # Coloque o IP/DNS real aqui
    # print(f"Servidor Zabbix restaurado para: {config.ZABBIX_SERVER}")

    # print("Tentando processar o cache...")
    # if wifi_manager.conectar(): # Precisa de Wi-Fi para processar cache
    #     if processar_cache():
    #         print("Cache processado com sucesso (ou estava vazio).")
    #     else:
    #         print("Falha ao processar o cache ou alguns itens permaneceram.")
    #     wifi_manager.desconectar()
    # else:
    #     print("Não foi possível conectar ao Wi-Fi para testar o processamento do cache.")

    print("\nFim do teste do zabbix_client.")
