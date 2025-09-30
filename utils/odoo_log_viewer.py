#!/usr/bin/env python3
"""
ITMS Odoo Log Viewer
Web-based streaming log viewer for Odoo instances
"""

import json
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template_string


class OdooLogStreamer:
    """Stream Odoo logs to web interface"""

    def __init__(self):
        self.app = Flask(__name__)
        self.log_files = {}
        self.running = True

        # Odoo log file paths
        self.odoo_logs = {
            "enterprise18": "/Users/markshaw/Desktop/git/odoo/odoo18-enterprise.log",
            "community18": "/Users/markshaw/Desktop/git/odoo/odoo18-community.log",
            "enterprise19": "/Users/markshaw/Desktop/git/odoo/odoo19-enterprise.log",
            "community19": "/Users/markshaw/Desktop/git/odoo/odoo19-community.log",
        }

        # Setup routes
        self.setup_routes()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def setup_routes(self):
        """Setup Flask routes"""

        @self.app.route("/")
        def index():
            """Main log viewer page"""
            return render_template_string(
                LOG_VIEWER_HTML, logs=list(self.odoo_logs.keys())
            )

        @self.app.route("/api/logs/<instance>")
        def get_logs(instance):
            """Get recent logs for an instance"""
            if instance not in self.odoo_logs:
                return jsonify({"error": "Invalid instance"}), 404

            log_file = Path(self.odoo_logs[instance])
            if not log_file.exists():
                return (
                    jsonify({"error": "Log file not found", "path": str(log_file)}),
                    404,
                )

            try:
                # Get last 100 lines
                lines = self.tail_file(log_file, 100)
                return jsonify(
                    {
                        "lines": lines,
                        "instance": instance,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/stream/<instance>")
        def stream_logs(instance):
            """Stream logs in real-time"""
            if instance not in self.odoo_logs:
                return "Invalid instance", 404

            def generate():
                log_file = Path(self.odoo_logs[instance])
                if not log_file.exists():
                    yield f"data: {json.dumps({'error': 'Log file not found'})}\n\n"
                    return

                # Start from end of file
                with open(log_file, "r") as f:
                    f.seek(0, 2)  # Go to end

                    while self.running:
                        line = f.readline()
                        if line:
                            yield f"data: {json.dumps({'line': line.strip(), 'timestamp': datetime.now().isoformat()})}\n\n"
                        else:
                            time.sleep(0.1)

            return Response(
                generate(),
                mimetype="text/event-stream",
                headers={"Cache-Control": "no-cache"},
            )

        @self.app.route("/api/status")
        def status():
            """Get status of all Odoo instances"""
            status_info = {}
            for instance, log_path in self.odoo_logs.items():
                log_file = Path(log_path)
                status_info[instance] = {
                    "log_exists": log_file.exists(),
                    "log_path": str(log_file),
                    "size": log_file.stat().st_size if log_file.exists() else 0,
                    "modified": log_file.stat().st_mtime if log_file.exists() else 0,
                }

            return jsonify(status_info)

    def tail_file(self, file_path: Path, lines: int = 100) -> list:
        """Get last N lines from file"""
        if not file_path.exists():
            return []

        try:
            with open(file_path, "rb") as f:
                # Go to end
                f.seek(0, 2)
                file_size = f.tell()

                # Read in chunks from end
                lines_found = []
                buffer_size = 8192
                position = file_size

                while len(lines_found) < lines and position > 0:
                    # Read chunk
                    position = max(0, position - buffer_size)
                    f.seek(position)
                    chunk = f.read(min(buffer_size, file_size - position))

                    # Split into lines
                    chunk_lines = chunk.decode("utf-8", errors="ignore").split("\n")
                    lines_found = chunk_lines + lines_found

                # Return last N lines
                return lines_found[-lines:] if len(lines_found) > lines else lines_found

        except Exception as e:
            return [f"Error reading file: {e}"]

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.running = False
        sys.exit(0)

    def run(self, host="127.0.0.1", port=5001, debug=False):
        """Run the log viewer server"""
        print(f"🚀 Starting Odoo Log Viewer on http://{host}:{port}")
        print("📊 Available instances:")
        for instance, log_path in self.odoo_logs.items():
            exists = Path(log_path).exists()
            status = "✅" if exists else "❌"
            print(f"   {status} {instance}: {log_path}")

        print(f"\n🌐 Access the log viewer at: http://{host}:{port}")
        print("🔄 Press Ctrl+C to stop")

        try:
            self.app.run(host=host, port=port, debug=debug, threaded=True)
        except KeyboardInterrupt:
            print("\n👋 Log viewer stopped")


# HTML template for the log viewer
LOG_VIEWER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ITMS Odoo Log Viewer</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background-color: #1e1e1e;
            color: #ffffff;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #333;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }
        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .instance-selector {
            padding: 8px 12px;
            background-color: #333;
            color: white;
            border: 1px solid #555;
            border-radius: 4px;
            font-family: inherit;
        }
        .btn {
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-family: inherit;
        }
        .btn:hover {
            background-color: #45a049;
        }
        .btn.stop {
            background-color: #f44336;
        }
        .btn.stop:hover {
            background-color: #da190b;
        }
        .status {
            margin-bottom: 15px;
            padding: 10px;
            background-color: #333;
            border-radius: 4px;
            font-size: 14px;
        }
        .log-container {
            background-color: #000;
            border: 1px solid #333;
            border-radius: 4px;
            height: 600px;
            overflow-y: auto;
            padding: 15px;
            font-size: 13px;
            line-height: 1.4;
        }
        .log-line {
            margin-bottom: 2px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .log-line.error {
            color: #ff6b6b;
        }
        .log-line.warning {
            color: #ffa726;
        }
        .log-line.info {
            color: #4fc3f7;
        }
        .log-line.debug {
            color: #9e9e9e;
        }
        .timestamp {
            color: #666;
            font-size: 11px;
        }
        .auto-scroll {
            margin-left: 10px;
        }
        .footer {
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">🚀 ITMS Odoo Log Viewer</div>
        <div class="controls">
            <select id="instanceSelect" class="instance-selector">
                {% for log in logs %}
                <option value="{{ log }}">{{ log }}</option>
                {% endfor %}
            </select>
            <button id="startBtn" class="btn" onclick="startStreaming()">▶️ Start</button>
            <button id="stopBtn" class="btn stop" onclick="stopStreaming()">⏹️ Stop</button>
            <label class="auto-scroll">
                <input type="checkbox" id="autoScroll" checked> Auto-scroll
            </label>
        </div>
    </div>

    <div id="status" class="status">
        Select an instance and click Start to begin streaming logs...
    </div>

    <div id="logContainer" class="log-container">
        <div class="log-line">Ready to stream logs...</div>
    </div>

    <div class="footer">
        ITMS Developer Setup • Real-time Odoo Log Streaming
    </div>

    <script>
        let eventSource = null;
        let currentInstance = null;

        function updateStatus(message, type = 'info') {
            const status = document.getElementById('status');
            const timestamp = new Date().toLocaleTimeString();
            status.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${message}`;
            status.className = `status ${type}`;
        }

        function addLogLine(content, type = '') {
            const container = document.getElementById('logContainer');
            const line = document.createElement('div');
            line.className = `log-line ${type}`;
            line.textContent = content;
            container.appendChild(line);

            // Auto-scroll if enabled
            if (document.getElementById('autoScroll').checked) {
                container.scrollTop = container.scrollHeight;
            }

            // Keep only last 1000 lines
            while (container.children.length > 1000) {
                container.removeChild(container.firstChild);
            }
        }

        function getLogType(line) {
            const lower = line.toLowerCase();
            if (lower.includes('error') || lower.includes('exception')) return 'error';
            if (lower.includes('warning') || lower.includes('warn')) return 'warning';
            if (lower.includes('info')) return 'info';
            if (lower.includes('debug')) return 'debug';
            return '';
        }

        function startStreaming() {
            const instance = document.getElementById('instanceSelect').value;
            if (!instance) {
                updateStatus('Please select an instance', 'error');
                return;
            }

            stopStreaming(); // Stop any existing stream

            currentInstance = instance;
            updateStatus(`Starting stream for ${instance}...`);

            // Load recent logs first
            fetch(`/api/logs/${instance}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        updateStatus(data.error, 'error');
                        return;
                    }

                    // Clear container
                    document.getElementById('logContainer').innerHTML = '';

                    // Add recent logs
                    data.lines.forEach(line => {
                        if (line.trim()) {
                            addLogLine(line, getLogType(line));
                        }
                    });

                    updateStatus(`Loaded ${data.lines.length} recent lines. Starting real-time stream...`);

                    // Start streaming
                    eventSource = new EventSource(`/api/stream/${instance}`);

                    eventSource.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        if (data.error) {
                            updateStatus(data.error, 'error');
                            return;
                        }
                        if (data.line) {
                            addLogLine(data.line, getLogType(data.line));
                        }
                    };

                    eventSource.onerror = function(event) {
                        updateStatus('Stream connection error', 'error');
                        stopStreaming();
                    };

                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                })
                .catch(error => {
                    updateStatus(`Error loading logs: ${error}`, 'error');
                });
        }

        function stopStreaming() {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            updateStatus('Stream stopped');
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }

        function clearLogs() {
            document.getElementById('logContainer').innerHTML = '';
            updateStatus('Logs cleared');
        }

        // Auto-start with first instance
        window.onload = function() {
            document.getElementById('stopBtn').disabled = true;
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ITMS Odoo Log Viewer")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5001, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    streamer = OdooLogStreamer()
    streamer.run(host=args.host, port=args.port, debug=args.debug)
