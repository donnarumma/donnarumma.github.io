# Website Migration

Prima importazione: 2026-09-14. Aggiornamento: 2026-09-15.
Proprietario dei CV e del sito: **Francesco Donnarumma**.

## Stato

- Repository clonato in `CurriculumVitae/Website`, da `donnarumma/donnarumma.github.io`.
- Versione locale costruita e separata dal Git del CV.
- Prima versione completa caricata il 2026-09-15, commit `8c65efd`.
- GitHub Pages era gia' abilitato: il deploy automatico esistente ha pubblicato
  questa versione su `https://donnarumma.github.io/` dopo il push.
- Nessuna modifica a Google Sites, impostazioni Pages, dominio, redirect o DNS.
- Workflow alternativo di pubblicazione preparato con avvio manuale, non eseguito.
- Indicizzazione disabilitata nella copia locale/staging (`allow_indexing: false`).

## Rifiniture Del 2026-09-15

- Il riquadro testuale OpenAlex e' sostituito dal simbolo bianco originale in PNG
  a 526 x 526 pixel, scaricato dal repository ufficiale. L'icona occupa 62 pixel
  su desktop e 40 su mobile, dentro gli stessi spazi della barra dei profili.
  Fonte e hash in [assets.json](assets.json).
- Copiato nuovamente `DONNARUMMA_CV.pdf`, ultima compilazione disponibile del
  2026-09-09. Il confronto SHA-256 conferma che il PDF gia' presente era identico;
  aggiornato il registro [cv-snapshot.json](cv-snapshot.json). Non e' stata avviata
  una nuova compilazione o modificato il CV canonico.
- Caricamento dei file nel solo repository Website, senza avviare manualmente
  il workflow alternativo e senza modificare dominio, Google Sites o repository
  del CV. Il deploy automatico preesistente e' terminato con successo:
  [esecuzione GitHub](https://github.com/donnarumma/donnarumma.github.io/actions/runs/34953271002).

## Copertura

| Sorgente pubblica | Pagina locale | Contenuti conservati |
| --- | --- | --- |
| [/](https://www.francescodonnarumma.net/) e [/home](https://www.francescodonnarumma.net/home) | `index.html`, `home/index.html` | Nome in GIF animate, Angel, quattro video, 16 highlights. |
| [/research](https://www.francescodonnarumma.net/research) | `research/index.html` | Ritratto, presentazione e interessi scientifici. |
| [/papers](https://www.francescodonnarumma.net/papers) | `papers/index.html` | Tutte le 70 voci e il loro ordine, dal 2026 al 2006; download CV/BibTeX. |
| [/personal](https://www.francescodonnarumma.net/personal) | `personal/index.html` | Tutte le tre immagini e la didascalia storica della mappa citazionale. |
| [/contacts](https://www.francescodonnarumma.net/contacts) | `contacts/index.html` | Percorso mantenuto; contatti resi utilizzabili come indicato sotto. |
| [/researchmore](https://www.francescodonnarumma.net/researchmore) | `researchmore/index.html` | Progetti, metodi, lavori citati e attivita' didattica storica. |

Sono 70 **voci bibliografiche del sito**, non 70 articoli di rivista: comprendono
anche tesi, interventi e conferenze. Il conteggio non va equiparato a quello del
CV o di Scholar/OpenAlex. Nessuna voce eliminata perche' assente dal BibTeX.

## Adattamenti Espliciti

- Grafica ricostruita in HTML/CSS leggibile, mantenendo immagini, lettere animate,
  colori di riferimento e font Lato/Pacifico. Non e' un'esportazione del codice
  proprietario Google Sites e non pretende di essere identica pixel per pixel.
- 36 asset distinti conservati nei formati originali. Deduplicati solo file con
  lo stesso SHA-256; GIF ancora animate. La fascia fotografica e' 2560 x 1707.
  Angel e lo sfondo disponibili dal sito sono 333 x 447: nessun ingrandimento
  artificiale presentato come originale ad alta risoluzione.
- Barra dei profili unificata fra pagine. Aggiunto OpenAlex dal registro del CV;
  WSocial, Substack e Instagram compaiono tra i contatti. X e LinkedIn restano
  consultabili in "Archived profiles", coerentemente con il README del CV.
- La pagina Contacts originale contieneva solo il titolo e lo sfondo. Inseriti
  nome, istituzione, citta' ed email ISTC gia' nel CV. Non pubblicati PEC, indirizzi
  personali o informazioni su un'altra persona.
- Quattro video conservati con miniature locali e link a YouTube. Gli iframe
  YouTube, Twitter e SnapWidget sono sostituiti da collegamenti espliciti: nessun
  tracker/cookie banner Google o feed caricato automaticamente. I contenuti
  esterni non diventano disponibili offline.
- Ricerca interna e filtro per anno/testo aggiunti senza servizi esterni.
- CV e BibTeX disponibili localmente come copie dei file canonici. La data e gli
  hash sono in [cv-snapshot.json](cv-snapshot.json). Il PDF contiene gli stessi
  dati del CV canonico: rivederne la pubblicabilita' prima del primo deploy.
- Le vecchie etichette `[pdf]` / `[bib]` prive di link non vengono mostrate come
  risorse disponibili. I link effettivi sono mantenuti, anche se alcuni esterni
  richiederanno un controllo successivo.
- Riuniti i due titoli degli highlights che nel Google Site erano spezzati in
  paragrafi consecutivi. Nessuna parola o pubblicazione persa nel passaggio.

## Correzioni Documentate

Fonte per le correzioni bibliografiche: `CurriculumVitae/donnarumma.bib`, gia'
aggiornato nel lavoro sul CV; il file canonico non e' stato modificato qui.

| Voce | Intervento |
| --- | --- |
| Inferential planning in the frontal cortex | Da "Accepted" a Cell Reports 45 (9), 117905 (2026), DOI `10.1016/j.celrep.2026.117905`. Conservato il link bioRxiv. |
| Active Digital Twins via Active Inference | Tolto il punto finale erroneo dal link DOI e corretto "olume". Rimossi i collegamenti arXiv/OSF duplicati da PAM: `2411.13203` e' PAM, non Digital Twins. Il PDF dell'editore e il DOI restano. |
| From particles to collectives | Corretto il DOI nel testo: `10.1016/j.plrev.2023.12.009`, non quello di Interactive inference. |
| Programming in the Brain, in ResearchMore | Il segnaposto `#BAD_URL` ora porta al DOI gia' presente in bibliografia. |
| Mental imagery in the navigation domain | Corretto il prefisso DOI malformato `dx.doi.org/doi:...`. |
| A differential discrete particle swarm optimization approach... | Il vecchio hostname inesistente `donnarumma10differential.bib` rimanda ora al BibTeX complessivo locale, non a un file individuale inventato. |

## Da Rivedere Prima Del Passaggio

- Presentazione Research/ResearchMore e highlights sono intenzionalmente quelli
  storici: non includono automaticamente ogni progetto o articolo recente del CV.
- Alcune date del sito indicano pubblicazione online/preprint anziche' fascicolo
  finale: Interactive inference (2023/2024), From particles to collectives
  (2023/2024), survey Active Inference (2023/2024), PAM (preprint 2024 indicato
  nel sito fra le voci 2026). Conservato l'ordine esistente; armonizzazione da
  decidere con l'autore, non risolta silenziosamente durante la replica.
- Link storici verso editori, SharePoint, Filedn, vecchi servizi WoS/Scopus e
  siti di progetti possono essere scaduti, richiedere login o contenere parametri
  di sessione. La verifica offline non certifica il loro funzionamento.
- Le mappe in Personal sono documenti storici; la didascalia del 12/01/2021
  non e' stata presentata come una nuova rilevazione delle metriche.
- Rivedere l'aspetto locale, i download pubblicabili e l'eventuale aggiornamento
  della selezione in Home prima di sostituire il sito esistente.

## Pubblicazione E Dominio

Questa e' una procedura da eseguire **dopo approvazione**, non un'operazione gia'
effettuata. Non cambiare i record della posta elettronica.

1. Revisionare i file e fare commit/push nel repository `Website`, non nel Git
   del CV. La configurazione Pages esistente pubblica automaticamente gli
   aggiornamenti: verificare prima `https://donnarumma.github.io/`.
2. Per il passaggio definitivo, verificare la proprieta' del dominio su GitHub
   e configurare il custom domain nelle impostazioni Pages **prima** di cambiare
   i DNS. Per il sottodominio `www`, la destinazione CNAME e'
   `donnarumma.github.io`, senza percorso. Esaminare a parte il dominio senza
   `www`, conservando una copia dei record esistenti per il ripristino.
3. Aggiornare `public_url` in `content/settings.json` a
   `https://www.francescodonnarumma.net`, abilitare l'indicizzazione quando pronto,
   ricostruire e pubblicare. Verificare HTTPS, vecchi percorsi, CV e BibTeX.
4. Conservare temporaneamente il Google Site per confronto e possibile rollback.

Prima del cambio di dominio verificare la sorgente di pubblicazione nelle
impostazioni Pages. Se si pubblica da branch, il file `CNAME` aggiunto da GitHub
va conservato e sincronizzato; con un workflow Actions personalizzato non e'
necessario. Il dominio si configura nelle impostazioni Pages.
Riferimenti ufficiali consultati
il 2026-09-14: [workflow Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
e [gestione del dominio](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

## Comandi Principali Eseguiti

Clonazione, dalla cartella CurriculumVitae:

```bash
env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git clone https://github.com/donnarumma/donnarumma.github.io.git Website
```

La configurazione locale riscrive gli URL GitHub HTTPS in SSH, ma SSH incontra
un errore di permessi in un file di configurazione di sistema. La clonazione
HTTPS e' stata eseguita ignorando la configurazione **solo per quel comando**;
nessun file globale Git/SSH modificato e nessuna credenziale salvata.

Dalla cartella Website:

```bash
python3 tools/import_google_site.py --source-dir .local/browser-source
python3 tools/sync_cv.py
python3 tools/build.py
python3 tools/check.py
python3 tools/browser_check.py
```

Gli asset Google sono stati letti dalla cache di un Chromium dedicato, perche'
il download diretto restituiva 403. Sorgenti HTML e cache in `.local/`, esclusi
da Git; [assets.json](assets.json) conserva la provenienza dei file trasferiti.
Il workflow manuale predisposto non e' stato eseguito e non e' stato usato
`overpush`. Il deploy automatico Pages gia' esistente e' invece partito al push.

## Comandi Git Del 2026-09-15

Dalla cartella `Website`:

```bash
git -c core.sshCommand='ssh -F /home/donnarumma/.ssh/config -o BatchMode=yes' fetch origin
git add --all
git diff --cached --check
git commit -m "Add offline personal website with official OpenAlex logo and current CV"
git -c core.sshCommand='ssh -F /home/donnarumma/.ssh/config -o BatchMode=yes' push origin main
```

La configurazione SSH e' selezionata solo per i singoli comandi: viene usato
il file personale gia' esistente, evitando l'errore del file di sistema senza
modificarlo. Nessun force-push. `.local/` e `_site/` restano esclusi da Git.
