#include <Arduino.h>
#include <NewPing.h>
#include <EEPROM.h>

#define trigPin 12
#define echoPin 11
#define ledRed 2
#define ledGreen 3
#define caliBtn 5
#define EEPROM_ADDR 0
#define maxDistance 200

NewPing sonar(trigPin, echoPin, maxDistance);

int idealDistance = 0;
unsigned long badPosture = 0;
const int tolerance = 10;
const int threshold = 5000;

void calibrate();
void trigger();
void reset();
void standby();

void setup()
{
  Serial.begin(9600);
  
  pinMode(caliBtn, INPUT_PULLUP);
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);

  int saveDist = 0;
  EEPROM.get(EEPROM_ADDR, saveDist);

  if (saveDist > 0 && saveDist < maxDistance) {
    idealDistance = saveDist;
    Serial.print(idealDistance);
    Serial.println(",CALIBRATED_MEM");
  }

  delay(3000);
}

void loop()
{
  if (digitalRead(caliBtn) == LOW)
  {
    delay(200);
    calibrate();
  }

  if (idealDistance == 0)
  {
    digitalWrite(ledRed, HIGH);
    digitalWrite(ledGreen, HIGH);
    Serial.print(0);
    Serial.print(",");
    Serial.println("ERROR");
    delay(500);
    digitalWrite(ledRed, LOW);
    digitalWrite(ledRed, LOW);
    delay(500);
    return;
  } else if((idealDistance < 40) || (idealDistance >= 70)){
    digitalWrite(ledRed, HIGH);
    digitalWrite(ledGreen, LOW);
    Serial.print(idealDistance);
    Serial.print(",");
    Serial.println("BATAS");
    delay(500);
    digitalWrite(ledRed, LOW);
    delay(500);
    return;
  }

  int currentDist = sonar.ping_cm();
  
  if (currentDist == 0) 
  {
    currentDist = 250;
  }

  String status = "";

  if (currentDist < (idealDistance - tolerance))
  {
    if (badPosture == 0) badPosture = millis();

    if (millis() - badPosture > threshold) 
    {
      status = "BAHAYA";
      trigger();
    } 
    else 
    {
      status = "WARNING";
    }
  }
  else if (currentDist > (idealDistance + tolerance + 10) && currentDist <= (idealDistance + tolerance + 40))
  {
    if (badPosture == 0) badPosture = millis();

    if (millis() - badPosture > threshold) 
    {
      status = "BAHAYA";
      trigger();
    } 
    else 
    {
      status = "WARNING";
    }
  }
  else if (currentDist >= (idealDistance - tolerance) && currentDist <= (idealDistance + tolerance + 10))
  {
    status = "AMAN";
    reset();
  }
  else
  {
    if (badPosture == 0) badPosture = millis();

    if (millis() - badPosture > threshold)
    {
      status = "STANDBY";
      standby();
      badPosture = 0;
    }
  }

  Serial.print(currentDist);
  Serial.print(",");
  Serial.println(status);

  delay(100);
}

void calibrate()
{
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, LOW);

  long total = 0;
  int validReadings = 0;

  for (int i = 10; i > 0; i--)
  {
    Serial.print("0,CALIB_"); 
    Serial.println(i);

    digitalWrite(ledRed, HIGH);
    delay(200);
    digitalWrite(ledRed, LOW);
    delay(800);
  }

  for (int i = 0; i < 10; i++)
  {
    int reading = sonar.ping_cm();
    if (reading > 0)
    {
      total += reading;
      validReadings++;
    }
    
    Serial.print(reading);
    Serial.print(",");
    Serial.println("CALIBRATING");
    
    digitalWrite(ledRed, HIGH);
    delay(100);
    digitalWrite(ledRed, LOW);
    delay(100); 
  }

  if (validReadings > 0)
  {
    idealDistance = total / validReadings;
    EEPROM.put(EEPROM_ADDR, idealDistance);
  }
  else
  {
    idealDistance = 0;
  }

  digitalWrite(ledGreen, HIGH);
  Serial.print(idealDistance);
  Serial.print(",");
  Serial.println("CALIBRATED");
  delay(1000);
}

void trigger(){
  analogWrite(ledGreen, LOW);
  analogWrite(ledRed, 155);
}

void reset(){
  badPosture = 0;
  digitalWrite(ledRed, LOW);
  digitalWrite(ledGreen, HIGH);
}

void standby(){
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, LOW);
  delay(300);
}
