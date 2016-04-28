//Pin Digital pour activer et d�sactiver les capteurs et les relais
//0 et 1 RX TX utilis� pour la communication s�rie ne pas utiliser
//HUM pour humidit�
//LUM pour lumi�re
//LUM pour photor�sistance ou luminosit�
//PIN_D pour pin digitale
//PIN_A pour pin analogique
//Capteur VH400 pour l'humidit�
const int PIN_D_CAPTEUR_HUM_A = 2;
const int PIN_D_CAPTEUR_HUM_B = 3;
const int PIN_D_CAPTEUR_HUM_C = 4;
const int PIN_D_CAPTEUR_HUM_D = 5;
 
//2 photor�sistances sont utilis�es comme capteurs de lumi�re avec une r�sistance de 950 Ohm comme diviseur de tension
//Les photor�sistances ont une grosse tol�rance. � tester avec un multim�tre avant utilisation.
const int PIN_D_CAPTEUR_LUM_A = 6;
const int PIN_D_CAPTEUR_LUM_B = 7;
 
//2 plaques relais Keyes Funduino 4 relais par plaque sont utilis�es.
//http://en.keyes-robot.com/productshow.aspx?id=763
//relais humidit�
const int PIN_D_relais_HUM_A = 8;
const int PIN_D_relais_HUM_B = 9;
const int PIN_D_relais_HUM_C = 10;
const int PIN_D_relais_HUM_D = 11;
//relais lumi�re
const int PIN_D_relais_LUM_A = 12;
const int PIN_D_relais_LUM_B = 13;
 
//Pin Analogique pour la lecture des capteurs
const int PIN_A_CAPTEUR_HUM_A = 0;
const int PIN_A_CAPTEUR_HUM_B = 1;
const int PIN_A_CAPTEUR_HUM_C = 2;
const int PIN_A_CAPTEUR_HUM_D = 3;
const int PIN_A_CAPTEUR_LUM_A = 4;
const int PIN_A_CAPTEUR_LUM_B = 5;
 
//Pour communiquer avec RaspberryPi en s�rie
//9600 de baud rate est amplement suffisant
const int BAUD_RATE = 9600;
 
//Variables contenant les �tats des relais
bool relaisValveA=false;
bool relaisValveB=false;
bool relaisValveC=false;
bool relaisValveD=false;
bool relaisLumA=false;
bool relaisLumB=false;
 
//Variables contenant les valeurs des capteurs
int capteurHumA=0;
int capteurHumB=0;
int capteurHumC=0;
int capteurHumD=0;
int capteurLumA=0;
int capteurLumB=0;
 
//Sert � attendre que la cha�ne de caract�res envoy�s par le raspberry pi soit toutes re�ue
bool CommandePiComplete = false;
//La commande envoy� par le RaspberryPi
String commandePi;
 
//Fonction d'initialisation utilis�e pour les relais, les capteurs et la communication s�rie avec le RaspberryPi
void setup() 
{
  pinMode(PIN_D_CAPTEUR_HUM_A,OUTPUT);//2
  digitalWrite(PIN_D_CAPTEUR_HUM_A,LOW);
  pinMode(PIN_D_CAPTEUR_HUM_B,OUTPUT);//3
  digitalWrite(PIN_D_CAPTEUR_HUM_B,LOW);
  pinMode(PIN_D_CAPTEUR_HUM_C,OUTPUT);//4
  digitalWrite(PIN_D_CAPTEUR_HUM_C,LOW);
  pinMode(PIN_D_CAPTEUR_HUM_D,OUTPUT);//5
  digitalWrite(PIN_D_CAPTEUR_HUM_D,LOW);
  pinMode(PIN_D_CAPTEUR_LUM_A,OUTPUT);//6
  digitalWrite(PIN_D_CAPTEUR_LUM_A,LOW);
  pinMode(PIN_D_CAPTEUR_LUM_B,OUTPUT);//7
  digitalWrite(PIN_D_CAPTEUR_LUM_B,LOW);
  //Les relais keyes funduino absorbe du courant alors HIGH �tain et LOW allume.
  //On les �tains tous
  pinMode(PIN_D_relais_HUM_A,OUTPUT);//8
  digitalWrite(PIN_D_relais_HUM_A,HIGH);
  pinMode(PIN_D_relais_HUM_B,OUTPUT);//9
  digitalWrite(PIN_D_relais_HUM_B,HIGH);
  pinMode(PIN_D_relais_HUM_C,OUTPUT);//10
  digitalWrite(PIN_D_relais_HUM_C,HIGH);
  pinMode(PIN_D_relais_HUM_D,OUTPUT);//11
  digitalWrite(PIN_D_relais_HUM_D,HIGH);
  pinMode(PIN_D_relais_LUM_A,OUTPUT);//12
  digitalWrite(PIN_D_relais_LUM_A,HIGH);
  pinMode(PIN_D_relais_LUM_B,OUTPUT);//13
  digitalWrite(PIN_D_relais_LUM_B,HIGH);
 
  //On initialise le port s�rie pour communiquer avec Raspberry Pi
  Serial.begin(BAUD_RATE);
 
  //On r�serve un bloc de m�moire de 15 caract�res pour recevoir les donn�es du Raspberry Pi
  commandePi.reserve(15);
}
 
//boucle principale
void loop() 
{
  //si la commande du Raspberry Pi est toute re�ue, on change l'�tat des relais selon la commande envoy�
  if(CommandePiComplete)
  {
    miseAJourEtat();
    CommandePiComplete=false;
  }
  //On lit les donn�es des capteurs
  miseAJourCapteur();
  //On envoie les �tats des relais au Raspberry Pi et on attend 10 millisecondes pour s'assurer qu'il l'a bien re�ue
  envoiEtat();
  delay(10);
 
  //On envoie la valeur des capteurs au Raspberry Pi et on attend 10 millisecondes pour s'assurer qu'il l'a bien re�ue
  envoiValeurCapteur();
  delay(10);
}
 
 
void  miseAJourEtat()
{
    //le premier caract�re est le code du relais: A = relais de la valve A | B = relais de la valve B | C = relais de la valve C | D = relais de la valve D | E = relais lumi�re A | F = relais lumi�re B
    String relais = commandePi.substring(0,1);
    //le deuxi�me caract�re est l'�tat du relais voulu: 0 = OFF et 1 = ON
    String valeur =  commandePi.substring(1);
    int iValeur=-1;
    //s'il y avait bel et bien un caract�re, on le convertit en entier
    if(valeur!="")
    {
      iValeur = valeur.toInt();
    }
     //On regarde, quel est le relais voulu et le changement d'�tat voulu, puis on active ou d�sactive le relais en fonction de cette commande
     //relais valve
     if(relais == "A")
     {
       if(iValeur==1)
       {
         activerelais(PIN_D_relais_HUM_A);
         relaisValveA = true;
       }
       else if(iValeur==0)
       {
         etainrelais(PIN_D_relais_HUM_A); 
         relaisValveA = false;
       } 
     }
     else if(relais == "B")
      {
       if(iValeur==1)
       {
         activerelais(PIN_D_relais_HUM_B);
         relaisValveB = true;
       }
       else if(iValeur==0)
       {
         etainrelais(PIN_D_relais_HUM_B); 
         relaisValveB = false;
       }
      }
     else if(relais == "C")
     {
       if(iValeur==1)
       {
         activerelais(PIN_D_relais_HUM_C);
         relaisValveC = true;
       }       
       else if(iValeur==0)
       {
         etainrelais(PIN_D_relais_HUM_C);
         relaisValveC = false; 
       } 
     }
       else if(relais == "D")
       {
         if(iValeur==1)
         {
           activerelais(PIN_D_relais_HUM_D);
           relaisValveD = true;
         }
         else if(iValeur==0)
         {
           etainrelais(PIN_D_relais_HUM_D);
           relaisValveD = false; 
         }  
       }
       //relais lumiere  
       else if(relais == "E")
       {
         if(iValeur==1)
         {
           activerelais(PIN_D_relais_LUM_A);
           relaisLumA = true;
         }
         else if(iValeur==0)
         {
           etainrelais(PIN_D_relais_LUM_A);
           relaisLumA = false; 
         }
       }
       else if(relais == "F")
       {
         if(iValeur==1)
         {
           activerelais(PIN_D_relais_LUM_B);
           relaisLumB = true;
         }
         else if(iValeur==0)
         {
           etainrelais(PIN_D_relais_LUM_B);
           relaisLumB = false; 
         } 
       }
    //On vide la commande envoy�e par le Raspberry Pi, afin d'�tre pr�t � en recevoir une autre     
    commandePi ="";
}
 
//Fonction qui envoie les �tats des relais au Raspberry Pi
//Le protocole de communication est R pour relais, V pour Valve et L pour lumi�re ensuite _, la lettre du relais et :l'�tat du relais
//exemple: RV_C:0 veut dire que le relais de la valve C est �teint
//exemple2: RL_A:1 veut dire que le relais de la valve A est allum�
void envoiEtat()
{
  //RV = relais Valve
  //RL = relais Lumi�re
  Serial.print(" RV_A:"+String(relaisValveA)+' ');
  Serial.print("RV_B:"+String(relaisValveB)+' ');
  Serial.print("RV_C:"+String(relaisValveC)+' ');
  Serial.print("RV_D:"+String(relaisValveD)+' ');
  Serial.print("RL_A:"+String(relaisLumA)+' ');
  Serial.println("RL_B:"+String(relaisLumB)+' ');
}
 
//Fonction qui envoie les valeurs des capteurs au Raspberry Pi
//Le protocole de communication est C pour Capteur, Humidit� pour Humidit� et L pour lumi�re ensuite _, la lettre du capteur et :sa valeurs
//exemple: CH_B:2573 veut dire que le capteur d'humidit� C a un taux d'humidit� de 25.73%
//exemple2: CL_A:1458 veut dire que le capteur de lumi�re A a une r�sistance de 1458 Ohm
void envoiValeurCapteur()
{
  //Capteur Humidit� ==CH 
  //Capteur Lumi�re ==CL
  Serial.print(" CH_A:"+ String(capteurHumA)+' ');
  Serial.print("CH_B:"+ String(capteurHumB)+' ');
  Serial.print("CH_C:"+ String(capteurHumC)+' ');
  Serial.print("CH_D:"+ String(capteurHumD)+' ');
  Serial.print("CL_A:"+ String(capteurLumA)+' ');
  Serial.println("CL_B:"+ String(capteurLumB)+' ');
}
 
//La fonction va lire les valeurs des capteurs et elles sont gard�es en m�moire
 void miseAJourCapteur()
 {
   capteurHumA = litValeurHumidite(PIN_D_CAPTEUR_HUM_A,PIN_A_CAPTEUR_HUM_A);
   capteurHumB = litValeurHumidite(PIN_D_CAPTEUR_HUM_B,PIN_A_CAPTEUR_HUM_B);
   capteurHumC = litValeurHumidite(PIN_D_CAPTEUR_HUM_C,PIN_A_CAPTEUR_HUM_C);
   capteurHumD = litValeurHumidite(PIN_D_CAPTEUR_HUM_D,PIN_A_CAPTEUR_HUM_D);
   capteurLumA = litValeurCapteurLumiere(PIN_D_CAPTEUR_LUM_A,PIN_A_CAPTEUR_LUM_A);
   capteurLumB = litValeurCapteurLumiere(PIN_D_CAPTEUR_LUM_B,PIN_A_CAPTEUR_LUM_B);
 }
 
 
//Cette fonction est appel�e � chaque fin de la boucle loop()
//Lit un caract�re qui est envoy� par le Raspberry Pi et si le caract�re est un saut de ligne, cela veut dire que la commande est compl�t�e.
void serialEvent() 
{
  //tant qu'il y a des caract�res dans le port s�rie
  while (Serial.available()) 
  {
    //Lit un caract�re
    char caractereCommande = (char)Serial.read();
    // l'ajoute � la commande que le raspberry pi � envoy�
    commandePi += caractereCommande;
    //Si le caract�re est un saut de ligne sela veut dire que nous avons re�us l'ensemble de la commande
    if (caractereCommande == '\n') 
    {
      CommandePiComplete = true;
    }
  }
}
 
//convertie un nombre � virgule en entier arrondi.
int FloatAIntEtArondie(float valeur)
{
  int iTemp=(int)valeur;
  float fTemp=valeur-iTemp;
  if(fTemp>0.5)
  {
    return (int)(valeur+1);
  }
  return (int)valeur;
}
 
//retourne la valeur du capteur de 0 � 1023 
//lit le capteur un certain nombre de fois et en fait une moyennne
//Le capteur est activ� pour la lecture puis est d�sactiv�
int litValeurCapteur(const int PIN_ECRITURE,const int PIN_LECTURE,const int NOMBRE_DE_LECTURE)
{
  //temps d'attente pour s'assurer que le capteur est bien activ�.
  const int ATTENTE_LECTURE_MS = 100;
  int valeur = 0;
 
  for(int i=0;i!=NOMBRE_DE_LECTURE;i++)
  {
    digitalWrite(PIN_ECRITURE,HIGH);
    delay(ATTENTE_LECTURE_MS);
    valeur += analogRead(PIN_LECTURE);
    digitalWrite(PIN_ECRITURE,LOW);  
  }
  return valeur/NOMBRE_DE_LECTURE;
}
 
//retourne la valeur du capteur en voltage
//le arduino donne une valeur de 0 � 1023 qui repr�sente le voltage du capteur sur 5 volts. Chaque nombre repr�sente environ 0.005 volt
float litValeurCapteurVoltage(const int PIN_ECRITURE,const int PIN_LECTURE,const int NOMBRE_DE_LECTURE)
{
  return litValeurCapteur(PIN_ECRITURE,PIN_LECTURE,NOMBRE_DE_LECTURE)*(5.0/1023.0);
}
 
//retourne la r�sistance en Ohm du capteur photo-r�sistif
int litValeurCapteurLumiere (const int PIN_ECRITURE,const int PIN_LECTURE)
{
  //le nombre de fois que le capteur sera lu par le arduino pour en faire une moyenne
  const int NOMBREDELECTURE = 4;
  const int VIN = 5; //Voltage d'arduino
  const float RESISTANCE_FIXE = 975; //vrai==975Ohm(sur paquet 1000Ohm) pour les 2!
  //retourne un entier contenant la r�sistance de la photor�sistance en Ohm � l'aide du principe de la division du voltage
  return FloatAIntEtArondie(RESISTANCE_FIXE/((VIN / litValeurCapteurVoltage(PIN_ECRITURE,PIN_LECTURE,NOMBREDELECTURE)) - 1));
}
 
//capteur vh400
//retourne la teneur en eau volum�trique(Volumetric Water Content) en %
//�quation fond�e sur les calculs de la compagnie qui produit le capteur d'humidit�: http://vegetronix.com/Products/VH400/VH400-Piecewise-Curve.phtml
int litValeurHumidite (const int PIN_ECRITURE,const int PIN_LECTURE)
{ 
  const int NOMBREDELECTURE = 4;
  float ValeurHumidite = 0.0;
  //pour retourner un entier au lieu d'un nombre � virgule et conserver une pr�cision de 2 d�cimales
  const int NOMBREDECIMAL = 100;
  float valeurCapteurVoltage = litValeurCapteurVoltage(PIN_ECRITURE,PIN_LECTURE,NOMBREDELECTURE);
  if (valeurCapteurVoltage < 1.1)
    ValeurHumidite = 10.0*valeurCapteurVoltage-1.0;
  if(valeurCapteurVoltage < 1.3)
    ValeurHumidite = 25.0*valeurCapteurVoltage-17.5;
  if(valeurCapteurVoltage < 1.82)
    ValeurHumidite = 48.08*valeurCapteurVoltage-47.5;
  if(valeurCapteurVoltage < 2.2)
    ValeurHumidite = 26.32*valeurCapteurVoltage-7.89; 
  // si la valeur est en haut de 50 la pente est approximativement lin�aire 
  if(valeurCapteurVoltage >= 2.2)
    ValeurHumidite = 26.32*valeurCapteurVoltage-7.89; 
 
    return ValeurHumidite*NOMBREDECIMAL;
 }
 
//LOW active le relais
void activerelais(const int PIN_ECRITURE)
{
  delay(25);
  digitalWrite(PIN_ECRITURE,LOW); 
}
 
//HIGH �taint le relais
void etainrelais(const int PIN_ECRITURE)
{
  delay(25);
  digitalWrite(PIN_ECRITURE,HIGH);
}