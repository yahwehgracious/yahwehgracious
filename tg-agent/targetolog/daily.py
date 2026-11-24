"""Щоранковий звіт у Telegram: вчора й 7 днів, відхилені оголошення, рішення таргетолога.

Правила ті самі, що в застосунку (recs у miniapp.py). Нічого в кабінеті не змінює:
рішення виконуються лише кнопкою в застосунку після твого «так»."""
import math
import os
import urllib.parse
from datetime import datetime, timezone

from . import telegram
from .telegram import esc
from .util import http, log

CONV = "onsite_conversion.messaging_conversation_started_7d"
RT = {"conv": [CONV], "lead": ["lead", "onsite_conversion.lead_grouped", "leadgen_grouped"], "link": ["link_click"]}
RES = {"conv": ("переписка", "переписки", "переписок"), "lead": ("заявка", "заявки", "заявок"), "link": ("перехід", "переходи", "переходів")}
INS = "spend,impressions,clicks,inline_link_clicks,frequency,actions"


def pl(n, f):
    n = abs(int(round(n)))
    a, b = n % 10, n % 100
    return f[0] if a == 1 and b != 11 else f[1] if 2 <= a <= 4 and not 12 <= b <= 14 else f[2]


def money(v, cur="₴"):
    return "—" if v is None else f"{cur}{v:,.0f}".replace(",", " ")


def px(r):
    o = {"spend": float(r.get("spend") or 0), "impr": int(r.get("impressions") or 0), "freq": float(r.get("frequency") or 0)}
    acts = {a["action_type"]: float(a["value"]) for a in r.get("actions") or []}
    for k, types in RT.items():
        o[k] = next((acts[t] for t in types if t in acts), 0)
    return o


def goal_res(adset):
    og = (adset or {}).get("optimization_goal")
    return "lead" if og in ("LEAD_GENERATION", "QUALITY_LEAD") else "link" if og in ("LINK_CLICKS", "LANDING_PAGE_VIEWS") else "conv"


def norms(kpi):
    return {"conv": kpi.get("target_cpl", 60), "lead": kpi.get("target_lead", 150), "link": kpi.get("target_click", 8)}


def _age_h(iso, now):
    return (now - datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)).total_seconds() / 3600


RULES = {"risk": 10, "scale": 10, "step": 20, "minh": 48}


def pcdf(k, lam):
    """P(X ≤ k) для Пуассона: шанс отримати не більше k результатів, якщо в середньому чекаємо lam."""
    t = s = math.exp(-lam)
    for i in range(1, int(k) + 1):
        t *= lam / i
        s += t
    return min(1.0, s)


def scale_wait_days(T, budget):
    """Скільки чекати після зміни бюджету: поки група витратить ~3 норми за новим бюджетом, від 2 до 7 днів."""
    return min(7, max(2, -(-3 * T // max(budget, 1))))


def pct(p):
    return f"{p * 100:.0f}%" if p >= 0.01 else "<1%"


def evaluate(ads, sets, ins, sins, kpi, now, rules=None):
    """Рішення pause / replace / fatigue / scale за статистикою, як у застосунку.
    Вимкнути: якби оголошення було в нормі, такий поганий результат випадає рідше ніж у risk% випадків.
    Додати бюджет: якби група була лише в нормі, такий хороший результат випадає рідше ніж у scale% випадків."""
    R = {**RULES, **(rules or {})}
    N, by_set = norms(kpi), {s["id"]: s for s in sets}
    active = [a for a in ads if a.get("effective_status") == "ACTIVE"]
    per_set = {}
    for a in active:
        per_set[a["adset_id"]] = per_set.get(a["adset_id"], 0) + 1
    out = []
    for a in active:
        if _age_h(a["created_time"], now) < R["minh"]:
            continue
        r = goal_res(by_set.get(a["adset_id"]))
        T, i = N[r], ins.get(a["id"]) or {"spend": 0, r: 0, "freq": 0}
        k, lam = i.get(r, 0), i["spend"] / T
        p = pcdf(k, lam)
        if k < lam and p * 100 < R["risk"]:
            can = per_set[a["adset_id"]] > 1
            got = f"жодного результату" if not k else f"{RES[r][0]} по {money(i['spend'] / k)}"
            out.append({"kind": "pause" if can else "replace", "name": a["name"],
                        "why": f"{money(i['spend'])} за тиждень, {got}; шанс, що воно в нормі й просто не пощастило, {pct(p)}"
                               + ("" if can else ". Це єдине оголошення в групі, тож спершу додай заміну")})
        if i.get("freq", 0) > 3.2:
            out.append({"kind": "fatigue", "name": a["name"], "why": f"частота {i['freq']:.1f}: люди втомились, пора новий креатив"})
    for s in sets:
        if s.get("effective_status") != "ACTIVE" or not s.get("daily_budget"):
            continue
        r = goal_res(s)
        b = int(s["daily_budget"]) / 100
        since = min(_age_h(s["created_time"], now), _age_h(s.get("updated_time") or s["created_time"], now))
        if since < 24 * scale_wait_days(N[r], b):
            continue
        si = sins.get(s["id"]) or {"spend": 0, r: 0}
        k, lam = si.get(r, 0), si["spend"] / N[r]
        p = 1 - pcdf(k - 1, lam) if k else 1
        if k > lam and p * 100 < R["scale"]:
            nb = b * (1 + R["step"] / 100)
            out.append({"kind": "scale", "name": s["name"],
                        "why": f"{RES[r][0]} по {money(si['spend'] / k)} при нормі {money(N[r])}, шанс випадковості {pct(p)}: "
                               f"можна +{R['step']:.0f}% ({money(b)} → {money(nb)}/день)"})
    return out


def rules_from_labels(labels):
    """Правила рішень із застосунку: мітка «ai_rules risk=10 scale=10 step=20 minh=48»."""
    for lab in labels:
        n = lab.get("name", "")
        if n.startswith("ai_rules "):
            kv = dict(x.split("=", 1) for x in n.split()[1:] if "=" in x)
            return {k: float(v) for k, v in kv.items() if k in RULES and v.replace(".", "", 1).isdigit()}
    return {}


def reasons(ad):
    out = []
    for grp in (ad.get("ad_review_feedback") or {}).values():
        if isinstance(grp, dict):
            out += [v if isinstance(v, str) else k for k, v in grp.items()]
    out += [x.get("error_summary") or x.get("error_message") for x in ad.get("issues_info") or []]
    return [x for x in dict.fromkeys(out) if x]


ACC_STATUS = {2: "кабінет заблоковано", 3: "неоплачений борг: реклама зупинена, доки не оплатиш", 7: "кабінет на перевірці ризиків Meta",
              8: "чекає оплати", 9: "пільговий період оплати: скоро зупиниться", 100: "кабінет закривається", 101: "кабінет закрито"}
DISABLE = {1: "порушення правил реклами", 2: "перевірка інтелектуальної власності", 3: "проблема з оплатою", 4: "неактивний або підозрілий кабінет",
           5: "перевірка Meta", 6: "перевірка бізнесу", 7: "закрито назавжди"}


def account_alert(acc):
    """Блокування кабінету або проблема з оплатою: одним рядком, щоб не загубилось."""
    st = acc.get("account_status")
    if st in (None, 1, 201):
        return ""
    why = DISABLE.get(acc.get("disable_reason") or 0)
    return f"🚨 <b>{ACC_STATUS.get(st, f'статус кабінету {st}')}</b>" + (f" · причина: {why}" if why else "") + \
        ". Перевір у business.facebook.com → Якість облікового запису."


def message(acc_name, y, w, ads, recs, kpi, alert=""):
    N = norms(kpi)
    main = next((r for r in ("conv", "lead", "link") if w.get(r)), "conv")
    lines = [f"☀️ <b>Реклама · {esc(acc_name)}</b>"] + ([alert] if alert else [])
    if not w["spend"]:
        lines.append("За тиждень реклама нічого не витратила." + (" Активних оголошень нема." if not any(a.get("effective_status") == "ACTIVE" for a in ads) else ""))
    else:
        def line(label, d):
            parts = [f"{money(d['spend'])}"] + [f"{int(d[r])} {pl(d[r], RES[r])}" + (f" по {money(d['spend'] / d[r])}" if d[r] else "") for r in ("conv", "lead", "link") if d.get(r)]
            return f"<b>{label}:</b> " + " · ".join(parts)
        lines += [line("Вчора", y), line("7 днів", w)]
        c = w["spend"] / w[main] if w.get(main) else None
        if c is not None:
            v = "✅ у нормі" if c <= N[main] else "🟡 трохи дорожче норми" if c <= N[main] * 1.5 else "🔴 дорого"
            lines.append(f"Ціна: {v} (норма {money(N[main])} за {RES[main][0]})")
    rej = [a for a in ads if a.get("effective_status") in ("DISAPPROVED", "WITH_ISSUES")]
    if rej:
        lines.append("\n⛔ <b>Відхилено Meta:</b>")
        lines += [f"• {esc(a['name'])}: {esc((reasons(a) or ['причина в застосунку'])[0][:160])}" for a in rej[:5]]
    if recs:
        ico = {"pause": "⏸", "replace": "↻", "fatigue": "↻", "scale": "↗"}
        lines.append("\n🧠 <b>Рішення (підтверди в застосунку):</b>")
        lines += [f"{ico[x['kind']]} {esc(x['name'])}: {esc(x['why'])}" for x in recs[:6]]
    elif w["spend"]:
        lines.append("\nРішень не треба, все працює рівно.")
    return "\n".join(lines)


def norms_from_labels(labels):
    """Норми, які ти задав у застосунку, лежать міткою «ai_norms conv=… lead=… link=…» у кабінеті Meta."""
    for lab in labels:
        n = lab.get("name", "")
        if n.startswith("ai_norms "):
            kv = dict(x.split("=", 1) for x in n.split()[1:] if "=" in x)
            keys = {"conv": "target_cpl", "lead": "target_lead", "link": "target_click"}
            return {keys[k]: float(v) for k, v in kv.items() if k in keys and v.replace(".", "", 1).isdigit()}
    return {}


def _get(path, token, v, **params):
    params["access_token"] = token
    return http(f"https://graph.facebook.com/{v}/{path}?{urllib.parse.urlencode(params)}", timeout=60)


def run(cfg, now=None, send=True):
    now = now or datetime.now(timezone.utc)
    token = os.environ.get(cfg["meta"].get("token_env", "META_ACCESS_TOKEN"), "")
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN не задано")
    v, A = cfg["meta"].get("api_version", "v24.0"), f"act_{cfg['meta']['ad_account_id']}"
    acc = _get(A, token, v, fields="name,account_status,disable_reason")
    ads = _get(f"{A}/ads", token, v, fields="id,name,adset_id,effective_status,created_time,ad_review_feedback,issues_info", limit=200)["data"]
    sets = _get(f"{A}/adsets", token, v, fields="id,name,daily_budget,effective_status,optimization_goal,created_time,updated_time", limit=100)["data"]
    ins = {r["ad_id"]: px(r) for r in _get(f"{A}/insights", token, v, level="ad", date_preset="last_7d", fields="ad_id," + INS, limit=300)["data"]}
    sins = {r["adset_id"]: px(r) for r in _get(f"{A}/insights", token, v, level="adset", date_preset="last_7d", fields="adset_id," + INS, limit=100)["data"]}
    tot = lambda preset: px((_get(f"{A}/insights", token, v, date_preset=preset, fields=INS)["data"] or [{}])[0])  # noqa: E731
    y, w = tot("yesterday"), tot("last_7d")
    labels = _get(f"{A}/adlabels", token, v, fields="name", limit=200).get("data", [])
    kpi = {**cfg["kpi"], **norms_from_labels(labels)}
    recs = evaluate(ads, sets, ins, sins, kpi, now, rules_from_labels(labels))
    txt = message(acc.get("name", ""), y, w, ads, recs, kpi, account_alert(acc))
    log(txt)
    t = cfg.get("telegram") or {}
    if send and t.get("chat_id"):
        telegram.send(t["chat_id"], txt, app_url=t.get("miniapp_url"), app_text="📊 Відкрити таргетолога")
    return {"recs": recs, "text": txt}
