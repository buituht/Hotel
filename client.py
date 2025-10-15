#!/usr/bin/env python3
"""
Client tương tác cho server quản lý khách sạn.

Sử dụng:
- python3 client.py [host] [port]

Gõ HELP để xem lệnh, QUIT để thoát.
"""
import socket
import sys

def run(host="127.0.0.1", port=9009):
    with socket.create_connection((host, port)) as s:
        fp = s.makefile(mode="rw", encoding="utf-8", newline="\n")
        # Đọc welcome
        welcome = fp.readline()
        if welcome:
            print(welcome.strip())
        # Background reader thread is not necessary; we'll do synchronous request/response
        try:
            while True:
                cmd = input("> ").strip()
                if not cmd:
                    continue
                fp.write(cmd + "\n")
                fp.flush()
                # Read response lines until a blank line or next prompt?
                # Server responses always end with '\n' and typically single block.
                # We'll read until there's no more immediate data: read one line and print.
                # For multi-line responses, server sends multiple newline-terminated lines without a terminator.
                # We'll read the first line. For LIST and HELP server sends multiple lines, but they are
                # sent as several lines; we'll read until there's no data available on socket.
                # Simpler: read one line, and if it starts with "OK" and the response might be multi-line,
                # just read subsequent lines with a small timeout. For simplicity, we will read lines
                # until a blank line or next prompt - server doesn't send blank lines so we read just one
                # and then try to peek more (not straightforward). To keep it simple: read lines until
                # a line that starts with "OK" or "ERR" and then break. But LIST returns OK first line then others.
                # So we will attempt to read lines until socket has no immediate data by setting timeout.
                s.settimeout(0.15)
                try:
                    while True:
                        line = fp.readline()
                        if not line:
                            break
                        print(line.rstrip())
                except (socket.timeout):
                    pass
                finally:
                    s.settimeout(None)
                if cmd.upper() == "QUIT":
                    break
        except KeyboardInterrupt:
            print("\nBye")

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) >= 2 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else 9009
    run(host, port)