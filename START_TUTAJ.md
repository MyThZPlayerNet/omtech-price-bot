# Monitor jest skonfigurowany i uruchomiony

Repozytorium: https://github.com/MyThZPlayerNet/omtech-price-bot

**Nie musisz ponownie dodawać plików ani sekretów.** Wszystkie 41 testów przeszło na GitHubie. Prawdziwy test Telegrama i pierwszy pomiar z zapisem historii zakończyły się sukcesem. Wskazany wariant kosztował **699,99 EUR** i był dostępny **1 listopada 2026 o 19:51 czasu polskiego**. Telegram potwierdził przyjęcie wiadomości testowej i inicjalizacyjnej.

- Historia: https://github.com/MyThZPlayerNet/omtech-price-bot/blob/main/data/price_history.csv
- Monitor: https://github.com/MyThZPlayerNet/omtech-price-bot/actions/workflows/check-price.yml
- Powiadomienia: **tylko po zmianie ceny**, o każdym spadku lub wzroście. Stała cena i sama dostępność pozostają bez wiadomości.
- Zatrzymanie: powyższa strona monitora → menu ⋯ → **Disable workflow**.
- Harmonogram: **co 10 minut**, w minutach 07, 17, 27, 37, 47 i 57 każdej godziny. Możliwe są opóźnienia GitHuba; pierwszego wyzwolenia schedule jeszcze nie obserwowano.

Poniższe kroki pozostawiono na potrzeby ponownej konfiguracji, np. po zmianie tokenu. Nie wykonuj ich ponownie bez potrzeby.

1. Otwórz https://t.me/BotFather, kliknij Start i wyślij `/newbot`. Podaj nazwę i unikalny username zakończony `bot`. BotFather pokaże token — nie wysyłaj go asystentowi.
2. Otwórz nowego bota przez link z BotFather i kliknij **Start**.
3. Pobierz i rozpakuj całą paczkę na komputerze. Kliknij dwukrotnie **KONFIGURUJ_TELEGRAM.cmd**, aby uzyskać Chat ID. Dokładnie opisuje to **punkt 5 w README.md**. Token wpisujesz lokalnie, w ukrytym polu PowerShell; pomocnik nie zapisuje go do pliku. Samo otwarcie README na GitHubie nie pobiera skryptów na komputer.
4. Otwórz https://github.com/MyThZPlayerNet/omtech-price-bot/settings/secrets/actions. Kliknij **New repository secret**. Dodaj osobno `TELEGRAM_BOT_TOKEN` (wartość skopiowana bezpośrednio z BotFather) i `TELEGRAM_CHAT_ID` (liczba z pomocnika).
5. Otwórz https://github.com/MyThZPlayerNet/omtech-price-bot/actions/workflows/check-price.yml. Kliknij **Run workflow**, wybierz **main**, **mode: test**, pozostaw alert_id puste i kliknij zielone **Run workflow**. Oczekiwany wynik: wiadomość testowa na Telegramie i zielony wynik w Actions.
6. Powtórz z **mode: check**. Powinien pojawić się pierwszy wiersz w `data/price_history.csv` i plik `data/store.json`. Pierwszy odczyt jest cichy; dopiero zmiana ceny powoduje wiadomość. Potem monitor działa z harmonogramu co 10 minut, z możliwymi opóźnieniami GitHuba.
7. Możesz też napisać asystentowi **„sekrety gotowe”**, bez ich wartości, aby dokończył ręczny test i pierwszy pomiar.

Progi **650 EUR** i **5% od poprzedniego odczytu** w `config.json` służą wyróżnianiu promocji w treści wiadomości. Zgodnie z późniejszą preferencją użytkownika każda rzeczywista zmiana ceny powoduje wiadomość; sama zmiana progów lub dostępności jej nie powoduje. Wiadomość inicjalizacyjna wymieniona wyżej została wysłana przez wcześniejszą wersję — nowe uruchomienia jej nie wysyłają.

**Repozytorium zostało utworzone jako Public.** Kod i przyszła historia są publiczne; wartości Secrets pozostają ukryte. Jeśli wolisz prywatne: Settings → General → Danger Zone → Change repository visibility → Private. Prywatne Actions korzystają z limitu bezpłatnej puli planu; nie włączaj płatnych przekroczeń.

Pełne instrukcje zmiany progu, oglądania historii, rozwiązywania błędów i zatrzymania monitora są w README.md. Raport z dowodami jest w RAPORT_TESTOW.md.
