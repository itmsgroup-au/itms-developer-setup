#!/bin/bash
# Quick start script for the Odoo Log Viewer

echo "🚀 Starting ITMS Odoo Log Viewer..."
echo "📊 This will stream Odoo logs to a web interface"
echo "🌐 Access at: http://127.0.0.1:5001"
echo "🔄 Press Ctrl+C to stop"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Start the log viewer
python3 odoo_log_viewer.py --host 127.0.0.1 --port 5001