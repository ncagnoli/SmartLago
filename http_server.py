import socket
import time
import config
import utils
import sensor_manager
import wifi_manager
import json

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
    try:
        request_lines = request_data.splitlines()
        if not request_lines:
            raise ValueError("Empty request")

        request_line = request_lines[0]
        parts = request_line.split()
        if len(parts) < 2:
            raise ValueError("Malformed request line")

        method, path = parts[0], parts[1]
    except ValueError as e:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Error parsing request line: {e}")
        response_body = '{"error": "Bad Request", "detail": "Malformed request line"}'
        response = build_http_response(response_body, status_code=400)
        conn.sendall(response)
        return

    print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Received {method} for {path}")

    handler = route_handlers.get(path)

    if handler:
        if method == "GET":
            try:
                response_data = handler()
                if response_data is None:
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
            response_body_json = '{"error": "Method Not Allowed"}'
            response = build_http_response(response_body_json, status_code=405)
    else:
        response_body_json = '{"error": "Not Found"}'
        response = build_http_response(response_body_json, status_code=404)

    try:
        conn.sendall(response)
    except OSError as e:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] OSError sending response for {path}: {e}")

def start_server():
    """
    Initializes the HTTP server and enters the listening loop for connections.
    """
    if not wifi_manager.is_connected():
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Wi-Fi not connected. Server cannot start.")
        return

    try:
        addr_info = socket.getaddrinfo('0.0.0.0', config.HTTP_PORT)[0][-1]
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(addr_info)
        server_socket.listen(config.HTTP_MAX_PENDING_CONN)
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Listening on {wifi_manager.get_ip()}:{config.HTTP_PORT}")
    except Exception as e:
        print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Error binding/listening on socket: {e}")
        return

    while True:
        client_conn = None
        try:
            client_conn, addr = server_socket.accept()
            client_conn.settimeout(config.HTTP_CLIENT_TIMEOUT_S)
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Connection from {addr[0]}:{addr[1]}")

            request_bytes = client_conn.recv(config.HTTP_MAX_REQUEST_SIZE)
            if request_bytes:
                handle_request(request_bytes.decode('utf-8'), client_conn)

        except OSError as e:
            print(f"[{utils.get_timestamp()}] [HTTP_SERVER] Connection error: {e}")
        finally:
            if client_conn:
                client_conn.close()

# --- Route Handlers ---
def handle_temperature_request():
    result = sensor_manager.read_specific_sensor("temperature")
    return { "temperature": result.get("value") } if result and result.get("value") is not None else None

def handle_distance_request():
    result = sensor_manager.read_specific_sensor("distance")
    return { "distance": result.get("value") } if result and result.get("value") is not None else None

def handle_turbidity_request():
    result = sensor_manager.read_specific_sensor("turbidity")
    return { "turbidity": result.get("value") } if result and result.get("value") is not None else None

def handle_tds_request():
    result = sensor_manager.read_specific_sensor("tds")
    return { "tds": result.get("value") } if result and result.get("value") is not None else None

def handle_all_sensors_request():
    return sensor_manager.read_all_sensors()

# --- Route Registration ---
route_handlers["/temperature"] = handle_temperature_request
route_handlers["/distance"] = handle_distance_request
route_handlers["/turbidity"] = handle_turbidity_request
route_handlers["/tds"] = handle_tds_request
route_handlers["/all_sensors"] = handle_all_sensors_request
