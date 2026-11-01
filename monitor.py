#!/usr/bin/env python3
"""Exact-variant OMTech monitor. Python 3.12+, standard library only.

collect -> durable Git commit -> deliver -> durable Git commit.
The JSON store is authoritative; CSV is a readable projection of observations.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE = "https://de.omtech.com"
HANDLE = "k40-lasercutter-graviermaschine"
VARIANT_ID = "43552694304950"
PRODUCT_URL = f"{BASE}/products/{HANDLE}?variant={VARIANT_ID}"
ENDPOINT = f"{BASE}/products/{HANDLE}.js"
ROOT = Path(__file__).resolve().parent
MAX_BODY = 2_000_000


class MonitorError(Exception):
    """Safe message, without secrets or request URLs containing credentials."""


class DeliveryError(MonitorError):
    def __init__(self, message, *, uncertain=False):
        super().__init__(message)
        self.uncertain = uncertain


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def euro(cents):
    return f"{cents // 100},{cents % 100:02d} EUR"


def availability(value):
    return {True: "Dostępny", False: "Niedostępny", None: "Brak informacji"}[value]


def decimal_setting(value, name, *, maximum=None):
    if not isinstance(value, str) or not re.fullmatch(r"\d{1,7}([.,]\d{1,2})?", value):
        raise MonitorError(f"Niepoprawne ustawienie {name} (np. 650 lub 650.00).")
    number = Decimal(value.replace(",", "."))
    if number <= 0 or (maximum is not None and number > maximum):
        raise MonitorError(f"Ustawienie {name} poza dozwolonym zakresem.")
    return number


@dataclass(frozen=True)
class Config:
    drop: Decimal
    target: int | None

    @classmethod
    def load(cls, path):
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or set(obj) != {"price_drop_percent", "target_price_eur"}:
            raise MonitorError("config.json ma nieprawidłowe pola.")
        drop = decimal_setting(obj["price_drop_percent"], "price_drop_percent", maximum=100)
        raw = obj["target_price_eur"]
        target = None if raw in (None, "") else int(decimal_setting(raw, "target_price_eur") * 100)
        return cls(drop, target)


@dataclass(frozen=True)
class Offer:
    price_cents: int
    available: bool | None
    title: str
    variant_title: str


def parse_offer(payload, currency):
    if currency != "EUR":
        raise MonitorError("Nie potwierdzono waluty EUR; odczyt odrzucony.")
    if not isinstance(payload, dict) or payload.get("handle") != HANDLE:
        raise MonitorError("Nieprawidłowy produkt w odpowiedzi sklepu.")
    variants = payload.get("variants")
    if not isinstance(variants, list):
        raise MonitorError("Brak listy wariantów produktu.")
    matches = [v for v in variants if isinstance(v, dict) and str(v.get("id")) == VARIANT_ID]
    if len(matches) != 1:
        raise MonitorError(f"Brak jednoznacznego wariantu {VARIANT_ID}.")
    variant = matches[0]
    price = variant.get("price")
    # Ajax .js uses whole minor currency units. Never round malformed data.
    if type(price) is not int or price <= 0:
        raise MonitorError("Brak poprawnej dodatniej ceny w centach.")
    stock = variant.get("available")
    if stock is not None and type(stock) is not bool:
        raise MonitorError("Nieprawidłowy status dostępności.")
    return Offer(price, stock, str(payload.get("title", "OMTech K40")),
                 str(variant.get("title", "")))


def get_json(opener, url, *, sleep=time.sleep):
    """Retry transient GET failures only; never bypass access restrictions."""
    request = Request(url, headers={"Accept": "application/json",
        "User-Agent": "OMTechPersonalPriceMonitor/2.0", "Cache-Control": "no-cache"})
    for attempt in range(3):
        delay = 2 ** (attempt + 1)
        try:
            with opener.open(request, timeout=25) as response:
                final = urlsplit(response.geturl())
                if final.scheme != "https" or final.netloc != "de.omtech.com":
                    raise MonitorError("Sklep przekierował zapytanie poza oczekiwaną domenę.")
                raw = response.read(MAX_BODY + 1)
                if len(raw) > MAX_BODY:
                    raise MonitorError("Odpowiedź sklepu jest zbyt duża.")
                result = json.loads(raw)
                if not isinstance(result, dict):
                    raise MonitorError("Sklep nie zwrócił obiektu JSON.")
                return result
        except HTTPError as exc:
            code = exc.code
            retry_after = exc.headers.get("Retry-After", "") if exc.headers else ""
            exc.close()
            if code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise MonitorError(f"OMTech HTTP {code}; brak odczytu ceny.") from None
            if retry_after.isdigit():
                if int(retry_after) > 30:
                    raise MonitorError("OMTech prosi o dłuższą przerwę; spróbuję przy następnej kontroli.") from None
                delay = max(delay, int(retry_after))
        except (URLError, TimeoutError, OSError):
            if attempt == 2:
                raise MonitorError("Błąd sieci OMTech po 3 próbach.") from None
        except (ValueError, UnicodeError):
            raise MonitorError("OMTech nie zwrócił poprawnego JSON; brak odczytu ceny.") from None
        sleep(delay)
    raise AssertionError("unreachable")


def fetch_offer():
    # Both calls share cookies: currency confirmation applies to this session.
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    cart = get_json(opener, BASE + "/cart.js")
    if cart.get("currency") != "EUR":
        raise MonitorError("Waluta sesji sklepu różni się od EUR lub jej brakuje.")
    product = get_json(opener, ENDPOINT)
    return parse_offer(product, cart["currency"])


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as file:
        file.write(text)
        file.flush()
        os.fsync(file.fileno())
    temporary.replace(path)


def empty_store():
    return {"schema": 2, "variant_id": VARIANT_ID, "currency": "EUR",
            "observations": [], "outbox": []}


def load_store(directory):
    path = directory / "store.json"
    if not path.exists():
        if (directory / "price_history.csv").exists():
            raise MonitorError("Brak store.json przy istniejącej historii; przywróć dane z Git.")
        return empty_store()
    try:
        store = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(store, dict)
        assert store["schema"] == 2 and store["variant_id"] == VARIANT_ID and store["currency"] == "EUR"
        assert isinstance(store["observations"], list) and isinstance(store["outbox"], list)
        for i, row in enumerate(store["observations"], 1):
            assert row["id"] == i and type(row["price_cents"]) is int and row["price_cents"] > 0
            assert row["available"] is None or type(row["available"]) is bool
            assert type(row["target_cents"]) is int or row["target_cents"] is None
            datetime.fromisoformat(row["checked_at_utc"])
        ids = set()
        for event in store["outbox"]:
            assert event["id"] not in ids
            ids.add(event["id"])
            assert event["status"] in ("pending", "sent", "uncertain")
            assert isinstance(event["text"], str)
        return store
    except (ValueError, KeyError, TypeError, AssertionError):
        raise MonitorError("Uszkodzony lub niezgodny store.json; dane nie zostały wyzerowane.") from None


def save_store(directory, store):
    atomic_write(directory / "store.json", json.dumps(store, ensure_ascii=False, indent=2) + "\n")
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["checked_at_utc", "variant_id", "price_eur", "currency", "available"])
    for row in store["observations"]:
        price = row["price_cents"]
        writer.writerow([row["checked_at_utc"], VARIANT_ID,
            f"{price // 100}.{price % 100:02d}", "EUR",
            "unknown" if row["available"] is None else str(row["available"]).lower()])
    atomic_write(directory / "price_history.csv", output.getvalue())


def collect(directory, config, offer, *, timestamp=None):
    store = load_store(directory)
    previous = store["observations"][-1] if store["observations"] else None
    if type(offer.price_cents) is not int or offer.price_cents <= 0:
        raise MonitorError("Nieprawidłowa cena; nie zapisano odczytu.")
    stamp = timestamp or now_utc()
    reasons = []
    old_price = previous["price_cents"] if previous else None
    if old_price is not None:
        drop = Decimal(old_price - offer.price_cents) * 100 / old_price
        if offer.price_cents < old_price and drop >= config.drop:
            reasons.append(f"Obniżka: {drop:.1f}%".replace(".", ","))
    target_hit = config.target is not None and offer.price_cents <= config.target
    # A target alert re-arms after an above-target observation. Further lower prices
    # below target are new offers; unchanged price does not generate repeated alerts.
    target_new = target_hit and (previous is None or old_price > config.target
        or offer.price_cents < old_price or previous["target_cents"] != config.target
        or (previous["available"] is False and offer.available is True))
    if target_new:
        reasons.append(f"Cena alarmowa osiągnięta: {euro(config.target)} lub mniej")
    number = len(store["observations"]) + 1
    store["observations"].append({"id": number, "checked_at_utc": stamp,
        "price_cents": offer.price_cents, "available": offer.available,
        "target_cents": config.target})
    if reasons or previous is None:
        header = "🔥 PROMOCJA OMTECH K40!" if reasons else "✅ Monitoring OMTech K40 uruchomiony"
        lines = [header, f"Pomiar: {stamp}", f"Wariant: {VARIANT_ID}"]
        lines.append(f"Poprzednia cena: {euro(old_price)}" if old_price is not None else "Pierwszy poprawny odczyt — brak poprzedniej ceny.")
        lines += [f"Aktualna cena: {euro(offer.price_cents)}", *reasons,
                  f"Status: {availability(offer.available)}", PRODUCT_URL]
        text = "\n".join(lines)
        event_id = hashlib.sha256(f"{VARIANT_ID}:{number}:{text}".encode()).hexdigest()[:16]
        store["outbox"].append({"id": event_id, "status": "pending", "text": text + f"\nID alertu: {event_id}"})
    save_store(directory, store)
    return store


def credentials():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not re.fullmatch(r"\d+:[A-Za-z0-9_-]+", token) or not re.fullmatch(r"-?\d+", chat):
        raise MonitorError("Brak lub niepoprawne TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID w Secrets.")
    return token, chat


def telegram_send(text):
    token, chat = credentials()
    request = Request(f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat, "text": text,
                         "link_preview_options": {"is_disabled": True}}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with build_opener().open(request, timeout=25) as response:
            result = json.loads(response.read(MAX_BODY + 1))
        if not isinstance(result, dict) or result.get("ok") is not True:
            raise DeliveryError("Telegram odrzucił wiadomość.")
        message_id = result.get("result", {}).get("message_id")
        if type(message_id) is not int:
            raise DeliveryError("Telegram zwrócił niejednoznaczne potwierdzenie.", uncertain=True)
        return message_id
    except HTTPError as exc:
        code = exc.code
        exc.close()
        raise DeliveryError(f"Telegram HTTP {code}. Sprawdź token, chat ID i Start u bota.",
                            uncertain=code >= 500) from None
    except (URLError, OSError, TimeoutError, ValueError, AttributeError):
        # A POST timeout may occur AFTER delivery. Blind retries could duplicate it.
        raise DeliveryError("Nieznany wynik wysyłki Telegram; sprawdź czat przed ponowieniem.", uncertain=True) from None


def deliver(directory, *, sender=telegram_send, retry_uncertain=False):
    store = load_store(directory)
    if retry_uncertain:
        for event in store["outbox"]:
            if event["status"] == "uncertain":
                event["status"] = "pending"
    for event in store["outbox"]:
        if event["status"] != "pending":
            continue
        try:
            message_id = sender(event["text"])
        except DeliveryError as exc:
            if exc.uncertain:
                event["status"] = "uncertain"
            save_store(directory, store)
            raise
        event.update(status="sent", telegram_message_id=message_id, sent_at_utc=now_utc())
        save_store(directory, store)
    if any(e["status"] == "uncertain" for e in store["outbox"]):
        raise MonitorError("Pozostał alert o nieznanym wyniku wysyłki; przeczytaj instrukcję odzyskiwania.")


def acknowledge(directory, event_id):
    store = load_store(directory)
    matches = [e for e in store["outbox"] if e["id"] == event_id and e["status"] == "uncertain"]
    if len(matches) != 1:
        raise MonitorError("Podane ID nie wskazuje alertu o niepewnej wysyłce.")
    matches[0].update(status="sent", acknowledged_by_user_at_utc=now_utc())
    save_store(directory, store)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["fetch", "collect", "deliver", "test", "retry", "acknowledge"], default="fetch")
    parser.add_argument("--alert-id", default="")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args(argv)
    try:
        config = Config.load(ROOT / "config.json")
        if args.mode == "fetch":
            offer = fetch_offer()
            print(json.dumps({"checked_at_utc": now_utc(), "variant_id": VARIANT_ID,
                "price_eur": f"{offer.price_cents // 100}.{offer.price_cents % 100:02d}", "currency": "EUR",
                "available": offer.available, "variant_title": offer.variant_title,
                "source": ENDPOINT}, ensure_ascii=False))
        else:
            credentials()
            if args.mode == "test":
                telegram_send("✅ TEST OMTech K40: Telegram działa. To wiadomość testowa, nie promocja.\n" + PRODUCT_URL)
                print("Wiadomość testowa wysłana i potwierdzona przez Telegram.")
            elif args.mode == "acknowledge":
                acknowledge(args.data_dir, args.alert_id)
                print("Oznaczono wskazany alert jako odebrany; bez ponownej wysyłki.")
            elif args.mode == "collect":
                offer = fetch_offer()
                collect(args.data_dir, config, offer)
                print(f"Zapisano: {euro(offer.price_cents)}; {availability(offer.available)}; wariant {VARIANT_ID}.")
            else:
                deliver(args.data_dir, retry_uncertain=args.mode == "retry")
                print("Kolejka Telegram obsłużona.")
        return 0
    except (MonitorError, OSError, ValueError):
        # Print known-safe messages only. Never expose arbitrary urllib exceptions.
        error = sys.exception()
        print(f"BŁĄD: {error}" if isinstance(error, MonitorError) else "BŁĄD pliku lub konfiguracji; sprawdź JSON i uprawnienia.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
