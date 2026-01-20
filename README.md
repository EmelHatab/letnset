# Let n Set
**Let n Set** on lokaatiopörssinettisivusto, jonka kautta käyttäjät voivat ilmoittaa ja etsiä kuvauspaikkoja video- ja valokuvaustuotantoihin. Sovelluksen avulla mielenkiintoisten tilojen omistajat ja visuaalisten alojen ammattilaiset saavat mahdollisuuden kohtaamaan toisiaan.

# Sovelluksen toiminnot
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.

- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan lokaatioilmoituksia.

- Käyttäjä pystyy lisäämään kuvan ilmoittamaansa lokaatioon.

- Käyttäjä näkee kaikki sovellukseen ilmoitetut kuvauspaikat.

- Käyttäjä pystyy etsimään lokaatioita hakusanalla tai kategorian perusteella.

- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja (esim. ilmoitusten määrä) ja käyttäjän omat ilmoitukset.

- Käyttäjä pystyy valitsemaan lokaatiolle yhden tai useamman luokittelun (esim. teollinen, retro, moderni).

- Käyttäjä pystyy lähettämään lokaatioon liittyviä varauskyselyitä tai viestejä omistajalle, sekä jättämään ilmoituksille palautetta kommenttien ja arvosanojen muodossa.

# Sovelluksen asennus
Asenna tarvittava flask-kirjasto:

$ pip install flask

Luo tietokannan taulut ja lisää tarvittavat alkutiedot (kuten kategoriat):

$ sqlite3 database.db < schema.sql

$ sqlite3 database.db < data.sql

Voit käynnistää sovelluksen näin:

$ flask run
