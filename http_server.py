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
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Empty request received.")
            response_body = '{"error": "Bad Request", "detail": "Empty request"}'
            response = build_http_response(response_body, status_code=400)
            conn.sendall(response)
            return

        request_lines = request_data.splitlines()
        if not request_lines:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Request data contains no lines.")
            response_body = '{"error": "Bad Request", "detail": "No lines in request"}'
            response = build_http_response(response_body, status_code=400)
            conn.sendall(response)
            return

        request_line_str = request_lines[0]
        parts = request_line_str.split()
        if len(parts) < 2:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Malformed request line: {request_line_str}")
            response_body = '{"error": "Bad Request", "detail": "Malformed request line"}'
            response = build_http_response(response_body, status_code=400)
            conn.sendall(response)
            return

        method, path = parts[0], parts[1]

    except ValueError:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] ValueError parsing request line: {request_line_str}")
        response_body = '{"error": "Bad Request", "detail": "ValueError parsing request line"}'
        response = build_http_response(response_body, status_code=400)
        conn.sendall(response)
        return
    except Exception as e:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Generic error parsing request line '{request_line_str}': {e}")
        response_body = '{"error": "Bad Request", "detail": "Generic parsing error"}'
        response = build_http_response(response_body, status_code=400)
        conn.sendall(response)
        return

    print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Received {method} for {path}")

    handler = route_handlers.get(path)

    if handler:
        if method == "GET":
            try:
                response_data = handler() # This will now be a simple dict for individual sensors or the full dict for all_sensors
                if response_data is None: # Handles cases where sensor reading failed critically
                    response_body_json = '{"error": "Failed to read sensor or no data"}'
                    response = build_http_response(response_body_json, status_code=500)
                else:
                    response_body_json = json.dumps(response_data)
                    response = build_http_response(response_body_json)
            except Exception as e:
                print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Error in handler for {path}: {e}")
                response_body_json = '{"error": "Internal Server Error", "detail": str(e)}'
                response = build_http_response(response_body_json, status_code=500)
        else:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Method {method} not allowed for {path}")
            response_body_json = '{"error": "Method Not Allowed"}'
            response = build_http_response(response_body_json, status_code=405)
    else:
        response_body_json = '{"error": "Not Found"}'
        response = build_http_response(response_body_json, status_code=404)

    try:
        conn.sendall(response)
    except OSError as e:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] OSError sending response for {path}: {e}")
    except Exception as e:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Unexpected error sending response for {path}: {e}")


def start_server():
    """
    Initializes the HTTP server and enters the listening loop for connections.
    Returns False if the server cannot start.
    """
    if not wifi_manager.is_connected():
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Wi-Fi not connected. Server cannot start.")
        return False

    server_socket = None
    try:
        addr_info_list = socket.getaddrinfo('0.0.0.0', config.HTTP_PORT)
        if not addr_info_list:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Error: getaddrinfo returned empty list for 0.0.0.0:{config.HTTP_PORT}")
            return False
        addr = addr_info_list[0][-1]

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(addr)
        server_socket.listen(config.HTTP_MAX_PENDING_CONN)
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Listening on {wifi_manager.get_ip()}:{config.HTTP_PORT}")
    except Exception as e:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Error binding/listening on socket: {e}")
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

            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Connection from {addr_client_str}")

            request_bytes = client_conn.recv(config.HTTP_MAX_REQUEST_SIZE)
            if not request_bytes:
                print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Connection from {addr_client_str} closed without data.")
            else:
                request_data_str = ""
                try:
                    request_data_str = request_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    print(f"[{utils.get_timestamp()}] [HTTP_SERVER] UnicodeDecodeError from {addr_client_str}. Sending Bad Request.")
                    response_body = '{"error": "Bad Request", "detail": "Invalid UTF-8 in request"}'
                    response = build_http_response(response_body, status_code=400)
                    client_conn.sendall(response)
                else:
                    handle_request(request_data_str, client_conn)

        except socket.timeout:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Socket timeout with {addr_client_str}")
        except OSError as e:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] OSError with {addr_client_str}: {e}")
        except Exception as e:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Unexpected error in server loop with {addr_client_str}: {e}")
            if client_conn and not getattr(client_conn, '_closed', True):
                try:
                    response_body = '{"error": "Server Loop Error"}'
                    response = build_http_response(response_body, status_code=500)
                    client_conn.sendall(response)
                except Exception as send_err:
                    print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Failed to send 500 error to {addr_client_str}: {send_err}")
        finally:
            if client_conn:
                try:
                    client_conn.close()
                    if addr_client_str != "unknown client":
                        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Connection with {addr_client_str} closed.")
                except Exception as e_close:
                    print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Error closing connection with {addr_client_str}: {e_close}")
            client_conn = None
            addr_client_str = "unknown client"

# --- Route Handlers ---
def handle_temperature_request():
    """Handler for the /temperature endpoint."""
    print(f"[{utils.get_timestamp()}] [HTTP_HANDLER] /temperature requested.")
    result = sensor_manager.read_specific_sensor("temperature")
    return { "temperature": result.get("value") } if result and result.get("value") is not None else None

def handle_distance_request():
    """Handler for the /distance endpoint."""
    print(f"[{utils.get_timestamp()}] [HTTP_HANDLER] /distance requested.")
    result = sensor_manager.read_specific_sensor("distance")
    return { "distance": result.get("value") } if result and result.get("value") is not None else None

def handle_turbidity_request():
    """Handler for the /turbidity endpoint."""
    print(f"[{utils.get_timestamp()}] [HTTP_HANDLER] /turbidity requested.")
    result = sensor_manager.read_specific_sensor("turbidity")
    return { "turbidity": result.get("value") } if result and result.get("value") is not None else None

def handle_tds_request():
    """Handler for the /tds endpoint."""
    print(f"[{utils.get_timestamp()}] [HTTP_HANDLER] /tds requested.")
    result = sensor_manager.read_specific_sensor("tds")
    return { "tds": result.get("value") } if result and result.get("value") is not None else None

def handle_all_sensors_request():
    """
    Handler for the /todos_sensores endpoint.
    Returns a dictionary with readings from all sensors.
    This endpoint will retain its existing structure with multiple sensor values.
    """
    print(f"[{utils.get_timestamp()}] [HTTP_HANDLER] /todos_sensores requested.")
    return sensor_manager.read_all_sensors()

# Register route handlers
route_handlers["/temperatura"] = handle_temperatura_request
route_handlers["/distancia"] = handle_distancia_request
route_handlers["/turbidez"] = handle_turbidez_request
route_handlers["/tds"] = handle_tds_request
route_handlers["/todos_sensores"] = handle_todos_sensores_request


if __name__ == "__main__":
    print(f"[{utils.get_timestamp()}] Testing http_server.py directly...")

    if not wifi_manager.is_connected():
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER_TEST] Wi-Fi not connected. Attempting to connect...")
        if not wifi_manager.connect_wifi(config.SSID, config.SENHA):
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER_TEST] Failed to connect to Wi-Fi. Aborting server test.")
        else:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER_TEST] Wi-Fi connected: {wifi_manager.get_ip()}")
    else:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER_TEST] Wi-Fi already connected: {wifi_manager.get_ip()}")

    if wifi_manager.is_connected():
        def handle_test_endpoint():
            return {"status": "success", "message": "HTTP server is running!", "timestamp": utils.get_timestamp()}
        route_handlers["/test"] = handle_test_endpoint

        def handle_sensor_example(): # This is a dummy example, not a real sensor.
            return {"sensor_name": "example_temp", "value": 25.5, "unit": "C"}
        route_handlers["/sensor_example"] = handle_sensor_example

        print(f"[{utils.get_timestamp()}] [HTTP_SERVER_TEST] Access test endpoints:")
        print(f"  http://{wifi_manager.get_ip()}:{config.HTTP_PORT}/test")
        print(f"  http://{wifi_manager.get_ip()}:{config.HTTP_PORT}/sensor_example")
        print(f"  http://{wifi_manager.get_ip()}:{config.HTTP_PORT}/temperatura")
        print(f"  http://{wifi_manager.get_ip()}:{config.HTTP_PORT}/todos_sensores")


        if not start_server():
             print(f"[{utils.get_timestamp()}] [HTTP_SERVER_TEST] Server failed to start.")
    else:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER_TEST] Cannot start server test without Wi-Fi.")

    print(f"[{utils.get_timestamp()}] [HTTP_SERVER_TEST] Server test finished or interrupted.")
