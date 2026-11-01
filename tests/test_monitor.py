import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import monitor as m


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.config = m.Config(Decimal(5), None)

    def offer(self, price, available=True):
        return m.Offer(price, available, "K40", "Without LightBurn")

    def record(self, price, available=True, config=None):
        return m.collect(self.directory, config or self.config, self.offer(price, available),
                         timestamp="2026-11-01T18:00:00+00:00")

    def payload(self, price=69999):
        return {"handle": m.HANDLE, "title": "K40", "price": 100,
                "variants": [{"id": 111, "price": 1},
                    {"id": int(m.VARIANT_ID), "price": price, "available": True}]}

    def test_exact_variant_not_product_minimum(self):
        self.assertEqual(m.parse_offer(self.payload(), "EUR").price_cents, 69999)

    def test_wrong_or_duplicate_variant(self):
        for variants in ([], [{"id": 1}], self.payload()["variants"] * 2):
            with self.subTest(variants=variants), self.assertRaises(m.MonitorError):
                m.parse_offer({"handle": m.HANDLE, "variants": variants}, "EUR")

    def test_reject_wrong_currency_or_product(self):
        for currency in ("PLN", "USD", None, ""):
            with self.subTest(currency=currency), self.assertRaises(m.MonitorError):
                m.parse_offer(self.payload(), currency)
        with self.assertRaises(m.MonitorError):
            m.parse_offer({"handle": "other", "variants": []}, "EUR")

    def test_reject_invalid_prices(self):
        for price in (None, 0, -1, True, 699.99, "69999", "NaN", "", float("inf")):
            with self.subTest(price=price), self.assertRaises(m.MonitorError):
                m.parse_offer(self.payload(price), "EUR")

    def test_availability_missing_is_unknown(self):
        payload = self.payload()
        del payload["variants"][1]["available"]
        self.assertIsNone(m.parse_offer(payload, "EUR").available)

    def test_invalid_availability(self):
        payload = self.payload()
        payload["variants"][1]["available"] = "false"
        with self.assertRaises(m.MonitorError):
            m.parse_offer(payload, "EUR")

    def test_initialization_is_silent(self):
        store = self.record(79900)
        self.assertEqual(store["outbox"], [])

    def test_exact_five_percent(self):
        self.record(80000)
        store = self.record(76000)
        self.assertIn("Obniżka: 5,0%", store["outbox"][-1]["text"])
        self.assertIn("Poprzednia cena: 800,00 EUR", store["outbox"][-1]["text"])

    def test_below_five_percent(self):
        self.record(80000)
        event = self.record(76001)["outbox"][0]
        self.assertIn("ZMIANA CENY", event["text"])
        self.assertNotIn("PROMOCJA", event["text"])

    def test_previous_observation_not_high_water_mark(self):
        self.record(80000)
        self.record(77000)
        store = self.record(74000)
        self.assertEqual(len(store["outbox"]), 2)
        self.assertIn("Poprzednia cena: 770,00 EUR", store["outbox"][-1]["text"])
        self.assertIn("Obniżka: 3,9%", store["outbox"][-1]["text"])

    def test_each_qualifying_drop(self):
        self.record(80000)
        self.record(76000)
        self.assertEqual(len(self.record(72200)["outbox"]), 2)

    def test_same_price_silent_and_increase_alerts_once(self):
        self.record(80000)
        self.record(76000)
        self.record(76000)
        self.assertEqual(len(self.record(76000)["outbox"]), 1)
        store = self.record(77000)
        self.assertEqual(len(store["outbox"]), 2)
        self.assertIn("Wzrost:", store["outbox"][-1]["text"])
        self.assertNotIn("PROMOCJA", store["outbox"][-1]["text"])

    def test_new_sale_after_rebound(self):
        self.record(80000)
        self.record(76000)
        self.record(80000)
        self.assertEqual(len(self.record(76000)["outbox"]), 3)

    def test_target_first_read_and_no_repeat(self):
        config = m.Config(Decimal(5), 65000)
        store = self.record(65000, config=config)
        self.assertEqual(store["outbox"], [])
        self.assertEqual(self.record(65000, config=config)["outbox"], [])

    def test_target_crossing_below_five_percent(self):
        config = m.Config(Decimal(5), 65000)
        self.record(66000, config=config)
        self.assertEqual(len(self.record(64999, config=config)["outbox"]), 1)

    def test_target_rearms_after_price_above_target(self):
        config = m.Config(Decimal(5), 65000)
        self.record(65000, config=config)
        self.record(65500, config=config)
        self.assertEqual(len(self.record(65000, config=config)["outbox"]), 2)

    def test_target_further_lower_price(self):
        config = m.Config(Decimal(5), 65000)
        self.record(64000, config=config)
        self.assertEqual(len(self.record(63900, config=config)["outbox"]), 1)

    def test_target_configuration_change(self):
        self.record(65000)
        config = m.Config(Decimal(5), 65000)
        self.assertEqual(self.record(65000, config=config)["outbox"], [])

    def test_promotion_reports_unavailable_honestly(self):
        self.record(80000)
        self.assertIn("Status: Niedostępny", self.record(70000, False)["outbox"][-1]["text"])

    def test_back_in_stock_at_target(self):
        config = m.Config(Decimal(5), 65000)
        self.record(65000, False, config=config)
        self.assertEqual(self.record(65000, True, config=config)["outbox"], [])

    def test_every_successful_check_is_in_csv(self):
        self.record(70000)
        self.record(70000)
        self.record(70000, None)
        csv = (self.directory / "price_history.csv").read_text()
        self.assertEqual(len(csv.splitlines()), 4)
        self.assertIn("unknown", csv)

    def test_bad_offer_does_not_modify_history(self):
        self.record(80000)
        before = (self.directory / "store.json").read_bytes()
        with self.assertRaises(m.MonitorError):
            self.record(0)
        self.assertEqual(before, (self.directory / "store.json").read_bytes())

    def test_corrupt_store_never_resets(self):
        self.record(80000)
        (self.directory / "store.json").write_text("{}")
        with self.assertRaises(m.MonitorError):
            self.record(70000)
        self.assertEqual((self.directory / "store.json").read_text(), "{}")

    def test_missing_store_with_history_fails(self):
        (self.directory / "price_history.csv").write_text("old history")
        with self.assertRaises(m.MonitorError):
            m.load_store(self.directory)

    def test_delivery_success_deduplicated_across_restarts(self):
        self.record(80000)
        self.record(76000)
        sender = Mock(return_value=123)
        m.deliver(self.directory, sender=sender)
        m.deliver(self.directory, sender=sender)
        sender.assert_called_once()
        self.assertEqual(m.load_store(self.directory)["outbox"][0]["status"], "sent")

    def test_definite_failure_remains_pending(self):
        self.record(80000)
        self.record(76000)
        with self.assertRaises(m.DeliveryError):
            m.deliver(self.directory, sender=Mock(side_effect=m.DeliveryError("HTTP 403")))
        self.assertEqual(m.load_store(self.directory)["outbox"][0]["status"], "pending")
        sender = Mock(return_value=1)
        m.deliver(self.directory, sender=sender)
        sender.assert_called_once()

    def test_uncertain_delivery_not_automatically_repeated(self):
        self.record(80000)
        self.record(76000)
        with self.assertRaises(m.DeliveryError):
            m.deliver(self.directory, sender=Mock(side_effect=m.DeliveryError("timeout", uncertain=True)))
        sender = Mock(return_value=1)
        with self.assertRaises(m.MonitorError):
            m.deliver(self.directory, sender=sender)
        sender.assert_not_called()
        m.deliver(self.directory, sender=sender, retry_uncertain=True)
        sender.assert_called_once()

    def test_acknowledge_uncertain_without_resending(self):
        self.record(80000)
        store = self.record(76000)
        event = store["outbox"][0]
        event["status"] = "uncertain"
        m.save_store(self.directory, store)
        m.acknowledge(self.directory, event["id"])
        sender = Mock(return_value=1)
        m.deliver(self.directory, sender=sender)
        sender.assert_not_called()
        with self.assertRaises(m.MonitorError):
            m.acknowledge(self.directory, "wrong")

    def response(self, raw=b'{}', url=m.ENDPOINT):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = raw
        response.geturl.return_value = url
        return response

    def test_transient_get_retries_then_success(self):
        opener, sleep = Mock(), Mock()
        opener.open.side_effect = [URLError("dns"), TimeoutError(), self.response()]
        self.assertEqual(m.get_json(opener, m.ENDPOINT, sleep=sleep), {})
        self.assertEqual(sleep.call_count, 2)

    def test_network_failure_exhausts_three_attempts(self):
        opener = Mock()
        opener.open.side_effect = URLError("dns")
        with self.assertRaises(m.MonitorError):
            m.get_json(opener, m.ENDPOINT, sleep=Mock())
        self.assertEqual(opener.open.call_count, 3)

    def test_access_denied_is_not_retried(self):
        opener, sleep = Mock(), Mock()
        opener.open.side_effect = HTTPError(m.ENDPOINT, 403, "Denied", {}, io.BytesIO())
        with self.assertRaisesRegex(m.MonitorError, "403"):
            m.get_json(opener, m.ENDPOINT, sleep=sleep)
        sleep.assert_not_called()

    def test_rate_limit_respects_retry_after(self):
        opener, sleep = Mock(), Mock()
        opener.open.side_effect = [HTTPError(m.ENDPOINT, 429, "Limit", {"Retry-After": "10"}, io.BytesIO()), self.response()]
        m.get_json(opener, m.ENDPOINT, sleep=sleep)
        sleep.assert_called_once_with(10)

    def test_long_retry_after_stops(self):
        opener, sleep = Mock(), Mock()
        opener.open.side_effect = HTTPError(m.ENDPOINT, 429, "Limit", {"Retry-After": "300"}, io.BytesIO())
        with self.assertRaises(m.MonitorError):
            m.get_json(opener, m.ENDPOINT, sleep=sleep)
        sleep.assert_not_called()

    def test_invalid_html_json_size_and_redirect(self):
        for response in (self.response(b'<html>blocked</html>'), self.response(b'[]'),
                         self.response(b'x' * (m.MAX_BODY + 1)),
                         self.response(url="https://other.example/product.js")):
            with self.subTest(response=response), self.assertRaises(m.MonitorError):
                m.get_json(Mock(open=Mock(return_value=response)), m.ENDPOINT, sleep=Mock())

    def test_fetch_currency_and_product_share_session(self):
        opener = Mock()
        with patch.object(m, "build_opener", return_value=opener), patch.object(m, "get_json", side_effect=[{"currency": "EUR"}, self.payload()]) as get:
            self.assertEqual(m.fetch_offer().price_cents, 69999)
            self.assertIs(get.call_args_list[0].args[0], get.call_args_list[1].args[0])

    def test_fetch_currency_failure_does_not_request_price(self):
        with patch.object(m, "get_json", return_value={"currency": "PLN"}) as get:
            with self.assertRaises(m.MonitorError):
                m.fetch_offer()
            get.assert_called_once()

    def test_config_validation_and_comma(self):
        config_path = self.directory / "config.json"
        config_path.write_text('{"price_drop_percent":"5", "target_price_eur":"650,50"}')
        self.assertEqual(m.Config.load(config_path).target, 65050)
        for value in ("NaN", "-5", "0", "101", "1e4"):
            config_path.write_text(json.dumps({"price_drop_percent": value, "target_price_eur": ""}))
            with self.subTest(value=value), self.assertRaises(m.MonitorError):
                m.Config.load(config_path)

    def test_no_credentials_fails_before_collecting(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(m, "fetch_offer") as fetch:
            with patch("sys.stderr", new=io.StringIO()):
                self.assertEqual(m.main(["--mode", "collect", "--data-dir", str(self.directory)]), 1)
            fetch.assert_not_called()

    def test_telegram_timeout_hides_token_and_is_uncertain(self):
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "123:secret_test", "TELEGRAM_CHAT_ID": "456"}), patch.object(m, "build_opener") as build:
            build.return_value.open.side_effect = URLError("https://api.telegram.org/bot123:secret_test/sendMessage")
            with self.assertRaises(m.DeliveryError) as caught:
                m.telegram_send("test")
            self.assertTrue(caught.exception.uncertain)
            self.assertNotIn("secret_test", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
