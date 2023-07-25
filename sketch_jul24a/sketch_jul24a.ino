#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include "oled_u8g2.h" 
#include <ArduinoJson.h> 

const char* ssid = "AndroidHotspot06_A2_F1";
const char* password = "****";

OLED_U8G2 oled; 
WebServer server(80);  
      
int tempSensor = A2; 

int Vo;
double R1 = 10000;
double logR2, R2, T, Tc;
double c1 = 1.009249522e-03, c2 = 2.378405444e-04, c3 = 2.019202697e-07;
double Tf = 0;
void setup(void) {
  Serial.begin(115200);  
  oled.setup();
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500);
    Serial.print("-> ");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP addr: ");
  Serial.println(WiFi.localIP()); 
  server.on("/", handleRootEvent);  
  server.begin();
  Serial.println("Web server started!");
}
void loop(void) {
  oled.setLine(1, "Inha Factory");
  oled.setLine(2, "Web Server");
  oled.display();
  server.handleClient();  
  delay(5); 
}
void handleRootEvent() {
  Serial.print("main page from ");
  String clientIP = server.client().remoteIP().toString();  
  // 192.168.15.245 clientIP
  int octet1, octet2, octet3, octet4;
  sscanf(clientIP.c_str(), "%d.%d.%d.%d", &octet1, &octet2, &octet3, &octet4);
  String maskedIP = String(octet1) + ".XXX.XXX." + String(octet4); 
  Vo = analogRead(tempSensor); 
  R2 = R1 * (4095.0 / (float)Vo - 1.0);
  logR2 = log(R2);
  T = (1.0 / (c1 + c2*logR2 + c3*logR2*logR2*logR2));
  Tc = T - 273.15;  
  Tf = (Tc * 9.0/5.0) + 32.0;  
  StaticJsonDocument<200> jsonDoc;  
  jsonDoc["message"] = "Welcome Inha SmartFactory WebServer!";
  jsonDoc["ip_address"] = maskedIP;
  jsonDoc["temperature_celsius"] = Tc;
  jsonDoc["temperature_fahrenheit"] = Tf;
  String jsonResponse; 
  serializeJson(jsonDoc, jsonResponse);
  server.send(200, "application/json", jsonResponse); 
  Serial.println(clientIP);
  Serial.print(Tc);
  Serial.print("C (");
  Serial.print(Tf);
  Serial.println("F)");
}
