import socket
import time
import config
import utils
import sensor_manager
import wifi_manager
import json

# Dictionary to store route handlers
route_handlers = {}

def build_http_response(body, status_code=200, content_type="application/json"):
    """Builds an HTTP response string."""
    status_description = "OK"
    if status_code == 404:
        status_description = "Not Found"
    elif status_code == 500:
        status_description = "Internal Server Error"
    elif status_code == 400:
        status_description = "Bad Request"
    elif status_code == 405:
        status_description = "Method Not Allowed"

    response = f"HTTP/1.1 {status_code} {status_description}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += f"Content-Length: {len(body)}\r\n"
    response += "Connection: close\r\n\r\n"
    response += body
    return response.encode('utf-8')

def handle_request(request_data, conn):
    """
    Processes the received HTTP request, identifies the route, and calls the appropriate handler.
    """
    request_line_str = ""
    try:
        if not request_data:
            print(f"[{utils.agora()}] [HTTP_SERVER] Empty request received.")
            response_body = '{"error": "Bad Request", "detail": "Empty request"}'
            response = build_http_response(response_body, status_code=400)
            conn.sendall(response)
            return

        request_lines = request_data.splitlines()
        if not request_lines:
            print(f"[{utils.agora()}] [HTTP_SERVER] Request data contains no lines.")
            response_body = '{"error": "Bad Request", "detail": "No lines in request"}'
            response = build_http_response(response_body, status_code=400)
            conn.sendall(response)
            return

        request_line_str = request_lines[0]
        parts = request_line_str.split()
        if len(parts) < 2:
            print(f"[{utils.agora()}] [HTTP_SERVER] Malformed request line: {request_line_str}")
            response_body = '{"error": "Bad Request", "detail": "Malformed request line"}'
            response = build_http_response(response_body, status_code=400)
            conn.sendall(response)
            return

        method, path = parts[0], parts[1]

    except ValueError:
        print(f"[{utils.agora()}] [HTTP_SERVER] ValueError parsing request line: {request_line_str}")
        response_body = '{"error": "Bad Request", "detail": "ValueError parsing request line"}'
        response = build_http_response(response_body, status_code=400)
        conn.sendall(response)
        return
    except Exception as e:
        print(f"[{utils.agora()}] [HTTP_SERVER] Generic error parsing request line '{request_line_str}': {e}")
        response_body = '{"error": "Bad Request", "detail": "Generic parsing error"}'
        response = build_http_response(response_body, status_code=400)
        conn.sendall(response)
        return

    print(f"[{utils.agora()}] [HTTP_SERVER] Received {method} for {path}")

    handler = route_handlers.get(path)

    if handler:
        if method == "GET":
            try:
                response_body_dict = handler()
                if response_body_dict is None:
                    response_body_json = '{"error": "Failed to read sensor or no data"}'
                    response = build_http_response(response_body_json, status_code=500)
                else:
                    response_body_json = json.dumps(response_body_dict)
                    response = build_http_response(response_body_json)
            except Exception as e:
                print(f"[{utils.agora()}] [HTTP_SERVER] Error in handler for {path}: {e}")
                response_body_json = '{"error": "Internal Server Error", "detail": str(e)}'
                response = build_http_response(response_body_json, status_code=500)
        else:
            print(f"[{utils.agora()}] [HTTP_SERVER] Method {method} not allowed for {path}")
            response_body_json = '{"error": "Method Not Allowed"}'
            response = build_http_response(response_body_json, status_code=405)
    else:
        response_body_json = '{"error": "Not Found"}'
        response = build_http_response(response_body_json, status_code=404)

    try:
        conn.sendall(response)
    except OSError as e:
        print(f"[{utils.agora()}] [HTTP_SERVER] OSError sending response for {path}: {e}")
    except Exception as e:
        print(f"[{utils.agora()}] [HTTP_SERVER] Unexpected error sending response for {path}: {e}")


def start_server():
    """
    Initializes the HTTP server and enters the listening loop for connections.
    Returns False if the server cannot start.
    """
    if not wifi_manager.esta_conectado():
        print(f"[{utils.agora()}] [HTTP_SERVER] Wi-Fi not connected. Server cannot start.")
        return False

    server_socket = None
    try:
        addr_info_list = socket.getaddrinfo('0.0.0.0', config.HTTP_PORT)
        if not addr_info_list:
            print(f"[{utils.agora()}] [HTTP_SERVER] Error: getaddrinfo returned empty list for 0.0.0.0:{config.HTTP_PORT}")
            return False
        addr = addr_info_list[0][-1]

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(addr)
        server_socket.listen(config.HTTP_MAX_PENDING_CONN)
        print(f"[{utils.agora()}] [HTTP_SERVER] Listening on {wifi_manager.get_ip()}:{config.HTTP_PORT}")
    except Exception as e:
        print(f"[{utils.agora()}] [HTTP_SERVER] Error binding/listening on socket: {e}")
        if server_socket:
            server_socket.close()
        return False

    client_conn = None
    addr_client_str = "unknown client"
    while True:
        try:
            client_conn, addr_client = server_socket.accept()
            addr_client_str = f"{addr_client[0]}:{addr_client[1]}"
            client_conn.settimeout(config.HTTP_CLIENT_TIMEOUT_S)

            print(f"[{utils.agora()}] [HTTP_SERVER] Connection from {addr_client_str}")

            request_bytes = client_conn.recv(config.HTTP_MAX_REQUEST_SIZE)
            if not request_bytes:
                print(f"[{utils.agora()}] [HTTP_SERVER] Connection from {addr_client_str} closed without data.")
            else:
                request_data_str = ""
                try:
                    request_data_str = request_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    print(f"[{utils.agora()}] [HTTP_SERVER] UnicodeDecodeError from {addr_client_str}. Sending Bad Request.")
                    response_body = '{"error": "Bad Request", "detail": "Invalid UTF-8 in request"}'
                    response = build_http_response(response_body, status_code=400)
                    client_conn.sendall(response)
                else:
                    handle_request(request_data_str, client_conn)

        except socket.timeout:
            print(f"[{utils.agora()}] [HTTP_SERVER] Socket timeout with {addr_client_str}")
        except OSError as e:
            print(f"[{utils.agora()}] [HTTP_SERVER] OSError with {addr_client_str}: {e}")
        except Exception as e:
            print(f"[{utils.agora()}] [HTTP_SERVER] Unexpected error in server loop with {addr_client_str}: {e}")
            if client_conn and not getattr(client_conn, '_closed', True): # Check if socket is not already closed
                try:
                    response_body = '{"error": "Server Loop Error"}'
                    response = build_http_response(response_body, status_code=500)
                    client_conn.sendall(response)
                except Exception as send_err:
                    print(f"[{utils.agora()}] [HTTP_SERVER] Failed to send 500 error to {addr_client_str}: {send_err}")
        finally:
            if client_conn:
                try:
                    client_conn.close()
                    # Evita log para clientes desconhecidos que podem não ter realmente conectado
                    # ou para casos onde addr_client_str não foi definido devido a um erro anterior.
                    if addr_client_str != "unknown client":
                        print(f"[{utils.agora()}] [HTTP_SERVER] Connection with {addr_client_str} closed.")
                except Exception as e_close:
                    print(f"[{utils.agora()}] [HTTP_SERVER] Error closing connection with {addr_client_str}: {e_close}")
            client_conn = None
            addr_client_str = "unknown client"

# --- Route Handlers ---
def handle_temperatura_request():
    """Handler para o endpoint /temperatura."""
    print(f"[{utils.agora()}] [HTTP_HANDLER] /temperatura solicitado.")
    return sensor_manager.ler_sensor_especifico("temperatura")

def handle_distancia_request():
    """Handler para o endpoint /distancia."""
    print(f"[{utils.agora()}] [HTTP_HANDLER] /distancia solicitado.")
    return sensor_manager.ler_sensor_especifico("distancia")

def handle_turbidez_request():
    """Handler para o endpoint /turbidez."""
    print(f"[{utils.agora()}] [HTTP_HANDLER] /turbidez solicitado.")
    return sensor_manager.ler_sensor_especifico("turbidez")

def handle_tds_request():
    """Handler para o endpoint /tds."""
    print(f"[{utils.agora()}] [HTTP_HANDLER] /tds solicitado.")
    return sensor_manager.ler_sensor_especifico("tds")

def handle_todos_sensores_request():
    """
    Handler para o endpoint /todos_sensores.
    Retorna um dicionário com as leituras de todos os sensores.
    """
    print(f"[{utils.agora()}] [HTTP_HANDLER] /todos_sensores solicitado.")
    # sensor_manager.ler_todos_sensores() retorna um dict como {"temperatura": X, "distancia": Y, ...}
    # ou um dict com valores None se alguma leitura falhar.
    # O servidor HTTP já trata o caso de o handler retornar None (erro 500),
    # mas ler_todos_sensores() pode retornar um dict com valores None parciais, o que é aceitável.
    return sensor_manager.ler_todos_sensores()

# Registrar os handlers de rota
route_handlers["/temperatura"] = handle_temperatura_request
route_handlers["/distancia"] = handle_distancia_request
route_handlers["/turbidez"] = handle_turbidez_request
route_handlers["/tds"] = handle_tds_request
route_handlers["/todos_sensores"] = handle_todos_sensores_request


if __name__ == "__main__":
    print(f"[{utils.agora()}] Testing http_server.py directly...")

    # Adicionada a rota /todos_sensores também para teste local.
    # Os handlers de teste /test e /sensor_example são mantidos para depuração básica do servidor.

    if not wifi_manager.esta_conectado():
        print(f"[{utils.agora()}] [HTTP_SERVER_TEST] Wi-Fi not connected. Attempting to connect...")
        if not wifi_manager.conectar(config.SSID, config.SENHA):
            print(f"[{utils.agora()}] [HTTP_SERVER_TEST] Failed to connect to Wi-Fi. Aborting server test.")
        else:
            print(f"[{utils.agora()}] [HTTP_SERVER_TEST] Wi-Fi connected: {wifi_manager.get_ip()}")
    else:
        print(f"[{utils.agora()}] [HTTP_SERVER_TEST] Wi-Fi already connected: {wifi_manager.get_ip()}")

    if wifi_manager.esta_conectado():
        def handle_test_endpoint():
            return {"status": "success", "message": "HTTP server is running!", "timestamp": utils.agora()}
        route_handlers["/test"] = handle_test_endpoint

        def handle_sensor_example():
            return {"sensor_name": "example_temp", "value": 25.5, "unit": "C"}
        route_handlers["/sensor_example"] = handle_sensor_example

        print(f"[{utils.agora()}] [HTTP_SERVER_TEST] Access test endpoints:")
        print(f"  http://{wifi_manager.get_ip()}:{config.HTTP_PORT}/test")
        print(f"  http://{wifi_manager.get_ip()}:{config.HTTP_PORT}/sensor_example")

        if not start_server():
             print(f"[{utils.agora()}] [HTTP_SERVER_TEST] Server failed to start.")
    else:
        print(f"[{utils.agora()}] [HTTP_SERVER_TEST] Cannot start server test without Wi-Fi.")

    print(f"[{utils.agora()}] [HTTP_SERVER_TEST] Server test finished or interrupted.")
