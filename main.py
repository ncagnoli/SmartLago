#import machine
import time
import config # Import config first
import utils
import wifi_manager # wifi_manager now depends on config
import sensor_manager # sensor_manager now depends on config
# zabbix_client removido
import led_signals

# Web server imports will be added later

def ciclo_principal():
    # 1. Sinalizar início do script
    led_signals.sinal_inicio_script()

    # 2. Conectar ao Wi-Fi (necessário para o servidor HTTP)
    if not wifi_manager.esta_conectado():
        print(f"[{utils.agora()}] Tentando conectar ao Wi-Fi: {config.SSID}...")
        conectado_wifi = wifi_manager.conectar(config.SSID, config.SENHA)
        led_signals.sinal_status_wifi(conectado_wifi)
        if conectado_wifi:
            print(f"[{utils.agora()}] Wi-Fi conectado com sucesso.")
        else:
            print(f"[{utils.agora()}] Falha ao conectar ao Wi-Fi. O servidor HTTP não será iniciado.")
            # Poderia tentar reconectar periodicamente ou reiniciar
            time.sleep(config.INTERVALO_RECONEXAO_WIFI)
            return # Adia o início do servidor se o Wi-Fi falhar
    else:
        print(f"[{utils.agora()}] Wi-Fi já está conectado.")


    # 3. Inicializar e iniciar o servidor HTTP (esta lógica será movida para uma função dedicada)
    #    Por enquanto, apenas um placeholder. A leitura de sensores será feita pelos endpoints.
    print(f"[{utils.agora()}] Lógica do servidor HTTP e endpoints será implementada aqui.")
    print(f"[{utils.agora()}] O servidor escutaria por requisições e chamaria sensor_manager.ler_sensor_especifico() por endpoint.")

    # O loop principal agora pode ser mais simples, focando em manter o servidor rodando
    # e talvez algumas tarefas de manutenção. A leitura de sensores será reativa (por requisição HTTP).

    # Exemplo de como poderia ser a estrutura do servidor (muito simplificado):
    # server_socket = setup_http_server()
    # print(f"[{utils.agora()}] Servidor HTTP iniciado em {wifi_manager.get_ip()}:{config.HTTP_PORT}")
    # while True:
    #     conn, addr = server_socket.accept()
    #     request = conn.recv(1024)
    #     # process_request(request, conn) # Aqui chamaria os handlers de endpoint

    # Por enquanto, o ciclo principal apenas garante que o Wi-Fi está ativo
    # e simula uma espera, já que o servidor HTTP real (com loop de escuta) ainda não está implementado.
    # A lógica de leitura de sensores (dados_sensores = sensor_manager.ler_todos_sensores())
    # será acionada pelos endpoints do servidor HTTP.

    # A desconexão do Wi-Fi não é mais desejável aqui, pois o servidor precisa dele.

    # A lógica de envio de dados para Zabbix foi removida.
    # A lógica de cache de dados para Zabbix também foi implicitamente removida.

    # O 'ciclo_principal' como era antes (leitura periódica + envio) não se aplica mais diretamente.
    # O novo 'ciclo' será o loop de escuta do servidor HTTP.
    # Este 'ciclo_principal' pode se tornar uma função de inicialização e manutenção.
    pass


if __name__ == "__main__":
    # Inicialização única
    led_signals.sinal_inicio_script() # Sinaliza uma vez no boot

    # Tenta conectar ao Wi-Fi na inicialização
    if not wifi_manager.conectar(config.SSID, config.SENHA):
        print(f"[{utils.agora()}] Falha crítica ao conectar ao Wi-Fi na inicialização. Verifique as credenciais e a rede.")
        # Poderia tentar um modo de fallback ou reiniciar após um tempo.
        # Por enquanto, vamos permitir que o script continue, mas o servidor não funcionará.
        led_signals.sinal_status_wifi(False)
    else:
        led_signals.sinal_status_wifi(True)
        print(f"[{utils.agora()}] Wi-Fi conectado. IP: {wifi_manager.get_ip()}")
        # Aqui é onde o servidor HTTP seria iniciado e entraria em seu próprio loop.
        # Ex: start_http_server() # Esta função conteria o loop de escuta.

    print(f"[{utils.agora()}] Configuração inicial completa. O servidor HTTP (a ser implementado) deve estar rodando se o Wi-Fi conectou.")
    print(f"[{utils.agora()}] O sistema agora aguardará por requisições HTTP nos endpoints dos sensores.")

    # O loop principal do programa se tornará o loop do servidor HTTP.
    # Por enquanto, vamos simular uma operação contínua,
    # e a lógica do servidor será adicionada nos próximos passos.
    # Este loop while True pode ser substituído pelo loop de escuta do servidor HTTP.
    # Ou, se o servidor rodar em uma thread (com _thread), este loop pode fazer outras coisas.

    # Por simplicidade inicial, vamos assumir que o servidor HTTP será bloqueante
    # e seu loop de escuta será o loop principal. A função `start_http_server()` faria isso.

    # Importar http_server aqui para que ele possa ser chamado
    import http_server

    if wifi_manager.esta_conectado():
        print(f"[{utils.agora()}] Wi-Fi conectado. Iniciando servidor HTTP...")
        # A função start_server() em http_server.py contém o loop principal do servidor.
        # Se start_server() retornar (o que não deveria acontecer em operação normal,
        # a menos que haja um erro fatal não tratado dentro dele ou seja interrompido),
        # o código abaixo será executado.
        if not http_server.start_server():
            print(f"[{utils.agora()}] Servidor HTTP falhou ao iniciar ou parou inesperadamente.")
            led_signals.sinal_erro_geral() # Sinaliza um erro se o servidor não puder iniciar
            # Poderia tentar reiniciar o dispositivo ou entrar em um loop de reconexão/re-setup.
            print(f"[{utils.agora()}] O dispositivo pode precisar ser reiniciado ou verificado.")
            # Loop de espera para evitar spam de logs se houver falha contínua.
            time.sleep(config.INTERVALO_RECONEXAO_WIFI) # Reutiliza o intervalo de reconexão para espera
    else:
        print(f"[{utils.agora()}] Wi-Fi não conectado na inicialização. Servidor HTTP não iniciado.")
        print(f"[{utils.agora()}] O sistema tentará reconectar o Wi-Fi e iniciar o servidor em um loop de manutenção.")
        # Entra em um loop para tentar reconectar o Wi-Fi e iniciar o servidor.
        # Este loop é um fallback caso a conexão inicial falhe.
        while not wifi_manager.esta_conectado():
            print(f"[{utils.agora()}] Tentando reconectar Wi-Fi...")
            if wifi_manager.conectar(config.SSID, config.SENHA):
                print(f"[{utils.agora()}] Wi-Fi reconectado. Tentando iniciar o servidor HTTP...")
                led_signals.sinal_status_wifi(True)
                if not http_server.start_server(): # Tenta iniciar o servidor
                    print(f"[{utils.agora()}] Falha ao iniciar o servidor HTTP após reconexão. Tentando novamente...")
                    led_signals.sinal_erro_geral()
                    # Se start_server falhar, o loop de while not wifi_manager.esta_conectado()
                    # não será re-acionado a menos que o Wi-Fi caia de novo.
                    # Precisamos de um delay aqui antes de tentar o start_server novamente.
                    time.sleep(config.INTERVALO_RECONEXAO_WIFI) # Pausa antes de tentar de novo
                else:
                    # Se start_server foi bem sucedido, ele entra em seu próprio loop infinito.
                    # Este ponto não deve ser alcançado a menos que start_server pare.
                    print(f"[{utils.agora()}] Servidor HTTP parou inesperadamente após reconexão.")
                    break # Sai do loop de reconexão se o servidor parar
            else:
                print(f"[{utils.agora()}] Falha ao reconectar Wi-Fi. Tentando novamente em {config.INTERVALO_RECONEXAO_WIFI}s.")
                led_signals.sinal_status_wifi(False)
                time.sleep(config.INTERVALO_RECONEXAO_WIFI)

    # Se o código chegar aqui, significa que o servidor HTTP (ou o loop de tentativa de inicialização) terminou,
    # o que geralmente indica um problema sério.
    print(f"[{utils.agora()}] Fim inesperado do script principal. O dispositivo pode precisar de atenção.")
    led_signals.sinal_erro_geral()
    # Loop de segurança para evitar que o script termine e o dispositivo entre em estado desconhecido.
    while True:
        time.sleep(60) # Apenas mantém o dispositivo "vivo"
        print(f"[{utils.agora()}] Script principal em estado de erro final. Por favor, verifique o dispositivo.")


    # O loop de manutenção antigo foi removido, pois o loop principal agora é o servidor HTTP.
    # A verificação de conectividade Wi-Fi e reconexão deve ser tratada
    # de forma mais robusta, possivelmente exigindo uma reinicialização do servidor HTTP
    # ou do próprio dispositivo se o Wi-Fi for perdido por muito tempo.
    # A implementação atual de start_server() é bloqueante e não retorna,
    # então o código abaixo do seu chamado só executa se ele falhar ao iniciar ou parar.

    # Código de erro e reinicialização que estava no loop while True anterior:
    # except Exception as e:
    # print(f"[{utils.agora()}] Erro inesperado no loop principal de manutenção: {e}")
            try:
                with open(config.ARQUIVO_FALHAS_LOG, "a") as f:
                    f.write(f"[{utils.agora()}] Erro no loop de manutenção: {e}\n")
            except Exception as log_e:
                print(f"[{utils.agora()}] Falha ao escrever no log de erros: {log_e}")

            led_signals.sinal_erro_geral()
            print(f"[{utils.agora()}] Considerar reinicialização ou tratamento mais robusto aqui.")
            # Para evitar loops de erro rápidos, um delay maior antes de tentar de novo ou reiniciar.
            time.sleep(30)
            # machine.reset() # Descomentar se uma reinicialização for desejada em caso de erro grave aqui.
