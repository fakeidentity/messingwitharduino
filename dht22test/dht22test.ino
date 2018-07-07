#include <DHT.h>

#define DHTPIN 8
#define DHTTYPE DHT22

// Initialize DHT sensor.
DHT dht(DHTPIN, DHTTYPE);

bool inDone = true;
bool doOne = true;
bool doForever = false;
String inString = "";

void setup() {
  Serial.begin(19200);
  Serial.print("Hello!\n");
  Serial.print("Send a newline to recieve current sensor data and stop.\n");
  Serial.print("Send 'go' and a newline to recieve sensor data continuously.\n");
  dht.begin();
}

void loop() {
  if (inDone) {
    //Serial.print("Got serial input ending in newline.\n");
    //printSerialInput();

    //Serial.print("doOne = true\n");
    doOne = true;

    String cmd = inString;
    cmd.trim();
    if (cmd == "go") {
      //Serial.print("'go' command!\n");
      //Serial.print("doForever = true\n");
      doForever = true;
    }
    else {
      //Serial.print("no 'go' command!\n");
      //Serial.print("doForever = false\n");
      doForever = false;
    }
    
    inDone = false;
    inString = "";
  }

  if (doForever || doOne) {
    //Serial.print("doForever or doOne is true!\n");
    printSensorData();
    //Serial.print("doOne = false\n");
    doOne = false;
  }
}

void printSerialInput() {
  if (inDone) {
    Serial.print("printSerialInput()\n");
    Serial.print(inString);
  }
}

void serialEvent() {
  //Serial.print("serialEvent()\n");
  
  while (Serial.available()) {
    //Serial.print("Serial.available()\n");
    char inChar = Serial.read();
    inString += inChar;
    if (inChar == '\n') {
        inDone = true;
    }
  }
}

float getTempCelcius() {
  return dht.readTemperature();
}

float getHumidity() {
  return dht.readHumidity();
}

float getHeatIndex(float tempCelcius, float humidity) {
  // Compute heat index in Celsius (isFahrenheit=false)
  return dht.computeHeatIndex(tempCelcius, humidity, false);
}

void printSensorData() {
  float temp = getTempCelcius();
  float humidity = getHumidity();
  // Check if any sensor reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temp)) {
    Serial.println("Failed to read sensors!");
    return;
  }

  float hic = getHeatIndex(temp, humidity);

  Serial.print("Temperature: " + String(temp) + "C");
  Serial.print(" \t");
  Serial.print("Humidity: " + String(humidity) + "%");
  Serial.print(" \t");
  Serial.print("Heat index: " + String(hic));
  Serial.print("\n");
  delay(2000); // dht22 has 0.5hz sample rate 
}

