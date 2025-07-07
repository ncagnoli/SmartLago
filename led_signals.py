import machine
import time
import config

# Inicialização do LED Onboard
# O pino "LED" é um alias comum no Pico W para o LED onboard.
try:
    led_onboard = machine.Pin(config.PIN_LED_ONBOARD, machine.Pin.OUT)
except TypeError:
    # Fallback para o caso de config.PIN_LED_ONBOARD ser um número de pino inteiro
    # Isso pode acontecer se o usuário mudar a config para, por ex, um LED externo
    led_onboard = machine.Pin(int(config.PIN_LED_ONBOARD), machine.Pin.OUT)


def _piscar_led(vezes=1, duracao_on=0.1, duracao_off=0.1):
    """Função auxiliar para piscar o LED."""
    for _ in range(vezes):
        led_onboard.on()
        time.sleep(duracao_on)
        led_onboard.off()
        time.sleep(duracao_off)

def sinal_inicio_script():
    """Sinaliza que o script principal começou a rodar."""
    print("[LED] Sinal: Início do script")
    _piscar_led(vezes=3, duracao_on=0.05, duracao_off=0.05)
    time.sleep(0.5) # Pequena pausa após o sinal

def sinal_status_wifi(conectado: bool):
    """Sinaliza o status da conexão Wi-Fi."""
    if conectado:
        print("[LED] Sinal: Wi-Fi Conectado")
        # Pisca 2 vezes rápido para sucesso
        _piscar_led(vezes=2, duracao_on=0.1, duracao_off=0.1)
    else:
        print("[LED] Sinal: Falha na conexão Wi-Fi")
        # Pisca 1 vez longo para falha
        _piscar_led(vezes=1, duracao_on=0.5, duracao_off=0.1)

def sinal_envio_dados(sucesso: bool):
    """Sinaliza o status do envio de dados."""
    if sucesso:
        print("[LED] Sinal: Envio de dados com sucesso")
        # Pisca verde (se disponível) ou uma sequência específica.
        # Como é só um LED, vamos piscar rapidamente 3 vezes.
        _piscar_led(vezes=3, duracao_on=0.05, duracao_off=0.05)
    else:
        print("[LED] Sinal: Falha no envio de dados")
        # Pisca vermelho (se disponível) ou uma sequência longa.
        # Pisca lentamente 2 vezes.
        _piscar_led(vezes=2, duracao_on=0.3, duracao_off=0.2)

def sinal_erro_geral():
    """Sinaliza um erro geral/fatal antes de um reset, por exemplo."""
    print("[LED] Sinal: Erro Geral")
    # Sequência rápida e contínua (SOS-like)
    for _ in range(3): # Repete a sequência SOS 3x
        _piscar_led(vezes=3, duracao_on=0.05, duracao_off=0.05) # S
        time.sleep(0.1)
        _piscar_led(vezes=3, duracao_on=0.15, duracao_off=0.05) # O
        time.sleep(0.1)
        _piscar_led(vezes=3, duracao_on=0.05, duracao_off=0.05) # S
        time.sleep(0.3)

def sinal_leitura_sensores_em_andamento():
    """Sinaliza que a leitura dos sensores está ocorrendo (opcional)."""
    print("[LED] Sinal: Lendo sensores...")
    # Pulso curto para indicar atividade
    led_onboard.on()
    time.sleep(0.05)
    led_onboard.off()

if __name__ == '__main__':
    print("Testando sinais do LED...")
    sinal_inicio_script()
    time.sleep(1)

    print("Testando sinal Wi-Fi conectado...")
    sinal_status_wifi(True)
    time.sleep(1)

    print("Testando sinal Wi-Fi falha...")
    sinal_status_wifi(False)
    time.sleep(1)

    print("Testando sinal envio sucesso...")
    sinal_envio_dados(True)
    time.sleep(1)

    print("Testando sinal envio falha...")
    sinal_envio_dados(False)
    time.sleep(1)

    print("Testando sinal leitura sensores...")
    sinal_leitura_sensores_em_andamento()
    time.sleep(1)

    print("Testando sinal erro geral (longo)...")
    sinal_erro_geral()
    print("Teste de LED concluído.")
