"""Importkø: kjører alle (eller utvalgte) spørsmål etter tur, med lagret fremdrift.

  python3 -m dypdykk_data queue              kjør alle som ikke er ferdige i dag
  python3 -m dypdykk_data queue --all        kjør alle uansett
  python3 -m dypdykk_data queue --retry      prøv feilede jobber på nytt
  python3 -m dypdykk_data status             vis køstatus

- Fremdrift lagres i state/jobs.json etter hver jobb (atomisk skriving).
- Avbrytes kjøringen, fortsetter neste kjøring der den slapp. Ferdige deler av
  store uttrekk ligger i cache/, så ingenting hentes på nytt.
- En feil i én kategori stopper ikke køen; den registreres og køen går videre.
- Publisering skjer bare hvis alle kontroller består (se pipeline.publish).
"""
import datetime
import json
import os
import time
import traceback

from . import pipeline

STATE = os.path.join(pipeline.WORK, "state", "jobs.json")


def load_state():
    return pipeline.load_json(STATE, {"jobs": {}})


def save_state(st):
    pipeline.save_json(STATE, st)


def run_queue(force_all=False, retry=False, only=None, max_attempts=3):
    st = load_state()
    today = datetime.date.today().isoformat()
    ids = only or pipeline.list_configs()
    ids = [i for i in ids if not i.startswith("_")]
    if not only:   # kategorier merket "aktiv": false (for tunge eller for små) hoppes over i den automatiske køen
        ids = [i for i in ids if (pipeline.load_json(pipeline.p("config", "questions", i + ".json")) or {}).get("aktiv", True)]
    summary = {"ok": 0, "skipped": 0, "failed": 0}
    for qid in ids:
        job = st["jobs"].setdefault(qid, {"attempts": 0})
        if not force_all and job.get("status") == "publisert" and job.get("day") == today:
            summary["skipped"] += 1
            continue
        if job.get("status") == "feilet" and not retry and job.get("day") == today and job["attempts"] >= max_attempts:
            summary["skipped"] += 1
            continue
        job.update({"status": "kjører", "started": datetime.datetime.now().isoformat(timespec="seconds"), "day": today})
        job["attempts"] = job.get("attempts", 0) + 1
        save_state(st)
        t0 = time.time()
        try:
            res = pipeline.build(qid)
            job.update({"count": res["count"], "keys": res["keys"], "tiers": res["tiers"],
                        "problems": res["problems"], "review": _review_count(qid)})
            if res["problems"]:
                job["status"] = "stoppet (kontroll)"
                summary["failed"] += 1
            elif pipeline.publish(qid):
                job["status"] = "publisert"
                job["attempts"] = 0
                summary["ok"] += 1
            else:
                job["status"] = "stoppet (publisering)"
                summary["failed"] += 1
        except Exception as e:  # noqa: BLE001 – køen skal tåle alle feil i én jobb
            job.update({"status": "feilet", "error": f"{type(e).__name__}: {e}",
                        "trace": traceback.format_exc()[-1500:]})
            summary["failed"] += 1
        job["seconds"] = round(time.time() - t0, 1)
        job["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
        save_state(st)
        print(f"[kø] {qid}: {job['status']} ({job.get('count', '-')} svar, {job['seconds']}s)", flush=True)
    print(f"[kø] ferdig: {summary}", flush=True)
    return summary


def status():
    st = load_state()
    for qid in pipeline.list_configs():
        j = st["jobs"].get(qid, {})
        print(f"{qid:28} {j.get('status', 'ikke kjørt'):22} {str(j.get('count', '-')):>8} "
              f"{j.get('finished', ''):20} {j.get('error', '')[:60]}")


def _review_count(qid):
    r = pipeline.load_json(pipeline.p("review", qid + ".json"), [])
    return len(r)
