# KlausurBot

[Der Bot kann mit diesem Link eingeladen werden.](https://discord.com/oauth2/authorize?client_id=914273155277791332&permissions=8&scope=bot)

Alternativ kann der Bot auch selbst gehostet werden, indem `python bot.py` ausgeführt wird. Hierfür muss zuerst eine App erstellt werden, wie in zum Beispiel [dieser Anleitung](https://www.digitaltrends.com/gaming/how-to-make-a-discord-bot/) gezeigt wird. Der Token muss dann in einer Datei `token` gespeichert werden. Danach muss der Bot aus der selbst erstellten App eingeladen werden.

### Initialisierung
Nachdem ein neuer Standard Server erstellt wurde, kann mit dem `!create arg` Command der Server automatisch aufgebaut werden. Es werden automatisch folgende Einstellungen vorgenommen:

- Rollen werden erstellt und zugewiesen:
  - Tutor\*in: Hat Admin-Rechte, wird der Nachrichtenautor*in zugewiesen
  - Bot: Keine zusätzlichen Rechte, wird dem Bot zugewiesen
- Benachrichtigung wird auf nur mention gesetzt
- Channel werden erstellt/verschoben:
  - neue Kategorie `Allgemein` wird angelegt
    - general Text- und Voice-Channel werden hinzugefügt
  - neuer privater Channel `bot` wird hinzugefügt
  - `arg` viele neue Kategorien `Raum i` werden angelegt
    - jede Kategorie bekommt einen Text-Channel `text-1`
    - jede Kategorie bekommt einen Voice-Channel `voice-2`
      - ist auf eine Person beschränkt

### Commands
Hier sind alle Commands auflistet und was sie machen. Die commands werden nicht auf Groß-Kleinschreibung überprüft und können auch länger sein, also sind zum Beispiel `!ping` und `!PinGEliNG teSt` äquivalent.

Studierende können nur die Commands `!ping` und `!rem` ausführen.

##### `!init`

Aktualisiert die Einstellungen für den Server. Muss eigentlich nicht manuell ausgeführt werden.

##### `!create arg`
Ändert die nötigen Einstellungen und Channel für den Server. Für genaueres siehe Initialisierung oben.

##### `!ping`
Schickt eine Benachrichtigung, wenn jemand eine Frage hat. Die pingende Person bekommt eine Antwort als Bestätigung und der Bot schickt eine Nachricht in den Bot-Channel für die Tutor\*in.

###### Beispiele:

Falls Student\*in nicht in einem Voice-Channel ist:\
`@Paul: Sophie hat eine Frage!`\
Falls Student\*in in einem Voice-Channel `voice-x` mit der Kategorie `Raum k` ist:\
`@Paul: Sophie hat eine Frage in Raum k!`\
Falls Student\*in in einem Voice-Channel `voice-x` ohne Kategorie ist:\
`@Paul: Sophie hat eine Frage in voice-x!`

##### `!room`
Teilt alle teilnehmenden Studierenden auf die Räume auf. Alle Personen, die gerade im allgemeinen Voice-Channel sind werden aufgeteilt, wobei Personen mit der Tutor\*in Rolle übersprungen werden. Jede Person wird in den ersten freien Voice-Channel geschoben.

Weil der Bot nur eine begrenzte bandwidth hat dauert es ein paar Sekunden bis alle Studierenden verschoben wurden. Das Verschieben passiert deshalb auch in Batches.

##### `!start`
Stellt einen Klausur-Timer für 90 Minuten. Es kann nur ein Timer gleichzeitig laufen (pro Server).

Nach 45 Minuten wird folgende Nachricht in den general-Channel geschickt:\
`@everyone Die Hälfte der Zeit ist um, ihr habt noch 45 Minuten!`\
Nach 80 Minuten wird folgende Nachricht in den general-Channel geschickt:\
`@everyone Die Zeit ist fast um, ihr habt noch 10 Minuten!`\
Wenn der Timer zuende ist wird folgende Nachricht in den general-Channel geschickt:\
`@everyone Die Zeit für die Klausur ist um!`

##### `!cancel`
Bricht den aktuellen Timer ab.

##### `!rem`
Gibt zurück wie lange die Klausur noch geht.

##### `!ann`
Schickt eine Benachrichtigung, dass alle in den allgemeinen Channel kommen sollen.

##### `!help`
Gibt eine Hilfsnachricht aus. Für Studierende werden nur `!ping` und `!rem` aufgelistet.
