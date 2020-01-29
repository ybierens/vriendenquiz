Namen: Rik, Yannick, Rama & Mijntje  <br>
Cursustitel: Webprogrammeren en databases <br>
Opdracht: Bouwen webapplicatie <br>
Groep: IK12 <br>
Datum: 29/01/2020

# Projectvoorstel

## Samenvatting

Er is niets uniekers dan jijzelf. Met onze webapplicatie maak je een quiz over jezelf en deel je deze met je vrienden. Wie weet het meest en is jouw beste vriend? En wat is nou een betere manier om de kennis van je vrienden te meten dan een foto? *After all, a picture says a thousand words…* Wie beantwoord de meeste vragen goed binnen jouw vriendengroep en is de **BESTE VRIEND**?

## Applicatie

![screenshot](doc/application.png =200x)

## Features
1. Account aanmaken om quizzes in op te slaan
1. Nieuwe quiz aanmaken met een naam, gif en dankwoord
1. Aan je nieuw aangemaakte quiz kan je zoveel vragen als je wilt toevoegen, met ieder zoveel multiple choice antwoorden als je wilt. Aan iedere vraag moet je een foto toevoegen
1. Iedere quiz kan je vinden via een code of via een URL
1. Je kan een quiz invullen, aan het einde kan je een opmerking achterlaten
1. Na het invullen zie je meteen je score en je positie in de ranglijst, en kan je zien wat je fout had en wat eigenlijk goed is
1. Je kan van alle quizzen zien wie de hoogste score heeft
1. Je kan per quiz zien we de hoogste score heeft
1. Je kan van iedereen zien wat ze precies hebben ingevuld
1. Je kan alle foto's zien die je hebt toegevoegd aan je quizzen
1. je kan quizzen verwijderen
1. Je kan je gebruikersnaam en wachtwoord aanpassen
1. Je kan een profielfoto aan je gebruiker toevoegen
1. Je kan een quiz delen via Whatsapp

## Minimum viable product features
1. Quiz creëren door foto's te uploaden en hierbij passende vragen en antwoorden in te voeren
1. Quiz invullen
1. GIFs toevoegen
1. Scorelijsten inzien: wie heeft de meeste vragen goed?

## Wie heeft wat gebouwd
1. Mijntje: afhandelen van de foto's en gifs
1. Rik: veel van het javascript, vooral de ingewikkelde stukken
1. Rama: styling van de website
1. Yannick: veel van de routes in application
Daarnaast hebben we elkaar veel geholpen met debuggen, oplossingen bedenken voor problemen, etc

## Uitleg repository
We hebben een helpers bestand met daarin een aantal functies. Alle foto's die zijn toegevoegd aan quizvragen staan in UPLOAD_FOLDER

## Afhankelijkheden
Databronnen:
* Giphy API
* Eigen database-structuur (SQLite): tables voor (1) gebruikers, (2) de quizzen, de quizvragen en -antwoorden, (3) de participanten en hun antwoorden

Externe componenten:
* Documentatie HTML, CSS, JavaScript & SQL
* SQL-bibliotheek tijdens coderen
* Flask-framework bibliotheek tijdens coderen
* Bootstrap

Opmerkelijke punten concurrerende websites:
* Allereerst zijn er niet heel veel online vriendenquizzes te vinden die gebruikers toestaan een quiz over zichzelf te creëren
* De interfaces van de meeste online vriendenquizzes zien er erg schreeuwerig, ouderwets en/of kinderlijk uit
* Slechts een paar quizzes hebben de mogelijkheid echt zélf de vragen en antwoorden in te typen
* In geen enkele andere quiz worden vragen gesteld op basis van foto’s

Moeilijkste punten realisatie applicatie:
* Uitzoeken hoe de database-structuur van de quiz ingedeeld gaat worden
* De opgehaalde data (GIFs) integreren in de quiz
* Een consistente en flowende user experience bewerkstelligen