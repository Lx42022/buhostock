"""Build the English and German pages from the Spanish source pages.

Spanish (repo root) is the single source. This script copies index.html,
condiciones.html and privacidad.html into en/ and de/, swaps every Spanish
text for its translation and fixes paths + language switch.

If a Spanish text changes, the script stops with "missing" so the
translation table below gets updated too (nothing goes live half-translated).

Run:  python tools/build_i18n.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "condiciones.html", "privacidad.html"]
LANGS = {"en": {"locale": "en_GB", "nav": "Language"}, "de": {"locale": "de_DE", "nav": "Sprache"}}

# (spanish, english, german). Applied in this order; every row must be found
# in at least one page. Rows marked by a page name apply only there.
SHARED: list[tuple[str, str, str]] = [
    ('aria-label="BuhoStock, inicio"', 'aria-label="BuhoStock, home"', 'aria-label="BuhoStock, Startseite"'),
    ('aria-label="Legal y contacto"', 'aria-label="Legal and contact"', 'aria-label="Rechtliches und Kontakt"'),
    (">Pruébalo gratis<", ">Try it free<", ">Gratis testen<"),
    (">Condiciones de uso<", ">Terms of use<", ">Nutzungsbedingungen<"),
    (">Privacidad<", ">Privacy<", ">Datenschutz<"),
    ("© 2026 BuhoStock. BuhoStock es una herramienta independiente, no está afiliada a Wallapop ni cuenta con su respaldo.",
     "© 2026 BuhoStock. BuhoStock is an independent tool, not affiliated with or endorsed by Wallapop.",
     "© 2026 BuhoStock. BuhoStock ist ein unabhängiges Werkzeug, nicht mit Wallapop verbunden und nicht von Wallapop unterstützt."),
]

INDEX: list[tuple[str, str, str]] = [
    # head
    ("BuhoStock · Tus anuncios de Wallapop, arriba cada noche",
     "BuhoStock · Your Wallapop listings back on top every night",
     "BuhoStock · Deine Wallapop-Anzeigen jede Nacht wieder oben"),
    ("BuhoStock vuelve a subir tus anuncios de Wallapop cada noche, baja poco a poco el precio de lo que no se vende hasta tu mínimo y cada mañana te manda un informe. 30 días gratis, sin permanencia.",
     "BuhoStock relists your Wallapop listings every night, lowers the price of what isn't selling step by step down to your minimum and sends you a report every morning. 30 days free, no commitment.",
     "BuhoStock stellt deine Wallapop-Anzeigen jede Nacht neu ein, senkt den Preis von Ladenhütern Schritt für Schritt bis zu deinem Mindestpreis und schickt dir jeden Morgen einen Bericht. 30 Tage gratis, ohne Bindung."),
    ("BuhoStock · Mientras duermes, tus anuncios vuelven arriba",
     "BuhoStock · While you sleep, your listings go back to the top",
     "BuhoStock · Während du schläfst, landen deine Anzeigen wieder oben"),
    ("Renueva tus anuncios cada noche, ajusta precios sin bajar de tu mínimo y te manda el informe por la mañana. 30 días gratis.",
     "Relists your listings every night, adjusts prices without going below your minimum and sends you the report in the morning. 30 days free.",
     "Stellt deine Anzeigen jede Nacht neu ein, passt Preise an, ohne unter deinen Mindestpreis zu gehen, und schickt dir morgens den Bericht. 30 Tage gratis."),
    ("Saltar al contenido", "Skip to content", "Zum Inhalt springen"),
    ('aria-label="Principal"', 'aria-label="Main"', 'aria-label="Hauptmenü"'),
    (">Cómo funciona<", ">How it works<", ">So funktioniert's<"),
    (">Resultados<", ">Results<", ">Ergebnisse<"),
    (">Precios<", ">Pricing<", ">Preise<"),
    (">Preguntas<", ">FAQ<", ">Fragen<"),
    # hero
    ("Para tiendas de segunda mano en Wallapop", "For second-hand shops on Wallapop", "Für Second-Hand-Shops auf Wallapop"),
    ("Mientras duermes, tus anuncios vuelven arriba.", "While you sleep, your listings go back to the top.", "Während du schläfst, landen deine Anzeigen wieder oben."),
    ("Cada noche BuhoStock vuelve a subir tus anuncios y baja poco a poco el precio de lo que no se vende, nunca por debajo de tu mínimo. A las seis tienes el informe en tu correo.",
     "Every night BuhoStock relists your listings and lowers the price of what isn't selling, bit by bit and never below your minimum. By six in the morning the report is in your inbox.",
     "Jede Nacht stellt BuhoStock deine Anzeigen neu ein und senkt nach und nach den Preis von dem, was sich nicht verkauft – nie unter deinen Mindestpreis. Um sechs Uhr liegt der Bericht in deinem Postfach."),
    ("Quiero probarlo · 30 días gratis", "Try it · 30 days free", "Jetzt testen · 30 Tage gratis"),
    ("Sin permanencia. Cancelas cuando quieras.", "No commitment. Cancel any time.", "Keine Mindestlaufzeit. Jederzeit kündbar."),
    ('aria-label="Ejemplo del informe que recibes cada mañana"', 'aria-label="Example of the report you get every morning"', 'aria-label="Beispiel für den Bericht, den du jeden Morgen bekommst"'),
    ("Correo · hoy 06:12", "E-mail · today 06:12", "E-Mail · heute 06:12"),
    ("Buenos días: esto hizo Búho esta noche", "Good morning: here's what Búho did last night", "Guten Morgen: Das hat Búho heute Nacht gemacht"),
    ("<span>revisados</span>", "<span>checked</span>", "<span>geprüft</span>"),
    ("<span>renovados</span>", "<span>relisted</span>", "<span>neu eingestellt</span>"),
    ("<span>vendidos</span>", "<span>sold</span>", "<span>verkauft</span>"),
    ("<span>trabajadas</span>", "<span>worked</span>", "<span>gearbeitet</span>"),
    ("<b>renovado</b>", "<b>relisted</b>", "<b>neu eingestellt</b>"),
    ("<b>en tu mínimo</b>", "<b>at your minimum</b>", "<b>beim Mindestpreis</b>"),
    ("Ejemplo: una noche media de nuestras cuentas.", "Example: an average night on our own accounts.", "Beispiel: eine durchschnittliche Nacht auf unseren Konten."),
    # numbers
    ("Resultados reales", "Real results", "Echte Ergebnisse"),
    ("<b>18.544</b>", "<b>18,544</b>", "<b>18.544</b>"),
    ("<b>2.706</b>", "<b>2,706</b>", "<b>2.706</b>"),
    ("noches seguidas trabajando", "nights in a row", "Nächte am Stück gearbeitet"),
    ("productos gestionados", "products handled", "Produkte bearbeitet"),
    ("anuncios renovados a tiempo", "listings relisted at the right time", "Anzeigen rechtzeitig neu eingestellt"),
    ("ventas al mes desde que lo usamos", "sales per month since we started using it", "Verkäufe pro Monat, seit wir es nutzen"),
    ("Nuestras 2 cuentas de electrónica, abril–julio 2026. Correlación, no garantía.",
     "Our 2 electronics accounts, April–July 2026. Correlation, not a guarantee.",
     "Unsere 2 Elektronik-Konten, April–Juli 2026. Zusammenhang, keine Garantie."),
    # one night
    ("Una noche de trabajo, mientras tú descansas", "A night's work while you rest", "Eine Nacht Arbeit, während du dich ausruhst"),
    ("<h3>Arranca solo</h3><p>El programa despierta tu PC y abre tu cuenta.</p>",
     "<h3>Starts on its own</h3><p>The program wakes your PC and opens your account.</p>",
     "<h3>Startet von selbst</h3><p>Das Programm weckt deinen PC und öffnet dein Konto.</p>"),
    ("<h3>Ajusta precios</h3><p>Baja paso a paso lo que está parado. Nunca por debajo de tu mínimo.</p>",
     "<h3>Adjusts prices</h3><p>Lowers what isn't moving, step by step. Never below your minimum.</p>",
     "<h3>Passt Preise an</h3><p>Senkt Schritt für Schritt, was liegen bleibt. Nie unter deinen Mindestpreis.</p>"),
    ("<h3>Renueva anuncios</h3><p>Los que llevan tiempo quietos vuelven a salir arriba en las búsquedas.</p>",
     "<h3>Relists listings</h3><p>The ones that have been sitting still show up at the top of search again.</p>",
     "<h3>Stellt Anzeigen neu ein</h3><p>Was länger stillsteht, erscheint wieder oben in der Suche.</p>"),
    ("<h3>Te lo cuenta</h3><p>Informe por correo: qué cambió y qué se vendió. Tú solo cobras y repones.</p>",
     "<h3>Tells you about it</h3><p>Report by e-mail: what changed and what sold. You just get paid and restock.</p>",
     "<h3>Erzählt es dir</h3><p>Bericht per E-Mail: was sich geändert hat und was verkauft wurde. Du kassierst nur und füllst nach.</p>"),
    # you are in control
    ("Tú pones las reglas. Búho las cumple.", "You set the rules. Búho follows them.", "Du machst die Regeln. Búho hält sich dran."),
    ("Nada se mueve fuera de lo que tú decides. Y lo puedes cambiar cuando quieras.",
     "Nothing happens outside what you decide. And you can change it whenever you like.",
     "Nichts passiert außerhalb dessen, was du festlegst. Und du kannst es jederzeit ändern."),
    ("<strong>Tu precio mínimo</strong><span>Uno por artículo, o una regla para todos. Búho nunca baja de ahí.</span>",
     "<strong>Your minimum price</strong><span>One per item, or one rule for all. Búho never goes below it.</span>",
     "<strong>Dein Mindestpreis</strong><span>Einer pro Artikel oder eine Regel für alle. Búho geht nie darunter.</span>"),
    ("<strong>Tu ritmo</strong><span>Cuánto baja cada vez y cada cuántos días.</span>",
     "<strong>Your pace</strong><span>How much it drops each time and how often.</span>",
     "<strong>Dein Tempo</strong><span>Wie viel jedes Mal gesenkt wird und in welchem Abstand.</span>"),
    ("<strong>Tus anuncios</strong><span>Eliges cuáles entran. Lo que vende bien, no se toca.</span>",
     "<strong>Your listings</strong><span>You choose which ones take part. What sells well isn't touched.</span>",
     "<strong>Deine Anzeigen</strong><span>Du wählst, welche mitmachen. Was gut läuft, bleibt unangetastet.</span>"),
    ("<strong>Pausa cuando quieras</strong><span>Vacaciones, inventario o lo que sea: lo paras y lo reanudas.</span>",
     "<strong>Pause whenever you want</strong><span>Holidays, stocktaking or anything else: stop it and start it again.</span>",
     "<strong>Pausieren, wann du willst</strong><span>Urlaub, Inventur oder was auch immer: anhalten und wieder starten.</span>"),
    # delivery
    (">Cómo lo tienes<", ">How you get it<", ">So bekommst du es<"),
    ('<span class="tag on">Para empezar</span><h3>Programa para tu PC</h3><p>Para Windows. Despierta el PC de noche, trabaja y lo deja descansar. Tu cuenta, tu conexión.</p>',
     '<span class="tag on">To start</span><h3>Program for your PC</h3><p>For Windows. Wakes the PC at night, does the work and lets it rest again. Your account, your connection.</p>',
     '<span class="tag on">Zum Start</span><h3>Programm für deinen PC</h3><p>Für Windows. Weckt den PC nachts, arbeitet und lässt ihn wieder ruhen. Dein Konto, deine Verbindung.</p>'),
    ('<span class="tag">Opcional · +15 €/mes</span><h3>Búho-Box</h3><p>Un aparato pequeño junto a tu router, para si tu PC se apaga del todo por la noche. Desde el plan Starter.</p>',
     '<span class="tag">Optional · +15 €/month</span><h3>Búho-Box</h3><p>A small device next to your router, in case your PC is fully switched off at night. From the Starter plan.</p>',
     '<span class="tag">Optional · +15 €/Monat</span><h3>Búho-Box</h3><p>Ein kleines Gerät neben deinem Router, falls dein PC nachts ganz aus ist. Ab dem Starter-Plan.</p>'),
    ('<span class="tag">Próximamente</span><h3>Extensión de Chrome</h3><p>Sin instalar nada más. Si te das de alta, te avisamos cuando esté lista.</p>',
     "<span class=\"tag\">Coming soon</span><h3>Chrome extension</h3><p>Nothing else to install. Sign up and we'll let you know when it's ready.</p>",
     '<span class="tag">Bald verfügbar</span><h3>Chrome-Erweiterung</h3><p>Ohne weitere Installation. Wenn du dich anmeldest, sagen wir dir Bescheid, sobald sie fertig ist.</p>'),
    # founders
    ('aria-label="Por qué existe BuhoStock"', 'aria-label="Why BuhoStock exists"', 'aria-label="Warum es BuhoStock gibt"'),
    ("Lo hicimos para nuestra propia tienda de electrónica. Ahora buscamos los primeros comercios.",
     "We built it for our own electronics shop. Now we're looking for the first shops to join.",
     "Wir haben es für unseren eigenen Elektronik-Shop gebaut. Jetzt suchen wir die ersten Händler."),
    ("Las cifras de esta página salen de nuestras propias cuentas, no de clientes. Si empiezas ahora, el precio con el que entras se queda para siempre.",
     "The figures on this page come from our own accounts, not from customers. If you start now, the price you join at stays yours for good.",
     "Die Zahlen auf dieser Seite stammen aus unseren eigenen Konten, nicht von Kunden. Wenn du jetzt einsteigst, behältst du deinen Startpreis für immer."),
    # pricing
    ("Pagas según tus anuncios", "You pay by number of listings", "Du zahlst nach Anzahl deiner Anzeigen"),
    ("30 días gratis · luego al mes, sin permanencia", "30 days free · then monthly, no commitment", "30 Tage gratis · danach monatlich, ohne Mindestlaufzeit"),
    ("¿Cuántos anuncios tienes?</label>", "How many listings do you have?</label>", "Wie viele Anzeigen hast du?</label>"),
    ('¿Cuántos anuncios tienes? <span class="opt">(aprox.)</span>', 'How many listings do you have? <span class="opt">(approx.)</span>', 'Wie viele Anzeigen hast du? <span class="opt">(ca.)</span>'),
    ('placeholder="p. ej. 120"', 'placeholder="e.g. 120"', 'placeholder="z. B. 120"'),
    ("hasta 50 anuncios", "up to 50 listings", "bis 50 Anzeigen"),
    ("hasta 150 anuncios", "up to 150 listings", "bis 150 Anzeigen"),
    ("hasta 400 anuncios", "up to 400 listings", "bis 400 Anzeigen"),
    ("hasta 1.000 anuncios", "up to 1,000 listings", "bis 1.000 Anzeigen"),
    ("<small> /mes</small>", "<small> /month</small>", "<small> /Monat</small>"),
    ("Los primeros 30 días son gratis y no te pedimos tarjeta.", "The first 30 days are free and we don't ask for a card.", "Die ersten 30 Tage sind gratis, ohne Kreditkarte."),
    ("Sin permanencia: cancelas o pausas cuando quieras.", "No commitment: cancel or pause whenever you like.", "Keine Mindestlaufzeit: jederzeit kündigen oder pausieren."),
    ("Pago anual: 2 meses gratis.", "Yearly payment: 2 months free.", "Jahreszahlung: 2 Monate gratis."),
    ("Más de 1.000 anuncios: te hacemos un precio a medida.", "More than 1,000 listings: we'll make you a custom price.", "Mehr als 1.000 Anzeigen: individueller Preis."),
    ("Búho-Box: +15 €/mes, desde Starter, mínimo 6 meses.", "Búho-Box: +15 €/month, from Starter, minimum 6 months.", "Búho-Box: +15 €/Monat, ab Starter, mindestens 6 Monate."),
    ("Precio de lanzamiento: el que tienes al empezar se queda.", "Launch price: the price you start with stays.", "Startpreis: Der Preis, mit dem du startest, bleibt."),
    # FAQ
    ("¿Qué hace exactamente cada noche?", "What exactly does it do every night?", "Was macht es genau jede Nacht?"),
    ("Revisa tus anuncios uno por uno. Si alguno lleva días parado, le baja el precio un poco, sin pasar nunca del mínimo que tú fijas, y vuelve a subir los que llevan tiempo quietos para que salgan otra vez arriba. Por la mañana te llega un informe con lo que ha hecho y lo que se ha vendido.",
     "It goes through your listings one by one. If one has been sitting for days, it lowers the price a little, never past the minimum you set, and relists the ones that have been still for a while so they show up at the top again. In the morning you get a report of what it did and what sold.",
     "Es geht deine Anzeigen einzeln durch. Steht eine seit Tagen still, senkt es den Preis ein wenig, nie unter deinen Mindestpreis, und stellt länger unbewegte Anzeigen neu ein, damit sie wieder oben erscheinen. Morgens bekommst du einen Bericht, was es gemacht hat und was verkauft wurde."),
    ("¿Tengo que dejar el ordenador encendido?", "Do I have to leave my computer on?", "Muss mein Computer an bleiben?"),
    ("Basta con dejarlo en reposo (suspensión). El programa lo despierta por la noche, trabaja y lo vuelve a dejar descansar. Si lo apagas del todo cada noche, para eso existe la Búho-Box.",
     "Sleep mode is enough. The program wakes it up at night, does the work and lets it sleep again. If you switch it off completely every night, that's what the Búho-Box is for.",
     "Der Ruhezustand reicht. Das Programm weckt ihn nachts, arbeitet und lässt ihn wieder schlafen. Wenn du ihn jede Nacht ganz ausschaltest, gibt es dafür die Búho-Box."),
    ("¿Me pedís la contraseña de mi cuenta?", "Do you ask for my account password?", "Fragt ihr nach meinem Passwort?"),
    ("No. Inicias sesión tú, en tu propio ordenador. Nosotros no te pedimos ni guardamos tu contraseña, y si la cambias, Búho se queda fuera al momento.",
     "No. You log in yourself, on your own computer. We never ask for or store your password, and if you change it, Búho is locked out immediately.",
     "Nein. Du meldest dich selbst an, auf deinem eigenen Computer. Wir fragen nie nach deinem Passwort und speichern es nicht. Änderst du es, ist Búho sofort ausgesperrt."),
    ("¿Para qué productos funciona?", "What products does it work for?", "Für welche Produkte funktioniert es?"),
    ("Empezamos con electrónica y lo que va con ella: móviles, informática, consolas y videojuegos, TV, audio y foto, electrodomésticos y herramientas eléctricas. Otras categorías, cuando las hayamos probado a fondo.",
     "We're starting with electronics and related items: phones, computers, consoles and video games, TV, audio and photo, home appliances and power tools. Other categories once we've tested them thoroughly.",
     "Wir starten mit Elektronik und allem, was dazugehört: Handys, Computer, Konsolen und Videospiele, TV, Audio und Foto, Haushaltsgeräte und Elektrowerkzeuge. Andere Kategorien, sobald wir sie gründlich getestet haben."),
    ("¿Qué pasa cuando acaban los 30 días?", "What happens after the 30 days?", "Was passiert nach den 30 Tagen?"),
    ("Eliges el plan que te encaje o lo dejas. No te cobramos nada sin preguntarte antes.",
     "You pick the plan that suits you, or you stop. We never charge you without asking first.",
     "Du wählst den passenden Plan oder hörst auf. Wir berechnen nichts, ohne dich vorher zu fragen."),
    ("¿Cuándo voy a ver resultados?", "When will I see results?", "Wann sehe ich Ergebnisse?"),
    ("Depende de tu tienda y de tu stock, y no podemos prometerte cifras. Por eso miramos tu punto de partida antes de empezar: así puedes comparar con datos reales. En nuestras cuentas las ventas pasaron de unas 22 a unas 49 al mes desde que lo usamos, aunque no podemos asegurar que sea solo por eso.",
     "It depends on your shop and your stock, and we can't promise numbers. That's why we look at your starting point first, so you can compare with real data. On our accounts, sales went from about 22 to about 49 a month since we started using it, although we can't say for sure that this was the only reason.",
     "Das hängt von deinem Shop und deinem Bestand ab, Zahlen können wir nicht versprechen. Deshalb schauen wir uns vorher deinen Ausgangspunkt an, damit du mit echten Daten vergleichen kannst. Auf unseren Konten stiegen die Verkäufe von etwa 22 auf etwa 49 pro Monat, seit wir es nutzen – ob das allein daran liegt, können wir nicht sicher sagen."),
    ("¿Quién me atiende?", "Who will help me?", "Wer betreut mich?"),
    ("El equipo de BuhoStock, por correo o WhatsApp. Usamos un sistema automatizado supervisado por personas; si prefieres hablar con una persona, dínoslo y te lo organizamos.",
     "The BuhoStock team, by e-mail or WhatsApp. We use an automated system supervised by people; if you'd rather talk to a person, just tell us and we'll arrange it.",
     "Das BuhoStock-Team, per E-Mail oder WhatsApp. Wir nutzen ein automatisiertes System, das von Menschen überwacht wird; wenn du lieber mit einem Menschen sprichst, sag es uns und wir organisieren das."),
    # sign-up
    ("Pruébalo 30 días gratis", "Try it free for 30 days", "30 Tage gratis testen"),
    ("Déjanos tus datos y te escribimos para ponerlo en marcha contigo.",
     "Leave your details and we'll get in touch to set it up with you. For now the service and its e-mails are in Spanish.",
     "Hinterlass deine Daten, wir melden uns und richten es mit dir ein. Der Service und die E-Mails sind vorerst auf Spanisch."),
    ("Te escribimos en menos de 48 horas (días laborables).</li>", "We'll write to you within 48 hours (working days).</li>", "Wir melden uns innerhalb von 48 Stunden (Werktage).</li>"),
    ("Vemos juntos tus anuncios y fijamos tus precios mínimos.", "We go through your listings together and set your minimum prices.", "Wir gehen gemeinsam deine Anzeigen durch und legen deine Mindestpreise fest."),
    ("Instalas el programa y esa misma noche empieza a trabajar.", "You install the program and it starts working that same night.", "Du installierst das Programm, und noch in derselben Nacht legt es los."),
    ("Tu nombre o el de tu tienda", "Your name or your shop's name", "Dein Name oder der deines Shops"),
    ("Dinos cómo te llamas o cómo se llama tu tienda.", "Tell us your name or your shop's name.", "Sag uns deinen Namen oder den deines Shops."),
    (">Correo electrónico<", ">E-mail<", ">E-Mail<"),
    ('placeholder="tu@correo.es"', 'placeholder="you@email.com"', 'placeholder="du@beispiel.de"'),
    ("Revisa el correo, parece que falta algo.", "Check your e-mail address, something seems to be missing.", "Prüfe deine E-Mail-Adresse, da scheint etwas zu fehlen."),
    ("Tu perfil de Wallapop", "Your Wallapop profile", "Dein Wallapop-Profil"),
    ('placeholder="Enlace o nombre de tu perfil"', 'placeholder="Link or name of your profile"', 'placeholder="Link oder Name deines Profils"'),
    ("En la app: Perfil › Compartir perfil › Copiar enlace.", "In the app: Profile › Share profile › Copy link.", "In der App: Profil › Profil teilen › Link kopieren."),
    ("Pega el enlace o escribe el nombre de tu perfil.", "Paste the link or type your profile name.", "Füge den Link ein oder schreib deinen Profilnamen."),
    (">Elige una opción<", ">Choose an option<", ">Bitte wählen<"),
    (">Hasta 50<", ">Up to 50<", ">Bis 50<"),
    (">De 51 a 150<", ">51 to 150<", ">51 bis 150<"),
    (">De 151 a 400<", ">151 to 400<", ">151 bis 400<"),
    (">De 401 a 1.000<", ">401 to 1,000<", ">401 bis 1.000<"),
    (">Más de 1.000<", ">More than 1,000<", ">Mehr als 1.000<"),
    ("(opcional)", "(optional)", "(optional)"),
    ("Revisa el número: 9 cifras.", "Check the number: 9 digits.", "Prüfe die Nummer: 9 Ziffern."),
    ("No rellenes este campo", "Leave this field empty", "Dieses Feld leer lassen"),
    ("Quiero recibir novedades de BuhoStock por correo. Te pediremos que lo confirmes y puedes darte de baja cuando quieras.",
     "I'd like to receive BuhoStock news by e-mail. We'll ask you to confirm, and you can unsubscribe at any time.",
     "Ich möchte Neuigkeiten von BuhoStock per E-Mail erhalten. Wir bitten dich um eine Bestätigung, abmelden kannst du dich jederzeit."),
    ('He leído y acepto las <a href="condiciones.html" target="_blank" rel="noopener">condiciones de uso</a> y la <a href="privacidad.html" target="_blank" rel="noopener">política de privacidad</a>.',
     'I have read and accept the <a href="condiciones.html" target="_blank" rel="noopener">terms of use</a> and the <a href="privacidad.html" target="_blank" rel="noopener">privacy policy</a>.',
     'Ich habe die <a href="condiciones.html" target="_blank" rel="noopener">Nutzungsbedingungen</a> und die <a href="privacidad.html" target="_blank" rel="noopener">Datenschutzerklärung</a> gelesen und akzeptiere sie.'),
    (">Quiero probarlo gratis<", ">Try it for free<", ">Gratis testen<"),
    ("¡Recibido!", "Got it!", "Angekommen!"),
    ("Te escribimos en menos de 48 horas (días laborables) para ponerlo en marcha contigo.",
     "We'll write to you within 48 hours (working days) to set it up with you.",
     "Wir melden uns innerhalb von 48 Stunden (Werktage), um es mit dir einzurichten."),
    ("Te hemos enviado también un correo para confirmar que quieres recibir novedades.",
     "We've also sent you an e-mail to confirm that you want to receive news.",
     "Wir haben dir außerdem eine E-Mail geschickt, um zu bestätigen, dass du Neuigkeiten erhalten möchtest."),
    ("Sin JavaScript el formulario no funciona. Escríbenos a buhostock.team@gmail.com y te contestamos.",
     "The form needs JavaScript. Write to us at buhostock.team@gmail.com and we'll reply.",
     "Ohne JavaScript funktioniert das Formular nicht. Schreib uns an buhostock.team@gmail.com, wir antworten dir."),
]

LEGAL_NOTE = (
    "Version of 23 October 2026 · This translation is for information only; the Spanish version is binding.",
    "Fassung vom 23. Oktober 2026 · Diese Übersetzung dient nur zur Information; verbindlich ist die spanische Fassung.",
)

CONDICIONES: list[tuple[str, str, str]] = [
    ("Condiciones de uso · BuhoStock", "Terms of use · BuhoStock", "Nutzungsbedingungen · BuhoStock"),
    ("Condiciones de uso de BuhoStock: prueba gratuita, planes, uso en tu cuenta de Wallapop y cancelación.",
     "BuhoStock terms of use: free trial, plans, use on your Wallapop account and cancellation.",
     "Nutzungsbedingungen von BuhoStock: Gratis-Test, Pläne, Nutzung auf deinem Wallapop-Konto und Kündigung."),
    ("Versión del 23 de octubre de 2026", *LEGAL_NOTE),
    ("1. Qué es BuhoStock", "1. What BuhoStock is", "1. Was BuhoStock ist"),
    ("BuhoStock es una herramienta que gestiona tus anuncios de Wallapop por la noche: vuelve a subir los que llevan tiempo quietos, baja poco a poco el precio de lo que no se vende sin pasar nunca del mínimo que tú fijas, y te envía cada mañana un informe. Funciona desde tu propio equipo (programa para Windows) o desde una Búho-Box conectada a tu router.",
     "BuhoStock is a tool that manages your Wallapop listings at night: it relists the ones that have been still for a while, gradually lowers the price of what isn't selling without ever going past the minimum you set, and sends you a report every morning. It runs from your own computer (Windows program) or from a Búho-Box connected to your router.",
     "BuhoStock ist ein Werkzeug, das deine Wallapop-Anzeigen nachts verwaltet: Es stellt länger unbewegte Anzeigen neu ein, senkt nach und nach den Preis von dem, was sich nicht verkauft, ohne je unter deinen Mindestpreis zu gehen, und schickt dir jeden Morgen einen Bericht. Es läuft auf deinem eigenen Computer (Windows-Programm) oder auf einer Búho-Box an deinem Router."),
    ("2. Prueba gratuita", "2. Free trial", "2. Gratis-Test"),
    ("Los primeros 30 días son gratis. No te pedimos tarjeta ni datos de pago para empezar. Al terminar la prueba eliges un plan o el servicio se detiene; no te cobramos nada sin preguntarte antes.",
     "The first 30 days are free. We don't ask for a card or payment details to get started. When the trial ends you choose a plan or the service stops; we never charge you without asking first.",
     "Die ersten 30 Tage sind gratis. Zum Start brauchen wir keine Kreditkarte und keine Zahlungsdaten. Nach dem Test wählst du einen Plan oder der Dienst endet; wir berechnen nichts, ohne dich vorher zu fragen."),
    ("3. Planes y precios", "3. Plans and prices", "3. Pläne und Preise"),
    ("El precio depende del número de anuncios: Mini (hasta 50) 29 €/mes, Starter (hasta 150) 49 €/mes, Pro (hasta 400) 89 €/mes y Business (hasta 1.000) 149 €/mes. Para más de 1.000 anuncios hacemos una oferta a medida. Con el pago anual tienes 2 meses gratis. El precio con el que empiezas se mantiene mientras sigas con nosotros.",
     "The price depends on the number of listings: Mini (up to 50) 29 €/month, Starter (up to 150) 49 €/month, Pro (up to 400) 89 €/month and Business (up to 1,000) 149 €/month. For more than 1,000 listings we make a custom offer. With yearly payment you get 2 months free. The price you start with stays as long as you stay with us.",
     "Der Preis hängt von der Anzahl der Anzeigen ab: Mini (bis 50) 29 €/Monat, Starter (bis 150) 49 €/Monat, Pro (bis 400) 89 €/Monat und Business (bis 1.000) 149 €/Monat. Für mehr als 1.000 Anzeigen machen wir ein individuelles Angebot. Bei Jahreszahlung bekommst du 2 Monate gratis. Dein Startpreis bleibt, solange du bei uns bist."),
    ("La Búho-Box cuesta 15 €/mes adicionales, está disponible desde el plan Starter y tiene una duración mínima de 6 meses. El aparato sigue siendo propiedad de BuhoStock y nos lo devuelves cuando termines el servicio.",
     "The Búho-Box costs an extra 15 €/month, is available from the Starter plan and has a minimum term of 6 months. The device remains the property of BuhoStock and you return it when you end the service.",
     "Die Búho-Box kostet zusätzlich 15 €/Monat, ist ab dem Starter-Plan erhältlich und hat eine Mindestlaufzeit von 6 Monaten. Das Gerät bleibt Eigentum von BuhoStock und geht bei Vertragsende an uns zurück."),
    ("4. Uso de BuhoStock en tu cuenta de Wallapop", "4. Using BuhoStock on your Wallapop account", "4. Nutzung von BuhoStock auf deinem Wallapop-Konto"),
    ("BuhoStock es una herramienta externa que gestiona tus anuncios en tu nombre, desde tu propio equipo y tu propia conexión, a ritmo humano y siempre respetando el precio mínimo que tú fijas. Wallapop no autoriza oficialmente el uso de herramientas externas en su plataforma y puede aplicar sus propias normas a las cuentas que las usan. Al darte de alta confirmas que conoces esta circunstancia y que decides usar BuhoStock bajo tu propia responsabilidad. BuhoStock no garantiza resultados de venta concretos ni que la plataforma no tome medidas sobre tu cuenta; si detectamos cualquier aviso de la plataforma, pausamos el servicio en tu cuenta y te informamos de inmediato. Puedes pausar o cancelar el servicio en cualquier momento.",
     "BuhoStock is an external tool that manages your listings on your behalf, from your own computer and your own connection, at a human pace and always respecting the minimum price you set. Wallapop does not officially authorise the use of external tools on its platform and may apply its own rules to accounts that use them. By signing up you confirm that you are aware of this and that you choose to use BuhoStock at your own risk. BuhoStock does not guarantee specific sales results, nor that the platform will not take action on your account; if we detect any warning from the platform, we pause the service on your account and inform you immediately. You can pause or cancel the service at any time.",
     "BuhoStock ist ein externes Werkzeug, das deine Anzeigen in deinem Namen verwaltet – von deinem eigenen Computer und deiner eigenen Verbindung aus, in menschlichem Tempo und immer unter Beachtung deines Mindestpreises. Wallapop erlaubt die Nutzung externer Werkzeuge auf seiner Plattform nicht offiziell und kann eigene Regeln auf Konten anwenden, die solche nutzen. Mit deiner Anmeldung bestätigst du, dass du das weißt und BuhoStock auf eigene Verantwortung nutzt. BuhoStock garantiert weder bestimmte Verkaufsergebnisse noch, dass die Plattform keine Maßnahmen gegen dein Konto ergreift; bemerken wir einen Hinweis der Plattform, pausieren wir den Dienst auf deinem Konto und informieren dich sofort. Du kannst den Dienst jederzeit pausieren oder kündigen."),
    ("5. Lo que te pedimos", "5. What we ask of you", "5. Was wir von dir erwarten"),
    ("Usar BuhoStock solo con tu propia cuenta o con una cuenta que tengas permiso para gestionar.",
     "Use BuhoStock only with your own account or an account you are allowed to manage.",
     "BuhoStock nur mit deinem eigenen Konto oder einem Konto nutzen, das du verwalten darfst."),
    ("Fijar tú los precios mínimos y revisarlos cuando cambie tu stock.",
     "Set the minimum prices yourself and review them when your stock changes.",
     "Die Mindestpreise selbst festlegen und prüfen, wenn sich dein Bestand ändert."),
    ("Que tus anuncios cumplan la ley y las normas de la plataforma en cuanto a su contenido.",
     "Make sure the content of your listings complies with the law and the platform's rules.",
     "Dafür sorgen, dass der Inhalt deiner Anzeigen dem Gesetz und den Regeln der Plattform entspricht."),
    ("No intentar copiar, revender o manipular el programa.",
     "Not try to copy, resell or tamper with the program.",
     "Das Programm nicht kopieren, weiterverkaufen oder manipulieren."),
    ("6. Resultados", "6. Results", "6. Ergebnisse"),
    ("Las cifras que mostramos en la web salen de nuestras propias cuentas. Cada tienda es distinta, por eso no prometemos ventas ni resultados concretos.",
     "The figures we show on the website come from our own accounts. Every shop is different, so we do not promise specific sales or results.",
     "Die Zahlen auf der Website stammen aus unseren eigenen Konten. Jeder Shop ist anders, deshalb versprechen wir keine bestimmten Verkäufe oder Ergebnisse."),
    ("7. Responsabilidad", "7. Liability", "7. Haftung"),
    ("Trabajamos con cuidado para que BuhoStock funcione cada noche, pero puede haber interrupciones, por ejemplo cuando la plataforma cambia su web. En ese caso te avisamos y lo corregimos lo antes posible. En la medida en que la ley lo permita, nuestra responsabilidad se limita a lo que nos hayas pagado en los últimos 12 meses.",
     "We work carefully so that BuhoStock runs every night, but interruptions can happen, for example when the platform changes its website. In that case we let you know and fix it as soon as possible. To the extent permitted by law, our liability is limited to what you have paid us in the last 12 months.",
     "Wir arbeiten sorgfältig, damit BuhoStock jede Nacht läuft, aber es kann Unterbrechungen geben, etwa wenn die Plattform ihre Website ändert. Dann sagen wir dir Bescheid und beheben es so schnell wie möglich. Soweit gesetzlich zulässig, ist unsere Haftung auf das begrenzt, was du uns in den letzten 12 Monaten bezahlt hast."),
    ("8. Pausa y cancelación", "8. Pausing and cancelling", "8. Pausieren und Kündigen"),
    ("Puedes pausar o cancelar el servicio cuando quieras, sin permanencia, escribiéndonos por correo. La cancelación vale para el siguiente periodo de pago; lo ya pagado no se devuelve, salvo que la ley diga otra cosa.",
     "You can pause or cancel the service whenever you want, with no minimum term, by e-mailing us. Cancellation applies from the next billing period; amounts already paid are not refunded unless the law says otherwise.",
     "Du kannst den Dienst jederzeit ohne Mindestlaufzeit per E-Mail pausieren oder kündigen. Die Kündigung gilt ab dem nächsten Abrechnungszeitraum; bereits Bezahltes wird nicht erstattet, sofern das Gesetz nichts anderes vorsieht."),
    ("9. Datos personales", "9. Personal data", "9. Personenbezogene Daten"),
    ('Cómo tratamos tus datos lo explicamos en la <a href="privacidad.html">política de privacidad</a>.',
     'How we handle your data is explained in the <a href="privacidad.html">privacy policy</a>.',
     'Wie wir mit deinen Daten umgehen, steht in der <a href="privacidad.html">Datenschutzerklärung</a>.'),
    ("10. Cambios", "10. Changes", "10. Änderungen"),
    ("Si cambiamos estas condiciones te avisamos por correo antes de que se apliquen. Si no estás de acuerdo, puedes cancelar.",
     "If we change these terms we will tell you by e-mail before they apply. If you don't agree, you can cancel.",
     "Ändern wir diese Bedingungen, informieren wir dich per E-Mail, bevor sie gelten. Bist du nicht einverstanden, kannst du kündigen."),
    ("11. Contacto", "11. Contact", "11. Kontakt"),
    ("Para cualquier duda:", "For any questions:", "Bei Fragen:"),
]

PRIVACIDAD: list[tuple[str, str, str]] = [
    ("Política de privacidad · BuhoStock", "Privacy policy · BuhoStock", "Datenschutzerklärung · BuhoStock"),
    ("Qué datos recoge BuhoStock, para qué los usa y cuáles son tus derechos.",
     "What data BuhoStock collects, what it uses it for and what your rights are.",
     "Welche Daten BuhoStock erhebt, wofür es sie nutzt und welche Rechte du hast."),
    ("<h1>Política de privacidad</h1>", "<h1>Privacy policy</h1>", "<h1>Datenschutzerklärung</h1>"),
    ("Versión del 23 de octubre de 2026", *LEGAL_NOTE),
    ("1. Quién trata tus datos", "1. Who processes your data", "1. Wer deine Daten verarbeitet"),
    ("BuhoStock. Puedes escribirnos para cualquier asunto de privacidad a",
     "BuhoStock. You can write to us about any privacy matter at",
     "BuhoStock. Für alle Datenschutzfragen erreichst du uns unter"),
    ("2. Qué datos recogemos", "2. What data we collect", "2. Welche Daten wir erheben"),
    ("Solo los que nos das en el formulario «Pruébalo 30 días gratis»: tu nombre o el de tu tienda, tu correo, tu perfil de Wallapop, el número aproximado de anuncios y, si quieres, tu WhatsApp. Guardamos también la fecha del alta y la versión de las condiciones que aceptaste.",
     "Only what you give us in the “Try it free for 30 days” form: your name or your shop's name, your e-mail, your Wallapop profile, the approximate number of listings and, if you like, your WhatsApp. We also store the date of sign-up and the version of the terms you accepted.",
     "Nur die Angaben aus dem Formular „30 Tage gratis testen“: deinen Namen oder den deines Shops, deine E-Mail, dein Wallapop-Profil, die ungefähre Anzahl deiner Anzeigen und, wenn du willst, deine WhatsApp-Nummer. Außerdem speichern wir das Anmeldedatum und die Version der akzeptierten Bedingungen."),
    ("Esta web no usa cookies, ni herramientas de analítica, ni publicidad. Las fuentes tipográficas están alojadas en nuestro propio servidor.",
     "This website uses no cookies, no analytics tools and no advertising. The fonts are hosted on our own server.",
     "Diese Website verwendet keine Cookies, keine Analyse-Werkzeuge und keine Werbung. Die Schriften liegen auf unserem eigenen Server."),
    ("3. Para qué los usamos", "3. What we use it for", "3. Wofür wir sie nutzen"),
    ("<strong>Ponernos en contacto contigo y preparar tu prueba gratuita.</strong> Base: tu solicitud, como paso previo a un posible contrato (art. 6.1.b RGPD).",
     "<strong>To contact you and prepare your free trial.</strong> Legal basis: your request, as a step prior to a possible contract (Art. 6(1)(b) GDPR).",
     "<strong>Um dich zu kontaktieren und deinen Gratis-Test vorzubereiten.</strong> Rechtsgrundlage: deine Anfrage als Schritt vor einem möglichen Vertrag (Art. 6 Abs. 1 lit. b DSGVO)."),
    ("<strong>Enviarte novedades de BuhoStock por correo</strong>, solo si marcas la casilla y lo confirmas en el correo que te enviamos (doble confirmación). Base: tu consentimiento (art. 6.1.a RGPD y art. 21 LSSI-CE). Puedes darte de baja en cualquier momento.",
     "<strong>To send you BuhoStock news by e-mail</strong>, only if you tick the box and confirm it in the e-mail we send you (double opt-in). Legal basis: your consent (Art. 6(1)(a) GDPR and Art. 21 LSSI-CE). You can unsubscribe at any time.",
     "<strong>Um dir Neuigkeiten von BuhoStock per E-Mail zu schicken</strong> – nur wenn du das Kästchen ankreuzt und es in der E-Mail bestätigst, die wir dir senden (Double-Opt-in). Rechtsgrundlage: deine Einwilligung (Art. 6 Abs. 1 lit. a DSGVO und Art. 21 LSSI-CE). Du kannst dich jederzeit abmelden."),
    ("No vendemos tus datos ni los usamos para otra cosa.", "We do not sell your data or use it for anything else.", "Wir verkaufen deine Daten nicht und nutzen sie für nichts anderes."),
    ("4. Cuánto tiempo los guardamos", "4. How long we keep it", "4. Wie lange wir sie speichern"),
    ("Si no llegas a ser cliente, borramos tus datos a los 12 meses de tu alta. Los datos para novedades, hasta que te des de baja. Si te haces cliente, mientras dure el servicio y después durante los plazos que exija la ley.",
     "If you don't become a customer, we delete your data 12 months after signing up. Data for news is kept until you unsubscribe. If you become a customer, for as long as the service lasts and afterwards for the periods required by law.",
     "Wirst du kein Kunde, löschen wir deine Daten 12 Monate nach der Anmeldung. Daten für Neuigkeiten bis zu deiner Abmeldung. Wirst du Kunde, solange der Dienst läuft und danach für die gesetzlich vorgeschriebenen Fristen."),
    ("5. Quién más los ve", "5. Who else sees it", "5. Wer sie sonst sieht"),
    ("Usamos estos proveedores, que tratan los datos por encargo nuestro:",
     "We use these providers, who process data on our behalf:",
     "Wir nutzen diese Dienstleister, die Daten in unserem Auftrag verarbeiten:"),
    ("(formulario, hoja de cálculo y correo electrónico).", "(form, spreadsheet and e-mail).", "(Formular, Tabelle und E-Mail)."),
    ("(alojamiento de esta web; registra datos técnicos como la dirección IP para poder servir las páginas).",
     "(hosting of this website; it logs technical data such as the IP address in order to serve the pages).",
     "(Hosting dieser Website; protokolliert technische Daten wie die IP-Adresse, um die Seiten auszuliefern)."),
    ("Ambos pueden tratar datos fuera de la UE, en Estados Unidos, al amparo del Marco de Privacidad de Datos UE-EE. UU. y de las cláusulas contractuales tipo de la Comisión Europea.",
     "Both may process data outside the EU, in the United States, under the EU-US Data Privacy Framework and the European Commission's standard contractual clauses.",
     "Beide können Daten außerhalb der EU, in den USA, verarbeiten – auf Grundlage des EU-US-Datenschutzrahmens und der Standardvertragsklauseln der EU-Kommission."),
    ("6. Tus derechos", "6. Your rights", "6. Deine Rechte"),
    ("Puedes pedirnos acceso, rectificación, supresión, oposición, limitación y portabilidad de tus datos, y retirar tu consentimiento cuando quieras, escribiendo a",
     "You can ask us for access, rectification, erasure, objection, restriction and portability of your data, and withdraw your consent at any time, by writing to",
     "Du kannst Auskunft, Berichtigung, Löschung, Widerspruch, Einschränkung und Übertragbarkeit deiner Daten verlangen und deine Einwilligung jederzeit widerrufen – schreib an"),
    (". Te contestamos en un mes como máximo.", ". We will reply within one month at most.", ". Wir antworten spätestens innerhalb eines Monats."),
    ("Si crees que no hemos atendido bien tu petición, puedes reclamar ante la Agencia Española de Protección de Datos",
     "If you think we have not handled your request properly, you can complain to the Spanish Data Protection Agency",
     "Wenn du meinst, dass wir deine Anfrage nicht richtig bearbeitet haben, kannst du dich bei der spanischen Datenschutzbehörde beschweren"),
    ("7. Cambios", "7. Changes", "7. Änderungen"),
    ("Si cambiamos esta política, publicamos aquí la nueva versión con su fecha.",
     "If we change this policy, we publish the new version here with its date.",
     "Ändern wir diese Erklärung, veröffentlichen wir hier die neue Fassung mit Datum."),
]

TABLES = {"index.html": SHARED + INDEX, "condiciones.html": SHARED + CONDICIONES, "privacidad.html": SHARED + PRIVACIDAD}


def language_switch(page: str, current: str, nav_label: str) -> str:
    """Language links as seen from a page inside en/ or de/."""
    links = []
    for code in ["es", "en", "de"]:
        href = f"../{page}" if code == "es" else (page if code == current else f"../{code}/{page}")
        mark = ' aria-current="true"' if code == current else ""
        links.append(f'<a href="{href}" hreflang="{code}" lang="{code}"{mark}>{code.upper()}</a>')
    return f'<nav class="lang" aria-label="{nav_label}">' + "".join(links) + "</nav>"


def translate(page: str, html: str, column: int) -> tuple[str, list[str]]:
    """Swap Spanish texts for column 1 (en) or 2 (de); return html + texts not found."""
    missing = []
    for row in TABLES[page]:
        spanish, target = row[0], row[column]
        if spanish not in html:
            if row not in SHARED:
                missing.append(spanish[:80])
            continue
        html = html.replace(spanish, target)
    return html, missing


def build_page(page: str, code: str) -> list[str]:
    """Write <code>/<page>; returns the list of untranslated texts."""
    settings = LANGS[code]
    html = (ROOT / page).read_text(encoding="utf-8")
    html, missing = translate(page, html, 1 if code == "en" else 2)
    html = html.replace('<html lang="es">', f'<html lang="{code}">', 1)
    html = html.replace('content="es_ES"', f'content="{settings["locale"]}"')
    html = html.replace('href="assets/', 'href="../assets/').replace('src="assets/', 'src="../assets/')
    html = re.sub(r'<nav class="lang".*?</nav>', language_switch(page, code, settings["nav"]), html, count=1, flags=re.S)
    target = ROOT / code / page
    target.parent.mkdir(exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return missing


def main() -> int:
    """Build all pages; exit code 1 if any Spanish text had no translation."""
    problems = []
    for code in LANGS:
        for page in PAGES:
            problems += [f"{code}/{page}: {text}" for text in build_page(page, code)]
    if problems:
        print("missing translations (Spanish text changed?):")
        print("\n".join(problems))
        return 1
    print("built:", ", ".join(f"{code}/{page}" for code in LANGS for page in PAGES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
