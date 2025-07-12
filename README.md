# Projeto de Monitoramento com Raspberry Pi Pico W e Micropython

Este projeto utiliza um Raspberry Pi Pico W programado em Micropython para coletar dados de sensores e enviá-los para um sistema de monitoramento.

## Funcionalidades

*   Leitura de dados dos seguintes sensores:
    *   Temperatura (DS18B20)
    *   Distância (HC-SR04)
    *   Turbidez (Sensor de turbidez analógico)
    *   Sólidos Totais Dissolvidos (TDS)
*   Conexão à rede Wi-Fi para envio de dados.
*   Sinalização de status e operações através do LED onboard.
*   Servidor HTTP embarcado para expor os dados dos sensores através de endpoints JSON.

## Endpoints HTTP

O servidor HTTP expõe os seguintes endpoints para consulta dos dados dos sensores. Todos os endpoints utilizam o método `GET` e não requerem parâmetros na requisição.

### `/temperatura`

*   **Método:** `GET`
*   **Descrição:** Retorna a leitura atual do sensor de temperatura.
*   **Resposta (Sucesso - 200 OK):**
    ```json
    {
      "sensor": "temperatura",
      "valor": 25.5,
      "unidade": "C"
    }
    ```
*   **Resposta (Erro - 500 Internal Server Error):** Se a leitura do sensor falhar.
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### `/distancia`

*   **Método:** `GET`
*   **Descrição:** Retorna a leitura atual do sensor de distância.
*   **Resposta (Sucesso - 200 OK):**
    ```json
    {
      "sensor": "distancia",
      "valor": 10.2,
      "unidade": "cm"
    }
    ```
*   **Resposta (Erro - 500 Internal Server Error):** Se a leitura do sensor falhar.
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### `/turbidez`

*   **Método:** `GET`
*   **Descrição:** Retorna a leitura atual do sensor de turbidez (valor ADC bruto).
*   **Resposta (Sucesso - 200 OK):**
    ```json
    {
      "sensor": "turbidez",
      "valor": 3000,
      "unidade": "ADC"
    }
    ```
*   **Resposta (Erro - 500 Internal Server Error):** Se a leitura do sensor falhar.
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### `/tds`

*   **Método:** `GET`
*   **Descrição:** Retorna a leitura atual do sensor de TDS (Sólidos Totais Dissolvidos - valor ADC bruto).
*   **Resposta (Sucesso - 200 OK):**
    ```json
    {
      "sensor": "tds",
      "valor": 1500,
      "unidade": "ADC"
    }
    ```
*   **Resposta (Erro - 500 Internal Server Error):** Se a leitura do sensor falhar.
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### `/todos_sensores`

*   **Método:** `GET`
*   **Descrição:** Retorna as leituras atuais de todos os sensores configurados.
*   **Resposta (Sucesso - 200 OK):**
    ```json
    {
      "temperatura": 25.5,
      "distancia": 10.2,
      "turbidez": 3000,
      "tds": 1500
    }
    ```
    *Nota: Se a leitura de um sensor específico falhar, seu valor no JSON será `null`.*
*   **Resposta (Erro - 500 Internal Server Error):** Em caso de falha crítica ao tentar ler os sensores (raro, pois falhas individuais são tratadas com `null`).
    ```json
    {
      "error": "Failed to read sensor or no data"
    }
    ```

### Outras Respostas HTTP Comuns

*   **`400 Bad Request`**: Se a requisição HTTP for malformada.
    ```json
    {"error": "Bad Request", "detail": "Descrição do erro"}
    ```
*   **`404 Not Found`**: Se o caminho (path) solicitado não existir.
    ```json
    {"error": "Not Found"}
    ```
*   **`405 Method Not Allowed`**: Se um método HTTP diferente de `GET` for utilizado.
    ```json
    {"error": "Method Not Allowed"}
    ```

## Estrutura do Código

O código é modularizado para melhor organização e manutenção, com os seguintes arquivos principais:

*   `main.py`: Script principal que inicializa o Wi-Fi e o servidor HTTP.
*   `config.py`: Armazena todas as configurações do projeto (credenciais Wi-Fi, pinos dos sensores, parâmetros de leitura, configurações do servidor HTTP, etc.).
*   `wifi_manager.py`: Gerencia a conexão com a rede Wi-Fi.
*   `sensor_manager.py`: Responsável pela interface com os sensores, leitura dos dados e processamento (filtragem, moda/média).
*   `http_server.py`: Implementa o servidor HTTP e o roteamento para os handlers dos sensores.
*   `led_signals.py`: Controla os sinais visuais do LED para indicar diferentes estados do sistema.
*   `utils.py`: Contém funções utilitárias (ex: formatação de timestamp).

## Hardware

*   Raspberry Pi Pico W
*   Sensor de Temperatura DS18B20
*   Sensor Ultrassônico de Distância HC-SR04
*   Sensor de Turbidez Analógico
*   Sensor de Sólidos Totais Dissolvidos (TDS)
*   Resistores e jumpers conforme necessário para as conexões.

## Próximos Passos

1.  Implementar tratamento mais robusto de erros e reconexão Wi-Fi.
2.  Adicionar mais testes unitários e de integração.
3.  Explorar a conversão dos valores ADC de Turbidez e TDS para unidades mais significativas (NTU, ppm), se aplicável e com calibração.
4.  Otimizar o consumo de energia.
5.  Adicionar novas funcionalidades conforme necessário.
