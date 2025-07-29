ACCEPTED_VERSIONS = ["1.0", "1.1", "1.2"]
VALID_COMMANDS = [
    "CONNECT",
    "SEND",
    "SUBSCRIBE",
    "UNSUBSCRIBE",
    "BEGIN",
    "COMMIT",
    "ABORT",
    "ACK",
    "NACK",
    "DISCONNECT",
    "CONNECTED",
    "MESSAGE",
    "RECEIPT",
    "ERROR",
    "STOMP"
]

def build_frame(command, headers=None, body=""):
    frame = command + "\n"
    if headers:
        for key, value in headers.items():
            frame += f"{key}:{value}\n"
    frame += "\n"
    frame += body
    frame += "\0"
    return frame

def generate_connect_frame(login=None, passcode=None, host="", heartbeat=(0, 0), connectHeaders=None):
    headers = {
        "accept-version": ",".join(ACCEPTED_VERSIONS),
        "host": host,
    }

    if login is not None:
        headers["login"] = login
    
    if passcode is not None:
        headers["passcode"] = passcode

    if len(heartbeat) != 2:
        raise ValueError("heartbeat must be a tuple of two integers (client, server)")

    headers["heart-beat"] = f"{heartbeat[0]},{heartbeat[1]}"

    if connectHeaders is not None:
        headers.update(connectHeaders)

    return build_frame("CONNECT", headers)

def generate_send_frame(destination, body, content_type="text/plain"):
    headers = {
        "destination": destination,
        "content-type": content_type,
    }

    return build_frame("SEND", headers, body)

def generate_subscribe_frame(id, destination, ack="auto"):
    headers = {
        "id": id,
        "destination": destination,
        "ack": ack,
    }

    return build_frame("SUBSCRIBE", headers)

def generate_unsubscribe_frame(id):
    headers = {
        "id": id,
    }

    return build_frame("UNSUBSCRIBE", headers)

def generate_ack_frame(id, transaction=None):
    headers = {
        "id": id,
    }

    if transaction is not None:
        headers["transaction"] = transaction

    return build_frame("ACK", headers)

def generate_nack_frame(id, transaction=None):
    headers = {
        "id": id,
    }

    if transaction is not None:
        headers["transaction"] = transaction

    return build_frame("NACK", headers)

def generate_begin_frame(transaction):
    headers = {
        "transaction": transaction,
    }

    return build_frame("BEGIN", headers)

def generate_commit_frame(transaction):
    headers = {
        "transaction": transaction,
    }

    return build_frame("COMMIT", headers)

def generate_abort_frame(transaction):
    headers = {
        "transaction": transaction,
    }

    return build_frame("ABORT", headers)

def generate_disconnect_frame(receipt):
    headers = {
        "receipt": receipt,
    }

    return build_frame("DISCONNECT", headers)

def parse_frame(frame):
    frame = frame.rstrip('\0')

    lines = frame.split('\n')
    if not lines:
        raise ValueError("empty frame")

    command = lines[0].strip()
    if not command:
        raise ValueError("missing command in frame")
    
    if command not in VALID_COMMANDS:
        raise ValueError(f"invalid command: {command}")

    try:
        empty_line_index = lines.index('')
    except ValueError:
        empty_line_index = len(lines)

    header_lines = lines[1:empty_line_index]
    headers = {}
    for line in header_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
        else:
            raise ValueError("invalid header line: " + line)

    body_lines = lines[empty_line_index + 1:] if empty_line_index + 1 < len(lines) else []
    body = '\n'.join(body_lines)

    return {
        "command": command,
        "headers": headers,
        "body": body
    }