#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include <NewPing.h>

#define trigPin 12
#define echoPin 11
#define ledRed 2
#define ledGreen 3
#define caliBtn 5
#define maxDistance 200
#define pirPin 6

LiquidCrystal_I2C lcd(0x27, 16, 2);
NewPing sonar(trigPin, echoPin, maxDistance);

int idealDistance = 0;
unsigned long badPosture = 0;
bool warningActive = false;
const int tolerance = 10;
const int threshold = 5000;

void setup()
{
  lcd.init();
  lcd.backlight();

  Serial.begin(9600);

  lcd.setCursor(0, 0);
  lcd.print("   ERGOSENSE   ");
  lcd.setCursor(0, 1);
  lcd.print("  ARDUINO UNO  ");

  Serial.print("ERGOSENSE");
  Serial.print("\nARDUINO UNO");

  pinMode(caliBtn, INPUT_PULLUP);
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(pirPin, INPUT);

  delay(3000);

  calibrate();
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
    lcd.setCursor(0, 0);
    lcd.print("JARAK TERLALU");
    lcd.setCursor(0, 1);
    lcd.print("DEKAT! TEKAN LAGI!");

    Serial.print("JARAK TERLALU DEKAT!");
    Serial.print("\nTEKAN KALIBRASI!");

    return;
  }

  int currentDist = sonar.ping_cm();
  if (currentDist == 0)
    return;

  lcd.setCursor(0, 0);
  lcd.print("SAFE ");
  lcd.print(idealDistance);
  lcd.print("cm|");
  lcd.print(currentDist);
  lcd.print("cm");

  Serial.print("----------------------------------------------------------------");
  Serial.print("\nKONDISI AMAN\t: ");
  Serial.print(idealDistance);
  Serial.print(" cm");
  Serial.print("\nJARAK SAAT INI\t: ");
  Serial.print(currentDist);
  Serial.print(" cm");
  Serial.print("\n----------------------------------------------------------------\n");

  if (currentDist < (idealDistance - tolerance))
  {
    if (badPosture == 0)
      badPosture = millis();

    lcd.setCursor(0, 1);
    lcd.print("ALERT! : ");
    lcd.print((millis() - badPosture) / 1000);
    lcd.print("s ");

    Serial.print("\nPERINGATAN!\t:");
    Serial.println(idealDistance);
    Serial.println(" cm");
    Serial.print("\nDURASI\t\t: ");
    Serial.println((millis() - badPosture) / 1000);
    Serial.println(" s");
    Serial.print("\n----------------------------------------------------------------\n");

    if (millis() - badPosture > threshold)
      trigger();
  }
  else if (currentDist > (idealDistance - tolerance) && currentDist < (idealDistance + tolerance + 20))
  {
    reset();
    lcd.setCursor(0, 1);
    lcd.print("KONDISI AMAN");
  }
  else
  {
    if (badPosture == 0)
      badPosture = millis();

    lcd.setCursor(0, 1);
    lcd.print("ALERT! : ");
    lcd.print((millis() - badPosture) / 1000);
    lcd.print("s ");

    if (millis() - badPosture > threshold)
    {
      trigger();
    }
  }

  delay(100);
}

void calibrate()
{
  do
  {
    digitalWrite(ledGreen, LOW);

    lcd.clear();
    lcd.backlight();

    lcd.setCursor(0, 0);
    lcd.print("MULAI KALIBRASI!");

    Serial.print("\nMEMULAI KALIBRASI!");

    for (int i = 9; i > 0; i--)
    {
      lcd.setCursor(0, 1);
      lcd.print("DALAM: ");
      lcd.print(i);
      lcd.print("s");

      digitalWrite(ledRed, HIGH);
      delay(200);
      digitalWrite(ledRed, LOW);
      delay(800);
    }

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("SEDANG KALIBRASI!");

    Serial.print("\nSEDANG KALIBRASI!");

    long total = 0;

    for (int i = 0; i < 10; i++)
    {
      total += sonar.ping_cm();
      lcd.setCursor(0, 1);
      lcd.print("JARAK : ");
      lcd.print(total);
      delay(50);
    }

    idealDistance = total / 10;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("HASIL KALIBRASI");
    lcd.setCursor(0, 1);
    lcd.print("JARAK : ");
    lcd.print(idealDistance);
    lcd.print(" cm");

    digitalWrite(ledGreen, HIGH);

    delay(3000);
    lcd.clear();

  } while (idealDistance <= tolerance);
}

void trigger()
{
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, HIGH);
}

void reset()
{
  badPosture = 0;
  digitalWrite(ledRed, LOW);
  digitalWrite(ledGreen, HIGH);
}