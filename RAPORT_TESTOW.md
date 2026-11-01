# Raport weryfikacji — 1 listopada 2026

## Wykonane lokalnie

| Kontrola | Wynik |
|---|---|
| 39 testów logiki, plików, konfiguracji, API i obsługi błędów | **39/39 OK**, Python 3.12.14 |
| Walidacja obu workflow GitHub Actions | **OK**, actionlint 1.7.12, kod wyjścia 0 |
| Składnia pomocnika Telegram PowerShell | **OK**, parser PowerShell, bez wysyłania tokenu |
| Rzeczywisty odczyt gotowym skryptem | **OK**, 01.11.2026 19:34:18 czasu polskiego (18:34:18 UTC) |
| Cena i wariant | **699,99 EUR**, `43552694304950`, dostępny, „Maschine + 6 Acrylplatten geschenkt / Ohne LightBurn” |
| Dwa testy integracji Git w lokalnym Windows | **Nie zaliczone z powodu ograniczenia środowiska**, przed właściwym testem zapisu |
| Wysyłka do rzeczywistego Telegrama użytkownika | **Niewykonana**, brak skonfigurowanych sekretów |

Lokalne testy Git nie przeszły etapu utworzenia klona repozytorium testowego: Git for Windows nie mógł uruchomić procesu powłoki MSYS (`NtCreateDirectoryObject`, `0xC0000022`). Nie jest to wynik dowodzący poprawności ani błędu procedury push/rebase. Te same testy są dodane do workflow na Ubuntu; wynik online zostanie dopisany po uruchomieniu.

## Zakres 39 zaliczonych testów

Wybór dokładnego wariantu zamiast minimalnej ceny produktu; brak i duplikat wariantu; inna waluta i produkt; puste, zerowe, ujemne, tekstowe i niecałkowite ceny; dostępność znana i nieznana; inicjalizacja bez fałszywej promocji; dokładnie 5% i tuż poniżej; porównanie z poprzednią ceną zamiast maksimum historycznego; kolejne obniżki i ponowna promocja po wzroście; próg kwotowy i jego zmiana; brak ponowienia przy tej samej cenie; powrót dostępności; zapis każdego odczytu CSV; odrzucanie uszkodzonego stanu; zachowanie kolejki przy awarii; deduplikacja po restarcie; ręczne potwierdzanie niepewnej wysyłki; ograniczone ponawianie GET; 403 bez ponawiania; 429 z Retry-After; HTML zamiast JSON; nadmiarowy rozmiar odpowiedzi; przekierowanie; wspólna sesja waluty i produktu; brak sekretów przed pomiarem; ukrywanie tokenu w komunikacie błędu Telegrama.

Wywołania Telegrama w tych testach były **symulowane**. Nie wysłano wiadomości do prawdziwego konta.

## Dowody i odtworzenie

- `verification/unit-tests.txt` — pełny wynik 39 testów.
- `verification/git-integration.txt` — nieudana lokalna próba integracji Git, ścieżki domowe zanonimizowane.
- `verification/workflow-lint.txt` — puste wyjście oznacza brak błędów; kod wyjścia zapisano w results.json.
- `verification/live-fetch.json` i `.txt` — rzeczywisty odczyt API przez monitor.py, bez zapisu produkcyjnej historii.
- `verification/results.json` — kody wyjścia i identyfikacja poprzedniej paczki.

Do odtworzenia: `python -m unittest discover -s tests -v`, `python monitor.py --mode fetch`. W lokalnym środowisku Windows testy plikowe wykonano z TEMP/TMP skierowanymi do zapisywalnego folderu roboczego. Projekt nie wymaga instalowania pakietów pip.

## Stan wdrożenia

Repozytorium wskazane przez użytkownika: https://github.com/MyThZPlayerNet/omtech-price-bot (widoczność Public w momencie sprawdzenia). Projekt przygotowano do wgrania. Potwierdzenie wdrożenia i testów online zostanie uzupełnione po zakończeniu operacji.

Końcowa akceptacja działania wymaga: zielonego testu online, poprawnego odczytu z GitHuba, odebrania rzeczywistej wiadomości testowej, pierwszego `check` z zapisem danych i co najmniej jednej późniejszej kontroli wyzwolonej harmonogramem. Samo istnienie plików workflow tego nie dowodzi.
