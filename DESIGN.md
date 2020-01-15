Namen: Rik, Yannick, Rama & Mijntje  <br>
Cursustitel: Webprogrammeren en databases <br>
Opdracht: Technisch ontwerp <br>
Groep: IK12 <br>
Datum: 14/1/12

# Technisch ontwerp

## Controllers

Het is de bedoeling dat gebruikers van deze webapplicatie in staat worden gesteld om een quiz met zelfbedachte vragen op basis van door hen geüploade foto’s te creëren.
Om een quiz aan te maken is het vereist dat gebruikers zich registreren; op hun persoonlijke accountpagina staan alle quizzes die deze gebruiker heeft aangemaakt weergegeven.
Bij elke quiz staat er natuurlijk ook een link waarmee gebruikers de quiz  deze met hun vrienden te delen. Via deze link kunnen hun vrienden deze quiz vervolgens invullen,
zonder hiervoor zelf een account aan te hoeven maken. Ten slotte dient iedereen de resultaten van de quiz in kwestie in te kunnen zien door doorverwezen te worden naar een
publieke resultatenpagina. Dit wordt allemaal mogelijk gemaakt door functies te definiëren in de main controller (application.py) die bepaalde routes afhandelen.
Om de webapplicatie (en, specifieker; de MVP-versie van de webapplicatie) soepel te laten functioneren zijn de volgende webroutes van cruciaal belang;

1. /home
    * Dit is de eerste pagina waar de gebruiker op terecht komt bij het openen van de webapplicatie. Een simpele en duidelijke maar aantrekkelijk ontworpen homepagina, vanuit waar
    een samenvatting gegeven wordt waar de gebruiker de site voor kan gebruiken, met links naar de inlog- en registreerpagina's.
1. /registreren
    * Op dit scherm kunnen gebruikers een nieuw account aanmaken. Als gebruikers zich registreren worden zij via deze route toegevoegd aan de database. Vanaf het moment dat ze toegevoegd zijn
    aan de database kunnen gebruikers inloggen.
1. /inloggen
    * Als gebruikers inloggen leidt deze route naar de index-pagina. Hier zien gebruikers de mogelijkheid om een nieuwe quiz aan te maken, of al hun aangemaakte quizzes te bekijken.
1. /mijnquizzes
    * Via deze route komen gebruikers op een webpagina waar alle quizzes met link om te delen staan weergegeven.
1. /quizaanmaken
    * Via deze route kunnen gebruikers een quiz aanmaken; titel en GIF kunnen ingevuld worden. Daarnaast kunnen er foto's geüpload worden, waar gebruikers vragen en bijbehorende
    antwoorden bij verzinnen.
1. /quizinvullen
    * Via deze route komen vrienden van de gebruiker op de pagina waar zij de quiz kunnen invullen. Deze vrienden hoeven zelf geen account aan te maken, maar vullen hun naam handmatig in
    op invulvelden, welke samen met hun uiteindelijke score worden opgeslagen in de database. Na het voltooien van de quiz worden vrienden geredirect naar de resultatenpagina.
1. /resultaten
    * Deze route leidt tot de webpagina waar de resultaten van de quiz worden gepubliceerd; de resultaten van iedereen staan weergegeven op een leaderboard.

## Views
![schets](doc/Homescreen.png)
![schets](doc/Log_in.png)
![schets](doc/Maak_account.png)
![schets](doc/Maak_quiz.png)
![schets](doc/Maak_quiz_meer.png)
![schets](doc/Mijn_quiz.png)
![schets](doc/Mijn_quizzes.png)


## Models
* Apology scherm
    * Hier wordt de gebruiker naar herleid als hij/zij een ongeldige actie uitvoert.
* Functie die GIFs ophaalt van de API
    * Deze functie zorgt ervoor dat GIFs geïntegreerd kunnen worden; zo kunnen deze toegevoegd worden als "profielfoto" van een quiz.
* Login vereist functie
    * Deze functie zorgt ervoor dat bepaalde webpagina's alleen maar toegankelijk worden onder de voorwaarde dat de gebruiker is ingelogd.

## Plugins en frameworks
* Bootstrap plugin voor frontend ontwerp
* Flask framework voor backend ontwerp
