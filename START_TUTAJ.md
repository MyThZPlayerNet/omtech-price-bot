# Projekt jest już wgrany — pozostała konfiguracja Telegrama

Repozytorium: https://github.com/MyThZPlayerNet/omtech-price-bot

**Nie musisz ponownie dodawać plików.** Wszystkie 41 testów przeszło na GitHubie. Sklep został sprawdzony z serwera GitHuba: wskazany wariant kosztował 699,99 EUR i był dostępny 1 listopada 2026 o 19:43 czasu polskiego.

1. Otwórz https://t.me/BotFather, kliknij Start i wyślij `/newbot`. Podaj nazwę i unikalny username zakończony `bot`. BotFather pokaże token — nie wysyłaj go asystentowi.
2. Otwórz nowego bota przez link z BotFather i kliknij **Start**.
3. Uzyskaj Chat ID pomocnikiem `scripts/telegram-chat-id.ps1`. Dokładnie opisuje to **punkt 5 w README.md**. Token wpisujesz lokalnie, w ukrytym polu PowerShell; pomocnik nie zapisuje go do pliku.
4. Otwórz https://github.com/MyThZPlayerNet/omtech-price-bot/settings/secrets/actions. Kliknij **New repository secret**. Dodaj osobno `TELEGRAM_BOT_TOKEN` (wartość skopiowana bezpośrednio z BotFather) i `TELEGRAM_CHAT_ID` (liczba z pomocnika).
5. Otwórz https://github.com/MyThZPlayerNet/omtech-price-bot/actions/workflows/check-price.yml. Kliknij **Run workflow**, wybierz **main**, **mode: test**, pozostaw alert_id puste i kliknij zielone **Run workflow**. Oczekiwany wynik: wiadomość testowa na Telegramie i zielony wynik w Actions.
6. Powtórz z **mode: check**. Powinien pojawić się pierwszy wiersz w `data/price_history.csv`, plik `data/store.json` i wiadomość z ceną. Potem monitor działa z harmonogramu co 2 godziny, z możliwymi opóźnieniami GitHuba.
7. Możesz też napisać asystentowi **„sekrety gotowe”**, bez ich wartości, aby dokończył ręczny test i pierwszy pomiar.

Cena alarmowa jest już ustawiona na **650 EUR** w `config.json`. Obniżka procentowa to **5% od poprzedniego poprawnego odczytu**. Przy obecnej cenie próg kwotowy nie jest osiągnięty.

**Repozytorium zostało utworzone jako Public.** Kod i przyszła historia są publiczne; wartości Secrets pozostają ukryte. Jeśli wolisz prywatne: Settings → General → Danger Zone → Change repository visibility → Private. Prywatne Actions korzystają z limitu bezpłatnej puli planu; nie włączaj płatnych przekroczeń.

Pełne instrukcje zmiany progu, oglądania historii, rozwiązywania błędów i zatrzymania monitora są w README.md. Raport z dowodami jest w RAPORT_TESTOW.md.
