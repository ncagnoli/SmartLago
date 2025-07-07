import time

def agora():
    """Retorna a data e hora atuais formatadas como string."""
    # Micropython's time.localtime() retorna:
    # (ano, mês, dia_mês, hora, minuto, segundo, dia_semana, dia_ano)
    # dia_semana: 0 para Segunda, 6 para Domingo
    # dia_ano: 1 a 366

    # ntptime.settime() precisa ser chamado em algum lugar para sincronizar o RTC
    # Isso geralmente é feito após a conexão Wi-Fi.

    t = time.localtime()
    # Formato: YYYY-MM-DD HH:MM:SS
    return f"{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

if __name__ == '__main__':
    # Teste rápido da função
    print("Hora atual formatada:", agora())
    time.sleep(2)
    print("Hora atual formatada (após 2s):", agora())
