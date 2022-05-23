#include <OneWire.h>
#include <DallasTemperature.h>

#define Vin 5 //5V
#define Resistance 10000 //10kOhm

int rawReadTemp,rawReadLuminance,rawReadHumidity;  
float voltage, temp;
int dry = 1023,wet= 283;

int oneWireBus = 7;
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

int sensorRawToLuminosity(int analogValue){
   float Vout = getVoltage(analogValue);            
   float resistanceToVoltage = (Resistance * (Vin - Vout))/ Vout;    
   int luminosity = 500/(resistanceToVoltage/1000);               
   return luminosity;
}

float getVoltage(int analogValue) { 
    return (analogValue * Vin) / 1023;
}

void setup() { 
  Serial.begin(9600); 
  sensors.begin();
}

void loop() {
  //Meranie teploty
  sensors.requestTemperatures();
  temp = sensors.getTempCByIndex(0);
  Serial.print(temp);
  Serial.print(",");
  
   //Prevod svietivosti 
  rawReadLuminance = analogRead(A2);
  int lumen = sensorRawToLuminosity(rawReadLuminance);
  Serial.print(lumen);
  Serial.print(",");

  //Meranie vlhkosti pôdy
  rawReadHumidity = analogRead(A3);
  int humidity = map(rawReadHumidity,wet,dry,100,0);
  Serial.println(humidity);
  delay(1500);
}
