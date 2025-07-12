import time
import config
import utils
import wifi_manager
import http_server # Importado aqui pois é chamado diretamente no fluxo principal
import led_signals
# sensor_manager é usado por http_server, não diretamente por main.py no fluxo principal

if __name__ == "__main__":
    led_signals.sinal_inicio_script()

    # 1. Conexão Wi-Fi Inicial
    print(f"[{utils.agora()}] Iniciando tentativa de conexão Wi-Fi para '{config.SSID}'...")

    if wifi_manager.conectar(config.SSID, config.SENHA):
        led_signals.sinal_status_wifi(True)
        print(f"[{utils.agora()}] Wi-Fi conectado com sucesso. IP: {wifi_manager.get_ip()}")
    else:
        led_signals.sinal_status_wifi(False)
        print(f"[{utils.agora()}] Falha crítica ao conectar ao Wi-Fi na inicialização. Verifique as credenciais e a rede.")
        # O script prosseguirá para o loop de tentativa de inicialização do servidor.

    # 2. Loop Principal: Tentar iniciar o servidor HTTP ou reconectar Wi-Fi
    # Este loop continua indefinidamente, tentando manter o servidor operacional.
    while True:
        if wifi_manager.esta_conectado():
            print(f"[{utils.agora()}] Wi-Fi conectado. Tentando iniciar/verificar servidor HTTP...")

            # http_server.start_server() é bloqueante e contém seu próprio loop de escuta.
            # Ele só retorna False se não puder iniciar (ex: erro de socket).
            # Se parar por uma exceção interna não tratada, o script pode sair do start_server.
            server_started_successfully = http_server.start_server()

            if not server_started_successfully:
                print(f"[{utils.agora()}] Servidor HTTP falhou ao iniciar (ex: bind error). Verifique a configuração da porta.")
                led_signals.sinal_erro_geral()
            else:
                # Se start_server() retornar True (ou qualquer valor não False),
                # significa que ele parou por algum motivo após iniciar (o que não deveria ocorrer).
                # Isso pode indicar um erro inesperado dentro do loop do servidor.
                print(f"[{utils.agora()}] Servidor HTTP parou inesperadamente após iniciar.")
                led_signals.sinal_erro_geral()

            # Pausa antes de tentar reiniciar o servidor ou reconectar o Wi-Fi.
            print(f"[{utils.agora()}] Aguardando {config.INTERVALO_RECONEXAO_WIFI}s antes da próxima tentativa...")
            time.sleep(config.INTERVALO_RECONEXAO_WIFI)

        else: # Wi-Fi não está conectado
            print(f"[{utils.agora()}] Wi-Fi desconectado. Tentando reconectar...")
            led_signals.sinal_status_wifi(False)
            if wifi_manager.conectar(config.SSID, config.SENHA):
                led_signals.sinal_status_wifi(True)
                print(f"[{utils.agora()}] Wi-Fi reconectado com sucesso. IP: {wifi_manager.get_ip()}")
                # Imediatamente tenta (re)iniciar o servidor no próximo ciclo do while True
            else:
                print(f"[{utils.agora()}] Falha ao reconectar Wi-Fi. Tentando novamente em {config.INTERVALO_RECONEXAO_WIFI}s.")
                time.sleep(config.INTERVALO_RECONEXAO_WIFI)

    # O código abaixo deste loop while True não deve ser alcançado em operação normal.
    # Se chegar aqui, é um estado de erro não previsto pelo loop.
    print(f"[{utils.agora()}] Fim inesperado do script principal (fora do loop de recuperação).")
    led_signals.sinal_erro_geral()
    # Mantém o dispositivo "vivo" em um loop final para inspeção, se necessário.
    while True:
        time.sleep(60)
        print(f"[{utils.agora()}] Script principal em estado de erro final. Por favor, verifique o dispositivo.")
