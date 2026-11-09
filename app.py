from flask import Flask, render_template, request, jsonify
from datetime import datetime
from threading import Lock

app = Flask(__name__)
lock = Lock()

# Demo state. Replace this in-memory store with SQLite / a real ANPR engine in production.
events = [
    {"time": datetime.now().strftime("%H:%M:%S"), "plate": "KA03MN4821",
     "vehicle": "Car", "camera": "Gate Camera 01", "status": "AUTHORIZED"},
    {"time": datetime.now().strftime("%H:%M:%S"), "plate": "UNKNOWN",
     "vehicle": "Unknown", "camera": "Gate Camera 02", "status": "REVIEW"},
]
cameras = [
    {"id": 1, "name": "Gate Camera 01", "location": "Main Entrance", "status": "ONLINE"},
    {"id": 2, "name": "Gate Camera 02", "location": "Exit Lane", "status": "ONLINE"},
]
zones = [
    {"id": 1, "name": "Entry Zone", "camera": "Gate Camera 01", "enabled": True},
    {"id": 2, "name": "Exit Zone", "camera": "Gate Camera 02", "enabled": True},
]

@app.get("/")
def dashboard():
    return render_template("index.html", events=events, cameras=cameras, zones=zones)

@app.get("/api/state")
def state():
    with lock:
        return jsonify({"events": events[:30], "cameras": cameras, "zones": zones})

@app.post("/api/events")
def add_event():
    data = request.get_json(silent=True) or request.form
    plate = (data.get("plate") or "UNKNOWN").strip().upper()[:20]
    vehicle = (data.get("vehicle") or "Unknown").strip()[:30]
    camera = (data.get("camera") or "Gate Camera 01").strip()[:50]
    status = (data.get("status") or "REVIEW").strip().upper()
    if status not in {"AUTHORIZED", "DENIED", "REVIEW"}:
        status = "REVIEW"
    item = {"time": datetime.now().strftime("%H:%M:%S"), "plate": plate,
            "vehicle": vehicle, "camera": camera, "status": status}
    with lock:
        events.insert(0, item)
        del events[100:]
    return jsonify({"ok": True, "event": item}), 201

@app.post("/api/zones/<int:zone_id>/toggle")
def toggle_zone(zone_id):
    with lock:
        for zone in zones:
            if zone["id"] == zone_id:
                zone["enabled"] = not zone["enabled"]
                return jsonify({"ok": True, "zone": zone})
    return jsonify({"ok": False, "error": "Zone not found"}), 404

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "Vehicle Access Control Demo"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
