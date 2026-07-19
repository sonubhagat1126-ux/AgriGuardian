/**
 * SmartEdge AgriGuardian — STM32U585 MCU Sketch
 * ==============================================
 * File: agriguardian_sketch.ino
 * Board: Arduino UNO Q (ABX00173) - Arduino/MCU Side
 * 
 * Exposes hardware interfaces to the Python Flask backend running on the
 * Linux MPU side using the official Arduino RouterBridge MessagePack-RPC protocol.
 * 
 * Hardware Pins:
 *   - Soil Moisture Sensor : Analog pin A0 (ADC reading 0 - 1023)
 *   - DHT22 Temp/Humidity  : Digital pin D2
 *   - Relay Module (Pump)  : Digital pin D6 (configured as Active-LOW)
 * 
 * Exposed RPC Methods:
 *   - "read_sensors"   -> returns JSON string: {"moisture": adc, "temperature": t, "humidity": h, "dht_error": boolean}
 *   - "set_pump"       -> accepts boolean, actuates relay, returns true
 *   - "get_pump_state" -> returns boolean indicating current relay status
 */

#include <Arduino.h>
#include <Arduino_RouterBridge.h>
#include <DHT.h>

// ── Pins and Hardware Configuration ──────────────────────────────────────────
#define SOIL_MOISTURE_PIN   A0
#define DHT_PIN            2
#define DHT_TYPE           DHT22
#define PUMP_RELAY_PIN     6

// ── Relay Logic Polarity ─────────────────────────────────────────────────────
// Most common relay modules are Active-LOW (LOW activates relay, HIGH deactivates).
// If your relay is Active-HIGH, swap these values:
#define PUMP_RELAY_ON      LOW
#define PUMP_RELAY_OFF     HIGH

// ── Global Objects ───────────────────────────────────────────────────────────
DHT dht(DHT_PIN, DHT_TYPE);

// Internal state tracking
bool pumpState = false;

// ── RPC Handler: read_sensors ────────────────────────────────────────────────
/**
 * Reads sensor values and returns them formatted as a compact JSON string.
 * This combines all sensor data into a single RPC round-trip.
 */
String readSensorsHandler() {
  int moistureADC = analogRead(SOIL_MOISTURE_PIN);
  
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  bool dhtError = false;

  // Check if DHT read failed
  if (isnan(temperature) || isnan(humidity)) {
    temperature = 0.0;
    humidity = 0.0;
    dhtError = true;
  }

  // Construct JSON string response manually to avoid external JSON library dependencies
  String jsonResponse = "{";
  jsonResponse += "\"moisture\":" + String(moistureADC) + ",";
  jsonResponse += "\"temperature\":" + String(temperature, 1) + ",";
  jsonResponse += "\"humidity\":" + String(humidity, 1) + ",";
  jsonResponse += "\"dht_error\":" + String(dhtError ? "true" : "false");
  jsonResponse += "}";

  return jsonResponse;
}

// ── RPC Handler: set_pump ────────────────────────────────────────────────────
/**
 * Turns the pump relay ON (PUMP_RELAY_ON) or OFF (PUMP_RELAY_OFF).
 * Accepts a boolean parameter from Python.
 */
bool setPumpHandler(bool state) {
  pumpState = state;
  if (pumpState) {
    digitalWrite(PUMP_RELAY_PIN, PUMP_RELAY_ON);
  } else {
    digitalWrite(PUMP_RELAY_PIN, PUMP_RELAY_OFF);
  }
  return true;
}

// ── RPC Handler: get_pump_state ──────────────────────────────────────────────
/**
 * Returns the current pump relay state (true = ON, false = OFF).
 */
bool getPumpStateHandler() {
  return pumpState;
}

// ── Setup ────────────────────────────────────────────────────────────────────
void setup() {
  // Initialize Serial for local MCU debugging (optional)
  Serial.begin(115200);

  // Initialize Pump Relay Pin
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  digitalWrite(PUMP_RELAY_PIN, PUMP_RELAY_OFF); // Start in safe/deactivated state
  pumpState = false;

  // Initialize DHT Sensor
  dht.begin();

  // Initialize the Arduino Router Bridge
  // This opens the internal UART communication channel to the Linux side
  Bridge.begin();

  // Register the RPC methods with the Router Bridge
  // These names MUST match the method names used in the Python device_manager
  Bridge.provide("read_sensors", readSensorsHandler);
  Bridge.provide("set_pump", setPumpHandler);
  Bridge.provide("get_pump_state", getPumpStateHandler);

  Serial.println("SmartEdge AgriGuardian MCU initialized. Router Bridge is active.");
}

// ── Main Loop ────────────────────────────────────────────────────────────────
void loop() {
  // Process incoming Bridge messages from the Linux side
  Bridge.loop();
  
  // Yield to other system threads
  delay(1);
}
