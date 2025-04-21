
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <SoftwareSerial.h>

SoftwareSerial picoSerial(D5, D6);


int sendCount = 0;
const int maxSends = 20;

const char* ssid = "Richard";
const char* password = "Jjjrrr@777";


const char* host = "api.thingspeak.com";
const String apiKey = "IS28D2SJ28KAHFC3";


WiFiClient client;

void setup() {
  Serial.begin(115200); 
  picoSerial.begin(9600);
  
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  if (picoSerial.available()) { 
    String sensorData = picoSerial.readStringUntil('\n');
    delay(100);
    sensorData.trim();  
    Serial.println(sensorData);

  
    float temp, hum, aqi;
    if (parseSensorData(sensorData, temp, hum, aqi)) {
      sendToThingSpeak(temp, hum, aqi);
      picoSerial.println("OK");
      sendCount++;
    } else {
      Serial.println("Failed to parse sensor data");
    }
    
  }
  delay(1000);
}

bool parseSensorData(String data, float &temperature, float &humidity, float &aqi) {
  int firstComma = data.indexOf(',');
  int secondComma = data.indexOf(',', firstComma + 1);

  if (firstComma != -1 && secondComma != -1) {
    temperature = data.substring(0, firstComma).toFloat();
    humidity = data.substring(firstComma + 1, secondComma).toFloat();
    aqi = data.substring(secondComma + 1).toFloat();
    return true;
  }

  return false;
}

void sendToThingSpeak(float temp, float hum, float aqi) {
  if (client.connect(host, 80)) {
    String url = "/update?api_key=" + apiKey +
                 "&field1=" + String(temp) +
                 "&field2=" + String(hum) +
                 "&field3=" + String(aqi);
                 
    client.print(String("GET ") + url + " HTTP/1.1\r\n" +
                 "Host: " + host + "\r\n" +
                 "Connection: close\r\n\r\n");

    client.stop();
    Serial.println("Data sent to ThingSpeak!");
  } else {
    Serial.println("Failed to connect to ThingSpeak");
  }
}