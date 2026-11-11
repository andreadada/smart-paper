# Folio · Smart Paper per D&D

Una lavagna per mappe da gioco di ruolo, disegnata come un foglio di carta infinito: griglia SVG, disegno vettoriale, pedine e sticker spostabili, importazione di mappe PNG/JPG, pannelli flottanti e salvataggio locale. **È un unico file HTML**, senza dipendenze JavaScript esterne o build step.

## Avvio

- Scarica `index.html` e aprilo in un browser moderno; non è necessario installare nulla.
- In alternativa, dalla cartella del repository esegui `python -m http.server 8000` e visita `http://localhost:8000`.
- Il salvataggio automatico usa IndexedDB, con fallback a localStorage. Le mappe possono essere esportate/importate tramite backup JSON. I dati salvati dal browser in `file://` e `http://localhost` possono essere separati: **esporta un backup prima di cambiare origine o browser**.

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
- Mappe multiple, rinomina, duplicazione, dimensioni personalizzabili.
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
```

I test sintetici verificano penna automatica, campioni di pressione, navigazione con un dito, pinch, gomma, disattivazione della modalità automatica, rifiuto del palmo durante la penna e assenza di errori JavaScript. Per verificare palm rejection, pressione e pulsanti hardware sul dispositivo reale è necessario provare su ciascuna combinazione dispositivo/browser.

## Riferimenti

- [Pointer Events – MDN](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events)
- [PointerEvent.pointerType – MDN](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent/pointerType)
- [PointerEvent.pressure – MDN](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent/pressure)
