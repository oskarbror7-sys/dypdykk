"""Tester for innsamlingssystemet. Kjør:  python3 -m unittest discover -s tests -v

Testene bruker testdata i tests/fixtures (merket TESTDATA) og skriver til en
midlertidig mappe, så de aldri rører ekte staging eller den publiserte nettsiden.
"""
import importlib
import json
import os
import random
import shutil
import string
import subprocess
import sys
import tempfile
import time
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def fresh_pipeline(tmp):
    os.environ["DYPDYKK_WORK"] = tmp
    os.environ["DYPDYKK_SITE"] = os.path.join(tmp, "site")
    import dypdykk_data.pipeline as pl
    return importlib.reload(pl)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.pl = fresh_pipeline(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def keys(self, res):
        from dypdykk_data.normalize import norm
        m = {}
        for e in res["entries"]:
            for n in [e["label"]] + e["aliases"]:
                m[norm(n)] = e
        return m


class TestNormalize(unittest.TestCase):
    CASES = ["Ålesund", "Tromsø", "Bærum", "São Tomé og Príncipe", "Zlatan Ibrahimović", "C++", "C#", "F#",
             "Kárášjohka", "N'Djamena", "Lillestrøm", "  Ole   Gunnar Solskjær ", "Müller", "100 m", "Ærøskøbing",
             "Ødegaard", "Bjørgvin", "Pelé", "Côte d'Ivoire", "Łódź", "Straße", "ÆØÅ æøå"]

    def test_samme_som_spillet(self):
        """Python-normaliseringen må gi nøyaktig samme nøkler som spillets JavaScript."""
        from dypdykk_data.normalize import norm
        tpl = os.path.join(os.path.dirname(ROOT), "dypdykk", "template.html")
        if not os.path.exists(tpl) or not shutil.which("node"):
            self.skipTest("spillkode eller node mangler")
        src = open(tpl, encoding="utf-8").read()
        start = src.index("function norm(s)")
        end = src.index('/g,"");}', start) + len('/g,"");}')
        js = src[start:end] + "\nconsole.log(JSON.stringify(%s.map(norm)));" % json.dumps(self.CASES)
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout
        self.assertEqual(json.loads(out), [norm(c) for c in self.CASES])

    def test_cpp_og_csharp_er_forskjellige(self):
        from dypdykk_data.normalize import norm
        self.assertEqual(len({norm("C"), norm("C++"), norm("C#")}), 3)


class TestKommuner(Base):
    def setUp(self):
        super().setUp()
        self.res = self.pl.build("kommuner", offline=True, quiet=True)
        self.k = self.keys(self.res)

    def test_gyldige_svar_godkjennes(self):
        for s in ["Oslo", "Bergen", "Lillestrøm", "Midt-Telemark", "Bindal"]:
            self.assertIn(self._n(s), self.k, s)

    def test_ugyldige_svar_avvises(self):
        for s in ["Norge", "Vestland", "Uoppgitt", "Stockholm"]:
            self.assertNotIn(self._n(s), self.k, s)

    def test_alias_fungerer(self):
        self.assertEqual(self.k[self._n("Kárášjohka")]["label"], "Karasjok")   # samisk navn
        self.assertEqual(self.k[self._n("Kristiania")]["label"], "Oslo")       # historisk navn
        self.assertEqual(self.k[self._n("Tråante")]["label"], "Trondheim")

    def test_duplikater_gir_ett_svar(self):
        oslo = [e for e in self.res["entries"] if e["label"] == "Oslo"]
        self.assertEqual(len(oslo), 1)                    # 0301 finnes to ganger i testdataene
        self.assertEqual(len({e["id"] for e in self.res["entries"]}), len(self.res["entries"]))

    def test_sjeldenhet_stiger_med_mindre_kjente(self):
        t = {e["label"]: e["tier"] for e in self.res["entries"]}
        self.assertLess(t["Oslo"], t["Bindal"])
        self.assertLessEqual(t["Bergen"], t["Karasjok"])
        self.assertEqual(sorted(e["tier"] for e in self.res["entries"]), [e["tier"] for e in self.res["entries"]])

    def _n(self, s):
        from dypdykk_data.normalize import norm
        return norm(s)


class TestFotball(Base):
    def setUp(self):
        super().setUp()
        self.res = self.pl.build("fotballspillere", offline=True, quiet=True)
        self.k = self.keys(self.res)

    def n(self, s):
        from dypdykk_data.normalize import norm
        return norm(s)

    def test_gyldige_og_ugyldige(self):
        self.assertIn(self.n("Erling Haaland"), self.k)
        self.assertIn(self.n("Zlatan Ibrahimovic"), self.k)     # uten aksent
        self.assertNotIn(self.n("Magnus Carlsen"), self.k)
        self.assertNotIn(self.n("Q999002"), self.k)             # objekt uten navn forkastes

    def test_etternavn_til_den_mest_kjente(self):
        self.assertEqual(self.k[self.n("Haaland")]["label"], "Erling Haaland")
        self.assertNotIn(self.n("Larsen"), self.k)               # tvetydig, ingen dominerer

    def test_hovednavn_slaar_alias(self):
        self.assertEqual(self.k[self.n("Ronaldo")]["label"], "Ronaldo")   # Ronaldo Nazário heter «Ronaldo»
        self.assertEqual(self.k[self.n("CR7")]["label"], "Cristiano Ronaldo")

    def test_parentes_fjernes(self):
        labels = {e["label"] for e in self.res["entries"]}
        self.assertIn("Ola Nordmann", labels)
        self.assertNotIn("Ola Nordmann (fotballspiller)", labels)

    def test_navnebrodre_gir_ikke_dobbelt(self):
        self.assertEqual(sum(1 for e in self.res["entries"] if self.n(e["label"]) == "paulinho"), 1)

    def test_kjent_er_vanligere_enn_ukjent(self):
        t = {e["label"]: e["tier"] for e in self.res["entries"]}
        self.assertLess(t["Lionel Messi"], t["Steffen Iversen"])
        self.assertLess(t["Erling Haaland"], t["Per Larsen"])


class TestOverstyringOgPublisering(Base):
    def test_manuelle_rettelser_overlever_ny_import(self):
        os.makedirs(os.path.join(self.tmp, "overrides"), exist_ok=True)
        with open(os.path.join(self.tmp, "overrides", "kommuner.json"), "w") as f:
            json.dump({"remove": ["kommune:1811"], "aliases": {"kommune:4601": ["Bergen by"]},
                       "tier": {"kommune:0301": 3}, "reject_alias": ["Christiania"]}, f)
        for _ in range(2):   # to importer på rad
            res = self.pl.build("kommuner", offline=True, quiet=True)
        labels = {e["label"]: e for e in res["entries"]}
        self.assertNotIn("Bindal", labels)
        self.assertIn("Bergen by", labels["Bergen"]["aliases"])
        self.assertEqual(labels["Oslo"]["tier"], 3)
        self.assertNotIn("Christiania", labels["Oslo"]["aliases"])

    def test_testdata_publiseres_ikke_uten_force(self):
        self.pl.build("kommuner", offline=True, quiet=True)
        self.assertFalse(self.pl.publish("kommuner", quiet=True))
        self.assertTrue(self.pl.publish("kommuner", force=True, quiet=True))
        pub = json.load(open(os.path.join(self.tmp, "site", "data", "kommuner.json")))
        self.assertEqual(pub["n"], 11)
        idx = json.load(open(os.path.join(self.tmp, "site", "data", "index.json")))
        self.assertEqual(idx["datasets"][0]["id"], "kommuner")

    def test_krymping_stopper_publisering_og_rollback(self):
        self.pl.build("kommuner", offline=True, quiet=True)
        self.pl.publish("kommuner", force=True, quiet=True)
        st = json.load(open(os.path.join(self.tmp, "staging", "kommuner.json")))
        st["entries"] = st["entries"][:3]; st["count"] = 3; st["offline"] = False
        json.dump(st, open(os.path.join(self.tmp, "staging", "kommuner.json"), "w"))
        self.assertFalse(self.pl.publish("kommuner", quiet=True))            # stoppet: 11 -> 3
        self.assertTrue(self.pl.publish("kommuner", force=True, quiet=True))
        self.assertEqual(json.load(open(os.path.join(self.tmp, "site", "data", "kommuner.json")))["n"], 3)
        self.assertTrue(self.pl.rollback("kommuner", quiet=True))
        self.assertEqual(json.load(open(os.path.join(self.tmp, "site", "data", "kommuner.json")))["n"], 11)

    def test_feilet_kontroll_stopper_publisering(self):
        res = self.pl.build("kommuner", offline=True, quiet=True)
        st = json.load(open(os.path.join(self.tmp, "staging", "kommuner.json")))
        st["problems"] = ["mangler kontrollsvar «Oslo»"]; st["offline"] = False
        json.dump(st, open(os.path.join(self.tmp, "staging", "kommuner.json"), "w"))
        self.assertFalse(self.pl.publish("kommuner", quiet=True))


class TestStortDatasett(Base):
    def test_150k_svar(self):
        """150 000 syntetiske objekter skal gå gjennom hele rørledningen på kort tid."""
        rnd = random.Random(1)
        def name():
            return " ".join("".join(rnd.choice(string.ascii_lowercase) for _ in range(rnd.randint(3, 9))).title()
                            for _ in range(2))
        fake = types.SimpleNamespace(
            collect=lambda cfg, log, refresh=False, fixture=None: None,
            to_entities=lambda raw, cfg: [{"id": f"Q{i}", "label": name(), "aliases": [name()],
                                           "metrics": {"sitelinks": rnd.randint(2, 200)}, "source": "test"}
                                          for i in range(150_000)])
        self.pl.SOURCES["fake"] = fake
        cfgdir = os.path.join(ROOT, "config", "questions")
        path = os.path.join(cfgdir, "_test_stor.json")
        json.dump({"question": "Test", "source": {"type": "fake"}, "validate": {"min_count": 140000},
                   "rarity": {"cuts": {"mode": "rank", "at": [60, 400, 2500, 12000, 50000]}}}, open(path, "w"))
        try:
            t = time.time()
            res = self.pl.build("_test_stor", quiet=True)
            took = time.time() - t
        finally:
            os.remove(path)
        self.assertGreater(res["count"], 140000)
        self.assertEqual(res["tiers"][0], 60)
        self.assertLess(took, 120, f"tok {took:.0f}s")


if __name__ == "__main__":
    unittest.main()


class TestEkteData(unittest.TestCase):
    """Kjøres bare når ekte importerte data finnes i staging/ (ikke testdata)."""
    def load(self, qid):
        f = os.path.join(ROOT, "staging", qid + ".json")
        if not os.path.exists(f):
            self.skipTest("ingen ekte data for " + qid)
        d = json.load(open(f, encoding="utf-8"))
        if d.get("offline"):
            self.skipTest("staging er testdata")
        from dypdykk_data.normalize import norm
        m = {}
        for e in d["entries"]:
            for n in [e["label"]] + e["aliases"]:
                m.setdefault(norm(n), e)
        return d, m, norm

    def test_fotball_kjente_er_vanligere(self):
        d, m, norm = self.load("fotballspillere")
        t = lambda s: m[norm(s)]["tier"]
        for kjent in ["Lionel Messi", "Cristiano Ronaldo", "Erling Haaland", "Kylian Mbappé"]:
            self.assertEqual(t(kjent), 0, kjent)
        self.assertLess(t("Ole Gunnar Solskjær"), t("Steffen Iversen"))
        self.assertEqual(m[norm("Messi")]["label"], "Lionel Messi")          # kallenavn går til den kjente
        self.assertEqual(t("Albert Camus"), 5)                              # kjent for noe annet = sjelden
        self.assertGreater(d["count"], 100000)
        self.assertNotIn(norm("Magnus Carlsen"), m)

    def test_fotball_meningsfull_fordeling(self):
        d, m, norm = self.load("fotballspillere")
        self.assertTrue(all(n > 0 for n in d["tiers"]), d["tiers"])        # alle seks nivåer er i bruk
        self.assertLess(d["tiers"][0], d["tiers"][5])

    def test_kommuner_antall_og_alias(self):
        d, m, norm = self.load("kommuner")
        self.assertEqual(d["count"], 357)
        self.assertEqual(m[norm("Kárášjohka")]["label"], "Karasjok")
        self.assertLess(m[norm("Oslo")]["tier"], m[norm("Modalen")]["tier"])
        self.assertNotIn(norm("Norge"), m)
