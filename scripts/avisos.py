# Despertador do Banco de Horas: roda a cada 5 min (GitHub Actions) e envia
# push 10 min antes da saida prevista e do limite legal de 2h extras.
# Le o Firestore e envia FCM com a conta de servico (segredo FIREBASE_SA).
import json
import os
import datetime
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

PROJ = "banco-de-horas-a181e"
SA = json.loads(os.environ["FIREBASE_SA"])
SCOPES = [
    "https://www.googleapis.com/auth/datastore",
    "https://www.googleapis.com/auth/firebase.messaging",
]
creds = service_account.Credentials.from_service_account_info(SA, scopes=SCOPES)
creds.refresh(Request())
H = {"Authorization": f"Bearer {creds.token}"}
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents"


def fv(v):
    """Valor REST do Firestore -> Python."""
    if "stringValue" in v: return v["stringValue"]
    if "integerValue" in v: return int(v["integerValue"])
    if "doubleValue" in v: return v["doubleValue"]
    if "booleanValue" in v: return v["booleanValue"]
    if "nullValue" in v: return None
    if "mapValue" in v:
        return {k: fv(x) for k, x in (v["mapValue"].get("fields") or {}).items()}
    if "arrayValue" in v:
        return [fv(x) for x in (v["arrayValue"].get("values") or [])]
    return None


def to_min(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def fmt(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def send(token, title, body, tag):
    msg = {"message": {
        "token": token,
        "data": {"title": title, "body": body, "tag": tag},
        "webpush": {"headers": {"Urgency": "high", "TTL": "1200"}},
    }}
    r = requests.post(
        f"https://fcm.googleapis.com/v1/projects/{PROJ}/messages:send",
        headers={**H, "Content-Type": "application/json"}, json=msg, timeout=20)
    print("fcm", r.status_code, r.text[:140])


# Agora em Sao Paulo (UTC-3; o Brasil nao tem horario de verao desde 2019)
now_sp = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)
today = now_sp.strftime("%Y-%m-%d")
now_min = now_sp.hour * 60 + now_sp.minute
if now_sp.weekday() >= 5:
    print("fim de semana — nada a fazer")
    raise SystemExit(0)

resp = requests.get(BASE + "/users", headers=H, params={"pageSize": 300}, timeout=30)
resp.raise_for_status()
docs = resp.json().get("documents", [])
print(f"{len(docs)} usuario(s), {today} {fmt(now_min)} (SP)")

for d in docs:
    f = {k: fv(v) for k, v in (d.get("fields") or {}).items()}
    setup = f.get("setup") or {}
    tokens = list((f.get("pushTokens") or {}).keys())
    if not tokens or not setup.get("notifyExit"):
        continue
    rec = (f.get("rec") or {}).get(today)
    if (not rec or rec.get("del") or rec.get("type") != "worked"
            or not rec.get("entry") or rec.get("exit")):
        continue
    work = to_min(setup.get("exitTime", "19:00")) - to_min(setup.get("entryTime", "10:00"))
    exit_n = to_min(rec["entry"]) + work
    ho = today in (setup.get("hoDates") or [])
    limit = exit_n if ho else exit_n + 120

    alerts = f.get("alerts") or {}
    if alerts.get("date") != today:
        alerts = {"date": today}
    changed = False

    if not alerts.get("exit") and exit_n - 10 <= now_min < exit_n:
        extra = " (HO: sem extras hoje)" if ho else ""
        for t in tokens:
            send(t, "Quase hora de sair",
                 f"Saida prevista as {fmt(exit_n)} — faltam {exit_n - now_min} min{extra}",
                 "bdh-exit")
        alerts["exit"] = True
        changed = True

    if not ho and not alerts.get("limit") and limit - 10 <= now_min < limit:
        for t in tokens:
            send(t, "Limite de 2h extras",
                 f"Voce atinge o limite legal as {fmt(limit)} — faltam {limit - now_min} min",
                 "bdh-limit")
        alerts["limit"] = True
        changed = True

    if changed:
        body = {"fields": {"alerts": {"mapValue": {"fields": {
            "date": {"stringValue": alerts["date"]},
            "exit": {"booleanValue": bool(alerts.get("exit"))},
            "limit": {"booleanValue": bool(alerts.get("limit"))},
        }}}}}
        requests.patch("https://firestore.googleapis.com/v1/" + d["name"],
                       headers=H, params={"updateMask.fieldPaths": "alerts"},
                       json=body, timeout=20)
        print("alertas marcados:", d["name"].rsplit("/", 1)[-1])

print("ok")
