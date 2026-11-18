"""Kommandolinje for Dypdykks datasett.

  python3 -m dypdykk_data list                    vis spørsmål og status
  python3 -m dypdykk_data build <id|all>          hent fra kildene og bygg staging
  python3 -m dypdykk_data publish <id|all>        publiser staging til nettsiden
  python3 -m dypdykk_data run <id|all>            build + publish
  python3 -m dypdykk_data rollback <id>           gå tilbake til forrige publiserte versjon
  python3 -m dypdykk_data queue [id ...]          kjør importkøen (fortsetter der den slapp)
  python3 -m dypdykk_data status                  vis status for køen
  python3 -m dypdykk_data report                  lag administrasjonsoversikt (admin.html)

Valg:
  --offline   bruk testdata i tests/fixtures (for testing uten nett)
  --refresh   ignorer cache og hent alt på nytt
  --force     publiser selv om en kontroll har stoppet publiseringen
"""
import os
import sys

from . import pipeline


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    if not args or args[0] in ("-h", "help"):
        print(__doc__)
        return 0
    cmd, target = args[0], (args[1] if len(args) > 1 else "all")
    ids = pipeline.list_configs() if target == "all" else [target]
    if cmd == "queue":
        from . import queue
        only = [a for a in args[1:]] or None
        r = queue.run_queue(force_all="--all" in flags, retry="--retry" in flags, only=only)
        return 0 if r["failed"] == 0 else 1
    if cmd == "status":
        from . import queue
        queue.status()
        return 0
    if cmd == "report":
        from . import report
        print(report.write())
        return 0
    if cmd == "list":
        for i in pipeline.list_configs():
            cfg = pipeline.load_json(pipeline.p("config", "questions", i + ".json"))
            st = pipeline.load_json(pipeline.p("staging", i + ".json"))
            pub = pipeline.load_json(os.path.join(pipeline.SITE, "data", i + ".json"))
            print(f"{i:22} {cfg['question'][:46]:48} staging={st['count'] if st else '-':>7}  "
                  f"publisert={pub['n'] if pub else '-':>7}")
        return 0
    ok = True
    for i in ids:
        try:
            if cmd in ("build", "run"):
                r = pipeline.build(i, offline="--offline" in flags, refresh="--refresh" in flags)
                ok &= not r["problems"]
            if cmd in ("publish", "run"):
                ok &= pipeline.publish(i, force="--force" in flags)
            if cmd == "rollback":
                ok &= pipeline.rollback(i)
        except Exception as e:  # én feilende kilde skal ikke stoppe resten
            print(f"FEIL i {i}: {e}", file=sys.stderr)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
