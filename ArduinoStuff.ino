#include <SPI.h>
#include <MFRC522.h>

#include <LiquidCrystal.h>
 
#define SS_PIN 10
#define RST_PIN 9
#define LED 8

MFRC522 mfrc522(SS_PIN, RST_PIN);

LiquidCrystal lcd(7, 6, 5, 4, 3, 2);
 
void setup() 
{
  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  lcd.begin(16, 2);
  lcd.clear();
}
void loop() 
{
  getCardData();
  getPiData();
  delay(1000);
}

void getCardData()
{
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent())
  {
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  digitalWrite(LED, HIGH);
  delay(50);
  digitalWrite(LED, LOW);
  //Show UID on serial monitor
  String content= "";
  content.concat(String(mfrc522.uid.uidByte[0] < 0x10 ? "0" : ""));
  content.concat(String(mfrc522.uid.uidByte[0], HEX));
  for (byte i = 1; i < mfrc522.uid.size; i++) 
  {
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  content.toUpperCase();
  Serial.println(content);
}

void getPiData()
{
  String fullInput = "";
  String fullInput2 = "";
  int input = Serial.read();
  if((char)input!='|')
  {
    bool switcheroo = false;
    if(input >= 0 && input != 10)
    {
      while(input >= 0)
      {
        if(input!=10)
        {
          if(((char)input)=='.')
          {
            switcheroo = true;
            input = Serial.read();
            input = Serial.read();
          }
          if(!switcheroo)
          {
            fullInput.concat((char)input);
          }
          else
          {
            fullInput2.concat((char)input);
          }
        }
        input = Serial.read();
      }
      if(!switcheroo)
      {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print(fullInput);
      }
      else
      {
        lcd.setCursor(0,1);
        lcd.print("Gone:" + fullInput.substring(0,5) + "-" + fullInput2.substring(0,5));
      }
    }
  }
  else
  {
    input = Serial.read();
    while(input >= 0)
    {
      if(input!=10)
      {
        fullInput.concat((char)input);
        input = Serial.read();
      }
    }
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print(fullInput);
  }
}
