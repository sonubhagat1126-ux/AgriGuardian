/**
 * Agro Snapdragon - ESP8266 Standalone Firmware
 * Connects directly to Wi-Fi and streams real-time sensor data to the public cloud (ntfy.sh)
 * so it can be viewed on your Expo Go mobile app over the internet without a laptop!
 * 
 * Pin Connections:
 * - DHT11 Data Pin -> NodeMCU D4 (GPIO2)
 * - Relay Signal -> NodeMCU D1 (GPIO5)
 * - Soil Moisture -> A0 (Analog Input)
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include "DHT.h"

// ==========================================
// 📶 Wi-Fi Settings (Change these to your hotspot details)
// ==========================================
const char* ssid = "YOUR_IPHONE_HOTSPOT_NAME";       // e.g. "iPhone" or "Devansh's iPhone"
const char* password = "YOUR_HOTSPOT_PASSWORD";    // Your hotspot passcode

// ==========================================
// ☁️ Cloud Topic (Matches your Expo mobile app)
// ==========================================
const char* cloudTopic = "smartedge-agriguardian-devansh";

// Pin Definitions
#define DHTPIN D4          // Digital pin connected to the DHT sensor (GPIO2)
#define DHTTYPE DHT11      // Change to DHT22 if using DHT22
#define PUMP_RELAY_PIN D1  // Digital pin connected to the relay (GPIO5)
#define SOIL_MOISTURE_PIN A0 // Analog pin connected to soil moisture sensor

// Calibration Values for Soil Moisture (Analog 0 to 1023)
const int AIR_VALUE = 850;   // Analog value in dry air (0% moisture)
const int WATER_VALUE = 350; // Analog value in water (100% moisture)

// System Variables
float temperature = 0.0;
float humidity = 0.0;
int soilMoisture = 0;
bool pumpStatus = false;
bool autoMode = true;        // If true, relay is controlled by soil moisture
int soilThreshold = 30;     // Pump turns ON below this %, turns OFF above it + hysteresis

DHT dht(DHTPIN, DHTTYPE);
unsigned long lastSensorReadTime = 0;
const unsigned long sensorReadInterval = 3000; // Send data every 3 seconds

void setup() {
  Serial.begin(115200);
  delay(10);
  
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  digitalWrite(PUMP_RELAY_PIN, LOW); // Start with pump off
  
  dht.begin();

  // Connect to Wi-Fi Hotspot
  Serial.println();
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected successfully!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 1. Read Sensors and run automation logic periodically
  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorReadTime >= sensorReadInterval) {
    lastSensorReadTime = currentMillis;
    
    readSensors();
    runAutomation();
    
    // Print to Serial (for debugging)
    sendSensorDataJSON();
    
    // Send directly to iPhone over the Internet
    sendSensorDataToCloud();
  }
}

void readSensors() {
  // Read Temperature & Humidity
  float tempRead = dht.readTemperature();
  float humRead = dht.readHumidity();
  
  // Verify readings are valid numbers
  if (!isnan(tempRead)) temperature = tempRead;
  if (!isnan(humRead)) humidity = humRead;

  // Read Soil Moisture
  int rawSoil = analogRead(SOIL_MOISTURE_PIN);
  soilMoisture = map(rawSoil, AIR_VALUE, WATER_VALUE, 0, 100);
  soilMoisture = constrain(soilMoisture, 0, 100);
}

void runAutomation() {
  if (autoMode) {
    if (soilMoisture < soilThreshold) {
      pumpStatus = true;
    } else if (soilMoisture >= (soilThreshold + 5)) {
      pumpStatus = false;
    }
    digitalWrite(PUMP_RELAY_PIN, pumpStatus ? HIGH : LOW);
  }
}

void sendSensorDataJSON() {
  Serial.print("{\"temperature\":");
  Serial.print(temperature, 1);
  Serial.print(",\"humidity\":");
  Serial.print(humidity, 1);
  Serial.print(",\"soil_moisture\":");
  Serial.print(soilMoisture);
  Serial.print(",\"pump_status\":");
  Serial.print(pumpStatus ? "true" : "false");
  Serial.print(",\"auto_mode\":");
  Serial.print(autoMode ? "true" : "false");
  Serial.print(",\"soil_threshold\":");
  Serial.print(soilThreshold);
  Serial.println("}");
}

void sendSensorDataToCloud() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure(); // Bypass SSL fingerprint checks for easier cloud access
    
    HTTPClient http;
    String serverUrl = "https://ntfy.sh/" + String(cloudTopic);
    
    Serial.println("[Cloud] Connecting to: " + serverUrl);
    
    if (http.begin(client, serverUrl)) {
      http.addHeader("Content-Type", "application/json");
      
      // Construct JSON payload string
      String payload = "{\"temperature\":" + String(temperature, 1) + 
                       ",\"humidity\":" + String(humidity, 1) + 
                       ",\"soil_moisture\":" + String(soilMoisture) + 
                       ",\"pump_status\":" + String(pumpStatus ? "true" : "false") + 
                       ",\"auto_mode\":" + String(autoMode ? "true" : "false") + "}";
      
      Serial.println("[Cloud] Posting payload: " + payload);
      
      int httpCode = http.POST(payload);
      
      if (httpCode > 0) {
        Serial.printf("[Cloud] POST Response code: %d\n", httpCode);
      } else {
        Serial.printf("[Cloud] POST Failed, error: %s\n", http.errorToString(httpCode).c_str());
      }
      
      http.end();
    } else {
      Serial.println("[Cloud] Unable to connect to host");
    }
  } else {
    Serial.println("[Cloud] WiFi disconnected. Skipping upload.");
  }
}
