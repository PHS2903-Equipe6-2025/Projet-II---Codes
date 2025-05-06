#include <AccelStepper.h>

// Mode 4 fils pour ULN2003
AccelStepper fullstep(AccelStepper::FULL4WIRE, 8, 10, 9, 11);
const int pin0 = 20;
const int pin1 = 19;
const int pin2 = 18;
const int pin3 = 17;

void setup() {
  Serial.begin(9600);
  pinMode(pin0, INPUT);
  pinMode(pin1, INPUT);
  pinMode(pin2, INPUT);
  pinMode(pin3, INPUT);
  fullstep.setMaxSpeed(5000); //Vitesse max
  fullstep.setAcceleration(200); // Accélération minimale
  digitalWrite(21, HIGH); //Pin de feedback allumé
}

//Fonction faisant avancer le moteur d'un nombre de pas défini
void avancer_moteur(int step){
    digitalWrite(21, LOW); //Eteint le pin de feedback
    delay(75);
    fullstep.move(step); 
    while (fullstep.distanceToGo() != 0) {
      fullstep.run();
    }
    digitalWrite(21, HIGH); //Rallume le pin de feedback
}

void loop() {
  // Lecture des bits (ordre : LSB à MSB)
  int b0 = digitalRead(pin0);
  int b1 = digitalRead(pin1);
  int b2 = digitalRead(pin2);
  int b3 = digitalRead(pin3);

  // Recomposition de l'entier binaire
  int action = b0 + 2*b1 + 4*b2 + 8*b3;  

  // Disjonction de cas
  switch(action) {
    case 1:
      avancer_moteur(1);
      break;
    case 2:
      avancer_moteur(5);
      break;
    case 3:
      avancer_moteur(10);
      break;
    case 4:
      avancer_moteur(20);
      break;
    case 5:
      avancer_moteur(50);
      break;
    case 6:
      avancer_moteur(100);
      break;
    case 7:
      avancer_moteur(1000);
      break;
    case 8:
      avancer_moteur(-1);
      break;
    case 9:
      avancer_moteur(-5);
      break;
    case 10:
      avancer_moteur(-10);
      break;
    case 11:
      avancer_moteur(-20);
      break;
    case 12:
      avancer_moteur(-50);
      break;
    case 13:
      avancer_moteur(-100);
      break;
    case 14:
      avancer_moteur(-1000);
      break;
  }
  delay(200);
}
