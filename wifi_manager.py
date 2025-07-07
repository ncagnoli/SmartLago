import network
import time
import config # Para acessar SSID e SENHA, se não passados como argumento
import utils # Para logging com timestamp

# Referência global para a interface WLAN
wlan = None

def conectar(ssid=None, senha=None, tentativas=3, timeout_conexao=15):
    """
    Tenta conectar à rede Wi-Fi especificada.
    Retorna True em sucesso, False em falha.
    """
    global wlan

    # Usa SSID e SENHA do config.py se não forem fornecidos
    _ssid = ssid if ssid else config.SSID
    _senha = senha if senha else config.SENHA

    if not wlan:
        wlan = network.WLAN(network.STA_IF)

    if not wlan.active():
        print(f"[{utils.agora()}] Ativando interface Wi-Fi...")
        wlan.active(True)
        time.sleep(1) # Pequena pausa para a interface ativar

    if wlan.isconnected():
        print(f"[{utils.agora()}] Wi-Fi já está conectado ao IP: {wlan.ifconfig()[0]}")
        return True

    print(f"[{utils.agora()}] Tentando conectar à rede Wi-Fi: '{_ssid}'...")

    for tentativa in range(tentativas):
        print(f"[{utils.agora()}] Tentativa {tentativa + 1} de {tentativas}...")
        try:
            wlan.connect(_ssid, _senha)

            # Espera pela conexão
            start_time = time.time()
            while not wlan.isconnected():
                if time.time() - start_time > timeout_conexao:
                    print(f"[{utils.agora()}] Timeout ({timeout_conexao}s) na tentativa {tentativa + 1}.")
                    break # Sai do while de espera, vai para próxima tentativa
                print(f"[{utils.agora()}] Aguardando conexão... Status: {wlan.status()}")
                time.sleep(1)

            if wlan.isconnected():
                print(f"[{utils.agora()}] Wi-Fi conectado com sucesso!")
                print(f"[{utils.agora()}] Configurações de IP: {wlan.ifconfig()}")
                # Sincronizar NTP após conectar ao Wi-Fi
                try:
                    import ntptime
                    ntptime.settime()
                    print(f"[{utils.agora()}] Hora sincronizada via NTP: {utils.agora()}")
                except Exception as e:
                    print(f"[{utils.agora()}] Falha ao sincronizar horário NTP: {e}")
                return True
            else:
                # Se o timeout ocorreu e não conectou, desliga a tentativa atual.
                wlan.disconnect() # Garante que não fique em estado de tentativa pendente
                time.sleep(1) # Pausa antes de tentar novamente

        except OSError as e:
            print(f"[{utils.agora()}] OSError durante a tentativa de conexão: {e}")
            # Desativar e reativar a interface pode ajudar em alguns casos de erro persistente
            wlan.active(False)
            time.sleep(1)
            wlan.active(True)
            time.sleep(1)

    print(f"[{utils.agora()}] Falha ao conectar ao Wi-Fi '{_ssid}' após {tentativas} tentativas.")
    return False

def desconectar():
    """Desconecta da rede Wi-Fi e desativa a interface para economizar energia."""
    global wlan
    if wlan and wlan.isconnected():
        print(f"[{utils.agora()}] Desconectando do Wi-Fi...")
        wlan.disconnect()

    if wlan and wlan.active():
        print(f"[{utils.agora()}] Desativando interface Wi-Fi.")
        wlan.active(False)
        # wlan = None # Opcional: resetar a variável global se não for mais usada até a próxima conexão

    print(f"[{utils.agora()}] Wi-Fi desconectado e interface desativada.")
    return True

def esta_conectado():
    """Verifica se o Wi-Fi está atualmente conectado."""
    global wlan
    if wlan and wlan.isconnected():
        return True
    return False

if __name__ == '__main__':
    # Para testar, você precisaria ter um config.py no mesmo diretório
    # ou passar SSID e SENHA diretamente.
    print("Testando módulo wifi_manager...")

    if conectar(): # Tenta usar SSID/SENHA do config.py
        print("Status da conexão:", "Conectado" if esta_conectado() else "Desconectado")
        print("IP:", wlan.ifconfig()[0] if esta_conectado() else "N/A")

        print("\nAguardando 5 segundos antes de desconectar...")
        time.sleep(5)
        desconectar()
        print("Status da conexão após desconectar:", "Conectado" if esta_conectado() else "Desconectado")
    else:
        print("Não foi possível conectar ao Wi-Fi.")

    print("\nTeste de reconexão (ativando e desativando manualmente):")
    # Simula um estado onde wlan pode não estar ativo
    if wlan and wlan.active():
        wlan.active(False)
        time.sleep(1)

    # Teste com SSID e Senha inválidos (ou válidos, se quiser testar sucesso)
    # print("\nTestando conexão com credenciais inválidas (espera-se falha):")
    # if conectar("ssid_invalido", "senha_invalida", tentativas=2, timeout_conexao=5):
    #     print("Conexão inesperada com credenciais inválidas!")
    #     desconectar()
    # else:
    #     print("Falha ao conectar com credenciais inválidas (esperado).")

    print("Fim do teste do wifi_manager.")
