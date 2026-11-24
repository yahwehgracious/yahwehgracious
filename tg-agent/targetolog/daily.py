"""Щоранковий звіт у Telegram: вчора й 7 днів, відхилені оголошення, рішення таргетолога.

Правила ті самі, що в застосунку (recs у miniapp.py). Нічого в кабінеті не змінює:
рішення виконуються лише кнопкою в застосунку після твого «так»."""
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


def evaluate(ads, sets, ins, sins, kpi, now):
    """Повертає список рішень: pause / replace / fatigue / scale. Ті самі запобіжники, що в застосунку."""
    N, by_set = norms(kpi), {s["id"]: s for s in sets}
    active = [a for a in ads if a.get("effective_status") == "ACTIVE"]
    per_set = {}
    for a in active:
        per_set[a["adset_id"]] = per_set.get(a["adset_id"], 0) + 1
    out = []
    for a in active:
        if _age_h(a["created_time"], now) < 72:
            continue
        r = goal_res(by_set.get(a["adset_id"]))
        T, i = N[r], ins.get(a["id"]) or {"spend": 0, r: 0, "freq": 0}
        c = i["spend"] / i[r] if i.get(r) else None
        can = per_set[a["adset_id"]] > 1
        if not i.get(r) and i["spend"] >= 2 * T:
            out.append({"kind": "pause" if can else "replace", "name": a["name"],
                        "why": f"{money(i['spend'])} за тиждень і жодного результату" + ("" if can else ". Це єдине оголошення в групі, тож спершу додай заміну")})
        elif i.get(r, 0) >= 3 and c > 1.5 * T and can:
            out.append({"kind": "pause", "name": a["name"], "why": f"{RES[r][0]} коштує {money(c)}, у {c / T:.1f} раза дорожче норми"})
        if i.get("freq", 0) > 3.2:
            out.append({"kind": "fatigue", "name": a["name"], "why": f"частота {i['freq']:.1f}: люди втомились, пора новий креатив"})
    for s in sets:
        if s.get("effective_status") != "ACTIVE" or not s.get("daily_budget") or _age_h(s["created_time"], now) < 72:
            continue
        r = goal_res(s)
        si = sins.get(s["id"]) or {"spend": 0, r: 0}
        c = si["spend"] / si[r] if si.get(r) else None
        if si.get(r, 0) >= 5 and c <= N[r]:
            b = int(s["daily_budget"]) / 100
            out.append({"kind": "scale", "name": s["name"],
                        "why": f"{RES[r][0]} по {money(c)} при нормі {money(N[r])}: можна +20% ({money(b)} → {money(b * 1.2)}/день)"})
    return out


def reasons(ad):
    out = []
    for grp in (ad.get("ad_review_feedback") or {}).values():
        if isinstance(grp, dict):
            out += [v if isinstance(v, str) else k for k, v in grp.items()]
    out += [x.get("error_summary") or x.get("error_message") for x in ad.get("issues_info") or []]
    return [x for x in dict.fromkeys(out) if x]


def message(acc_name, y, w, ads, recs, kpi):
    N = norms(kpi)
    main = next((r for r in ("conv", "lead", "link") if w.get(r)), "conv")
    lines = [f"☀️ <b>Реклама · {esc(acc_name)}</b>"]
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


def _get(path, token, v, **params):
    params["access_token"] = token
    return http(f"https://graph.facebook.com/{v}/{path}?{urllib.parse.urlencode(params)}", timeout=60)


def run(cfg, now=None, send=True):
    now = now or datetime.now(timezone.utc)
    token = os.environ.get(cfg["meta"].get("token_env", "META_ACCESS_TOKEN"), "")
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN не задано")
    v, A = cfg["meta"].get("api_version", "v24.0"), f"act_{cfg['meta']['ad_account_id']}"
    acc = _get(A, token, v, fields="name")
    ads = _get(f"{A}/ads", token, v, fields="id,name,adset_id,effective_status,created_time,ad_review_feedback,issues_info", limit=200)["data"]
    sets = _get(f"{A}/adsets", token, v, fields="id,name,daily_budget,effective_status,optimization_goal,created_time", limit=100)["data"]
    ins = {r["ad_id"]: px(r) for r in _get(f"{A}/insights", token, v, level="ad", date_preset="last_7d", fields="ad_id," + INS, limit=300)["data"]}
    sins = {r["adset_id"]: px(r) for r in _get(f"{A}/insights", token, v, level="adset", date_preset="last_7d", fields="adset_id," + INS, limit=100)["data"]}
    tot = lambda preset: px((_get(f"{A}/insights", token, v, date_preset=preset, fields=INS)["data"] or [{}])[0])  # noqa: E731
    y, w = tot("yesterday"), tot("last_7d")
    recs = evaluate(ads, sets, ins, sins, cfg["kpi"], now)
    txt = message(acc.get("name", ""), y, w, ads, recs, cfg["kpi"])
    log(txt)
    t = cfg.get("telegram") or {}
    if send and t.get("chat_id"):
        telegram.send(t["chat_id"], txt, app_url=t.get("miniapp_url"), app_text="📊 Відкрити таргетолога")
    return {"recs": recs, "text": txt}
