import asyncio
import threading
import time
import json
import serial
import random
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import ai_handler
from fastapi.middleware.cors import CORSMiddleware
from vedas_client import VedasClient

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active websocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

# Global Serial Configuration (defaults to COM3, customizable via env)
SERIAL_PORT = os.environ.get("SERIAL_PORT", "COM3")
BAUD_RATE = int(os.environ.get("BAUD_RATE", 9600))
ser = None

# Global state cache
latest_data = {
    "temperature": 26.5,
    "humidity": 62.0,
    "soil_moisture": 42,
    "raw_soil": 1024,
    "satellite_soil": None,
    "satellite_temp": None,
    "vegetation_ndvi": None,
    "crop_type": "tomato",
    "selected_field": "none",
    "latitude": None,
    "longitude": None,
    "pump_status": False,
    "auto_mode": True,
    "soil_threshold": 30,
    "simulation_mode": True,
    "serial_port": "Simulation Mode",
    "baud_rate": 9600,
    "custom_boundary": [],
    "saved_fields": []
}

loop = None

def send_to_serial(cmd_str):
    global ser
    if not latest_data["simulation_mode"] and ser and ser.is_open:
        try:
            print(f"[Serial TX]: {cmd_str}")
            ser.write((cmd_str + "\n").encode('utf-8'))
        except Exception as e:
            print(f"Failed to write to serial: {e}")
    else:
        print(f"[Simulated Serial TX]: {cmd_str}")

def broadcast_data(data):
    if loop:
        asyncio.run_coroutine_threadsafe(
            manager.broadcast(json.dumps(data)), 
            loop
        )
    
    # Upload to ntfy.sh in a daemon thread to prevent blocking
    import urllib.request
    import threading
    def upload_cloud(payload):
        try:
            url = "https://ntfy.sh/smartedge-agriguardian-dev-99"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                resp.read()
        except:
            pass
    threading.Thread(target=upload_cloud, args=(data.copy(),), daemon=True).start()

def parse_serial_line(line):
    global latest_data
    line = line.strip()
    if not line:
        return False
        
    # Check if JSON
    if line.startswith("{") and line.endswith("}"):
        try:
            data = json.loads(line)
            for key in latest_data:
                if key in data:
                    latest_data[key] = data[key]
            return True
        except json.JSONDecodeError:
            return False

    # Check if plain text line-by-line format
    updated = False
    try:
        # Check pump status (handles: "Soil Dry -> Pump ON" and "Soil Wet -> Pump OFF")
        if "pump on" in line.lower():
            latest_data["pump_status"] = True
            updated = True
        elif "pump off" in line.lower():
            latest_data["pump_status"] = False
            updated = True

        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip().lower()
            val = parts[1].strip()
            
            if "temperature" in key:
                val_clean = val.replace("ºC", "").replace("°C", "").replace("C", "").replace("", "").strip()
                latest_data["temperature"] = float(val_clean)
                updated = True
            elif "humidity" in key:
                val_clean = val.replace("%", "").strip()
                latest_data["humidity"] = float(val_clean)
                updated = True
            elif "soil" in key:  # matches "soil value", "soil moisture value", "soil analog"
                import re
                val_digits = re.sub(r"\D", "", val)
                if val_digits:
                    val_num = int(val_digits)
                    if "%" in val:
                        # Value is already a pre-calculated percentage!
                        latest_data["soil_moisture"] = max(0, min(100, val_num))
                    else:
                        latest_data["raw_soil"] = val_num
                        # Map 1024 (dry) to 0% and 300 (wet) to 100%
                        percentage = int((1024 - val_num) / (1024 - 300) * 100)
                        latest_data["soil_moisture"] = max(0, min(100, percentage))
                    updated = True
            elif "pump" in key:  # matches "PUMP        : OFF", "PUMP        : ON"
                latest_data["pump_status"] = ("on" in val.lower())
                updated = True
    except Exception as e:
        print(f"Error parsing serial line '{line}': {e}")
        
    return updated

def serial_reader_thread():
    global ser
    import serial.tools.list_ports
    reconnect_timer = 0
    
    while True:
        # 1. Attempt connection if not connected
        if ser is None or not ser.is_open:
            active_port = SERIAL_PORT
            try:
                available_ports = [p.device for p in serial.tools.list_ports.comports()]
                if available_ports:
                    if active_port not in available_ports:
                        active_port = available_ports[0]
                        print(f"[Serial]: Default port '{SERIAL_PORT}' not found. Auto-detected and switched to: {active_port}")
                
                ser = serial.Serial(active_port, BAUD_RATE, timeout=0.1)
                print(f"\n>>> Successfully connected to device on {active_port}! <<<")
                latest_data["simulation_mode"] = False
                latest_data["serial_port"] = active_port
                latest_data["baud_rate"] = BAUD_RATE
            except Exception as e:
                if ser:
                    try:
                        ser.close()
                    except:
                        pass
                    ser = None
                
                if not latest_data["simulation_mode"]:
                    print(f"Serial connection lost or unavailable: {e}")
                    print("!!! Switching to SIMULATION MODE !!! (Retrying connection in background...)")
                    latest_data["simulation_mode"] = True
                    latest_data["serial_port"] = "Simulation Mode"
                    latest_data["baud_rate"] = 0
        
        # 2. Run simulation loop or read actual serial port
        if latest_data["simulation_mode"]:
            time.sleep(2)
            
            # Generate realistic simulated values
            latest_data["temperature"] += round(random.uniform(-0.15, 0.15), 1)
            latest_data["temperature"] = max(18.0, min(38.0, latest_data["temperature"]))
            latest_data["temperature"] = round(latest_data["temperature"], 1)
            
            latest_data["humidity"] += round(random.uniform(-0.4, 0.4), 1)
            latest_data["humidity"] = max(30.0, min(90.0, latest_data["humidity"]))
            latest_data["humidity"] = round(latest_data["humidity"], 1)
            
            if latest_data["pump_status"]:
                latest_data["soil_moisture"] += random.randint(2, 5)
            else:
                latest_data["soil_moisture"] -= random.randint(1, 2)
            latest_data["soil_moisture"] = max(0, min(100, latest_data["soil_moisture"]))
            latest_data["raw_soil"] = int(1024 - (latest_data["soil_moisture"] * 7.24))
            
            if latest_data["auto_mode"]:
                if latest_data["soil_moisture"] < latest_data["soil_threshold"]:
                    latest_data["pump_status"] = True
                elif latest_data["soil_moisture"] >= (latest_data["soil_threshold"] + 8):
                    latest_data["pump_status"] = False
            
            broadcast_data(latest_data)
            
            # Periodically retry connecting (every 6 seconds)
            reconnect_timer += 2
            if reconnect_timer >= 6:
                reconnect_timer = 0
        else:
            try:
                # Read from active serial port
                if ser and ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"[Serial RX]: {line}")
                        latest_data["simulation_mode"] = False
                        
                        # Parse and update real-time database state
                        if parse_serial_line(line):
                            broadcast_data(latest_data)
                time.sleep(0.05)
            except Exception as e:
                print(f"Error reading from serial: {e}")
                if ser:
                    try:
                        ser.close()
                    except:
                        pass
                    ser = None
                latest_data["simulation_mode"] = True

def fetch_vedas_data(lat, lon):
    print(f"Triggering VEDAS satellite fetch for Lat: {lat}, Lon: {lon}...")
    client = VedasClient()
    
    # Check if active selection matches a saved field name
    field_name = latest_data.get("selected_field", "")
    crop = latest_data.get("crop_type", "")
    
    for f in latest_data.get("saved_fields", []):
        if str(f.get("id")) == str(field_name) or f.get("name") == field_name:
            field_name = f.get("name")
            crop = f.get("crop", crop)
            break
            
    data = client.get_regional_soil_moisture(lat, lon, field_name=field_name, crop=crop)
    if data and data.get("status") == "success":
        latest_data["satellite_soil"] = data["data"]["regional_soil_moisture_index"]
        latest_data["satellite_temp"] = round(data["data"]["surface_temp_k"] - 273.15, 1) # Kelvin to Celsius
        latest_data["vegetation_ndvi"] = data["data"]["vegetation_index_ndvi"]
        print(f"[VEDAS Sync Success]: NDVI: {latest_data['vegetation_ndvi']}, Reg. Soil: {latest_data['satellite_soil']}")
        broadcast_data(latest_data)

def vedas_fetch_thread():
    print("VEDAS background thread started...")
    while True:
        lat = latest_data.get("latitude")
        lon = latest_data.get("longitude")
        if lat is not None and lon is not None:
            fetch_vedas_data(lat, lon)
        time.sleep(300)

@app.on_event("startup")
async def startup_event():
    global loop
    loop = asyncio.get_event_loop()
    threading.Thread(target=serial_reader_thread, daemon=True).start()
    threading.Thread(target=vedas_fetch_thread, daemon=True).start()

@app.get("/")
async def get():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(content="<h3>AgriGuardian static/index.html not found yet.</h3>", status_code=404)

# Web Socket Endpoint for UI clients
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # Send current status immediately on connection
    await websocket.send_text(json.dumps(latest_data))
    try:
        while True:
            data = await websocket.receive_text()
            print(f"[WS RX]: {data}")
            try:
                cmd = json.loads(data)
                action = cmd.get("action")
                value = cmd.get("value")
                
                if action == "set_pump":
                    # Only allow manual override if auto mode is off
                    if not latest_data["auto_mode"]:
                        latest_data["pump_status"] = bool(value)
                        send_to_serial(f"{{\"pump\":{str(value).lower()}}}")
                elif action == "set_auto":
                    latest_data["auto_mode"] = bool(value)
                    send_to_serial(f"{{\"auto\":{str(value).lower()}}}")
                elif action == "set_threshold":
                    latest_data["soil_threshold"] = int(value)
                    send_to_serial(f"{{\"threshold\":{int(value)}}}")
                elif action == "set_crop":
                    latest_data["crop_type"] = str(value)
                elif action == "set_field":
                    f_val = value.get("field")
                    if f_val == "none" or not f_val:
                        latest_data["selected_field"] = "none"
                        latest_data["latitude"] = None
                        latest_data["longitude"] = None
                        latest_data["satellite_soil"] = None
                        latest_data["satellite_temp"] = None
                        latest_data["vegetation_ndvi"] = None
                    else:
                        latest_data["selected_field"] = f_val
                        latest_data["latitude"] = float(value.get("lat"))
                        latest_data["longitude"] = float(value.get("lon"))
                        # Immediately launch a background fetch for the new coordinates
                        threading.Thread(target=fetch_vedas_data, args=(latest_data["latitude"], latest_data["longitude"]), daemon=True).start()
                elif action == "set_boundary":
                    latest_data["custom_boundary"] = value.get("boundary", [])
                elif action == "save_field_plot":
                    name = value.get("name", "Field")
                    crop = value.get("crop", "tomato")
                    boundary = value.get("boundary", [])
                    lat = float(value.get("lat"))
                    lon = float(value.get("lon"))
                    
                    # Compute unique satellite data indices for this centroid
                    client = VedasClient()
                    res = client.get_regional_soil_moisture(lat, lon, field_name=name, crop=crop)
                    ndvi = 0.65
                    soil = 0.38
                    temp = 32.2
                    if res and res.get("status") == "success":
                        ndvi = res["data"]["vegetation_index_ndvi"]
                        soil = res["data"]["regional_soil_moisture_index"]
                        temp = round(res["data"]["surface_temp_k"] - 273.15, 1)
                    
                    new_field = {
                        "id": len(latest_data.get("saved_fields", [])) + 1,
                        "name": name,
                        "crop": crop,
                        "boundary": boundary,
                        "latitude": lat,
                        "longitude": lon,
                        "vegetation_ndvi": ndvi,
                        "satellite_soil": soil,
                        "satellite_temp": temp,
                        "timestamp": time.strftime("%d-%m-%Y %H:%M")
                    }
                    if "saved_fields" not in latest_data:
                        latest_data["saved_fields"] = []
                    latest_data["saved_fields"].append(new_field)
                
                # Broadcast state update back to all clients
                await manager.broadcast(json.dumps(latest_data))
                
            except json.JSONDecodeError:
                print("Failed to decode JSON command from websocket.")
            except Exception as e:
                print(f"Error handling UI command: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Mount static directory to serve CSS and JS
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/api/data")
async def get_sensor_data():
    print(f"[API Data GET]: {latest_data}")
    return latest_data

@app.post("/api/telemetry")
async def receive_telemetry(request: Request):
    global latest_data
    try:
        data = await request.json()
        print(f"[Telemetry RX]: {data}")
        # If the board is sending us HTTP telemetry, disable simulation mode immediately
        latest_data["simulation_mode"] = False
        
        # Update latest_data with the board's telemetry
        for key in ["temperature", "humidity", "soil_moisture", "pump_status", "auto_mode"]:
            if key in data:
                latest_data[key] = data[key]
        
        # Save client IP as the active board IP dynamically
        latest_data["board_ip"] = request.client.host
        
        broadcast_data(latest_data)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/control")
async def control_system(request: Request):
    try:
        body = await request.json()
        action = body.get("action")
        value = body.get("value")
        
        if action == "set_pump":
            if not latest_data["auto_mode"]:
                latest_data["pump_status"] = bool(value)
                send_to_serial(f"{{\"pump\":{str(value).lower()}}}")
        elif action == "set_auto":
            latest_data["auto_mode"] = bool(value)
            send_to_serial(f"{{\"auto\":{str(value).lower()}}}")
        elif action == "set_threshold":
            latest_data["soil_threshold"] = int(value)
            send_to_serial(f"{{\"threshold\":{int(value)}}}")
        elif action == "save_field_plot":
            name = value.get("name", "Field")
            crop = value.get("crop", "tomato")
            boundary = value.get("boundary", [])
            lat = float(value.get("lat"))
            lon = float(value.get("lon"))
            
            # Compute unique satellite data indices for this centroid
            client = VedasClient()
            res = client.get_regional_soil_moisture(lat, lon, field_name=name, crop=crop)
            ndvi = 0.65
            soil = 0.38
            temp = 32.2
            if res and res.get("status") == "success":
                ndvi = res["data"]["vegetation_index_ndvi"]
                soil = res["data"]["regional_soil_moisture_index"]
                temp = round(res["data"]["surface_temp_k"] - 273.15, 1)
            
            new_field = {
                "id": len(latest_data.get("saved_fields", [])) + 1,
                "name": name,
                "crop": crop,
                "boundary": boundary,
                "latitude": lat,
                "longitude": lon,
                "vegetation_ndvi": ndvi,
                "satellite_soil": soil,
                "satellite_temp": temp,
                "timestamp": time.strftime("%d-%m-%Y %H:%M")
            }
            if "saved_fields" not in latest_data:
                latest_data["saved_fields"] = []
            latest_data["saved_fields"].append(new_field)
            
        broadcast_data(latest_data)
        return {"status": "success", "data": latest_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/leaf/detect")
async def proxy_leaf_detect(request: Request):
    import requests
    try:
        form_data = await request.form()
        files = {}
        if "image" in form_data:
            upload_file = form_data["image"]
            files["image"] = (upload_file.filename, await upload_file.read(), upload_file.content_type)
        
        board_ip = latest_data.get("board_ip", "10.92.169.254")
        resp = requests.post(f"http://{board_ip}:5001/leaf/detect", files=files, timeout=15)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": f"Proxy failed: {e}"}

@app.post("/api/ai/chat")
async def local_ai_chat(request: Request):
    try:
        body = await request.json()
        question = body.get("question", "").strip()
        disease_query = body.get("disease", "Tomato_healthy")

        if not question:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Missing required field 'question'"}
            )

        # 1. Look up disease metadata
        disease_info = ai_handler.get_disease(disease_query)
        if not disease_info:
            disease_info = {
                "crop": "Crop",
                "disease": disease_query,
                "severity": "Low",
                "overview": "Information unavailable"
            }

        # 2. Get Sensor Data (either custom passed or from latest cached state)
        sensor_data = body.get("sensor_data")
        if not sensor_data:
            sensor_data = {
                "soil_moisture": latest_data.get("soil_moisture", 45.0),
                "temperature": latest_data.get("temperature", 28.5),
                "humidity": latest_data.get("humidity", 62.0)
            }

        # 3. Get Real-time Weather
        lat = latest_data.get("latitude", 28.5355)
        lon = latest_data.get("longitude", 77.3910)
        weather = await asyncio.to_thread(ai_handler.get_current_weather, lat, lon)

        # 4. Generate Sarvam AI / Offline Advisory
        advisory_res = await asyncio.to_thread(
            ai_handler.generate_crop_doctor_advisory,
            disease_info=disease_info,
            confidence=0.90,
            sensor_data=sensor_data,
            weather_data=weather,
            user_question=question
        )

        return {
            "status": "success",
            "reply_hindi": advisory_res.get("advisory_hindi"),
            "source": advisory_res.get("source")
        }
    except Exception as e:
        return {"status": "error", "message": f"AI Chat processing failed: {e}"}


@app.post("/api/ai/crop-doctor")
async def local_crop_doctor(request: Request):
    try:
        body = await request.json()
        disease_query = body.get("disease", "").strip()
        confidence = float(body.get("confidence", 0.95))
        user_question = body.get("question", "")

        if not disease_query:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Missing required field 'disease' in JSON body"}
            )

        # 1. Retrieve Knowledge Base Object
        disease_info = ai_handler.get_disease(disease_query)
        if not disease_info:
            disease_info = {
                "crop": "Crop",
                "disease": disease_query,
                "severity": "Medium",
                "overview": "Information unavailable",
                "action_plan": {
                    "today": ["Perform field inspection", "Remove damaged foliage"],
                    "next_3_days": ["Keep leaves dry"],
                    "expected_recovery": "10-14 Days"
                }
            }

        # 2. Get Sensor Data
        sensor_data = body.get("sensor_data")
        if not sensor_data:
            sensor_data = {
                "soil_moisture": latest_data.get("soil_moisture", 45.0),
                "temperature": latest_data.get("temperature", 28.5),
                "humidity": latest_data.get("humidity", 62.0)
            }

        # 3. Get Weather
        lat = latest_data.get("latitude", 28.5355)
        lon = latest_data.get("longitude", 77.3910)
        weather = await asyncio.to_thread(ai_handler.get_current_weather, lat, lon)

        # 4. Generate Sarvam AI Advisory
        advisory_res = await asyncio.to_thread(
            ai_handler.generate_crop_doctor_advisory,
            disease_info=disease_info,
            confidence=confidence,
            sensor_data=sensor_data,
            weather_data=weather,
            user_question=user_question
        )

        return {
            "status": "success",
            "disease_name": disease_info.get("name", disease_query),
            "confidence": confidence,
            "source": advisory_res.get("source"),
            "advisory_hindi": advisory_res.get("advisory_hindi"),
            "action_plan": disease_info.get("action_plan", {}),
            "disease_info": disease_info,
            "sensor_data": sensor_data,
            "weather": weather
        }
    except Exception as e:
        return {"status": "error", "message": f"Crop Doctor processing failed: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
