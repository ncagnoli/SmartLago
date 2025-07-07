import machine
import time
import config
import utils
import wifi_manager
import sensor_manager
import zabbix_client
import led_signals

def ciclo_principal():
    # 1. Sinalizar início do script
    # print(f"[{utils.agora()}] Script iniciado. Sinalizando LED... (placeholder)")
    led_signals.sinal_inicio_script()

    # 2. Ler dados dos sensores
    # print(f"[{utils.agora()}] Lendo sensores... (placeholder)")
    dados_sensores = sensor_manager.ler_todos_sensores()
    if not dados_sensores or any(value is None for value in dados_sensores.values()): # Verifica se o dict não é None e se algum valor é None
        print(f"[{utils.agora()}] Falha ao ler um ou mais sensores ou dados inválidos: {dados_sensores}. Tentando novamente no próximo ciclo.")
        # led_signals.sinal_erro_leitura_sensores() # Opcional: sinalizar erro específico de leitura
        # Considerar se deve retornar ou tentar enviar dados parciais. Por ora, retorna.
        return # Pula para o próximo ciclo

    # 3. Conectar ao Wi-Fi
    # print(f"[{utils.agora()}] Conectando ao Wi-Fi: {config.SSID}... (placeholder)")
    conectado_wifi = wifi_manager.conectar(config.SSID, config.SENHA)

    # 4. Sinalizar status da conexão Wi-Fi
    led_signals.sinal_status_wifi(conectado_wifi)
    if conectado_wifi:
        print(f"[{utils.agora()}] Wi-Fi conectado com sucesso. (placeholder)")
    else:
        print(f"[{utils.agora()}] Falha ao conectar ao Wi-Fi.")
        # Lógica de cache/armazenamento de dados_sensores para envio posterior aqui
        print(f"[{utils.agora()}] Dados dos sensores {dados_sensores} seriam armazenados para envio posterior.")
        # wifi_manager.desconectar() # Garante que o wifi esteja desligado se a conexão falhou parcialmente ou não é mais necessária.
        return # Pula para o próximo ciclo se não houver Wi-Fi para enviar

    # 5. Enviar dados para o Zabbix (somente se Wi-Fi conectado)
    if conectado_wifi:
        # print(f"[{utils.agora()}] Enviando dados para o Zabbix... (placeholder)")
        sucesso_envio = zabbix_client.enviar_dados(dados_sensores)
        led_signals.sinal_envio_dados(sucesso_envio)
        if sucesso_envio:
            print(f"[{utils.agora()}] Dados enviados com sucesso para o Zabbix.")
            # Aqui seria um bom lugar para tentar enviar dados do cache, se houver
            # if config.USAR_CACHE_ZABBIX:
            #    zabbix_client.processar_cache() # Tentaria enviar o que está em cache
        else:
            print(f"[{utils.agora()}] Falha ao enviar dados atuais para o Zabbix.")
            # Lógica de cache/armazenamento de dados_sensores para envio posterior aqui
            # if config.USAR_CACHE_ZABBIX:
            #    zabbix_client.salvar_dados_em_cache(dados_sensores, int(time.time()))
            print(f"[{utils.agora()}] Dados dos sensores {dados_sensores} seriam armazenados se o cache estivesse ativo.")

    # 6. Desconectar Wi-Fi (opcional, para economia de energia)
    if wifi_manager.esta_conectado(): # Verifica antes de tentar desconectar
        # print(f"[{utils.agora()}] Desconectando Wi-Fi para economizar energia... (placeholder)")
        wifi_manager.desconectar()

if __name__ == "__main__":
    while True:
        try:
            print(f"[{utils.agora()}] Iniciando novo ciclo de operações...")
            ciclo_principal()
            print(f"[{utils.agora()}] Ciclo concluído. Aguardando {config.INTERVALO_LOOP_PRINCIPAL} segundos.")
            time.sleep(config.INTERVALO_LOOP_PRINCIPAL)
        except Exception as e:
            print(f"[{utils.agora()}] Erro inesperado no loop principal: {e}")
            # Tenta logar o erro antes de reiniciar
            try:
                with open(config.ARQUIVO_FALHAS_LOG, "a") as f:
                    f.write(f"[{utils.agora()}] Erro fatal no main: {e}\n")
            except Exception as log_e:
                print(f"[{utils.agora()}] Falha ao escrever no log de erros: {log_e}")

            # Sinalizar erro geral antes de reiniciar, se possível
            try:
                if 'led_signals' in globals() and hasattr(led_signals, 'sinal_erro_geral'):
                    led_signals.sinal_erro_geral()
            except Exception:
                pass # Evita erro dentro do handler de erro

            print(f"[{utils.agora()}] Reiniciando o dispositivo em 5 segundos...")
            time.sleep(5)
            machine.reset()
