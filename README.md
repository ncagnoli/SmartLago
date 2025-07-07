# Projeto de Monitoramento com Raspberry Pi Pico W e Micropython

Este projeto utiliza um Raspberry Pi Pico W programado em Micropython para coletar dados de sensores e enviá-los para um sistema de monitoramento.

## Funcionalidades

*   Leitura de dados dos seguintes sensores:
    *   Temperatura (DS18B20)
    *   Distância (HC-SR04)
    *   Turbidez (Sensor de turbidez analógico)
    *   Sólidos Totais Dissolvidos (TDS)
*   Conexão à rede Wi-Fi para envio de dados.
*   Envio dos dados coletados para um servidor Zabbix.
*   Sinalização de status e operações através do LED onboard.

## Estrutura do Código Planejada

O código será modularizado para melhor organização e manutenção, com os seguintes arquivos principais:

*   `main.py`: Script principal que orquestra as operações de leitura e envio.
*   `config.py`: Armazena todas as configurações do projeto (credenciais Wi-Fi, informações do servidor Zabbix, pinos dos sensores, parâmetros de leitura, etc.).
*   `wifi_manager.py`: Gerencia a conexão com a rede Wi-Fi.
*   `sensor_manager.py`: Responsável pela interface com os sensores, leitura dos dados e cálculo de médias.
*   `zabbix_client.py`: Implementa a lógica para enviar os dados para o servidor Zabbix via socket.
*   `led_signals.py`: Controla os sinais visuais do LED para indicar diferentes estados do sistema.
*   `utils.py`: Contém funções utilitárias usadas em diferentes partes do projeto (ex: formatação de timestamp).

## Hardware

*   Raspberry Pi Pico W
*   Sensor de Temperatura DS18B20
*   Sensor Ultrassônico de Distância HC-SR04
*   Sensor de Turbidez Analógico
*   Sensor de Sólidos Totais Dissolvidos (TDS)
*   Resistores e jumpers conforme necessário para as conexões.

## Próximos Passos

1.  Refatorar o script inicial nos módulos descritos acima.
2.  Implementar a funcionalidade de envio de dados para o Zabbix.
3.  Adicionar novas funcionalidades conforme necessário.
