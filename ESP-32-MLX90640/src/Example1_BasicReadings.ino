#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "MLX90640_API.h"
#include "MLX90640_I2C_Driver.h"

const byte MLX90640_address = 0x33; //Default 7-bit unshifted address of the MLX90640
const char* ssid = "lenovo-mh";
const char* password = "12345678!!";

// Replace with your Flask server address
const char* serverAddress = "http://192.168.137.1:5000/mlxData";

#define STACK_SIZE 4096 // set the stack size to 4KB

#define TA_SHIFT 8 //Default shift for MLX90640 in open air

static float mlx90640To[768];
paramsMLX90640 mlx90640;

bool isConnected() {
    Wire.beginTransmission((uint8_t)MLX90640_address);
    if (Wire.endTransmission() == 0) {
      return true;
    }
    return false;
  }
void setup() {

  

  Wire.begin();
  Wire.setClock(400000); //Increase I2C clock speed to 400kHz

  Serial.begin(9600);
  while (!Serial); //Wait for user to open terminal
  Serial.println("MLX90640 IR Array Example");

  if (!isConnected()) {
    Serial.println("MLX90640 not detected at default I2C address. Please check wiring. Freezing.");
    while (1);
  }

  Serial.println("MLX90640 online!");

  // Connect to Wi-Fi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  // Wait for serial monitor to open
  while (!Serial);

  // Get device parameters - We only have to do this once
  int status;
  uint16_t eeMLX90640[832];
  status = MLX90640_DumpEE(MLX90640_address, eeMLX90640);
  if (status != 0) {
    Serial.println("Failed to load system parameters");
  }

  status = MLX90640_ExtractParameters(eeMLX90640, &mlx90640);
  if (status != 0) {
    Serial.println("Parameter extraction failed");
  }

  // Once params are extracted, we can release eeMLX90640 array
}

void loop() {
  long startTime = millis();
  for (byte x = 0 ; x < 2 ; x++)
  {
    uint16_t mlx90640Frame[834];
    int status = MLX90640_GetFrameData(MLX90640_address, mlx90640Frame);

    float vdd = MLX90640_GetVdd(mlx90640Frame, &mlx90640);
    float Ta = MLX90640_GetTa(mlx90640Frame, &mlx90640);

    float tr = Ta - TA_SHIFT; //Reflected temperature based on the sensor ambient temperature
    float emissivity = 0.95;

    MLX90640_CalculateTo(mlx90640Frame, &mlx90640, emissivity, tr, mlx90640To);
  }
  long stopTime = millis();

  for (int x = 0 ; x < 768 ; x++)
  {
    //if(x % 8 == 0) Serial.println();
    Serial.print(mlx90640To[x], 2);
    Serial.print(",");
  }
  Serial.println("");
  delay(1000);

 

  // Serialize the JSON object to a string
  // Define a String to hold the CSV data
String csvString;

// Loop over all the pixels and add their temperatures to the CSV data
for (int y = 0; y < 24; y++) {
  for (int x = 0; x < 32; x++) {
    // Calculate the pixel index based on its row and column
    int pixelIndex = y * 32 + x;

    // Add the pixel temperature to the CSV string
    csvString += String(mlx90640To[pixelIndex]) + ",";
  }
}

// Remove the trailing comma from the CSV string
csvString.remove(csvString.length() - 1);

// Send the POST request to the server
HTTPClient http;
http.begin(serverAddress);
http.addHeader("Content-Type", "text/csv");
int httpResponseCode = http.POST(csvString);

// Check for errors
if (httpResponseCode > 0) {
  Serial.print("HTTP Response code: ");
  Serial.println(httpResponseCode);
} else {
  Serial.print("Error code: ");
  Serial.println(httpResponseCode);
}

// Free resources
http.end();


}



   
