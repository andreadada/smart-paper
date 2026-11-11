# Folio · Smart Paper per D&D

Una lavagna per mappe da gioco di ruolo, disegnata come un foglio di carta davvero infinito: griglia SVG senza bordi in tutte le direzioni, disegno vettoriale, pedine e sticker spostabili, importazione di mappe PNG/JPG, pannelli flottanti e salvataggio locale. **È un unico file HTML**, senza dipendenze JavaScript esterne o build step.

## Avvio

- Scarica `index.html` e aprilo in un browser moderno; non è necessario installare nulla.
- In alternativa, dalla cartella del repository esegui `python -m http.server 8000` e visita `http://localhost:8000`.
- Il salvataggio automatico usa IndexedDB, con fallback a localStorage. Le mappe possono essere esportate/importate tramite backup JSON. I dati salvati dal browser in `file://` e `http://localhost` possono essere separati: **esporta un backup prima di cambiare origine o browser**.

## Foglio infinito e controlli visuale

- **La griglia è illimitata:** muoviti liberamente in tutte le direzioni, anche oltre l'area iniziale e su coordinate negative. Puoi disegnare, cancellare e aggiungere pedine ovunque.
- **Pannello zoom temporaneo:** appare durante scorrimento/panoramica, zoom con rotella o pinch. Mostra l'ingrandimento corrente, pulsanti `−` e `+` e il pulsante **Torna al centro**; si richiude automaticamente dopo l'inattività e resta accessibile finché lo stai usando.
- **Torna al centro:** il pulsante a mirino (oppure il tasto `0`, quando non stai modificando un campo di testo) ripristina il livello al **100%** e centra l'area iniziale della mappa. Il pulsante in alto a destra **Inquadra l'area iniziale** mantiene invece la funzione di adattamento allo schermo.
- **Nome mappa modificabile:** nel riquadro superiore a sinistra; il vecchio logo è stato rimosso.
- **Compatibilità con i vecchi salvataggi:** le colonne/righe dei progetti esistenti identificano solo l'area PNG di riferimento, non i limiti del mondo. Le pedine fuori da quell'area vengono conservate. Quando non è presente un PNG, non serve configurare alcuna dimensione.
- **Esportazione PNG:** essendo il mondo infinito, il PNG esporta l'**inquadratura visibile al momento**, non l'intero mondo. Il backup JSON conserva invece tutti i tratti, oggetti e mappe, anche fuori dallo schermo.

## Stylus, dita e mouse

Il rilevamento della penna usa il **Pointer Events API** (`pointerType === 'pen'`), senza identificare marche o modelli. Quindi, quando il browser le presenta come penne, sono supportate Apple Pencil, Samsung S Pen, Xiaomi Smart Pen e altri dispositivi compatibili.

| Ingresso | Comportamento iniziale |
| --- | --- |
| **Stylus** | Disegna immediatamente sulla mappa anche con Selezione attiva |
| **Stylus con gomma / pulsante laterale** | Cancella tratti quando il browser espone il pulsante (button 5 / 2, buttons 32 / 2) |
| **Un dito** | Sposta la mappa; se lo strumento Selezione è attivo, può anche spostare una pedina |
| **Due dita** | Pinch-to-zoom e spostamento della mappa |
| **Mouse** | Usa lo strumento selezionato nella barra inferiore |

- **Stylus · auto** nella parte alta del foglio: premilo per passare da disegno automatico a modalità manuale. In modalità manuale la penna usa lo strumento selezionato, quindi può anche spostare pedine, immagini e sticker.
- Apri il menu **Foglio** e raggiungi **Stylus e tocco** per attivare/disattivare penna automatica e **sensibilità alla pressione**.
- I tratti della stylus, quando la pressione è attiva, vengono salvati con la pressione per campione e renderizzati in SVG con spessore variabile. I campioni coalescenti vengono letti tramite `getCoalescedEvents()` se disponibili.
- Il contatto del palmo viene ignorato mentre la stylus è appoggiata e per un breve intervallo dopo il sollevamento. Il palm rejection del sistema operativo resta importante e non può essere garantito interamente dal browser.

### Limiti e compatibilità

- Il riconoscimento dipende **dal browser e dall'hardware**: una penna capacitiva passiva può essere segnalata come `touch`, non `pen`.
- **Pressione, inclinazione, gomma e pulsanti** non sono disponibili su tutti i dispositivi. Il supporto alla gomma dipende dai valori Pointer Events riportati dal browser; non è garantito.
- Gesti proprietari come il **doppio tocco di Apple Pencil** non sono esposti in modo uniforme alle pagine web.
- Per mantenere l'app completamente offline e senza dipendenze, i tratti sensibili alla pressione sono renderizzati tramite un algoritmo SVG integrato, non tramite SDK proprietari o servizi remoti.

## Funzionalità

- Griglia vettoriale con zoom, panoramica, disegno a penna, evidenziatore e gomma.
- Mappe multiple e infinite, rinomina e duplicazione; dimensioni di riferimento personalizzabili per lo sfondo PNG.
- Pedine per PG, mostri e oggetti, trascinabili e agganciate alle caselle; caricamento di sticker personali.
- PNG/JPG come sfondo, opacità, scala, modalità di adattamento e spostamento dell'immagine.
- Menu mobili trascinabili, ancorabili e persistenti; modalità schermo intero.
- Salvataggio automatico in locale, annulla/ripristina, esportazione PNG e backup JSON.

## Verifiche

Per test interattivi (richiede Python e Playwright):

```bash
pip install playwright
playwright install chromium
python tests/test_stylus.py
python tests/test_infinite_canvas.py
```

I test sintetici verificano penna automatica, campioni di pressione, navigazione con un dito, pinch, gomma, disattivazione della modalità automatica e rifiuto del palmo. Controllano anche griglia infinita, disegno e pedine fuori dall’area iniziale, visualizzazione temporanea dello zoom, reset al centro, modifica del nome e assenza di errori JavaScript. Per verificare palm rejection, pressione e pulsanti hardware sul dispositivo reale è necessario provare su ciascuna combinazione dispositivo/browser.

## Riferimenti

- [Pointer Events – MDN](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events)
- [PointerEvent.pointerType – MDN](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent/pointerType)
- [PointerEvent.pressure – MDN](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent/pressure)

