"""Telegram Mini App «ШІ-таргетолог»: живий кабінет Meta прямо в Telegram.

Усе про рекламу (кампанії, креативи, бюджети, звіти) застосунок бере з Meta API напряму з телефона.
Статично в сторінку вшиті лише конкуренти та ідеї, які щотижня оновлює пайплайн (GitHub Actions).
Ключі (Meta, ШІ) зберігаються в Telegram CloudStorage користувача й нікуди більше не йдуть."""
import json
from datetime import datetime, timezone

APP = r"""<!doctype html><html lang="uk"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<title>ШІ-таргетолог</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--bg:#07070c;--card:rgba(255,255,255,.045);--card2:rgba(255,255,255,.08);--line:rgba(255,255,255,.09);--ink:#f4f4f8;--mut:#9a9ab0;
--g1:#8b5cf6;--g2:#22d3ee;--good:#34d399;--bad:#fb7185;--mid:#fbbf24;--learn:#94a3b8}
*{box-sizing:border-box;min-width:0;-webkit-tap-highlight-color:transparent}
html,body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 Manrope,-apple-system,Segoe UI,Roboto,sans-serif;overflow-x:hidden;-webkit-text-size-adjust:100%}
b,h2,h3,.name,.big{text-wrap:balance}p,small,.h2s,.copy,.card,.item .tx{text-wrap:pretty;overflow-wrap:anywhere}
button,input,textarea{-webkit-appearance:none;appearance:none}
body::before{content:"";position:fixed;inset:-20% -30% auto;height:60vh;background:radial-gradient(closest-side,rgba(139,92,246,.22),transparent),radial-gradient(closest-side at 80% 40%,rgba(34,211,238,.14),transparent);pointer-events:none;z-index:0}
main{position:relative;z-index:1;padding:14px 14px calc(96px + env(safe-area-inset-bottom))}
.top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:4px 2px 14px}
.top .who{font-size:12.5px;color:var(--mut)}.top .name{font-size:19px;font-weight:800;letter-spacing:-.02em;line-height:1.2}
.how{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:20px;padding:8px 12px;font:700 12.5px Manrope,sans-serif;display:flex;gap:7px;align-items:center;white-space:nowrap;flex:none;cursor:pointer}
.how i{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,var(--g1),var(--g2));box-shadow:0 0 10px var(--g2);animation:pulse 1.8s infinite}
@keyframes pulse{50%{opacity:.35}}
.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px;margin-bottom:12px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.hero{background:linear-gradient(160deg,rgba(139,92,246,.22),rgba(34,211,238,.06) 60%,rgba(255,255,255,.03));position:relative;overflow:hidden}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.06) 50%,transparent 70%);transform:translateX(-100%);animation:shine 5s 1.5s infinite;pointer-events:none}
@keyframes shine{40%,100%{transform:translateX(100%)}}
.lab{color:var(--mut);font-size:13px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.big{font-size:clamp(32px,10vw,44px);font-weight:800;letter-spacing:-.03em;line-height:1.05;margin:6px 0 8px;white-space:nowrap}
.q{display:inline-flex;width:18px;height:18px;color:var(--mut);cursor:pointer;flex:none;vertical-align:-3px;padding:0;margin:-4px;box-sizing:content-box;border:4px solid transparent}.q svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;pointer-events:none}
.funnel{display:grid;grid-template-columns:1fr 12px 1fr;align-items:center;gap:4px;margin-top:16px}
.fn{background:rgba(0,0,0,.28);border:1px solid var(--line);border-radius:14px;padding:10px 4px;text-align:center;height:100%;display:flex;flex-direction:column;justify-content:center}
.fn b{display:block;font-size:19px;font-weight:800;white-space:nowrap}.fn span{font-size:11.5px;color:var(--mut);display:flex;justify-content:center;gap:4px;align-items:center}
.fn.hl{border-color:rgba(52,211,153,.5);background:rgba(52,211,153,.09)}.fn.hl b{color:var(--good)}
.flow{height:2px;background:repeating-linear-gradient(90deg,var(--g2) 0 4px,transparent 4px 8px);background-size:16px 2px;animation:flow .9s linear infinite;opacity:.85}
@keyframes flow{to{background-position:16px 0}}
.pill{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:5px 11px;font-size:13px;font-weight:700;white-space:nowrap}
.pill::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor;flex:none}
.p-good{color:var(--good);background:rgba(52,211,153,.13)}.p-bad{color:var(--bad);background:rgba(251,113,133,.13)}.p-mid{color:var(--mid);background:rgba(251,191,36,.13)}.p-learn{color:var(--learn);background:rgba(148,163,184,.13)}
.btn{display:block;border:0;border-radius:14px;padding:14px 16px;font:700 15px Manrope,sans-serif;color:#fff;background:linear-gradient(135deg,var(--g1),#6d5dfc 50%,var(--g2));width:100%;margin-top:10px;box-shadow:0 8px 24px -10px rgba(139,92,246,.8);cursor:pointer;text-align:center}
.btn:active{transform:scale(.98)}.btn[disabled]{opacity:.45;pointer-events:none}
.btn.ghost{background:var(--card2);box-shadow:none;color:var(--ink);border:1px solid var(--line)}.btn.bad{background:linear-gradient(135deg,#e11d48,#fb7185);box-shadow:0 8px 24px -10px rgba(251,113,133,.7)}.btn.good{background:linear-gradient(135deg,#059669,#34d399);box-shadow:0 8px 24px -10px rgba(52,211,153,.7)}
.btn.sm{padding:10px 12px;font-size:13.5px;margin-top:8px}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}.row2 .btn{font-size:13.5px;padding:13px 10px}
h2{font-size:20px;font-weight:800;letter-spacing:-.02em;margin:24px 2px 4px}.h2s{color:var(--mut);font-size:13.5px;margin:0 2px 12px}
.item{display:flex;gap:12px;align-items:flex-start;padding:14px;background:var(--card);border:1px solid var(--line);border-radius:18px;margin-bottom:10px;cursor:pointer;transition:transform .12s}
.item:active{transform:scale(.98)}.item.sel{border-color:var(--g2);background:rgba(34,211,238,.08)}
.ico{width:42px;height:42px;border-radius:13px;display:grid;place-items:center;flex:none;font-size:18px;font-weight:800}
.i-bad{background:rgba(251,113,133,.15);color:var(--bad)}.i-good{background:rgba(52,211,153,.15);color:var(--good)}.i-mid{background:rgba(251,191,36,.15);color:var(--mid)}.i-learn{background:rgba(148,163,184,.15);color:var(--learn)}.i-ai{background:linear-gradient(135deg,rgba(139,92,246,.35),rgba(34,211,238,.2))}
.th{width:46px;height:46px;border-radius:12px;object-fit:cover;flex:none}
.item .tx{flex:1;align-self:center}.item .tx b{display:block;font-weight:700;font-size:15px;line-height:1.32;letter-spacing:-.005em}.item .chev,.item .val{align-self:center}.item .tx small{color:var(--mut);font-size:13px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:3px}
.mg>.m:last-child:nth-child(odd){grid-column:1/-1}
.item .val{text-align:right;font-weight:800;white-space:nowrap;font-size:14px}.item .val small{display:block;color:var(--mut);font-weight:500;font-size:11.5px}
.chev{color:var(--mut);font-size:22px}
.chip{display:inline-block;border-radius:10px;padding:4px 9px;font-size:12px;font-weight:700;background:var(--card2);margin:2px 4px 2px 0}
.sec{margin-top:14px}.sec .l,.l{font-size:11.5px;color:var(--mut);font-weight:800;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px}
.fig{position:relative;height:170px;margin:12px -2px 4px}.fig svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.bar{transform-box:fill-box;transform-origin:bottom;animation:grow .7s cubic-bezier(.2,.8,.2,1) backwards}
@keyframes grow{from{transform:scaleY(0)}}
.ln{stroke-dasharray:var(--len);stroke-dashoffset:var(--len);animation:draw 1.3s .35s ease-out forwards}
@keyframes draw{to{stroke-dashoffset:0}}
.dp{opacity:0;animation:fade .35s forwards}@keyframes fade{to{opacity:1}}
svg text{font:600 11px Manrope,sans-serif;fill:var(--mut)}
.legend{display:flex;gap:14px;font-size:12px;color:var(--mut)}.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.mg{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
.m{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:10px 12px}.m span{color:var(--mut);font-size:12px;display:flex;gap:5px;align-items:center;flex-wrap:wrap}.m b{font-size:18px;font-weight:800;display:block;margin-top:2px}
.dbar{height:6px;background:var(--card2);border-radius:3px;margin-top:8px;overflow:hidden}.dbar i{display:block;height:100%;border-radius:3px;background:linear-gradient(90deg,var(--g1),var(--g2));animation:wid 1.1s cubic-bezier(.2,.8,.2,1) backwards}
@keyframes wid{from{width:0}}
.idea{background:linear-gradient(135deg,rgba(139,92,246,.16),rgba(34,211,238,.08));border:1px solid rgba(139,92,246,.38);border-radius:14px;padding:12px;margin-top:14px}
.idea b{color:#c4b5fd}
.seg{display:flex;gap:4px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:4px;margin:12px 0;overflow-x:auto;scrollbar-width:none}
.seg button{flex:1 1 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border:0;background:none;color:var(--mut);font:700 13px Manrope,sans-serif;padding:9px 4px;border-radius:10px;cursor:pointer}
.seg button.on{background:var(--card2);color:var(--ink)}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 0}
.chips button{flex:none;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:8px 13px;font:600 13px Manrope,sans-serif;cursor:pointer}
.chips button.on{background:linear-gradient(135deg,var(--g1),var(--g2));border-color:transparent}
.chips.scroll{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin:0 -14px 12px;padding:0 14px}
.step{display:grid;grid-template-columns:50px 1fr;gap:10px;padding:12px 0;border-top:1px solid var(--line)}.step:first-child{border-top:0;padding-top:0}
.step .tc{font-weight:800;color:var(--g2);font-size:13px}.step small{display:block;color:var(--mut);margin-top:4px;font-size:13px}
.copy{background:rgba(0,0,0,.3);border:1px solid var(--line);border-radius:14px;padding:12px;white-space:pre-wrap;margin-top:6px}
.in{width:100%;background:rgba(0,0,0,.3);border:1px solid var(--line);color:var(--ink);border-radius:12px;padding:12px;font:15px/1.45 Manrope,sans-serif;margin-top:4px}
textarea.in{resize:vertical}.in.mono{font:13px ui-monospace,monospace}
.stagger>*{animation:up .45s cubic-bezier(.2,.8,.2,1) backwards}
.stagger>*:nth-child(2){animation-delay:.05s}.stagger>*:nth-child(3){animation-delay:.1s}.stagger>*:nth-child(4){animation-delay:.15s}.stagger>*:nth-child(5){animation-delay:.2s}.stagger>*:nth-child(n+6){animation-delay:.25s}
@keyframes up{from{opacity:0;transform:translateY(12px)}}
nav{position:fixed;z-index:5;left:10px;right:10px;bottom:calc(10px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(4,1fr);background:rgba(18,18,28,.82);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid var(--line);border-radius:22px;padding:8px 2px 6px}
nav button{border:0;background:none;color:var(--mut);font:700 10px Manrope,sans-serif;display:flex;flex-direction:column;align-items:center;gap:3px;position:relative;padding:2px 0;cursor:pointer;white-space:nowrap}
nav svg{width:23px;height:23px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
nav button.on{color:#fff}nav button.on svg{stroke:url(#gr)}
nav .bd{position:absolute;top:-4px;left:calc(50% + 6px);background:var(--bad);color:#fff;border-radius:8px;font-size:10px;padding:0 5px;line-height:16px}
#sheet{position:fixed;inset:0;z-index:40;background:rgba(0,0,0,.6);display:flex;align-items:flex-end;opacity:0;pointer-events:none;transition:opacity .2s}
#sheet.on{opacity:1;pointer-events:auto}
#sheet .in2{background:#12121b;border:1px solid var(--line);border-radius:22px 22px 0 0;padding:22px 18px calc(22px + env(safe-area-inset-bottom));width:100%;transform:translateY(40px);transition:transform .25s}
#sheet.on .in2{transform:none}#sheet h3{margin:0 0 8px;font-size:18px}
.flowmap{position:relative;padding-left:58px}
.fs{position:relative;margin-bottom:22px;min-height:42px}.fs .dotc{position:absolute;z-index:1;left:-58px;top:0;width:42px;height:42px;border-radius:14px;display:grid;place-items:center;font-size:19px;background:linear-gradient(135deg,#2a2150,#132a3a);border:1px solid rgba(139,92,246,.45)}
.fs:not(:last-child)::before{content:"";position:absolute;left:-38px;top:50px;bottom:-14px;width:2px;background:repeating-linear-gradient(var(--g2) 0 5px,transparent 5px 10px);background-size:2px 20px;animation:vflow 1s linear infinite;opacity:.55}
@keyframes vflow{to{background-position:0 20px}}
.fs b{font-size:16px}.fs small{display:block;color:var(--mut);margin-top:3px;font-size:13.5px}
.toast{position:fixed;left:50%;bottom:104px;transform:translate(-50%,10px);background:#1c1c28;border:1px solid var(--line);padding:11px 16px;border-radius:14px;opacity:0;transition:.25s;z-index:50;font-weight:700;max-width:90vw;text-align:center}
.toast.on{opacity:1;transform:translate(-50%,0)}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
.ttl{font-size:19px;font-weight:800;line-height:1.28;letter-spacing:-.015em;margin-top:4px;text-wrap:balance}
.pro{font:600 10.5px ui-monospace,SFMono-Regular,Menlo,monospace;color:#8b8ba6;background:rgba(255,255,255,.06);border-radius:5px;padding:1px 5px;margin-left:4px;letter-spacing:.02em;white-space:nowrap;vertical-align:1px}
.hint{display:flex;gap:12px;align-items:center;background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.25);border-radius:16px;padding:12px 14px;margin-bottom:10px;cursor:pointer}
.hint.badh{background:rgba(251,113,133,.08);border-color:rgba(251,113,133,.3)}
.src{font-size:12.5px;color:var(--mut);margin-top:10px;padding-top:10px;border-top:1px solid var(--line)}
.brow{padding:8px 0;border-top:1px solid var(--line)}.brow:first-child{border-top:0}.brow .t{display:flex;justify-content:space-between;gap:8px;font-size:14px}.brow .t span{color:var(--mut);white-space:nowrap}
.spin{display:inline-block;width:14px;height:14px;border:2px solid var(--line);border-top-color:var(--g2);border-radius:50%;animation:sp .7s linear infinite;vertical-align:-2px}@keyframes sp{to{transform:rotate(360deg)}}
a{color:var(--g2)}
</style></head><body>
<svg width="0" height="0" style="position:absolute"><defs><linearGradient id="gr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a78bfa"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs></svg>
<main id="app"></main><nav id="tabs"></nav>
<div id="sheet"><div class="in2" id="sheetin"></div></div><div class="toast" id="toast"></div>
<script id="data" type="application/json">__DATA__</script>
<script>{
const D=JSON.parse(document.getElementById('data').textContent),K=D.kpi,LC=D.live||{};
const tg=window.Telegram?.WebApp;try{tg.ready();tg.expand();tg.setHeaderColor?.('#07070c');tg.setBackgroundColor?.('#07070c');tg.setBottomBarColor?.('#07070c')}catch(e){}
const IN_TG=!!tg?.initData;
const $=s=>document.querySelector(s),esc=s=>String(s??'—').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=v=>Math.round(v||0).toLocaleString('uk-UA').replace(/\s/g,' ');
const usd=v=>v==null||isNaN(v)?'—':D.cur+(v<10&&v%1?(+v).toFixed(1):fmt(v));
const hap=t=>{try{tg.HapticFeedback.impactOccurred(t||'light')}catch(e){}};
const okHap=()=>{try{tg.HapticFeedback.notificationOccurred('success')}catch(e){}};
const toast=t=>{const e=$('#toast');e.textContent=t;e.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('on'),2400)};
const err=e=>toast('Помилка: '+String(e.message||e).slice(0,110));
const ls={get:k=>{try{return localStorage.getItem(k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}},del:k=>{try{localStorage.removeItem(k)}catch(e){}}};
const confirmDo=(msg,fn)=>{if(IN_TG&&tg.showConfirm)tg.showConfirm(msg,ok=>{if(ok)fn()});else fn()};
const pl=(n,f)=>{n=Math.abs(Math.round(n));const a=n%10,b=n%100;return f[a===1&&b!==11?0:a>=2&&a<=4&&(b<10||b>=20)?1:2]};
const DAY=864e5;

/* словник: [проста назва, термін таргетолога, пояснення] */
const G={
 spend:['Витрати','Spend','Скільки грошей Meta списала за показ реклами за вибраний період.'],
 res:['Результати','Results','Те, за що ти платиш: переписки в Direct, заявки з форми або переходи в Telegram/на сайт. Залежить від мети кампанії.'],
 cards:['Розбивка по картках','Carousel card breakdown','Скільки кліків зібрала кожна картка каруселі. Таргетологи дивляться, чи гортають далі першої: якщо все на першій, решта карток не працює.'],
 cpr:['Ціна результату','Cost per result','Скільки коштує одна переписка, заявка чи перехід. Головна цифра: чим менша, тим краще. Для переписок таргетологи кажуть CPL або cost per conversation.'],
 cl:['Клієнти','Qualified / CAC','Переписки, які дійшли до дзвінка чи оплати. Їх відмічаєш ти (або вони підтягуються з таблиці). Саме вони показують, чи окупається реклама.'],
 norm:['Норма','Target CPA','Скільки максимум можна платити за один результат, щоб реклама окупалась. Рахується з твого середнього чека, частки на рекламу і того, скільки переписок стають клієнтами. Задається в ⚙ → Норми.'],
 freq:['Частота','Frequency','Скільки разів одна людина вже бачила рекламу. Більше 3 разів: люди втомлюються, реагують рідше, результат дорожчає.'],
 ctr:['Клікабельність','CTR','Скільки людей зі 100, що побачили рекламу, клікнули на неї. 1% і вище для цієї ніші нормально.'],
 cpm:['Ціна 1000 показів','CPM','Скільки коштує показати рекламу тисячі людей. Росте, коли аудиторія вузька або конкуренція велика.'],
 days:['Днів у показі','Days active','Скільки днів конкурент не вимикає рекламу. Збиткову рекламу довго не тримають, тож довгий показ означає, що вона окупається.'],
 budget:['Бюджет','Daily budget','Скільки Meta може витратити на день. За місяць виходить приблизно денний бюджет × 30. В окремий день Meta може витратити трохи більше, але за тиждень вкладеться в середнє.'],
 learn:['Навчання','Learning phase','Після запуску чи великої зміни Meta шукає, кому показувати рекламу, і цифри стрибають. Meta вважає навчання завершеним після ~50 результатів за тиждень; на малих бюджетах це недосяжно, тому я чекаю не днів, а грошей: дві норми ціни результату або 3 результати, мінімум 2 доби, максимум тиждень.'],
 place:['Плейсменти','Placements','Де саме показується реклама: стрічка Instagram, сторіс, Reels, стрічка Facebook. «Автоматично» (Advantage+ placements) зазвичай дешевше.'],
 goal:['Мета кампанії','Objective','Що Meta має приносити: переписки в Direct, заявки через форму всередині Instagram/Facebook або переходи за посиланням. Meta оптимізує показ саме під цю дію.'],
 rt:['Ретаргет','Retargeting','Показ реклами людям, які вже знають тебе: заходили в профіль, писали, реагували на пости. Зазвичай пишуть охочіше й дешевше.']};
const q=k=>`<span class="q" data-q="${k}"><svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="8.25"/><path d="M10 9v5"/><circle cx="10" cy="6.2" r=".6" fill="currentColor" stroke="none"/></svg></span>`;
const L=(k,name)=>`${name||G[k][0]}<span class="pro">${G[k][1]}</span>${q(k)}`;
function sheet(html){$('#sheetin').innerHTML=html;$('#sheet').classList.add('on');hap('soft')}
$('#sheet').onclick=e=>{if(e.target.id==='sheet'||e.target.dataset.x)$('#sheet').classList.remove('on')};
function countUp(){document.querySelectorAll('[data-cu]').forEach(el=>{if(el.dataset.done)return;el.dataset.done=1;const to=+el.dataset.cu,pre=el.dataset.pre||'',t0=performance.now();
 const f=n=>{const p=Math.min(1,(n-t0)/900),v=to*(1-Math.pow(1-p,3));el.textContent=pre+fmt(v);if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)})}
const cu=(v,pre='')=>v==null?'—':`<span data-cu="${Math.round(v)}" data-pre="${pre}">${pre}0</span>`;

/* ───── Сховище: Telegram CloudStorage (до 4096 символів на ключ), дублюється в localStorage ───── */
const CS={get:k=>new Promise(r=>{try{if(!tg?.CloudStorage||!IN_TG)throw 0;tg.CloudStorage.getItem(k,(e,v)=>r(e||!v?ls.get(k):v))}catch(e){r(ls.get(k))}}),
 set:(k,v)=>new Promise(r=>{v=String(v);ls.set(k,v);if(v.length>4000)console.warn('CS: завеликий ключ',k,v.length);try{if(!tg?.CloudStorage||!IN_TG)throw 0;tg.CloudStorage.setItem(k,v.slice(0,4096),()=>r())}catch(e){r()}}),
 del:k=>new Promise(r=>{ls.del(k);try{if(!IN_TG)throw 0;tg.CloudStorage.removeItem(k,()=>r())}catch(e){r()}})};
const CSj=async(k,d)=>{try{return JSON.parse(await CS.get(k)||'null')??d}catch(e){return d}};

/* ───── Meta Graph API ───── */
const GV=`https://graph.facebook.com/${LC.v||'v24.0'}`;
const L$={norms:null,nin:null,boot:true,token:'',ai:'',loading:false,acc:null,err:null,camps:[],sets:[],ads:[],ins:{},sins:{},crs:[],marks:[],sheet:[],sheetErr:null,sp90:0,cfg:{},ideas:[],rep:{},links:{},forms:null,leads:{}};
const meta=async(r)=>{const j=await r.json();if(j.error)throw new Error(j.error.error_user_msg||j.error.error_user_title||j.error.message);return j};
const gget=(p,t)=>fetch(`${GV}/${p}${p.includes('?')?'&':'?'}access_token=${encodeURIComponent(t||L$.token)}`).then(meta);
const gpost=(p,params,t)=>fetch(`${GV}/${p}`,{method:'POST',body:new URLSearchParams({...params,access_token:t||L$.token})}).then(meta);
const gform=(p,fd)=>{fd.append('access_token',L$.token);return fetch(`${GV}/${p}`,{method:'POST',body:fd}).then(meta)};
const ACT=()=>`act_${LC.acc}`;
const CONV='onsite_conversion.messaging_conversation_started_7d';
const RT={conv:[CONV],lead:['lead','onsite_conversion.lead_grouped','leadgen_grouped'],link:['link_click']};
const px=r=>{const o={spend:+r.spend||0,impr:+r.impressions||0,clicks:+(r.inline_link_clicks||r.clicks)||0,freq:+r.frequency||0,reach:+r.reach||0};
 for(const [k,ts] of Object.entries(RT)){let v=0;for(const t of ts){const a=(r.actions||[]).find(x=>x.action_type===t);if(a){v=+a.value;break}}o[k]=v}return o};
const add=(a,b)=>{for(const k of ['spend','impr','clicks','conv','lead','link','reach'])a[k]=(a[k]||0)+(b[k]||0);return a};
const zero=()=>({spend:0,impr:0,clicks:0,conv:0,lead:0,link:0,freq:0,reach:0});
const INS='spend,impressions,clicks,inline_link_clicks,frequency,reach,actions';

/* ───── Мети кампаній ───── */
const GOALS={
 direct:{name:'Переписки в Direct',ico:'💬',res:'conv',obj:'OUTCOME_ENGAGEMENT',desc:'Людина натискає «Написати» й одразу потрапляє у твій Direct. Найпростіше для послуг.',get norm(){return NR('conv')}},
 lead:{name:'Заявки через форму',ico:'📝',res:'lead',obj:'OUTCOME_LEADS',desc:'Форма відкривається всередині Instagram: ім\'я й телефон заповнені автоматично. Заявки бачиш тут же.',get norm(){return NR('lead')}},
 tg:{name:'Переходи в Telegram',ico:'✈️',res:'link',obj:'OUTCOME_TRAFFIC',desc:'Кнопка веде в твій Telegram чи бота. Meta шукає тих, хто клікає.',get norm(){return NR('link')}},
 site:{name:'Переходи на сайт',ico:'🌐',res:'link',obj:'OUTCOME_TRAFFIC',desc:'Кнопка веде на сайт чи лендинг. Meta шукає тих, хто клікає.',get norm(){return NR('link')}}};
const NR=r=>(L$.norms||{})[r]||{conv:K.target_cpl,lead:K.target_lead,link:K.target_click}[r];
const RES={conv:['переписка','переписки','переписок','Ціна переписки'],lead:['заявка','заявки','заявок','Ціна заявки'],link:['перехід','переходи','переходів','Ціна переходу']};
const rn=(n,r)=>`${fmt(n)} ${pl(n,RES[r])}`;
const goalOfSet=s=>{if(!s)return'direct';const og=s.optimization_goal;if(og==='LEAD_GENERATION'||og==='QUALITY_LEAD')return'lead';
 if(og==='LINK_CLICKS'||og==='LANDING_PAGE_VIEWS'){const c=L$.cfg[s.campaign_id];return c?.goal==='tg'?'tg':c?.goal==='site'?'site':'site'}return'direct'};
const goalOfCamp=cid=>L$.cfg[cid]?.goal||goalOfSet(L$.sets.find(s=>s.campaign_id===cid));
const goalOfAd=a=>goalOfSet(L$.sets.find(s=>s.id===a.adset_id));
const cost=(i,r)=>i&&i[r]?i.spend/i[r]:null;
/* Коли вже можна судити: залежить від грошей, а не від днів.
   Оголошення: витратило 2 норми або має 3 результати (мінімум 48 год), або спалило 3 норми за першу добу, або минув тиждень.
   Бюджет: після зміни група має витратити 3 норми за новим бюджетом, але не менше 2 і не більше 7 днів. */
const adReady=(ageH,spend,res,T)=>ageH>=168||(ageH>=48&&(spend>=2*T||res>=3))||(ageH>=24&&spend>=3*T);
const scaleWaitD=(T,b)=>Math.min(7,Math.max(2,Math.ceil(3*T/Math.max(b,1))));
const adWaitD=(T,b)=>Math.min(7,Math.max(2,Math.ceil(2*T/Math.max(b,1))));
const verd=(c,T,spend)=>c==null?(spend>=T*2?'bad':'learn'):c<=T?'good':c<=T*1.5?'mid':'bad';
const VL={good:'У нормі',mid:'Трохи дорожче норми',bad:'Дорого',learn:'Збирає дані'};
const alive=x=>!/DELETED|ARCHIVED/.test(x.effective_status||'');

/* ───── Завантаження ───── */
const normCr=c=>{c.texts=c.texts||[c.text||''];c.ads=c.ads||(c.ad_ids||[]).map((ad,k)=>({ad,cr:(c.crids||[])[k],k}));delete c.ad_ids;delete c.crids;delete c.ad_id;delete c.text;return c};
const saveCr=c=>{const o={...c,texts:c.texts.map(t=>(t||'').slice(0,900)),review:c.review?{...c.review,fix:(c.review.fix||[]).slice(0,4)}:undefined,preview:undefined};
 let j=JSON.stringify(o);if(j.length>4000&&o.review){o.review={...o.review,hook:o.review.hook.slice(0,120),offer:o.review.offer.slice(0,120),fix:o.review.fix.map(x=>x.slice(0,100))};j=JSON.stringify(o)}
 while(j.length>4000&&o.texts.some(t=>t)){const k=o.texts.reduce((m,t,i)=>t.length>o.texts[m].length?i:m,0);o.texts[k]=o.texts[k].slice(0,-60);j=JSON.stringify(o)}return CS.set('cr_'+c.id,j)};
const saveIdx=()=>CS.set('cr_index',JSON.stringify(L$.crs.map(c=>c.id)));
async function loadCrs(){const idx=await CSj('cr_index',[]);const out=[];for(const id of idx){const c=await CSj('cr_'+id,null);if(c)out.push(normCr(c))}L$.crs=out}
async function loadCfg(){const idx=await CSj('cmp_index',[]);L$.cfg={};for(const id of idx){const c=await CSj('cmp_'+id,null);if(c)L$.cfg[id]=c}}
const saveCfg=async(id,c)=>{L$.cfg[id]=c;await CS.set('cmp_'+id,JSON.stringify(c));await CS.set('cmp_index',JSON.stringify(Object.keys(L$.cfg)))};
async function loadIdeas(){const idx=await CSj('idea_index',[]);const out=[];for(const id of idx){const c=await CSj('idea_'+id,null);if(c)out.push(c)}L$.ideas=out}
const mkKey=d=>'mk_'+d.toISOString().slice(0,7).replace('-','');
async function loadMarks(){const now=new Date(),out=[];for(let k=0;k<3;k++){out.push(...await CSj(mkKey(new Date(now.getFullYear(),now.getMonth()-k,15)),[]))}L$.marks=out}
async function addMark(m){const key=mkKey(new Date());const arr=await CSj(key,[]);arr.push(m);await CS.set(key,JSON.stringify(arr.slice(-60)));L$.marks.push(m)}

async function liveLoad(){if(!LC.acc){render();return}
 L$.token=await CS.get('meta_token')||'';L$.ai=await CS.get('ai_key')||'';L$.gh=await CS.get('gh_token')||'';L$.links={tg:LC.tg_link,site:LC.site_link,privacy:LC.privacy,csv:'',...await CSj('links',{})};
 await loadCrs();await loadCfg();await loadMarks();await loadIdeas();L$.norms=await CSj('norms',null);L$.comps=await CSj('comps',[]);L$.nin=await CSj('norms_in',null);
 if(!L$.token){L$.boot=false;render();return}
 L$.loading=true;render();
 try{const A=ACT();
  const [acc,cm,as,ads,ai,si,s90]=await Promise.all([
   gget(`${A}?fields=name,currency,account_status,disable_reason,amount_spent,funding_source_details`),
   gget(`${A}/campaigns?fields=id,name,objective,effective_status,created_time&limit=50`),
   gget(`${A}/adsets?fields=id,name,campaign_id,daily_budget,effective_status,optimization_goal,destination_type,targeting,created_time,updated_time&limit=100`),
   gget(`${A}/ads?fields=id,name,adset_id,campaign_id,effective_status,created_time,creative{id,thumbnail_url,body},ad_review_feedback,issues_info&limit=200`),
   gget(`${A}/insights?level=ad&date_preset=last_7d&fields=ad_id,${INS}&limit=300`),
   gget(`${A}/insights?level=adset&date_preset=last_7d&fields=adset_id,${INS}&limit=100`),
   gget(`${A}/insights?date_preset=last_90d&fields=spend`)]);
  L$.acc=acc;L$.err=null;L$.camps=(cm.data||[]).filter(alive);L$.sets=(as.data||[]).filter(alive);L$.ads=(ads.data||[]).filter(alive);
  L$.ins={};for(const r of ai.data||[])L$.ins[r.ad_id]=px(r);
  L$.sins={};for(const r of si.data||[])L$.sins[r.adset_id]=px(r);
  L$.sp90=+(s90.data?.[0]?.spend||0);
  for(const c of L$.crs){let ch=false;for(const x of c.ads){const a=L$.ads.find(z=>z.id===x.ad);if(a&&!x.camp){x.camp=a.campaign_id;x.set=a.adset_id;ch=true}}if(!c.camp&&c.ads[0]?.camp){c.camp=c.ads[0].camp;ch=true}if(ch)saveCr(c)}
 }catch(e){L$.err=e.message}
 L$.loading=false;L$.boot=false;render();loadSheet()}
const tok=()=>!!(L$.token&&L$.acc&&!L$.err);
/* поки читаємо ключ і чекаємо Meta — не лякаємо «не підключено» */
const waiting=()=>(L$.boot||L$.loading)&&!L$.acc;
const waitCard=()=>`<div class="card hero" style="text-align:center;padding:34px 16px"><span class="spin" style="width:26px;height:26px;border-width:3px"></span><div style="font-weight:800;font-size:17px;margin-top:14px">Підключаюсь до кабінету…</div><div class="h2s" style="margin:4px 0 0">Беру свіжі дані з Meta</div></div>`;
const insOf=ids=>ids.reduce((a,id)=>add(a,L$.ins[id]||{}),zero());
const setsOf=cid=>L$.sets.filter(s=>s.campaign_id===cid);
const adsOf=cid=>L$.ads.filter(a=>a.campaign_id===cid);
const campIns=cid=>setsOf(cid).reduce((a,s)=>add(a,L$.sins[s.id]||{}),zero());
const liveAds=f=>L$.ads.filter(a=>f(a)&&/ACTIVE|PENDING|IN_PROCESS|REVIEW/.test(a.effective_status)).length;
const isRt=s=>(s.targeting?.custom_audiences||[]).length>0;
const dB=s=>s.daily_budget?+s.daily_budget/100:null;

/* ───── Таблиця клієнтів (Google Sheets → «Опублікувати в інтернеті» → CSV) ───── */
function csvRows(t){const rows=[];let row=[],f='',q=false;for(let i=0;i<t.length;i++){const c=t[i];
 if(q){if(c==='"'&&t[i+1]==='"'){f+='"';i++}else if(c==='"')q=false;else f+=c}else if(c==='"')q=true;else if(c===','){row.push(f);f=''}else if(c==='\n'||c==='\r'){if(c==='\r'&&t[i+1]==='\n')i++;row.push(f);rows.push(row);row=[];f=''}else f+=c}
 if(f||row.length){row.push(f);rows.push(row)}return rows}
/* будь-яке посилання на таблицю → CSV: «Опублікувати як CSV» або звичайне посилання з доступом «усі, хто має посилання» */
const csvUrl=u=>{if(/output=csv|format=csv|out:csv/.test(u))return u;const m=u.match(/spreadsheets\/d\/(e\/)?([\w-]{20,})/);if(!m)return u;
 if(m[1])return `https://docs.google.com/spreadsheets/d/e/${m[2]}/pub?output=csv`;const g=u.match(/[#&?]gid=(\d+)/);return `https://docs.google.com/spreadsheets/d/${m[2]}/gviz/tq?tqx=out:csv${g?'&gid='+g[1]:''}`};
async function loadSheet(){const u=L$.links.csv;if(!u){L$.sheet=[];return}
 try{let r;try{r=await fetch(csvUrl(u))}catch(e){throw new Error('Google не віддає таблицю: відкрий доступ «Усі, хто має посилання → Читач»')}
  if(!r.ok)throw new Error(`Google відповів ${r.status}: відкрий доступ «Усі, хто має посилання → Читач»`);const t=await r.text();
  if(/^\s*</.test(t))throw new Error('Замість таблиці прийшла сторінка входу: відкрий доступ «Усі, хто має посилання → Читач»');
  const rows=csvRows(t).filter(r=>r.some(x=>x.trim()));if(!rows.length){L$.sheet=[];L$.sheetErr=null;return}const h=rows.shift().map(x=>x.toLowerCase());
  if(!h.some(x=>/статус|status/.test(x)))throw new Error('У таблиці нема колонки «Статус»');
  const ix=re=>h.findIndex(x=>re.test(x));const iD=ix(/дат|date/),iT=ix(/статус|тип|етап|status|stage/),iS=ix(/сум|оплат.*грн|amount|sum|₴/),iA=ix(/реклам|креатив|ad/);
  const pd=s=>{s=(s||'').trim();let m=s.match(/^(\d{1,2})[./](\d{1,2})[./](\d{2,4})/);if(m)return new Date(+(m[3].length===2?'20'+m[3]:m[3]),m[2]-1,+m[1]).getTime();const v=Date.parse(s);return isNaN(v)?Date.now():v};
  L$.sheet=rows.map(r=>{const st=(r[iT]||'').toLowerCase();const s=+(String(r[iS]||'').replace(/[^\d.,]/g,'').replace(',','.'))||0;
   const t=/оплат|продаж|клієнт|paid|won|угод/.test(st)||(iT<0&&s>0)?'paid':/дзвін|дзвон|зустр|call|meet/.test(st)?'call':null;return t?{t,s,d:pd(r[iD]),ad:r[iA]||'',src:'sheet'}:null}).filter(x=>x&&Date.now()-x.d<92*DAY);L$.sheetErr=null}
 catch(e){L$.sheetErr=e.message;L$.sheet=[]}
 if(tab==='home'&&!stack.length)render()}

/* ───── ШІ (Anthropic або Gemini, ключ у CloudStorage) ───── */
const aiProv=()=>L$.ai.startsWith('sk-ant')?'anthropic':L$.ai.startsWith('AIza')?'gemini':null;
/* кадри для ШІ: фото → 1 картинка, відео → n кадрів рівномірно */
const shot=(el,w,h,max)=>{const k=Math.min(1,max/Math.max(w,h)),cv=document.createElement('canvas');cv.width=Math.round(w*k);cv.height=Math.round(h*k);cv.getContext('2d').drawImage(el,0,0,cv.width,cv.height);return {b64:cv.toDataURL('image/jpeg',.8).split(',')[1],mime:'image/jpeg'}};
async function fileImgs(f,n=6,max=1024){if(!f)return [];const u=URL.createObjectURL(f);try{
 if(!f.type.startsWith('video')){const im=new Image();im.src=u;await im.decode();return [shot(im,im.naturalWidth,im.naturalHeight,max)]}
 const v=document.createElement('video');v.muted=true;v.playsInline=true;v.preload='auto';v.src=u;
 await new Promise((r,j)=>{v.onloadeddata=r;v.onerror=j;setTimeout(j,10000)});const d=isFinite(v.duration)&&v.duration>0?v.duration:2,out=[];
 for(let i=0;i<n;i++){const t=Math.min(d-.05,d*(i+.5)/n);v.currentTime=t;const ok=await new Promise(r=>{v.onseeked=()=>r(1);setTimeout(()=>r(0),3000)});if(!ok&&i)break;
  const fr=shot(v,v.videoWidth,v.videoHeight,max);fr.t=Math.round(t);out.push(fr)}
 const uniq=out.filter((x,i)=>!i||x.b64!==out[i-1].b64);return uniq.map(x=>({...x,video:true,dur:Math.round(d)}))}catch(e){return []}finally{URL.revokeObjectURL(u)}}
async function toB64(blob){return await new Promise((r,j)=>{const fr=new FileReader();fr.onload=()=>r(String(fr.result).split(',')[1]);fr.onerror=j;fr.readAsDataURL(blob)})}
async function ai(system,user,img,heavy){const p=aiProv();if(!p)throw new Error('Додай ключ ШІ в налаштуваннях');
 let imgs=(Array.isArray(img)?img:img?[img]:[]).filter(Boolean).slice(0,16);
 if(p==='gemini')imgs=(await Promise.all(imgs.map(async x=>{if(!x.url)return x;try{const b=await (await fetch(x.url)).blob();return {b64:await toB64(b),mime:b.type||'image/jpeg'}}catch(e){return null}}))).filter(Boolean);
 if(p==='anthropic'){const content=[];for(const x of imgs)content.push({type:'image',source:x.url?{type:'url',url:x.url}:{type:'base64',media_type:x.mime,data:x.b64}});content.push({type:'text',text:user});
  const r=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'x-api-key':L$.ai,'anthropic-version':'2023-06-01','anthropic-dangerous-direct-browser-access':'true','content-type':'application/json'},
   body:JSON.stringify({model:heavy?(LC.ai_model_heavy||'claude-opus-5-5'):(LC.ai_model||'claude-sonnet-5-5'),max_tokens:4000,system,messages:[{role:'user',content}]})});const j=await r.json();if(j.error)throw new Error(j.error.message);return j.content.map(x=>x.text||'').join('')}
 const parts=imgs.map(x=>({inline_data:{mime_type:x.mime,data:x.b64}}));parts.push({text:user});
 const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${LC.gemini_model||'gemini-flash-latest'}:generateContent?key=${encodeURIComponent(L$.ai)}`,{method:'POST',headers:{'content-type':'application/json'},
  body:JSON.stringify({systemInstruction:{parts:[{text:system}]},contents:[{role:'user',parts}],generationConfig:{responseMimeType:'application/json'}})});
 const j=await r.json();if(j.error)throw new Error(j.error.message);return (j.candidates?.[0]?.content?.parts||[]).map(x=>x.text||'').join('')}
const pj=t=>{t=String(t).replace(/```(json)?/g,'');const a=t.indexOf('{');return JSON.parse(t.slice(a,t.lastIndexOf('}')+1))};
const SYSf=()=>`Ти досвідчений таргетолог і копірайтер для Meta Ads (Instagram/Facebook) в Україні. Пишеш лише українською, жива розмовна мова, без канцеляриту, без AI-кліше й без емодзі-спаму.
Правила Meta: не стверджуй особисті характеристики читача («ти власник бізнесу?», «у тебе проблеми з…»), не обіцяй гарантованих результатів, не вигадуй цифр і кейсів, яких нема в даних.
Продукт: ${D.product}
Ніша: ${D.niche}
${SKILLS}
Відповідай ТІЛЬКИ валідним JSON без пояснень.`;
function aiCtx(){const comp=D.winners.slice(0,6).map(w=>`- ${w.page_name}, ${w.days} дн: «${String(w.a?.hook?.text||w.text||'').slice(0,140)}»${w.a?.steal_this?' → взяти: '+w.a.steal_this:''}`).join('\n');
 const ours=L$.ads.map(a=>{const g=GOALS[goalOfAd(a)],i=L$.ins[a.id];return i&&i.spend?{n:a.name,b:(a.creative?.body||'').slice(0,160),c:cost(i,g.res),r:g.res,s:i.spend}:null}).filter(Boolean).sort((a,b)=>(a.c??1e9)-(b.c??1e9));
 const o=ours.length?ours.slice(0,6).map(x=>`- «${x.b||x.n}»: витрати ${Math.round(x.s)} ₴, ${x.c?'ціна результату '+Math.round(x.c)+' ₴':'результатів нема'}`).join('\n'):'ще нема статистики';
 return `Що крутиться в конкурентів довше 2 тижнів (отже окупається):\n${comp}\n\nНаша реклама за 7 днів (від кращої до гіршої):\n${o}`}

/* ───── Навігація ───── */
const IC={home:'<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',ads:'<path d="M4 7h16M4 12h16M4 17h10"/>',rep:'<path d="M4 20V11M10 20V5M16 20v-8M21 20H3"/>',ideas:'<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>'};
const TABS=[['home','Головне'],['ads','Реклама'],['rep','Звіт'],['ideas','Ідеї']];
let tab='home',stack=[];
function navbar(){const n=recs().length+rejected().length;$('#tabs').innerHTML=TABS.map(([k,l])=>`<button data-tab="${k}" class="${k===tab&&!stack.length?'on':''}"><svg viewBox="0 0 24 24">${IC[k]}</svg>${l}${k==='home'&&n?`<span class="bd">${n}</span>`:''}</button>`).join('')}
$('#tabs').onclick=e=>{const b=e.target.closest('button');if(!b)return;tab=b.dataset.tab;stack=[];hap('soft');render();if(tab==='rep')loadRep()};
const go=v=>{stack.push(v);hap();render()},back=()=>{stack.pop();render()},re=v=>{stack[stack.length-1]=v;render();return true};
try{tg.BackButton.onClick(back)}catch(e){}
function render(){navbar();const v=stack.at(-1);try{v?tg.BackButton.show():tg.BackButton.hide()}catch(e){}
 $('#app').innerHTML=(v&&!IN_TG?`<button class="how" data-back="1" style="margin:2px 0 12px">‹ Назад</button>`:'')+`<div class="${v?'':'stagger'}">${(v||V[tab])()}</div>`;
 if(v)window.scrollTo(0,0);requestAnimationFrame(()=>{charts();countUp()})}
const top=t=>`<div class="top"><div><div class="who">${esc(t||'ШІ-таргетолог')}${L$.loading?' · <span class="spin"></span>':''}</div><div class="name">${esc(D.client)}</div></div><button class="how" data-set="1" aria-label="Налаштування" style="padding:9px 11px;font-size:16px">⚙</button></div>`;
const V={};
const re0=()=>{if(stack.length)re(stack.at(-1));else render()};

/* ───── Підготовка ───── */
const steps=()=>[
 ['tok',tok(),'Кабінет Meta підключено',L$.err?'Meta відповіла: '+esc(L$.err):'Встав ключ доступу Meta, який ти згенерував для targetolog.'],
 ['card',!!L$.acc?.funding_source_details,'Карта для оплати реклами','Прив\'язується тільки в Meta, у застосунку оплати нема.'],
 ['camp',L$.camps.length>0,'Перша кампанія','Обери мету: переписки, заявки чи переходи.'],
 ['cr',L$.crs.length>0||L$.ads.length>0,'Перший креатив','Фото чи відео з галереї + текст.'],
 ['live',L$.ads.length>0,'Реклама запущена','Відкрий креатив і натисни «Запустити».']];
const stepBtn={tok:`<button class="btn" data-key="1">Вставити ключ Meta</button>`,card:`<button class="btn ghost" data-open="https://business.facebook.com/billing_hub/payment_settings/?asset_id=${LC.acc}">Відкрити оплату в Meta</button>`,
 camp:`<button class="btn" data-newcamp="1">＋ Створити кампанію</button>`,cr:`<button class="btn" data-add="1">＋ Додати креатив</button>`};
function setupCard(){if(!LC.acc)return'';const st=steps();if(st.every(x=>x[1]))return'';const next=st.find(x=>!x[1]);
 return `<div class="card"><div class="lab" style="margin-bottom:8px">Підготовка до запуску · ${st.filter(x=>x[1]).length} з ${st.length}</div>
 ${st.map(([k,ok,t,h])=>`<div style="display:flex;gap:10px;padding:7px 0;${ok?'opacity:.55':''}"><div style="width:22px;height:22px;border-radius:50%;flex:none;display:grid;place-items:center;font-size:12px;${ok?'background:linear-gradient(135deg,var(--g1),var(--g2))':'border:2px solid '+(k===next[0]?'var(--g2)':'var(--line)')}">${ok?'✓':''}</div><div><b style="font-size:14.5px">${t}</b>${!ok&&k===next[0]?`<small style="display:block;color:var(--mut);margin-top:2px">${h}</small>`:''}</div></div>`).join('')}
 ${L$.loading?'':stepBtn[next[0]]||''}</div>`}

/* ───── Рішення ШІ (правила таргетолога над живими даними) ───── */
function recs(){if(!tok())return[];const out=[],today=new Date().toISOString().slice(0,10);let dis={};try{dis=JSON.parse(ls.get('dis_'+today)||'{}')}catch(e){}
 const active=L$.ads.filter(a=>a.effective_status==='ACTIVE');const perSet={};for(const a of active)perSet[a.adset_id]=(perSet[a.adset_id]||0)+1;
 for(const a of active){const g=GOALS[goalOfAd(a)],T=g.norm,r=g.res,i=L$.ins[a.id]||zero();if(!adReady((Date.now()-new Date(a.created_time))/36e5,i.spend,i[r]||0,T))continue;
  const c=cost(i,r),can=perSet[a.adset_id]>1;
  if(!i[r]&&i.spend>=2*T)out.push(can?{id:'p'+a.id,kind:'pause',ad:a.id,title:`Вимкнути «${a.name}»`,why:`${usd(i.spend)} за тиждень і 0 ${RES[r][2]}. Норма ${usd(T)} за ${RES[r][0]}.`,btn:'Вимкнути'}:
   {id:'r'+a.id,kind:'new',title:`Заміни «${a.name}»`,why:`${usd(i.spend)} і жодного результату, але це єдине оголошення в групі: вимкнеш, і реклама зупиниться. Додай новий креатив, потім вимкнемо цей.`,btn:'Додати креатив'});
  else if(i[r]>=3&&c>1.5*T&&can)out.push({id:'p'+a.id,kind:'pause',ad:a.id,title:`Вимкнути «${a.name}»`,why:`${RES[r][3]} ${usd(c)}, у ${(c/T).toFixed(1)} раза дорожче норми. Гроші краще віддати кращим оголошенням.`,btn:'Вимкнути'});
  if(i.freq>3.2)out.push({id:'f'+a.id,kind:'new',title:`Люди втомились від «${a.name}»`,why:`Одна людина бачила її вже ${i.freq.toFixed(1)} раза. Реакція падатиме, пора новий креатив.`,btn:'Додати креатив'})}
 for(const s of L$.sets.filter(x=>x.effective_status==='ACTIVE')){const g=GOALS[goalOfSet(s)],si=L$.sins[s.id]||zero(),c=cost(si,g.res),b=dB(s),last=+ls.get('bch_'+s.id)||0;
  if(b&&si[g.res]>=5&&c<=g.norm&&Date.now()-Math.max(last,new Date(s.updated_time||s.created_time).getTime(),new Date(s.created_time).getTime())>scaleWaitD(g.norm,b)*DAY)out.push({id:'s'+s.id,kind:'scale',set:s.id,val:Math.round(b*1.2),title:`Додати бюджет «${s.name}»`,why:`${RES[g.res][3]} ${usd(c)} при нормі ${usd(g.norm)}, ${rn(si[g.res],g.res)} за тиждень. Можна обережно додати 20%: ${usd(b)} → ${usd(Math.round(b*1.2))} на день.`,btn:'Додати 20%'})}
 return out.filter(r=>!dis[r.id])}
const rejected=()=>L$.ads.filter(a=>/DISAPPROVED|WITH_ISSUES/.test(a.effective_status));
const reasons=a=>{const out=[];const f=a.ad_review_feedback||{};for(const grp of Object.values(f))if(grp&&typeof grp==='object')for(const [k,v] of Object.entries(grp))out.push(typeof v==='string'?v:k);
 for(const x of a.issues_info||[])out.push(x.error_summary||x.error_message);return [...new Set(out.filter(Boolean))]};
const recCard=()=>{const r=recs(),rj=rejected();let h='';
 if(rj.length)h+=`<h2>Відхилено Meta</h2>`+rj.map(a=>`<div class="hint badh" data-adlive="${a.id}"><div class="ico i-bad">!</div><div class="tx" style="flex:1"><b>${esc(a.name)}</b><small style="display:block;color:var(--mut);margin-top:3px">${esc((reasons(a)[0]||'Причину видно в Meta').slice(0,140))}</small></div><span class="chev">›</span></div>`).join('');
 if(!r.length)return h+(tok()&&L$.ads.length?`<h2>Рішення</h2><div class="card">Все в нормі, рішень не треба. Перевіряю щоразу, як відкриваєш застосунок, і щоранку пишу в Telegram.</div>`:'');
 return h+`<h2>Рішення</h2><p class="h2s">Перевірив рекламу за правилами таргетолога. Нове оголошення оцінюю, коли воно витратить дві норми ціни результату або набере 3 результати, але не раніше ніж за 2 доби. На малому бюджеті це довше, на великому швидше ${q('learn')}</p>`+r.map(x=>`<div class="card"><div style="display:flex;gap:12px"><div class="ico ${x.kind==='pause'?'i-bad':x.kind==='scale'?'i-good':'i-mid'}" style="font-size:${x.kind==='pause'?13:18}px">${x.kind==='pause'?'❚❚':x.kind==='scale'?'↗':'↻'}</div><div style="flex:1"><b>${esc(x.title)}</b><div style="color:var(--mut);font-size:13.5px;margin-top:4px">${x.why}</div></div></div>
 <div class="row2"><button class="btn ${x.kind==='pause'?'bad':x.kind==='scale'?'good':''}" data-rec="${x.id}">${x.btn}</button><button class="btn ghost" data-recno="${x.id}">Не зараз</button></div></div>`).join('')};
async function recClick(d){
 if(d.recno){const k='dis_'+new Date().toISOString().slice(0,10);let dis={};try{dis=JSON.parse(ls.get(k)||'{}')}catch(e){}dis[d.recno]=1;ls.set(k,JSON.stringify(dis));render();return true}
 if(d.rec){const r=recs().find(x=>x.id===d.rec);if(!r)return true;if(r.kind==='new'){draft={};go(addView());return true}
  confirmDo(r.title+'?',async()=>{try{if(r.kind==='pause'){await gpost(r.ad,{status:'PAUSED'});toast('⏸ Вимкнено')}else{await gpost(r.set,{daily_budget:String(r.val*100)});ls.set('bch_'+r.set,Date.now());toast('✓ Бюджет збільшено')}okHap();await liveLoad()}catch(e){err(e)}});return true}
 return false}

/* ───── Головне ───── */
function totals(){const t=zero();for(const v of Object.values(L$.ins))add(t,v);return t}
/* витрати по кожному типу результату окремо, щоб ціна переписки не включала гроші кампанії з формами */
const byRes=rows=>{const o={conv:0,lead:0,link:0};for(const [res,i] of rows)o[res]+=i.spend;return o};
const cpr=(t,sp,r)=>t[r]&&sp[r]?sp[r]/t[r]:null;
const heroCard=()=>{const t=totals(),types=Object.keys(RES).filter(r=>t[r]),main=types[0]||'conv';
 const sp=byRes(L$.ads.map(a=>[GOALS[goalOfAd(a)].res,L$.ins[a.id]||zero()]));
 const goal=Object.values(GOALS).find(g=>g.res===main),c=cpr(t,sp,main),v=verd(c,goal.norm,sp[main]);
 return `<div class="card hero"><div class="lab">${L('cpr',RES[main][3])}</div><div class="big">${c!=null?cu(c,D.cur):'—'}</div>
 ${c!=null?`<span class="pill p-${v}">${VL[v]}</span> <span style="color:var(--mut);font-size:13px">норма ${usd(goal.norm)} ${q('norm')}</span>`:`<span class="pill p-learn">${t.spend?'Ще нема результатів':'Реклама ще не крутилась'}</span>`}
 <div class="funnel"><div class="fn"><b>${cu(t.spend,D.cur)}</b><span>витрати ${q('spend')}</span></div><div class="flow"></div><div class="fn hl"><b>${cu(t[main])}</b><span>${RES[main][2]} ${q('res')}</span></div></div>
 ${types.length>1?`<div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:center;margin-top:10px">${types.filter(r=>r!==main).map(r=>`<span class="chip">${rn(t[r],r)} · ${usd(cpr(t,sp,r))}</span>`).join('')}</div>`:''}
 <div style="color:var(--mut);font-size:12px;margin-top:10px;text-align:center">за останні 7 днів · <a data-tab2="rep" style="cursor:pointer">детальний звіт ›</a></div></div>`};
const clientsCard=()=>{if(!tok()||(!L$.sp90&&!L$.marks.length&&!L$.sheet.length&&!L$.links.csv))return'';const all=[...L$.marks,...L$.sheet],calls=all.filter(m=>m.t==='call').length,paid=all.filter(m=>m.t==='paid'),rev=paid.reduce((a,m)=>a+(m.s||0),0),sp=L$.sp90;
 return `<h2>Клієнти з реклами</h2><p class="h2s">За 90 днів: витрачено ${usd(sp)}. ${L$.links.csv?'Підтягую з твоєї таблиці + ручні відмітки.':'Відмічай, хто дійшов до дзвінка й оплати, або підключи таблицю в налаштуваннях.'} ${q('cl')}</p>
 ${L$.sheetErr?`<div class="hint badh" data-set="1"><div class="ico i-bad">!</div><div class="tx" style="flex:1"><small style="color:var(--ink)">${L$.sheetErr}</small></div></div>`:''}
 <div class="mg"><div class="m"><span>Дзвінки <span class="pro">Qualified</span></span><b>${calls}</b></div><div class="m"><span>Ціна дзвінка <span class="pro">CPQL</span></span><b>${calls?usd(sp/calls):'—'}</b></div>
 <div class="m"><span>Оплати <span class="pro">Sales</span></span><b>${paid.length}${rev?' · '+usd(rev):''}</b></div><div class="m"><span>Ціна клієнта <span class="pro">CAC</span></span><b>${paid.length?usd(sp/paid.length):'—'}</b></div></div>
 ${rev&&sp?`<div class="card" style="text-align:center">На кожну 1 ₴ реклами повернулось <b style="color:var(--${rev>=sp?'good':'bad'})">${(rev/sp).toFixed(1)} ₴</b> <span class="pro">ROAS</span></div>`:''}
 <button class="btn ghost" data-mark="1">＋ Відмітити клієнта</button>`};
V.home=()=>{if(!LC.acc)return top()+`<div class="card">Кабінет не налаштований.</div>`;if(waiting())return top()+waitCard();
 if(!tok())return top()+setupCard()+`<div class="card hero"><div class="lab">Твоя реклама</div><div style="font-size:22px;font-weight:800;margin:6px 0">${L$.loading?'Перевіряю кабінет…':L$.token?'Meta не відповіла':'Кабінет не підключено'}</div><div class="h2s" style="margin:0">${L$.err?esc(L$.err):'Встав ключ Meta, і тут з\'являться витрати, ціна результату й рішення.'}</div></div>`;
 return top('Останні 7 днів')+setupCard()+(L$.ads.length?heroCard():'')+`<div class="item" data-askv="1"><div class="ico i-ai">🧠</div><div class="tx"><b>Спитати ШІ-таргетолога</b><small>${L$.norms?'Що змінити, чому дорого, що запускати':'Почни з норм: скільки можна платити за переписку'}</small></div><span class="chev">›</span></div>`+recCard()+clientsCard()+(L$.ads.length?'':`<h2>Поки готуєш креативи</h2><div class="card" data-tab2="ideas" style="cursor:pointer"><b>${D.concepts.length+L$.ideas.length} готових сценаріїв і ${CG.length} конкурентів</b><div class="h2s" style="margin:4px 0 0">у вкладці «Ідеї» ›</div></div>`)};

/* ───── Реклама: кампанії + креативи ───── */
const campItem=c=>{const g=GOALS[goalOfCamp(c.id)],i=campIns(c.id),cpr=cost(i,g.res),v=c.effective_status==='ACTIVE'?verd(cpr,g.norm,i.spend):'learn',b=setsOf(c.id).filter(s=>s.effective_status==='ACTIVE').reduce((a,s)=>a+(dB(s)||0),0);
 return `<div class="item" data-camp="${c.id}"><div class="ico i-${v}" style="font-size:19px">${g.ico}</div><div class="tx"><b>${esc(c.name)}</b><small>${c.effective_status!=='ACTIVE'?'на паузі · '+g.name:liveAds(a=>a.campaign_id===c.id)?`${usd(b)}/день · ${g.name}`:'чекає креатив · не витрачає'}</small></div><div class="val">${cpr!=null?usd(cpr):usd(i.spend)}<small>${cpr!=null?'за '+RES[g.res][0]:'за 7 дн'}</small></div></div>`};
const crSt=c=>{if(!c.ads.length)return c.error?['p-bad','помилка']:['p-mid','чернетка'];const st=c.ads.map(x=>L$.ads.find(a=>a.id===x.ad)?.effective_status).filter(Boolean);
 return st.includes('DISAPPROVED')?['p-bad','відхилено Meta']:st.includes('WITH_ISSUES')?['p-bad','є проблема']:st.includes('ACTIVE')?['p-good','у рекламі']:st.some(s=>/REVIEW|PENDING|IN_PROCESS/.test(s))?['p-mid','на перевірці Meta']:st.includes('PAUSED')||st.includes('CAMPAIGN_PAUSED')||st.includes('ADSET_PAUSED')?['p-learn','на паузі']:['p-learn',st[0]?'не показується':'видалено в Meta']};
const crIns=c=>insOf(c.ads.map(x=>x.ad));
const crItem=c=>{const s=crSt(c),i=crIns(c),g=c.camp?GOALS[goalOfCamp(c.camp)]:null;return `<div class="item" data-cr="${c.id}">${c.thumb?`<img class="th" src="${esc(c.thumb)}">`:`<div class="ico i-ai">${c.kind==='video'?'🎬':c.kind==='carousel'?'🎠':'🖼'}</div>`}<div class="tx"><b>${esc(c.headline||c.texts[0].slice(0,50)||'Без назви')}</b><small>${c.ads.length&&g?`${usd(i.spend)} · ${rn(i[g.res],g.res)} за 7 дн`:esc((c.texts[0]||'').slice(0,60))}</small><span class="pill ${s[0]}" style="margin-top:8px;padding:3px 10px;font-size:12.5px">${s[1]}</span></div><span class="chev">›</span></div>`};
V.ads=()=>{if(waiting())return top()+waitCard();if(!tok())return top()+setupCard();
 return top('Кампанії й креативи')+`<h2 style="margin-top:6px">Кампанії</h2><p class="h2s">Кожна кампанія має свою мету, бюджет і аудиторію ${q('goal')}</p>
 ${L$.camps.map(campItem).join('')||'<div class="card">Кампаній ще нема. Почни з переписок у Direct: для послуг це найпростіше.</div>'}
 <button class="btn${L$.camps.length?' ghost':''}" data-newcamp="1">＋ Нова кампанія</button>
 <h2>Креативи</h2><p class="h2s">Фото чи відео з телефона + текст. Запуск одним дотиком у будь-яку кампанію.</p>
 ${L$.crs.slice().reverse().map(crItem).join('')||`<div class="card" style="text-align:center"><div style="font-size:30px">📤</div><b>Креативів ще нема</b><div class="h2s" style="margin:6px 0 0">Можна взяти готовий текст із вкладки «Ідеї» або попросити ШІ написати.</div></div>`}
 <button class="btn ghost" data-add="1">＋ Додати креатив</button>`};

/* кампанія */
const campView=cid=>()=>{const c=L$.camps.find(x=>x.id===cid);if(!c)return'<div class="card">Кампанію не знайдено.</div>';const gk=goalOfCamp(cid),g=GOALS[gk],i=campIns(cid),cpr=cost(i,g.res),sets=setsOf(cid),ads=adsOf(cid),cf=L$.cfg[cid]||{};
 const v=verd(cpr,g.norm,i.spend);
 return `<div class="card hero"><div class="lab">${g.ico} ${g.name}</div><div class="ttl" style="margin:4px 0 10px">${esc(c.name)}</div>
  ${c.effective_status!=='ACTIVE'?'<span class="pill p-learn">На паузі</span>':liveAds(a=>a.campaign_id===cid)?`<span class="pill p-${v}">${VL[v]}</span>`:'<span class="pill p-mid">Чекає креатив</span><div class="h2s" style="margin:8px 0 0">Кампанія увімкнена, але оголошень у ній нема, тому Meta нічого не показує й не списує. Додай креатив нижче.</div>'}${cf.link?`<div class="h2s" style="margin:10px 0 0">Посилання: ${esc(cf.link)}</div>`:''}</div>
 <div class="mg"><div class="m"><span>Витрати за 7 дн ${q('spend')}</span><b>${usd(i.spend)}</b></div><div class="m"><span>${RES[g.res][2][0].toUpperCase()+RES[g.res][2].slice(1)} ${q('res')}</span><b>${fmt(i[g.res])}</b></div>
  <div class="m"><span>${RES[g.res][3]} ${q('cpr')}</span><b>${usd(cpr)}</b></div><div class="m"><span>Норма ${q('norm')}</span><b>${usd(g.norm)}</b></div></div>
 <h2>Групи й бюджет</h2><p class="h2s">Тут бюджет, аудиторія й плейсменти ${q('budget')}</p>
 ${sets.map(s=>{const si=L$.sins[s.id]||zero(),on=s.effective_status==='ACTIVE';return `<div class="item" data-set2="${s.id}"><div class="ico ${on?'i-good':'i-learn'}">${isRt(s)?'↺':on?'₴':'❚❚'}</div><div class="tx"><b>${esc(s.name)}</b><small>${!on?'на паузі':liveAds(a=>a.adset_id===s.id)?'працює':'нема оголошень'} · ${esc(audSum(parseT(s.targeting)))} · ${usd(si.spend)} → ${rn(si[g.res],g.res)}</small></div><div class="val">${usd(dB(s))}<small>на день</small></div></div>`}).join('')}
 ${sets.some(isRt)||!sets.length?'':`<button class="btn ghost" data-rt="${cid}">＋ Ретаргет на тих, хто знає @${esc(LC.ig_name||'тебе')}</button>`}
 ${gk==='lead'?`<h2>Заявки з форми</h2><div id="leads">${leadsHtml(cf.form)}</div>`:''}
 <h2>Оголошення</h2>${ads.map(adRow).join('')||'<div class="card">Тут ще нема оголошень. Додай креатив і запусти його в цю кампанію.</div>'}
 <button class="btn" data-add="1" data-addcamp="${cid}">＋ Креатив у цю кампанію</button>
 ${c.effective_status==='ACTIVE'?`<button class="btn bad" data-cpause="${cid}">⏸ Зупинити кампанію</button>`:`<button class="btn good" data-cresume="${cid}">▶ Увімкнути кампанію</button>`}`};
const adRow=a=>{const g=GOALS[goalOfAd(a)],i=L$.ins[a.id]||zero(),c=cost(i,g.res),v=a.effective_status!=='ACTIVE'?(/DISAPPROVED|ISSUES/.test(a.effective_status)?'bad':'learn'):verd(c,g.norm,i.spend);
 const st={ACTIVE:v==='good'?'Приносить '+RES[g.res][2]+' дешево':v==='bad'?(c?'Дорого':'Витрачає без результату'):v==='mid'?'Трохи дорожче норми':'Збирає дані',PAUSED:'На паузі',DISAPPROVED:'Відхилено Meta',WITH_ISSUES:'Є проблема',PENDING_REVIEW:'На перевірці Meta',IN_PROCESS:'Обробляється',CAMPAIGN_PAUSED:'Кампанія на паузі',ADSET_PAUSED:'Група на паузі'}[a.effective_status]||a.effective_status;
 return `<div class="item" data-adlive="${a.id}">${a.creative?.thumbnail_url?`<img class="th" src="${esc(a.creative.thumbnail_url)}">`:`<div class="ico i-${v}">📣</div>`}<div class="tx"><b>${esc(a.name)}</b><small style="color:var(--${v==='learn'?'mut':v})">${st}</small></div><div class="val">${c!=null?usd(c)+'<small>за '+RES[g.res][0]+'</small>':usd(i.spend)+'<small>витрати</small>'}</div></div>`};
const adLiveView=id=>()=>{const a=L$.ads.find(x=>x.id===id);if(!a)return'';const g=GOALS[goalOfAd(a)],i=L$.ins[id]||zero(),rs=reasons(a),mine=L$.crs.find(c=>c.ads.some(x=>x.ad===id));
 const m=(k,n,val)=>`<div class="m"><span>${n||G[k][0]} ${q(k)}</span><b>${val}</b><span class="pro" style="margin:4px 0 0;display:inline-block">${G[k][1]}</span></div>`;
 return `<div class="card hero"><div class="lab">${g.ico} ${g.name}</div><div class="ttl" style="margin:6px 0">${esc(a.name)}</div>${a.creative?.thumbnail_url?`<img src="${esc(a.creative.thumbnail_url)}" style="width:100%;border-radius:14px;margin-top:8px">`:''}
  ${a.creative?.body?`<div class="copy" style="margin-top:10px">${esc(a.creative.body)}</div>`:''}</div>
 ${rs.length||/DISAPPROVED|WITH_ISSUES/.test(a.effective_status)?rejCard(rs,mine):''}
 <div class="mg">${m('spend','',usd(i.spend))}${m('res',RES[g.res][2][0].toUpperCase()+RES[g.res][2].slice(1),fmt(i[g.res]))}${m('cpr',RES[g.res][3],usd(cost(i,g.res)))}${m('ctr','',i.impr?(i.clicks/i.impr*100).toFixed(2)+'%':'—')}${m('freq','',i.freq?i.freq.toFixed(1):'—')}${m('cpm','',i.impr?usd(i.spend/i.impr*1000):'—')}</div>
 <p class="h2s">За останні 7 днів.</p>
 ${mine?`<button class="btn ghost" data-cr="${mine.id}">Відкрити креатив і тексти</button>`:''}
 ${a.effective_status==='ACTIVE'?`<button class="btn bad" data-pause="${id}">⏸ Поставити на паузу</button>`:a.effective_status==='PAUSED'?`<button class="btn good" data-resume="${id}">▶ Відновити показ</button>`:''}`};
const rejCard=(rs,mine)=>`<div class="card" style="border-color:rgba(251,113,133,.4)"><div class="l" style="color:var(--bad)">Чому Meta не пропускає</div>${rs.map(r=>`<div style="margin-top:6px">• ${esc(r)}</div>`).join('')||'<div>Meta не вказала причину в API. Подивись у Business Support.</div>'}
 <div class="h2s" style="margin:10px 0 0">Що робити: найчастіше достатньо змінити текст (без «ти»-звернень до особистих рис, обіцянок гарантованого результату, «до/після»). Якщо впевнений, що відхилено помилково, запроси повторну перевірку.</div>
 ${mine?`<button class="btn" data-cr="${mine.id}">Змінити текст і перезапустити</button>`:''}<button class="btn ghost" data-open="https://www.facebook.com/business-support-home/">Оскаржити в Meta</button>
 <button class="btn ghost sm" data-open="https://business.facebook.com/accountquality/">Якість акаунта</button></div>`;

/* ───── Нова кампанія ───── */
const PL={ig_feed:['Instagram стрічка','instagram','stream'],ig_story:['Instagram сторіс','instagram','story'],ig_reels:['Instagram Reels','instagram','reels'],fb_feed:['Facebook стрічка','facebook','feed']};
const defAud=()=>({cities:[],radius:25,ageMin:23,ageMax:60,gender:0,adv:true,place:[]});
function buildT(a,rt){const geo=a.cities&&a.cities.length?{cities:a.cities.map(c=>({key:c.key,radius:a.radius||25,distance_unit:'kilometer'}))}:{countries:LC.countries||['UA']};
 const t=a.adv&&!rt?{geo_locations:geo,age_min:18,age_max:65,targeting_automation:{advantage_audience:1}}:{geo_locations:geo,age_min:a.ageMin||18,age_max:a.ageMax||65,...(a.gender?{genders:[a.gender]}:{}),targeting_automation:{advantage_audience:0}};
 if(rt)t.custom_audiences=rt;
 if(a.place&&a.place.length){const ps=a.place.map(k=>PL[k]);t.publisher_platforms=[...new Set(ps.map(p=>p[1]))];const ig=ps.filter(p=>p[1]==='instagram').map(p=>p[2]),fb=ps.filter(p=>p[1]==='facebook').map(p=>p[2]);
  if(ig.length)t.instagram_positions=ig;if(fb.length)t.facebook_positions=fb;t.device_platforms=['mobile','desktop']}
 return t}
function parseT(t){t=t||{};const g=t.geo_locations||{};const a={cities:(g.cities||[]).map(c=>({key:c.key,name:c.name||c.key,radius:c.radius})),radius:(g.cities||[])[0]?.radius||25,
 ageMin:t.age_min||18,ageMax:t.age_max||65,gender:(t.genders||[])[0]||0,adv:t.targeting_automation?.advantage_audience===1,place:[]};
 for(const [k,p] of Object.entries(PL))if((t.publisher_platforms||[]).includes(p[1])&&(t[p[1]+'_positions']||[]).includes(p[2]))a.place.push(k);return a}
const audSum=a=>(a.cities&&a.cities.length?a.cities.map(c=>c.name).join(', ')+` +${a.radius} км`:'вся Україна')+' · '+(a.adv?'авто':`${a.ageMin}–${a.ageMax}${a.gender===1?' ч':a.gender===2?' ж':''}`)+(a.place&&a.place.length?' · '+a.place.length+' плейсм.':'');
let nc=null;
const placeHtml=(a,gk)=>`<div class="chips"><button class="${!a.place.length?'on':''}" data-pauto="1">Автоматично</button>${Object.entries(PL).filter(([k])=>gk!=='direct'||k!=='fb_feed').map(([k,p])=>`<button class="${a.place.includes(k)?'on':''}" data-pl="${k}">${p[0]}</button>`).join('')}</div>
 <div class="h2s" style="margin:8px 0 0">${a.place.length?'Показуємо тільки у вибраних місцях.':'Meta сама розподіляє покази туди, де дешевше. Для малого бюджету зазвичай найкраще.'}</div>`;
const newCampView=()=>()=>{const n=nc,g=GOALS[n.goal];
 return `<h2 style="margin-top:6px">Нова кампанія</h2>
 <div class="l" style="margin:14px 2px 6px">1 · Що має приносити реклама ${q('goal')}</div>
 ${Object.entries(GOALS).map(([k,x])=>`<div class="item ${n.goal===k?'sel':''}" data-ngoal="${k}"><div class="ico i-ai">${x.ico}</div><div class="tx"><b>${x.name}</b><small>${x.desc}</small></div></div>`).join('')}
 ${n.goal==='tg'||n.goal==='site'?`<div class="card"><div class="l">Куди веде кнопка</div><input id="nlink" class="in" value="${esc(n.link||'')}" placeholder="${n.goal==='tg'?'https://t.me/…':'https://…'}"></div>`:''}
 ${n.goal==='lead'?`<div class="card"><div class="l">Форма заявки</div><div id="nforms">${formsHtml()}</div></div>`:''}
 <div class="card"><div class="l">2 · Бюджет на день ${q('budget')}</div><div class="chips">${[50,100,135,200,300].map(v=>`<button class="${n.budget==v?'on':''}" data-nbud="${v}">${v} ₴</button>`).join('')}</div>
  <div style="display:flex;align-items:center;gap:8px;margin-top:10px"><input id="nbudin" class="in" inputmode="numeric" value="${n.budget}" style="margin:0;max-width:140px"><span style="color:var(--mut)">₴ на день, свою суму</span></div>
  <div class="h2s" id="nbm" style="margin:8px 0 0">≈ ${usd(n.budget*30.4)} на місяць. Мінімум ${MINB} ₴. Карта списується в Meta.</div></div>
 <div class="card"><div class="l">3 · Кому показувати</div><div class="item" data-naud="1" style="margin:6px 0 0;padding:12px"><div class="tx"><b>${esc(audSum(n.aud))}</b><small>змінити місто, вік, стать</small></div><span class="chev">›</span></div></div>
 <div class="card"><div class="l">4 · Де показувати ${q('place')}</div>${placeHtml(n.aud,n.goal)}</div>
 <div class="card"><div class="l">Назва (необов'язково)</div><input id="nname" class="in" value="${esc(n.name||'')}" placeholder="${esc(g.name)}"></div>
 <button class="btn" data-ncreate="1">Створити кампанію</button><p class="h2s" style="margin-top:10px">Без оголошень кампанія нічого не витрачає. Далі додаєш креатив і запускаєш у неї.</p>`};
const formsHtml=()=>L$.forms==null?'<span class="spin"></span> завантажую форми…':(L$.forms.err?`<div style="color:var(--bad)">${esc(L$.forms.err)}</div>`:'')+
 `<div class="chips">${(L$.forms.list||[]).map(f=>`<button class="${nc?.form===f.id?'on':''}" data-nform="${f.id}">${esc(f.name)}</button>`).join('')}<button class="${nc?.form==='new'?'on':''}" data-nform="new">＋ Нова: ім'я + телефон</button></div>
 ${nc?.form==='new'?`<div class="h2s" style="margin:8px 0 0">Створю коротку форму. Для неї Meta вимагає політику конфіденційності: ${L$.links.privacy?`беру <a data-open="${esc(L$.links.privacy)}">${esc(L$.links.privacy)}</a>`:'додай посилання в налаштуваннях'}.</div>`:''}`;
async function pageTok(){if(L$.ptok)return L$.ptok;const j=await gget(`${LC.page}?fields=access_token`);if(!j.access_token)throw new Error('Нема доступу до сторінки: признач сторінку системному користувачу з повним доступом');return L$.ptok=j.access_token}
async function loadForms(){try{const pt=await pageTok();const j=await gget(`${LC.page}/leadgen_forms?fields=id,name,status&limit=50`,pt);L$.forms={list:(j.data||[]).filter(f=>f.status==='ACTIVE')}}catch(e){L$.forms={list:[],err:e.message}}
 const el=$('#nforms');if(el)el.innerHTML=formsHtml()}
async function createForm(){const pt=await pageTok();if(!L$.links.privacy)throw new Error('Додай посилання на політику конфіденційності в налаштуваннях');
 const j=await gpost(`${LC.page}/leadgen_forms`,{name:'Заявка · ім\'я + телефон · '+new Date().toLocaleDateString('uk-UA'),locale:'uk_UA',
  questions:JSON.stringify([{type:'FULL_NAME'},{type:'PHONE'}]),privacy_policy:JSON.stringify({url:L$.links.privacy,link_text:'Політика конфіденційності'}),
  thank_you_page:JSON.stringify({title:'Дякую!',body:'Я напишу або зателефоную протягом дня.',button_type:'VIEW_WEBSITE',button_text:'Мій Instagram',website_url:LC.link||'https://www.instagram.com/'})},pt);return j.id}
function setParams(goal,name,cid,budget,targeting){const p={name,campaign_id:cid,status:'ACTIVE',daily_budget:String(Math.round(budget*100)),billing_event:'IMPRESSIONS',bid_strategy:'LOWEST_COST_WITHOUT_CAP',targeting:JSON.stringify(targeting)};
 if(goal==='direct')Object.assign(p,{destination_type:'INSTAGRAM_DIRECT',optimization_goal:'CONVERSATIONS',promoted_object:JSON.stringify({page_id:LC.page})});
 else if(goal==='lead')Object.assign(p,{destination_type:'ON_AD',optimization_goal:'LEAD_GENERATION',promoted_object:JSON.stringify({page_id:LC.page})});
 else Object.assign(p,{destination_type:'WEBSITE',optimization_goal:'LINK_CLICKS'});return p}
async function createCamp(n){if(!(n.budget>=MINB))throw new Error(`Бюджет мінімум ${MINB} ₴ на день`);if((n.goal==='tg'||n.goal==='site')&&!/^https?:\/\//.test(n.link||''))throw new Error('Вкажи посилання, що починається з https://');
 if(n.goal==='lead'&&!n.form)throw new Error('Обери форму заявки');
 let form=n.form;if(form==='new')form=await createForm();
 const g=GOALS[n.goal],name=n.name||g.name;
 const cid=(await gpost(`${ACT()}/campaigns`,{name,objective:g.obj,status:'ACTIVE',special_ad_categories:'[]',buying_type:'AUCTION',is_adset_budget_sharing_enabled:'false'})).id;
 try{await gpost(`${ACT()}/adsets`,setParams(n.goal,'Основна · '+name,cid,n.budget,buildT(n.aud)))}catch(e){try{await gpost(cid,{status:'DELETED'})}catch(x){}throw e}
 await saveCfg(cid,{goal:n.goal,link:n.link||'',form:form||''});await CS.set('aud',JSON.stringify(n.aud));return cid}

/* група (адсет): бюджет, аудиторія, плейсменти */
const MINB=46;let budVal=null,sd=null;
const setView=id=>()=>{const s=L$.sets.find(x=>x.id===id);if(!s)return'';const gk=goalOfSet(s),g=GOALS[gk],cur=dB(s),si=L$.sins[s.id]||zero();if(budVal==null)budVal=cur||LC.budget;if(!sd||sd.id!==id)sd={id,a:parseT(s.targeting)};
 const ch=cur?Math.round((budVal/cur-1)*100):0,rt=isRt(s);
 return `<div class="card hero"><div class="lab">${g.ico} ${esc(s.name)}</div>
 <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin:12px 0 4px">
  <button class="btn ghost" data-bstep="-25" style="width:58px;margin:0;font-size:22px">−</button>
  <div style="text-align:center"><div class="big" id="bbig" style="margin:0">${usd(budVal)}</div><div id="bmon" style="color:var(--mut);font-size:13px">на день · ≈ ${usd(budVal*30.4)} на місяць</div></div>
  <button class="btn ghost" data-bstep="25" style="width:58px;margin:0;font-size:22px">+</button></div>
 <div class="chips" style="justify-content:center;margin-top:12px">${[50,100,135,200,300,500].map(v=>`<button class="${budVal==v?'on':''}" data-bset="${v}">${v} ₴</button>`).join('')}</div>
 <div style="display:flex;align-items:center;gap:8px;justify-content:center;margin-top:12px"><span style="color:var(--mut)">Своя сума</span><input id="bin" class="in" inputmode="numeric" value="${budVal}" style="margin:0;max-width:120px;text-align:center"><span style="color:var(--mut)">₴</span></div></div>
 <div class="mg"><div class="m"><span>Зараз</span><b>${usd(cur)}</b></div><div class="m"><span>Зміна</span><b style="color:var(--${ch>0?'good':ch<0?'bad':'ink'})">${ch>0?'+':''}${ch}%</b></div><div class="m"><span>Витрачено за 7 дн</span><b>${usd(si.spend)}</b></div><div class="m"><span>${RES[g.res][3]} ${q('cpr')}</span><b>${usd(cost(si,g.res))}</b></div></div>
 ${Math.abs(ch)>20?`<div class="hint" style="cursor:default"><div class="ico i-mid">!</div><div class="tx" style="flex:1"><b>Зміна більше ніж на 20%</b><small style="display:block;color:var(--mut);margin-top:3px">Meta може знову почати навчання, і кілька днів ціна результату стрибатиме. Безпечніше міняти поступово, не частіше ніж раз на 3 дні.</small></div></div>`:''}
 ${budVal<MINB?`<p class="h2s" style="color:var(--bad)">Мінімум у твоєму кабінеті ${MINB} ₴ на день.</p>`:''}
 <button class="btn" id="bsv" data-bsave="${id}" ${budVal<MINB||budVal==cur?'disabled':''}>Застосувати бюджет</button>
 <h2>Кому показувати</h2>${rt?`<div class="card">Людям, які за останній рік взаємодіяли з твоїм Instagram ${q('rt')}<div class="h2s" style="margin:6px 0 0">Географія: ${esc(audSum(sd.a).split(' · ')[0])}</div></div>`:audHtml(sd.a)}
 <h2>Де показувати ${q('place')}</h2><div class="card">${placeHtml(sd.a,gk)}</div>
 <button class="btn" data-tsave="${id}">Зберегти аудиторію й плейсменти</button>
 ${s.effective_status==='ACTIVE'?`<button class="btn bad" data-spause="${id}">⏸ Зупинити групу</button>`:`<button class="btn good" data-sresume="${id}">▶ Увімкнути групу</button>`}
 <p class="h2s" style="margin-top:10px">Мовою таргетолога: ad set, daily budget, targeting, placements.</p>`};
let citySearch=[];
const audHtml=a=>`<div class="card"><div class="l">Де</div>
  <div class="chips"><button class="${!a.cities.length?'on':''}" data-aall="1">Вся Україна</button>${a.cities.map((c,k)=>`<button class="on" data-arm="${k}">${esc(c.name)} ✕</button>`).join('')}</div>
  <input id="acity" class="in" placeholder="Додати місто: Київ, Львів…" style="margin-top:8px"><div id="ares"></div>
  ${a.cities.length?`<div class="chips" style="margin-top:10px">${[10,25,40,80].map(r=>`<button class="${a.radius==r?'on':''}" data-arad="${r}">+${r} км</button>`).join('')}</div>`:''}
 <div class="l" style="margin-top:14px">Хто</div>
  <div class="chips"><button class="${a.adv?'on':''}" data-aadv="1">Автоматично</button><button class="${!a.adv?'on':''}" data-aadv="0">Задати вручну</button></div>
  <div class="h2s" style="margin:8px 0 0">${a.adv?'Meta сама шукає тих, хто реагує (Advantage+ audience). Для малих бюджетів зазвичай найкраще.':'Показуємо лише вказаному віку й статі.'}</div>
  ${!a.adv?`<div style="display:flex;gap:8px;align-items:center;margin-top:10px;flex-wrap:wrap"><span style="color:var(--mut)">Вік</span><button class="btn ghost" data-aage="min:-1" style="width:42px;margin:0;padding:8px">−</button><b>${a.ageMin}</b><button class="btn ghost" data-aage="min:1" style="width:42px;margin:0;padding:8px">+</button><span style="color:var(--mut)">до</span><button class="btn ghost" data-aage="max:-1" style="width:42px;margin:0;padding:8px">−</button><b>${a.ageMax}</b><button class="btn ghost" data-aage="max:1" style="width:42px;margin:0;padding:8px">+</button></div>
  <div class="chips" style="margin-top:10px"><button class="${!a.gender?'on':''}" data-agen="0">Усі</button><button class="${a.gender===1?'on':''}" data-agen="1">Чоловіки</button><button class="${a.gender===2?'on':''}" data-agen="2">Жінки</button></div>`:''}</div>`;
document.addEventListener('input',e=>{const v=Math.round(+String(e.target.value).replace(/\D/g,''))||0;
 if(e.target.id==='bin'){budVal=v;$('#bbig').textContent=usd(v);$('#bmon').textContent=`на день · ≈ ${usd(v*30.4)} на місяць`;const s=L$.sets.find(x=>x.id===sd?.id);const b=$('#bsv');if(b)b.disabled=v<MINB||(s&&v==dB(s))}
 if(e.target.id==='nbudin'){nc.budget=v;$('#nbm').textContent=`≈ ${usd(v*30.4)} на місяць. Мінімум ${MINB} ₴. Карта списується в Meta.`}});
let cityT=null;
document.addEventListener('input',e=>{if(e.target.id!=='acity')return;clearTimeout(cityT);const v=e.target.value.trim();if(v.length<2)return;
 cityT=setTimeout(async()=>{try{const r=await gget(`search?type=adgeolocation&location_types=${encodeURIComponent('["city"]')}&country_code=UA&q=${encodeURIComponent(v)}&limit=6`);
  citySearch=(r.data||[]).map(c=>({key:c.key,name:c.name,region:c.region}));$('#ares').innerHTML=citySearch.map((c,k)=>`<div class="item" data-apick="${k}" style="padding:10px;margin:6px 0 0"><div class="tx"><b>${esc(c.name)}</b><small>${esc(c.region||'')}</small></div><span class="chev">＋</span></div>`).join('')||'<div class="h2s">Нічого не знайшов</div>'}catch(x){err(x)}},400)});
const reView=()=>{const v=stack.at(-1);return re(v.k==='new'?Object.assign(newCampView(),{k:'new'}):v.k==='naud'?Object.assign(nAudView(),{k:'naud'}):setView(sd.id))};
const nAudView=()=>()=>`<h2 style="margin-top:6px">Кому показувати</h2>${audHtml(nc.aud)}<button class="btn" data-back="1">Готово</button>`;
async function audClick(d){const v=stack.at(-1);const a=v?.k==='new'||v?.k==='naud'?nc.aud:sd?.a;if(!a)return false;
 if(d.aall){a.cities=[];return reView()}
 if(d.arm!==undefined){a.cities.splice(+d.arm,1);return reView()}
 if(d.apick!==undefined){const c=citySearch[+d.apick];if(!a.cities.some(x=>x.key===c.key))a.cities.push(c);citySearch=[];return reView()}
 if(d.arad){a.radius=+d.arad;return reView()}
 if(d.aadv!==undefined){a.adv=d.aadv==='1';return reView()}
 if(d.aage){const [k,x]=d.aage.split(':');if(k==='min')a.ageMin=Math.min(a.ageMax,Math.max(18,a.ageMin+(+x)));else a.ageMax=Math.max(a.ageMin,Math.min(65,a.ageMax+(+x)));return reView()}
 if(d.agen!==undefined){a.gender=+d.agen;return reView()}
 if(d.pauto){a.place=[];return reView()}
 if(d.pl){a.place=a.place.includes(d.pl)?a.place.filter(x=>x!==d.pl):[...a.place,d.pl];return reView()}
 return false}

/* ретаргет у кампанії */
async function makeRt(cid){let aud=await CS.get('rt_audience');
 if(!aud){aud=(await gpost(`${ACT()}/customaudiences`,{name:'Взаємодіяли з Instagram · 365 днів',subtype:'ENGAGEMENT',prefill:'1',
  rule:JSON.stringify({inclusions:{operator:'or',rules:[{event_sources:[{id:LC.ig,type:'ig_business'}],retention_seconds:31536000,filter:{operator:'and',filters:[{field:'event',operator:'eq',value:'ig_business_profile_all'}]}}]}})})).id;await CS.set('rt_audience',aud)}
 const main=setsOf(cid).find(s=>!isRt(s)),gk=goalOfCamp(cid),a=parseT(main?.targeting);a.cities=[];
 const sid=(await gpost(`${ACT()}/adsets`,setParams(gk,'Ретаргет · Instagram',cid,50,buildT(a,[{id:aud}])))).id;
 for(const ad of adsOf(cid).filter(x=>x.adset_id===main?.id&&x.effective_status==='ACTIVE'))try{await gpost(`${ACT()}/ads`,{name:ad.name+' · ретаргет',adset_id:sid,creative:JSON.stringify({creative_id:ad.creative.id}),status:'ACTIVE'})}catch(e){}
 return sid}

/* ───── Креативи ───── */
let draft=null;
const fileBtn=(id,label,f,multi)=>`<label class="btn ghost" style="margin:6px 0 0;cursor:pointer">${f?'✓ '+esc(f.name):label}<input id="${id}" type="file" accept="image/*,video/*" ${multi?'multiple':''} style="display:none"></label>`;
const isCar=d=>d?.mode==='car';
const cardRow=(c,i,n)=>`<div class="item" style="cursor:default;align-items:center">${c.preview?`<img class="th" src="${c.preview}">`:`<div class="ico i-ai">🎬</div>`}
 <div class="tx"><small>Картка ${i+1}</small><input id="cct${i}" class="in" style="margin-top:6px" maxlength="40" value="${esc(c.title||'')}" placeholder="Заголовок картки"></div>
 <div style="display:flex;flex-direction:column;gap:4px">${i?`<button class="btn ghost sm" style="margin:0;padding:4px 10px" data-cup="${i}">↑</button>`:''}${i<n-1?`<button class="btn ghost sm" style="margin:0;padding:4px 10px" data-cdown="${i}">↓</button>`:''}<button class="btn ghost sm" style="margin:0;padding:4px 10px" data-cdel="${i}">✕</button></div></div>`;
const addView=()=>()=>{const d=draft,car=isCar(d),has=car?d.cards?.length:d.file;return `<h2 style="margin-top:6px">Новий креатив</h2>
 <div class="seg"><button class="${car?'':'on'}" data-crmode="one">Одне фото / відео</button><button class="${car?'on':''}" data-crmode="car">Карусель</button></div>
 <div class="card">${car?`<div class="l">Картки · 2–10, усі однієї пропорції (1:1 або 4:5)</div>
 ${(d.cards||[]).map((c,i)=>cardRow(c,i,d.cards.length)).join('')}
 ${(d.cards||[]).length<10?fileBtn('ccar',(d.cards||[]).length?'+ Додати картки':'Вибрати фото чи відео',null,true):''}
 <div class="h2s" style="margin:6px 0 0">Можна обрати кілька файлів одразу. Фото й відео можна змішувати. Порядок міняй стрілками, перша картка найважливіша. Окремої версії 9:16 у каруселі нема, у сторіс Meta показує картки по черзі.</div>`
 :`<div class="l">Основний файл · квадрат або 4:5</div>${fileBtn('cf','Вибрати фото чи відео',d.file)}
 ${d.preview?`<img src="${d.preview}" style="width:100%;border-radius:12px;margin-top:10px">`:d.file?'<div class="h2s" style="margin:6px 0 0">🎬 Відео: ШІ подивиться 6 кадрів від початку до кінця. Звук не чує, тому суть озвучки напиши в полі «Про що реклама».</div>':''}
 <div class="l" style="margin-top:14px">Вертикальний 9:16 для сторіс і Reels (необов'язково)</div>${fileBtn('cf2','Додати вертикальну версію',d.file2)}
 <div class="h2s" style="margin:6px 0 0">Без нього Meta сама обріже основний файл під сторіс. Обидва файли мають бути одного типу: два фото або два відео.</div>`}</div>
 <div class="card"><div class="l">Про що реклама (для ШІ, необов'язково)</div><input id="ctopic" class="in" value="${esc(d.topic||'')}" placeholder="напр. AI-бот для салону: відповідає в Direct 24/7">
 <button class="btn ${L$.ai?'':'ghost'} sm" data-aitext="1">${L$.ai?(has?(car?'✨ ШІ напише тексти під усю карусель':'✨ ШІ напише 3 тексти під цей креатив'):'✨ ШІ напише 3 варіанти тексту'):'✨ Тексти від ШІ: додай ключ у налаштуваннях'}</button></div>
 <div class="card"><div class="l">Заголовок (необов'язково)</div><input id="ch" class="in" value="${esc(d.headline||'')}">
 <div class="l" style="margin-top:14px">Текст · варіант A</div><textarea id="ct" class="in" rows="6">${esc(d.text||'')}</textarea>
 <div class="l" style="margin-top:14px">Варіант B (необов'язково)</div><textarea id="ct2" class="in" rows="4" placeholder="Інший хук або інша пропозиція. Meta покаже обидва, а я скажу, який дешевший.">${esc(d.text2||'')}</textarea>
 <div class="l" style="margin-top:14px">Варіант C (необов'язково)</div><textarea id="ct3" class="in" rows="4">${esc(d.text3||'')}</textarea></div>
 <button class="btn" data-save="1">Зберегти креатив</button><p class="h2s" style="margin-top:10px">Після збереження ШІ може розібрати креатив, а ти обираєш, у яку кампанію запустити.</p>`};
const keepDraft=()=>{if(!$('#ct'))return;Object.assign(draft,{topic:$('#ctopic').value,headline:$('#ch').value,text:$('#ct').value,text2:$('#ct2').value,text3:$('#ct3').value});(draft.cards||[]).forEach((c,i)=>{const el=$('#cct'+i);if(el)c.title=el.value})};
document.addEventListener('change',e=>{if(!['cf','cf2','ccar'].includes(e.target.id))return;const fs=[...e.target.files];if(!fs.length)return;keepDraft();
 if(e.target.id==='ccar'){draft.cards=draft.cards||[];for(const f of fs){if(draft.cards.length>=10){toast('Максимум 10 карток');break}draft.cards.push({file:f,preview:f.type.startsWith('image')?URL.createObjectURL(f):'',title:''})}}
 else if(e.target.id==='cf'){draft.file=fs[0];draft.preview=fs[0].type.startsWith('image')?URL.createObjectURL(fs[0]):''}else draft.file2=fs[0];re(addView())});
async function upload(f){const fd=new FormData();
 if(f.type.startsWith('image')){fd.append('filename',f,f.name);const j=await gform(`${ACT()}/adimages`,fd);const im=Object.values(j.images)[0];return {kind:'image',ref:im.hash,thumb:im.url}}
 fd.append('source',f,f.name);const j=await gform(`${ACT()}/advideos`,fd);return {kind:'video',ref:j.id,thumb:''}}
async function videoReady(id){for(let i=0;i<40;i++){const s=await gget(`${id}?fields=status`);if(s.status?.video_status==='ready')break;if(s.status?.video_status==='error')throw new Error('Meta не змогла обробити відео');toast('Meta обробляє відео…');await new Promise(r=>setTimeout(r,5000))}
 const th=await gget(`${id}/thumbnails`);return ((th.data||[]).find(x=>x.is_preferred)||th.data?.[0])?.uri||''}
function ctaFor(gk,cf){if(gk==='direct')return {type:'INSTAGRAM_MESSAGE',value:{app_destination:'INSTAGRAM_DIRECT'}};if(gk==='lead')return {type:'SIGN_UP',value:{lead_gen_form_id:cf.form}};return {type:'LEARN_MORE',value:{link:cf.link}}}
async function crSpec(c,text,cid,two){const gk=goalOfCamp(cid),cf=L$.cfg[cid]||{},cta=ctaFor(gk,cf),link=gk==='direct'?(LC.link||'https://www.instagram.com/'):gk==='lead'?'https://fb.me/':cf.link;
 const oss={page_id:LC.page,...(LC.ig?{instagram_user_id:LC.ig}:{})};
 if(c.kind==='carousel'){const vt={};for(const x of c.cards)if(x.k==='v')vt[x.r]=await videoReady(x.r);
  oss.link_data={message:text,link,multi_share_optimized:false,multi_share_end_card:false,call_to_action:cta,
   child_attachments:c.cards.map(x=>({link,name:x.t||c.headline||'',call_to_action:cta,...(x.k==='i'?{image_hash:x.r}:{video_id:x.r,picture:vt[x.r]})}))};
  return {object_story_spec:oss}}
 if(c.kind==='video'){if(!c.thumb)c.thumb=await videoReady(c.ref);if(c.ref2&&!c.thumb2)c.thumb2=await videoReady(c.ref2)}
 if(two&&c.ref2){const F=c.kind==='image';const lab=(n,x)=>F?{hash:x,adlabels:[{name:n}]}:{video_id:x,thumbnail_url:n==='sq'?c.thumb:c.thumb2,adlabels:[{name:n}]};
  const rule=(spec,n,p)=>({customization_spec:spec,[F?'image_label':'video_label']:{name:n},priority:p});
  return {object_story_spec:oss,asset_feed_spec:{[F?'images':'videos']:[lab('sq',c.ref),lab('vt',c.ref2)],bodies:[{text}],titles:[{text:c.headline||''}],link_urls:[{website_url:link}],
   call_to_action_types:[cta.type],ad_formats:[F?'SINGLE_IMAGE':'SINGLE_VIDEO'],optimization_type:'PLACEMENT',
   ...(gk==='lead'?{call_to_actions:[{type:cta.type,value:cta.value}]}:{}),
   asset_customization_rules:[rule({publisher_platforms:['instagram','facebook'],instagram_positions:['story','reels'],facebook_positions:['story','facebook_reels']},'vt',1),rule({},'sq',2)]}}}
 if(c.kind==='image')oss.link_data={image_hash:c.ref,message:text,name:c.headline||'',link,call_to_action:cta};
 else oss.video_data={video_id:c.ref,message:text,title:c.headline||'',call_to_action:cta,...(c.thumb?{image_url:c.thumb}:{})};
 return {object_story_spec:oss}}
const LET='ABC';
async function mkCreative(c,k,cid){const name=`ШІ · креатив ${c.id}${c.texts.length>1?'-'+LET[k]:''}`;
 if(c.ref2&&!c.single)try{return (await gpost(`${ACT()}/adcreatives`,{name,...J(await crSpec(c,c.texts[k],cid,true))})).id}catch(e){c.single=true;c.note='Meta не прийняла два формати разом, тому запущено з основним файлом: '+e.message.slice(0,120)}
 return (await gpost(`${ACT()}/adcreatives`,{name,...J(await crSpec(c,c.texts[k],cid,false))})).id}
const J=o=>Object.fromEntries(Object.entries(o).map(([k,v])=>[k,JSON.stringify(v)]));
async function launchCr(c,cid){const sets=setsOf(cid);if(!sets.length)throw new Error('У кампанії нема груп');
 for(let k=0;k<c.texts.length;k++){const crid=await mkCreative(c,k,cid);
  for(const s of sets){const ad=(await gpost(`${ACT()}/ads`,{name:`#${c.id}${c.texts.length>1?'-'+LET[k]:''} ${c.headline||c.texts[k].slice(0,40)}${isRt(s)?' · ретаргет':''}`,adset_id:s.id,creative:JSON.stringify({creative_id:crid}),status:'ACTIVE'})).id;
   c.ads.push({ad,cr:crid,set:s.id,k,camp:cid})}}
 c.camp=cid;c.error=null}
/* розбивка каруселі по картках */
const CARD={};
async function loadCards(c){const res=c.camp?GOALS[goalOfCamp(c.camp)].res:'link',by={};
 for(const ad of new Set(c.ads.map(x=>x.ad))){const j=await gget(`${ad}/insights?fields=actions&action_breakdowns=action_type,action_carousel_card_id,action_carousel_card_name&date_preset=maximum`);
  for(const r of j.data||[])for(const a of r.actions||[]){const id=a.action_carousel_card_id;if(!id)continue;const o=by[id]=by[id]||{id,name:a.action_carousel_card_name||'',t:{}};o.t[a.action_type]=(o.t[a.action_type]||0)+(+a.value||0)}}
 const got=Object.values(by).map(o=>({...o,link:o.t.link_click||0,res:Math.max(0,...RT[res].map(k=>o.t[k]||0))})),rows=c.cards.map(()=>null),left=[];
 for(const o of got){const i=o.name?c.cards.findIndex((x,k)=>!rows[k]&&x.t&&x.t===o.name):-1;if(i>=0)rows[i]=o;else left.push(o)}
 left.sort((a,b)=>String(a.id).localeCompare(String(b.id),'en',{numeric:true}));for(let k=0;k<rows.length&&left.length;k++)if(!rows[k])rows[k]=left.shift();
 CARD[c.id]={rows,res,any:got.length>0}}
const cardsBlock=c=>{const d=CARD[c.id];
 if(!d){if(!CARD['l'+c.id]){CARD['l'+c.id]=1;loadCards(c).catch(e=>{CARD[c.id]={err:e.message}}).finally(()=>{delete CARD['l'+c.id];render()})}return `<h2>Картки</h2><div class="card"><small style="color:var(--mut)">Завантажую статистику по картках…</small></div>`}
 if(d.err)return `<h2>Картки</h2><div class="card"><small style="color:var(--mut)">Meta не віддала розбивку: ${esc(d.err.slice(0,140))}</small></div>`;
 if(!d.any)return `<h2>Картки</h2><div class="card"><small style="color:var(--mut)">Поки нема дій на картках. Розбивка з'явиться після перших кліків.</small></div>`;
 const showRes=d.res!=='link',tot=d.rows.reduce((m,r)=>m+(r?.link||0),0)||1,mx=Math.max(1,...d.rows.map(r=>r?.link||0));
 const first=d.rows[0]?.link||0,tail=d.rows.slice(1).reduce((m,r)=>m+(r?.link||0),0);
 const hint=d.rows.length>1?(first/tot>=.7?'Майже всі кліки на першій картці: далі гортають мало. Посиль другу картку або перенеси найсильнішу на початок.':(()=>{const w=d.rows.reduce((b,r,i)=>(r?.link||0)>(d.rows[b]?.link||0)?i:b,0);return w?`Найбільше кліків на картці ${w+1}. Спробуй поставити її першою: перша картка бачать усі, решту лише ті, хто гортає.`:'Кліки розподілені рівно: карусель гортають.'})()):'';
 return `<h2>Картки ${q('cards')}</h2><div class="card">${d.rows.map((r,i)=>{const n=r?.link||0;return `<div style="margin:${i?12:0}px 0 0"><div style="display:flex;justify-content:space-between;gap:10px"><small style="color:var(--ink)">${i+1}. ${esc(c.cards[i]?.t||'Картка '+(i+1))}</small><small><b>${fmt(n)}</b> ${pl(n,['клік','кліки','кліків'])}${showRes&&r?.res?` · ${rn(r.res,d.res)}`:''}</small></div>
  <div style="height:6px;border-radius:3px;background:var(--card2);margin-top:6px"><div style="height:6px;border-radius:3px;background:var(--g1);width:${Math.round(n/mx*100)}%"></div></div></div>`}).join('')}
  ${hint?`<div class="h2s" style="margin:12px 0 0">${hint}</div>`:''}<div class="h2s" style="margin:8px 0 0">За весь час. Meta рахує кліки по картках, а не скільки людей догортало до кожної, тому це оцінка інтересу, а не точний «відвал».</div></div>`};
const crView=id=>()=>{const c=L$.crs.find(x=>x.id==id);if(!c)return'';const s=crSt(c),i=crIns(c),gk=c.camp?goalOfCamp(c.camp):null,g=gk?GOALS[gk]:null;
 const ads=c.ads.map(x=>L$.ads.find(a=>a.id===x.ad)).filter(Boolean),rj=ads.filter(a=>/DISAPPROVED|WITH_ISSUES/.test(a.effective_status));
 const vs=c.texts.map((t,k)=>{const ids=c.ads.filter(x=>x.k===k).map(x=>x.ad),x=insOf(ids),act=ids.some(a=>L$.ads.find(z=>z.id===a)?.effective_status==='ACTIVE');return {t,k,ids,x,act,cpr:g?cost(x,g.res):null}});
 const best=vs.filter(v=>v.cpr!=null).sort((a,b)=>a.cpr-b.cpr)[0];const camps=[...new Set(c.ads.map(x=>x.camp||c.camp))].map(id=>L$.camps.find(z=>z.id===id)?.name).filter(Boolean);
 return `<div class="card hero"><span class="pill ${s[0]}">${s[1]}</span><div class="ttl" style="margin:10px 0 0">${esc(c.headline||'Креатив #'+c.id)}</div>
 ${camps.length?`<div class="h2s" style="margin:4px 0 0">У кампанії: ${esc(camps.join(', '))}</div>`:''}
 ${c.thumb||c.preview?`<img src="${esc(c.preview||c.thumb)}" style="width:100%;border-radius:14px;margin-top:12px">`:''}${c.ref2?'<div class="h2s" style="margin:8px 0 0">+ вертикальна версія для сторіс і Reels</div>':''}${c.kind==='carousel'?`<div class="h2s" style="margin:8px 0 0">Карусель · ${c.cards.length} карток${c.cards.some(x=>x.t)?': '+esc(c.cards.map(x=>x.t||'—').join(' · ')):''}</div>`:''}</div>
 ${c.note?`<div class="hint" style="cursor:default"><div class="ico i-mid">!</div><div class="tx"><small style="color:var(--ink)">${esc(c.note)}</small></div></div>`:''}
 ${rj.length?rejCard([...new Set(rj.flatMap(reasons))],null):''}
 ${c.ads.length&&g?`<div class="mg"><div class="m"><span>Витрати ${q('spend')}</span><b>${usd(i.spend)}</b></div><div class="m"><span>${RES[g.res][2][0].toUpperCase()+RES[g.res][2].slice(1)} ${q('res')}</span><b>${fmt(i[g.res])}</b></div><div class="m"><span>${RES[g.res][3]} ${q('cpr')}</span><b>${usd(cost(i,g.res))}</b></div><div class="m"><span>Клікабельність ${q('ctr')}</span><b>${i.impr?(i.clicks/i.impr*100).toFixed(2)+'%':'—'}</b></div></div>`:''}
 ${c.kind==='carousel'&&c.ads.length?cardsBlock(c):''}
 <h2>${vs.length>1?'Варіанти тексту':'Текст'}</h2>${vs.map(v=>`<div class="card">${vs.length>1?`<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><b>Варіант ${LET[v.k]}</b>${best&&best.k===v.k?'<span class="pill p-good">найдешевший</span>':v.ids.length&&!v.act?'<span class="pill p-learn">не показується</span>':''}</div>`:''}
  <div class="copy" style="margin:0">${esc(v.t)}</div>${v.ids.length&&g?`<div class="src">${usd(v.x.spend)} · ${rn(v.x[g.res],g.res)}${v.cpr!=null?' · '+usd(v.cpr)+' за '+RES[g.res][0]:''}</div>`:''}
  <div class="row2"><button class="btn ghost sm" data-edit="${c.id}:${v.k}">✎ Змінити текст</button>${v.act&&vs.length>1?`<button class="btn ghost sm" data-vpause="${c.id}:${v.k}" style="color:var(--bad)">Вимкнути варіант</button>`:'<span></span>'}</div></div>`).join('')}
 ${c.review?reviewHtml(c.review):`<button class="btn ghost" data-review="${c.id}">${L$.ai?'🧐 ШІ розбере креатив перед запуском':'🧐 Розбір ШІ: додай ключ у налаштуваннях'}</button>`}
 ${c.error?`<div class="card"><div class="l" style="color:var(--bad)">Що пішло не так</div>${esc(c.error)}</div>`:''}
 ${!c.ads.length?`<button class="btn good" data-launch="${c.id}">🚀 Запустити в рекламу</button><button class="btn ghost" data-delcr="${c.id}">Видалити чернетку</button>`:
  `<button class="btn ghost" data-launch="${c.id}">🚀 Запустити ще в іншу кампанію</button>`+(ads.some(a=>a.effective_status==='ACTIVE')?`<button class="btn bad" data-pausecr="${c.id}">⏸ Поставити на паузу</button>`:ads.some(a=>a.effective_status==='PAUSED')?`<button class="btn good" data-resumecr="${c.id}">▶ Відновити показ</button>`:'')}`};
const reviewHtml=r=>`<h2>Розбір ШІ</h2><div class="card"><div style="display:flex;justify-content:space-between;align-items:center"><b>Оцінка</b><span class="pill p-${r.score>=7?'good':r.score>=5?'mid':'bad'}">${r.score}/10</span></div>
 ${r.hook?`<div class="sec"><div class="l">Перші секунди</div>${esc(r.hook)}</div>`:''}${r.offer?`<div class="sec"><div class="l">Пропозиція</div>${esc(r.offer)}</div>`:''}
 ${(r.fix||[]).length?`<div class="sec"><div class="l">Що виправити</div>${r.fix.map(x=>`<div style="margin-top:4px">• ${esc(x)}</div>`).join('')}</div>`:''}
 ${r.risk?`<div class="idea" style="border-color:rgba(251,113,133,.4);background:rgba(251,113,133,.08)"><b style="color:var(--bad)">Ризик відхилення Meta:</b> ${esc(r.risk)}</div>`:''}</div>`;
let launchFor=null;
const launchView=id=>()=>{const c=L$.crs.find(x=>x.id==id);const used=new Set(c.ads.map(x=>x.camp||c.camp));const cs=L$.camps.filter(x=>!used.has(x.id));
 return `<h2 style="margin-top:6px">У яку кампанію?</h2><p class="h2s">${c.texts.length>1?c.texts.length+' варіанти тексту стануть окремими оголошеннями. ':''}Оголошення піде в усі групи кампанії${cs.some(x=>setsOf(x.id).some(isRt))?' (разом із ретаргетом)':''}.</p>
 ${cs.map(x=>{const g=GOALS[goalOfCamp(x.id)];return `<div class="item ${launchFor===x.id?'sel':''}" data-lcamp="${x.id}"><div class="ico i-ai">${g.ico}</div><div class="tx"><b>${esc(x.name)}</b><small>${g.name} · ${usd(setsOf(x.id).reduce((a,s)=>a+(dB(s)||0),0))}/день${x.effective_status!=='ACTIVE'?' · на паузі':''}</small></div></div>`}).join('')||'<div class="card">Нема вільних кампаній.</div>'}
 <button class="btn ghost" data-newcamp="1">＋ Нова кампанія</button>
 <button class="btn good" data-lgo="${id}" ${launchFor?'':'disabled'}>🚀 Запустити</button>`};
const editView=(id,k)=>()=>{const c=L$.crs.find(x=>x.id==id);return `<h2 style="margin-top:6px">Змінити текст${c.texts.length>1?' · варіант '+LET[k]:''}</h2>
 <div class="card"><textarea id="et" class="in" rows="8">${esc(c.texts[k])}</textarea>${L$.ai?`<button class="btn ghost sm" data-aifix="${id}:${k}">✨ ШІ перепише з урахуванням розбору</button>`:''}</div>
 <button class="btn" data-esave="${id}:${k}">Зберегти${c.ads.some(x=>x.k===k)?' й оновити в Meta':''}</button>
 <p class="h2s" style="margin-top:10px">${c.ads.some(x=>x.k===k)?'Оголошення залишиться тим самим, статистика збережеться. Meta заново перевірить текст (зазвичай до кількох годин).':'Це чернетка, в Meta ще нічого не змінюється.'}</p>`};

/* ───── Клієнти: ручна відмітка ───── */
let mkDraft=null;
const markView=()=>()=>{const m=mkDraft;const ads=L$.ads.filter(a=>(L$.ins[a.id]||{}).spend||a.effective_status==='ACTIVE');
 return `<h2 style="margin-top:6px">Новий клієнт</h2><div class="card"><div class="l">Що сталося</div>
 <div class="chips"><button class="${m.t==='call'?'on':''}" data-mt="call">📞 Відбувся дзвінок</button><button class="${m.t==='paid'?'on':''}" data-mt="paid">💳 Оплатив</button></div>
 ${m.t==='paid'?`<div class="l" style="margin-top:14px">Сума, ₴ (необов'язково)</div><input id="msum" class="in" inputmode="numeric" value="${m.s||''}">`:''}
 <div class="l" style="margin-top:14px">З якої реклами написав</div>
 <div class="chips"><button class="${!m.ad?'on':''}" data-mad="">Не знаю</button>${ads.map(a=>`<button class="${m.ad===a.id?'on':''}" data-mad="${a.id}">${esc(a.name.slice(0,28))}</button>`).join('')}</div></div>
 <button class="btn" data-msave="1">Зберегти</button>`};
const reMark=()=>{if($('#msum'))mkDraft.s=+$('#msum').value||0;return re(markView())};

/* ───── Заявки з лід-форми ───── */
const leadsHtml=form=>{if(!form)return'<div class="card">Форма не знайдена в налаштуваннях кампанії.</div>';const l=L$.leads[form];if(!l){L$.leads[form]={loading:1};setTimeout(()=>loadLeads(form),0)}if(!l||l.loading)return'<div class="card"><span class="spin"></span> завантажую заявки…</div>';
 if(l.err)return `<div class="card" style="color:var(--bad)">${esc(l.err)}${/terms|умов|TOS/i.test(l.err)?'<button class="btn ghost" data-open="https://www.facebook.com/ads/leadgen/tos">Прийняти умови лід-форм</button>':''}</div>`;
 return l.list.length?l.list.map(x=>{const f=Object.fromEntries((x.field_data||[]).map(z=>[z.name,(z.values||[]).join(', ')]));const ph=f.phone_number||f.phone||'';
  return `<div class="item" style="cursor:default"><div class="ico i-good">📝</div><div class="tx"><b>${esc(f.full_name||f.first_name||'Без імені')}</b><small>${esc(ph)} · ${new Date(x.created_time).toLocaleString('uk-UA',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})}</small></div>${ph?`<a class="how" href="tel:${esc(ph.replace(/[^\d+]/g,''))}">📞</a>`:''}</div>`}).join(''):'<div class="card">Заявок ще нема.</div>'};
async function loadLeads(form){try{const pt=await pageTok();const j=await gget(`${form}/leads?fields=created_time,field_data,ad_id&limit=50`,pt);L$.leads[form]={list:j.data||[]}}catch(e){L$.leads[form]={list:[],err:e.message}}
 const el=$('#leads');if(el)el.innerHTML=leadsHtml(form)}

/* ───── Звіт ───── */
let rp='last_7d',rc='',rb='age',rf='',rt2='';
const PER=[['last_7d','7 днів'],['last_30d','30 днів'],['this_month','Місяць'],['y1','Рік'],['maximum','Увесь час'],['custom','📅 Свій']];
const isoD=d=>new Date(d.getTime()-d.getTimezoneOffset()*6e4).toISOString().slice(0,10);
const MAXBACK=()=>{const d=new Date();d.setMonth(d.getMonth()-37);d.setDate(d.getDate()+1);return isoD(d)};/* Meta віддає статистику лише за останні 37 місяців */
const perQ=()=>{if(rp==='y1'){const d=new Date();d.setFullYear(d.getFullYear()-1);return `time_range=${encodeURIComponent(JSON.stringify({since:isoD(d),until:isoD(new Date())}))}`}
 if(rp==='custom')return `time_range=${encodeURIComponent(JSON.stringify({since:rf<MAXBACK()?MAXBACK():rf,until:rt2}))}`;return `date_preset=${rp}`};
/* крок графіка: дні для коротких періодів, тижні до року, місяці для довших */
const perStep=()=>{const days=rp==='last_7d'||rp==='last_30d'||rp==='this_month'?31:rp==='y1'?365:rp==='maximum'?1200:(new Date(rt2)-new Date(rf))/864e5;return days<=62?'1':days<=400?'7':'monthly'};
const STEPL=()=>({'1':'за день','7':'за тиждень',monthly:'за місяць'})[perStep()];
async function gall(p){let j=await gget(p),out=j.data||[];for(let n=0;j.paging?.next&&n<15;n++){j=await fetch(j.paging.next).then(meta);out=out.concat(j.data||[])}return {data:out}}
const BR={age:['Вік','age'],gender:['Стать','gender'],place:['Плейсменти','publisher_platform,platform_position']};
const LBL={male:'Чоловіки',female:'Жінки',unknown:'Невідомо',instagram:'Instagram',facebook:'Facebook',messenger:'Messenger',audience_network:'Audience Network',threads:'Threads',
 feed:'стрічка',story:'сторіс',instagram_stories:'сторіс',instagram_reels:'Reels',facebook_reels:'Reels',reels_overlay:'Reels-оверлей',explore:'Explore',explore_home:'Explore',instagram_explore:'Explore',
 marketplace:'Marketplace',video_feeds:'відео-стрічка',search:'пошук',profile_feed:'профіль',instagram_profile_feed:'профіль',right_hand_column:'права колонка',an_classic:'сайти й додатки'};
const repKey=()=>rp+'|'+rc+(rp==='custom'?'|'+rf+'|'+rt2:'');
async function loadRep(){if(!tok())return;if(rp==='custom'&&(!rf||!rt2||rf>rt2)){render();return}const k=repKey();if(L$.rep[k]){render();return}L$.rep[k]={loading:true};render();
 const base=rc||ACT(),f=`fields=${INS}&${perQ()}`;
 try{const [tot,day,age,gen,pla,ads,cmp]=await Promise.all([gget(`${base}/insights?${f}`),gall(`${base}/insights?${f}&time_increment=${perStep()}&limit=500`),
  gget(`${base}/insights?${f}&breakdowns=age&limit=50`),gget(`${base}/insights?${f}&breakdowns=gender&limit=10`),gget(`${base}/insights?${f}&breakdowns=publisher_platform,platform_position&limit=50`),
  gall(`${base}/insights?${f.replace('fields=','fields=ad_id,ad_name,')}&level=ad&limit=500`),gget(`${base}/insights?${f.replace('fields=','fields=campaign_id,')}&level=campaign&limit=50`)]);
  L$.rep[k]={tot:px(tot.data?.[0]||{}),day:(day.data||[]).map(r=>({d:r.date_start,...px(r)})),age:(age.data||[]).map(r=>({l:r.age,...px(r)})),gender:(gen.data||[]).map(r=>({l:LBL[r.gender]||r.gender,...px(r)})),
   place:(pla.data||[]).map(r=>({l:(LBL[r.publisher_platform]||r.publisher_platform)+' · '+(LBL[r.platform_position]||r.platform_position.replace(/_/g,' ')),...px(r)})),ads:(ads.data||[]).map(r=>({id:r.ad_id,n:r.ad_name,...px(r)})),sp:byRes((cmp.data||[]).map(r=>[GOALS[goalOfCamp(r.campaign_id)].res,px(r)]))}}
 catch(e){L$.rep[k]={err:e.message}}if(tab==='rep'&&!stack.length)render()}
const mainRes=()=>{if(rc)return GOALS[goalOfCamp(rc)].res;const R=L$.rep[repKey()];const t=R?.tot;if(!t)return'conv';return ['conv','lead','link'].find(x=>t[x])||'conv'};
V.rep=()=>{if(waiting())return top()+waitCard();if(!tok())return top()+setupCard();const R=L$.rep[repKey()]||{loading:true},r=mainRes(),g=Object.values(GOALS).find(x=>x.res===r);
 let h=top('Звіт')+`<div class="seg" style="overflow-x:auto">${PER.map(([k,l])=>`<button class="${rp===k?'on':''}" data-rp="${k}" style="flex:0 0 auto;padding:9px 12px">${l}</button>`).join('')}</div>
 ${rp==='custom'?`<div class="card"><div style="display:flex;gap:8px;align-items:center"><input type="date" id="rf" class="in" value="${rf}" min="${MAXBACK()}" style="margin:0"><span style="color:var(--mut)">—</span><input type="date" id="rt" class="in" value="${rt2}" style="margin:0"></div>
  <div class="chips" style="margin-top:10px"><button data-rq="prev">Минулий місяць</button><button data-rq="3">3 міс</button><button data-rq="6">6 міс</button><button data-rq="24">2 роки</button><button data-rq="37">3 роки</button></div>
  <button class="btn sm" data-rgo="1">Показати</button><div class="h2s" style="margin:8px 0 0">Meta зберігає статистику за останні 37 місяців (з ${MAXBACK().split('-').reverse().join('.')}). Старіше API не віддає.</div></div>`:''}
 <div class="chips scroll"><button class="${!rc?'on':''}" data-rc="">Усі кампанії</button>${L$.camps.map(c=>`<button class="${rc===c.id?'on':''}" data-rc="${c.id}">${esc(c.name)}</button>`).join('')}</div>`;
 if(R.loading)return h+'<div class="card"><span class="spin"></span> Рахую…</div>';if(R.err)return h+`<div class="card" style="color:var(--bad)">${esc(R.err)}</div>`;
 const t=R.tot,sp=R.sp||{conv:t.spend,lead:t.spend,link:t.spend},c=cpr(t,sp,r);
 if(!t.spend&&!t.impr)return h+`<div class="card" style="text-align:center;padding:30px 16px"><div style="font-size:30px">📭</div><b style="display:block;margin-top:8px">За цей період реклама не крутилась</b><div class="h2s" style="margin:6px 0 0">Як тільки запустиш оголошення, тут з'являться витрати, ціна результату, графік по днях і розбивки.</div>${L$.ads.length?'':'<button class="btn" data-tab2="ads">Перейти до реклами</button>'}</div>`;
 h+=`<div class="card hero"><div class="lab">${L('cpr',RES[r][3])}</div><div class="big">${c!=null?cu(c,D.cur):'—'}</div>${c!=null?`<span class="pill p-${verd(c,g.norm,sp[r])}">${VL[verd(c,g.norm,sp[r])]}</span> <span style="color:var(--mut);font-size:13px">норма ${usd(g.norm)}</span>`:''}
  ${R.day.length>1?`<div class="fig"><svg data-ser="1"></svg></div><div class="legend"><span><i style="background:#8b5cf6"></i>витрати ${STEPL()}</span><span><i style="background:#22d3ee;border-radius:50%"></i>${RES[r][2]}</span></div>`:''}</div>
 <div class="mg"><div class="m"><span>Витрати ${q('spend')}</span><b>${usd(t.spend)}</b></div>${['conv','lead','link'].filter(x=>t[x]||x===r).map(x=>`<div class="m"><span>${RES[x][2][0].toUpperCase()+RES[x][2].slice(1)}</span><b>${fmt(t[x])}${t[x]&&cpr(t,sp,x)!=null?` <small style="font-size:12px;color:var(--mut)">по ${usd(cpr(t,sp,x))}</small>`:''}</b></div>`).join('')}
  <div class="m"><span>Охоплення</span><b>${fmt(t.reach)}</b></div><div class="m"><span>Покази</span><b>${fmt(t.impr)}</b></div><div class="m"><span>Клікабельність ${q('ctr')}</span><b>${t.impr?(t.clicks/t.impr*100).toFixed(2)+'%':'—'}</b></div><div class="m"><span>Ціна 1000 показів ${q('cpm')}</span><b>${t.impr?usd(t.spend/t.impr*1000):'—'}</b></div></div>
 <h2>Розбивка</h2><div class="seg">${Object.entries(BR).map(([k,v])=>`<button class="${rb===k?'on':''}" data-rb="${k}">${v[0]}</button>`).join('')}</div>`;
 const rows=(R[rb]||[]).filter(x=>x.spend>0).sort((a,b)=>b.spend-a.spend),mx=Math.max(...rows.map(x=>x.spend),1);
 const mixed=!rc&&['conv','lead','link'].filter(x=>t[x]).length>1,cs=mixed?[]:rows.map(x=>cost(x,r)).filter(x=>x!=null),best=cs.length>1?Math.min(...cs):null;
 h+=`<div class="card">${mixed?'<div class="h2s" style="margin:0 0 6px">Кампанії мають різні цілі. Обери одну вгорі, щоб бачити ціну результату по сегментах.</div>':''}${rows.map(x=>{const cc=mixed?null:cost(x,r);return `<div class="brow"><div class="t"><b>${esc(x.l)}</b><span>${usd(x.spend)} · ${rn(x[r],r)}${cc!=null?` · <b style="color:var(--${cc===best?'good':cc>g.norm*1.5?'bad':'ink'})">${usd(cc)}</b>`:''}</span></div><div class="dbar"><i style="width:${Math.max(3,x.spend/mx*100)}%"></i></div></div>`}).join('')||'Ще нема даних.'}
  ${best!=null?`<div class="src">Зеленим найдешевший сегмент. Якщо різниця велика й тримається тиждень, можна звузити аудиторію чи плейсменти в групі.</div>`:''}</div>`;
 const ads=R.ads.filter(x=>x.spend>0).map(x=>{const a=L$.ads.find(z=>z.id===x.id),xr=a?GOALS[goalOfAd(a)].res:r;return {...x,xr,c:cost(x,xr)}}).sort((a,b)=>(a.c??1e9)-(b.c??1e9));
 if(ads.length)h+=`<h2>Оголошення за період</h2>`+ads.map(x=>`<div class="item" ${L$.ads.some(a=>a.id===x.id)?`data-adlive="${x.id}"`:''}><div class="tx"><b>${esc(x.n)}</b><small>${usd(x.spend)} · ${rn(x[x.xr],x.xr)}</small></div><div class="val">${x.c!=null?usd(x.c):'—'}<small>за ${RES[x.xr][0]}</small></div></div>`).join('');
 return h};
function charts(){document.querySelectorAll('svg[data-ser]').forEach(s=>{const R=L$.rep[repKey()];const r=mainRes();const ser=(R?.day||[]).map(x=>({day:x.d,spend:x.spend,res:x[r]}));const W=s.clientWidth,H=s.clientHeight;if(!W||ser.length<2)return;
 const m={l:4,r:4,t:24,b:20},w=W-m.l-m.r,h=H-m.t-m.b,ms=Math.max(...ser.map(d=>d.spend),1),ml=Math.max(...ser.map(d=>d.res),1),bw=w/ser.length;
 let g='<defs><linearGradient id="bgr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8b5cf6" stop-opacity=".6"/><stop offset="1" stop-color="#8b5cf6" stop-opacity=".1"/></linearGradient><linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22d3ee" stop-opacity=".3"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient></defs>';
 ser.forEach((d,i)=>{const bh=Math.max(2,d.spend/ms*h);g+=`<rect class="bar" style="animation-delay:${i*25}ms" x="${(m.l+i*bw+bw*.18).toFixed(1)}" y="${(m.t+h-bh).toFixed(1)}" width="${(bw*.64).toFixed(1)}" height="${bh.toFixed(1)}" rx="${Math.min(4,bw/4).toFixed(1)}" fill="url(#bgr)"/>`});
 const pts=ser.map((d,i)=>[m.l+i*bw+bw/2,m.t+h-d.res/ml*h*.9]);let len=0;for(let i=1;i<pts.length;i++)len+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);
 const path=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
 g+=`<path d="${path} L${pts.at(-1)[0].toFixed(1)} ${m.t+h} L${pts[0][0].toFixed(1)} ${m.t+h}Z" fill="url(#ar)" class="dp" style="animation-delay:1.3s"/>`;
 g+=`<path d="${path}" class="ln" style="--len:${Math.ceil(len)+2}" fill="none" stroke="#22d3ee" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>`;
 if(ser.length<=31)g+=pts.map((p,i)=>`<circle class="dp" style="animation-delay:${350+i*40}ms" cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="3" fill="#07070c" stroke="#22d3ee" stroke-width="2"/>`).join('');
 g+=`<text x="${m.l}" y="12">до ${usd(ms)} ${STEPL()}</text><text x="${W-m.r}" y="12" text-anchor="end" style="fill:#22d3ee">${RES[r][2]}: до ${ml} ${STEPL()}</text>`;
 const st=perStep(),dd=x=>st==='monthly'?x.slice(5,7)+'.'+x.slice(2,4):x.slice(8,10)+'.'+x.slice(5,7);g+=`<text x="${m.l}" y="${H-4}">${dd(ser[0].day)}</text><text x="${W-m.r}" y="${H-4}" text-anchor="end">${dd(ser.at(-1).day)}</text>`;s.innerHTML=g})}

/* ───── Мої конкуренти: додаєш сам, GitHub щотижня (або кнопкою) збирає їхню рекламу ───── */
let compRows=null,compMsg='';
const parseComp=v=>{v=(v||'').trim();if(!v)return null;let m=v.match(/view_all_page_id=(\d+)/)||v.match(/^(\d{6,})$/);if(m)return {kind:'fb',value:m[1]};
 m=v.match(/instagram\.com\/([A-Za-z0-9._]+)/i)||v.match(/^@?([A-Za-z0-9._]{2,30})$/);if(m&&!/^(p|reel|stories|explore)$/i.test(m[1]))return {kind:'ig',value:m[1].toLowerCase()};return {bad:v}};
const compShow=c=>c.ig?'@'+c.ig:c.kind==='ig'?'@'+c.value:'сторінка '+c.value;
const compCard=()=>{if(!compRows)compRows=[...(L$.comps||[]).map(c=>c.ig?'@'+c.ig:c.kind==='ig'?'@'+c.value:c.value)];while(compRows.length<3)compRows.push('');
 return `<div class="card"><div class="l">Твої конкуренти</div><div class="h2s" style="margin:0 0 6px">Посилання на Instagram (instagram.com/нік або @нік) чи посилання зі сторінки конкурента в бібліотеці реклами Meta. Я збираю всю їхню рекламу й розбираю, що окупається. Можна вставити кілька через пробіл чи кому в одне поле.</div>
 ${compRows.map((v,k)=>`<input class="in" data-crow="${k}" value="${esc(v)}" placeholder="instagram.com/…" style="margin-top:8px">`).join('')}
 <div class="row2"><button class="btn ghost sm" data-cadd="1">＋ Ще один</button><button class="btn sm" data-csave="1">Зберегти</button></div>
 <button class="btn ghost sm" data-ghrun="1">🔄 Оновити конкурентів та ідеї зараз</button>
 ${compMsg?`<div class="h2s" style="margin:10px 0 0;white-space:pre-wrap">${compMsg}</div>`:''}</div>`};
document.addEventListener('input',e=>{const k=e.target.dataset?.crow;if(k!==undefined&&compRows)compRows[+k]=e.target.value});
async function saveComps(){const parsed=compRows.flatMap(v=>String(v).split(/[\s,;]+/)).map(parseComp).filter(Boolean),bad=parsed.filter(x=>x.bad);if(bad.length){compMsg='Не розпізнав: '+bad.map(x=>esc(x.bad)).join(', ');return}
 const list=[...new Map(parsed.map(c=>[c.kind+c.value,c])).values()];const lines=[];
 const known=LC.known||{},unknown=[];
 for(const c of list){if(c.kind==='ig'&&known[c.value]){c.ig=c.value;c.kind='fb';c.value=known[c.value]}
  if(c.kind==='fb')lines.push('✓ '+compShow(c)+(c.ig?'':' (точний пошук)'));else{lines.push('• @'+c.value);unknown.push('@'+c.value)}}
 if(unknown.length)lines.push(`\nДля ${unknown.join(', ')} шукатиму рекламу за назвою акаунта: може не знайти, якщо назва сторінки у Facebook інша. Точніше вставити посилання з бібліотеки реклами.`);
 L$.comps=list;await CS.set('comps',JSON.stringify(list));
 const j=await gget(`${ACT()}/adlabels?fields=id,name&limit=200`);for(const l of (j.data||[]).filter(l=>/^ai_comp /.test(l.name)))try{await fetch(`${GV}/${l.id}?access_token=${encodeURIComponent(L$.token)}`,{method:'DELETE'})}catch(e){}
 for(const c of list)await gpost(`${ACT()}/adlabels`,{name:`ai_comp ${c.kind}=${c.value}${c.ig&&c.kind==='fb'?'|ig='+c.ig:''}`});
 compRows=list.map(c=>c.ig?'@'+c.ig:c.kind==='ig'?'@'+c.value:c.value);
 const run=await ghRun();compMsg=lines.join('\n')+'\n\n'+(run===true?'🚀 Оновлення запущено. За 3–5 хвилин прийде повідомлення в Telegram, тоді перезапусти застосунок.':run?'⚠ '+esc(run):'Збережено. Їхня реклама з\'явиться після оновлення: щопонеділка або кнопкою Run workflow → update на GitHub. Щоб запускати звідси, додай ключ GitHub у ⚙.')}
async function ghRun(){const t=await CS.get('gh_token');if(!t||!LC.repo)return false;
 try{const r=await fetch(`https://api.github.com/repos/${LC.repo}/actions/workflows/targetolog.yml/dispatches`,{method:'POST',headers:{Authorization:'Bearer '+t,Accept:'application/vnd.github+json'},body:JSON.stringify({ref:'main',inputs:{job:'update'}})});
  return r.status===204?true:`GitHub відповів ${r.status}: перевір ключ GitHub (Actions: Read and write)`}catch(e){return 'GitHub недоступний: '+e.message}}

/* ───── Ідеї ───── */
let iseg='ideas',bt='sum',aiBusy=false;const maxd=Math.max(...D.winners.map(w=>w.days),1);
const allIdeas=()=>[...L$.ideas.map(x=>({...x,ai:1})),...D.concepts];
V.ideas=()=>{const I=allIdeas();return top('Оновлено '+D.updated)+`<h2 style="margin-top:6px">Ідеї для реклами</h2>
<div class="seg"><button class="${iseg==='ideas'?'on':''}" data-iseg="ideas">Сценарії · ${I.length}</button><button class="${iseg==='comp'?'on':''}" data-iseg="comp">Конкуренти · ${CG.length}</button></div>
${iseg==='ideas'?`<p class="h2s">Готові сценарії на основі того, що окупається в конкурентів і що працює в тебе. Щопонеділка оновлюються самі.</p>
 <button class="btn ${L$.ai?'':'ghost'}" data-aiideas="1" style="margin:0 0 12px">${aiBusy?'<span class="spin"></span> ШІ думає…':L$.ai?'✨ Згенерувати 3 нові ідеї з урахуванням твоєї статистики':'✨ Свіжі ідеї від ШІ: додай ключ у налаштуваннях'}</button>
 ${I.map((c,i)=>`<div class="item" data-idea="${i}"><div class="ico i-ai">${c.ai?'✨':i+1-L$.ideas.length}</div><div class="tx"><b>${esc(c.concept)}</b><small>${esc((c.persona||'').split('(')[0])} · ${esc((c.format||'').split(',')[0])}</small></div><span class="chev">›</span></div>`).join('')||'<div class="card">Ідеї з\'являться після оновлення.</div>'}`
:`${CG.length?`<p class="h2s">Рекламу, яка не окупається, довго не тримають. Чим довше оголошення крутиться ${q('days')}, тим імовірніше воно приносить гроші.</p>`:`<div class="card" style="text-align:center"><div style="font-size:28px">🔍</div><b>Реклами конкурентів ще нема</b><div class="h2s" style="margin:6px 0 0">${(L$.comps||[]).length?`Конкурентів додано: ${L$.comps.length}. Їхня реклама з розбором ШІ з'явиться тут після оновлення.`:'Додай конкурентів у налаштуваннях, після оновлення тут з\'явиться їхня реклама з розбором ШІ.'}</div><button class="btn ghost sm" data-compset="1">⚙ ${(L$.comps||[]).length?'Конкуренти й оновлення':'Додати конкурентів'}</button></div>`}
${CG.map((g,k)=>{const w=g.ads[0];return `<div class="item" data-cgrp="${k}" style="display:block"><div style="display:flex;justify-content:space-between;gap:10px"><b>${esc(g.name)}</b><span style="font-weight:800;white-space:nowrap">${g.days} днів</span></div>
 <div style="color:var(--mut);font-size:13px;margin-top:3px">${g.ads.length>1?`${g.ads.length} ${pl(g.ads.length,['оголошення','оголошення','оголошень'])}, що окупаються · `:''}${esc(String(hookOf(w)).slice(0,110))}</div><div class="dbar"><i style="width:${Math.max(6,g.days/maxd*100)}%"></i></div></div>`}).join('')}`}`};
const hookOf=w=>(w.a?._model!=='mock'&&w.a?.hook?.text)||w.text||w.title||'';
/* один конкурент = одна картка, навіть якщо в нього кілька сторінок чи оголошень */
const CG=(()=>{const m=new Map();D.winners.forEach((w,i)=>{const k=String(w.page_name||'').toLowerCase().replace(/\s+-\s+.*$/,'').replace(/\s*(україна|ukraine|ua)\s*$/,'').trim();
 if(!m.has(k))m.set(k,{name:String(w.page_name).replace(/\s+(Україна|Ukraine)$/,''),ads:[]});m.get(k).ads.push({...w,i})});
 return [...m.values()].map(g=>({...g,ads:g.ads.sort((a,b)=>b.days-a.days),days:Math.max(...g.ads.map(x=>x.days))})).sort((a,b)=>b.days-a.days)})();
const igOf=pid=>Object.entries(LC.known||{}).find(([u,id])=>String(id)===String(pid))?.[0];
const whoLine=pid=>{const u=igOf(pid);return `<div class="h2s" style="margin:0 0 6px">${u?`<span data-open="https://www.instagram.com/${esc(u)}/" style="text-decoration:underline;cursor:pointer">@${esc(u)}</span> · `:''}<span data-open="https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=UA&view_all_page_id=${esc(pid)}" style="text-decoration:underline;cursor:pointer">усі їхні оголошення ↗</span></div>`};
const grpView=k=>()=>{const g=CG[k];return `<div class="card hero"><div class="lab">Конкурент</div><div class="ttl" style="margin:3px 0 6px">${esc(g.name)}</div>${g.ads[0]?.page_id?whoLine(g.ads[0].page_id):''}
 <div class="h2s" style="margin:0">${g.ads.length} ${pl(g.ads.length,['оголошення крутиться','оголошення крутяться','оголошень крутяться'])} 2+ тижні, найдовше ${g.days} днів</div></div>
 ${g.ads.map(w=>`<div class="item" data-comp="${w.i}" style="display:block"><div style="display:flex;justify-content:space-between;gap:10px"><span class="chip">${w.days} днів</span>${w.a?.steal_this&&w.a._model!=='mock'?'<span class="chip">💡 є що взяти</span>':''}</div>
  <div style="margin-top:8px;font-size:14px">${esc(String(hookOf(w)).slice(0,220))}</div></div>`).join('')}`};
const compView=i=>()=>{const w=D.winners[i],a=w.a?._model==='mock'?{}:(w.a||{}),h=a.hook||{},o=a.offer||{};
 return `<div class="card hero"><div class="lab">Конкурент</div><div class="ttl" style="margin:3px 0 4px">${esc(w.page_name)}</div>${w.page_id?whoLine(w.page_id):''}
 <span class="chip">крутиться ${w.days} днів</span>${w.variants>1?`<span class="chip">${w.variants} копій</span>`:''}${w.reuse?'<span class="chip">запускали повторно</span>':''}</div>
 <div class="card"><div class="sec" style="margin:0"><div class="l">Текст реклами</div>${esc(w.text||w.title)}</div>
 ${h.text?`<div class="sec"><div class="l">Чим чіпляє</div>${esc(h.text)}</div>`:'<div class="sec h2s" style="margin-left:0">Розбір ШІ з\'явиться після наступного оновлення.</div>'}${o.details?`<div class="sec"><div class="l">Що пропонує</div>${esc(o.details)}</div>`:''}
 ${a.persona?`<div class="sec"><div class="l">Для кого</div>${esc(a.persona)}</div>`:''}${a.why_works?`<div class="sec"><div class="l">Чому це працює</div>${esc(a.why_works)}</div>`:''}
 ${a.steal_this?`<div class="idea"><b>💡 Що взяти собі:</b> ${esc(a.steal_this)}</div>`:''}</div>
 ${w.snapshot_url?`<button class="btn ghost" data-open="${esc(w.snapshot_url)}">Відкрити в бібліотеці реклами</button>`:''}`};
const ideaView=i=>()=>{const c=allIdeas()[i];const segs=[['sum','Суть'],['shoot','Як зняти'],['hooks','Перші 3 сек'],['text','Текст']];
 const B={sum:`<div class="sec" style="margin:0"><div class="l">Для кого</div>${esc(c.persona)}</div><div class="sec"><div class="l">Формат</div>${esc(c.format)}</div>
  <div class="sec"><div class="l">Що пропонуємо</div>${esc(c.offer)}</div><div class="sec"><div class="l">Чому має спрацювати</div>${esc(c.hypothesis)}</div>${c.success?`<div class="sec"><div class="l">Як зрозуміємо, що спрацювало</div>${esc(c.success)}</div>`:''}`,
  shoot:(c.script||[]).map(s=>`<div class="step"><div class="tc">${esc(s.t)}</div><div>${esc(s.frame)}${s.on_screen?`<small>На екрані: «${esc(s.on_screen)}»</small>`:''}${s.voice&&s.voice!=='—'?`<small>Голос: «${esc(s.voice)}»</small>`:''}</div></div>`).join('')+(c.production?`<div class="sec"><div class="l">Що потрібно для зйомки</div>${esc(c.production)}</div>`:''),
  hooks:`<p class="h2s" style="margin:0 0 10px">Перші 3 секунди вирішують, чи прогорне людина. Три варіанти на тест:</p>`+(c.hooks||[]).map((h,n)=>`<div class="step"><div class="tc">#${n+1}</div><div>${esc(h)}</div></div>`).join(''),
  text:`<div class="sec" style="margin:0"><div class="l">Текст оголошення</div><div class="copy">${esc(c.primary_text)}</div></div><div class="sec"><div class="l">Заголовок</div><div class="copy">${esc(c.headline)}</div></div>
  <button class="btn" data-useidea="${i}">Використати для нового креативу</button><button class="btn ghost" data-copy="${i}">Скопіювати</button>`};
 return `<div class="card hero"><div class="lab">${c.ai?'✨ Від ШІ':'Ідея'}</div><div class="ttl">${esc(c.concept)}</div></div>
 <div class="seg">${segs.map(([k,l])=>`<button class="${k===bt?'on':''}" data-bt="${k}">${l}</button>`).join('')}</div><div class="card">${B[bt]}</div>${c.ai?`<button class="btn ghost sm" data-delidea="${i}">Видалити ідею</button>`:''}`};

/* ───── Налаштування ───── */
const mask=s=>s?s.slice(0,6)+'…'+s.slice(-4):'';
const compsView=()=>()=>`<h2 style="margin-top:6px">Конкуренти</h2>${compCard()}`;
const setView0=()=>()=>`<h2 style="margin-top:6px">Налаштування</h2>
 <div class="card"><div class="l">Кабінет Meta</div><b>${tok()?'✓ Підключено: '+esc(L$.acc.name):L$.token?'Ключ є, але Meta не відповідає':'Не підключено'}</b>${L$.err?`<div style="color:var(--bad);font-size:13px;margin-top:4px">${esc(L$.err)}</div>`:''}
  ${L$.token?`<div class="h2s" style="margin:4px 0 0">Ключ ${esc(mask(L$.token))}</div>`:''}<button class="btn ${L$.token?'ghost':''} sm" data-key="1">${L$.token?'Замінити ключ':'Вставити ключ Meta'}</button>${L$.token?'<button class="btn ghost sm" data-delkey="1">Відключити кабінет</button>':''}</div>
 <div class="item" data-norms="1" ><div class="ico i-ai">🎯</div><div class="tx"><b>Норми ціни результату</b><small>Переписка ${usd(NR('conv'))} · заявка ${usd(NR('lead'))} · перехід ${usd(NR('link'))}${L$.norms?'':' · стандартні, задай свої'}</small></div><span class="chev">›</span></div>
 <div class="item" data-compset="1"><div class="ico i-ai">🔍</div><div class="tx"><b>Конкуренти</b><small>${(L$.comps||[]).length?L$.comps.length+' у списку · '+esc(L$.comps.slice(0,3).map(compShow).join(', '))+(L$.comps.length>3?'…':''):'Ще не додано'}</small></div><span class="chev">›</span></div>
 <div class="card"><div class="l">ШІ для текстів, розборів та ідей</div><b>${L$.ai?'✓ '+(aiProv()==='anthropic'?'Claude (Anthropic)':aiProv()==='gemini'?'Gemini (Google)':'Невідомий ключ'):'Не підключено'}</b>
  <div class="h2s" style="margin:4px 0 0">Ключ Anthropic (sk-ant-…) або Gemini (AIza…). Зберігається тільки в твоєму Telegram. Один розбір чи 3 тексти коштують кілька центів.</div>
  <input id="aik" class="in mono" placeholder="${L$.ai?esc(mask(L$.ai)):'sk-ant-… або AIza…'}"><div class="row2"><button class="btn sm" data-aisave="1">Зберегти</button>${L$.ai?'<button class="btn ghost sm" data-aidel="1">Видалити</button>':'<span></span>'}</div></div>
 <div class="card"><div class="l">Ключ GitHub (необов'язково)</div><div class="h2s" style="margin:0 0 6px">Щоб після зміни конкурентів оновлення запускалось звідси, без GitHub. github.com → Settings → Developer settings → Fine-grained tokens → лише репозиторій ${esc(LC.repo||'')} → Actions: Read and write.</div>
  <input id="ghk" class="in mono" placeholder="${L$.gh?'збережено · '+esc(mask(L$.gh)):'github_pat_…'}"><div class="row2"><button class="btn sm" data-ghsave="1">Зберегти</button>${L$.gh?'<button class="btn ghost sm" data-ghdel="1">Видалити</button>':'<span></span>'}</div></div>
 <div class="card"><div class="l">Таблиця клієнтів</div><div class="h2s" style="margin:0 0 6px">Google Таблиця з колонками «Дата», «Статус» (Дзвінок / Оплата), «Сума». У таблиці: Поділитися → Загальний доступ → «Усі, хто має посилання» → Читач. Скопіюй посилання й встав сюди.</div>
  <input id="lcsv" class="in" value="${esc(L$.links.csv||'')}" placeholder="https://docs.google.com/spreadsheets/d/…">
  ${L$.sheet.length?`<div class="h2s" style="margin:6px 0 0">✓ Прочитано ${L$.sheet.length} записів за 90 днів</div>`:''}</div>
 <div class="card"><div class="l">Посилання за замовчуванням</div>
  <div class="h2s" style="margin:6px 0 0">Telegram для кампаній «Переходи в Telegram»</div><input id="ltg" class="in" value="${esc(L$.links.tg||'')}" placeholder="https://t.me/…">
  <div class="h2s" style="margin:10px 0 0">Сайт для кампаній «Переходи на сайт»</div><input id="lsite" class="in" value="${esc(L$.links.site||'')}" placeholder="https://…">
  <div class="h2s" style="margin:10px 0 0">Політика конфіденційності (обов'язкова для лід-форм)</div><input id="lpriv" class="in" value="${esc(L$.links.privacy||'')}"></div>
 <button class="btn" data-lsave="1">Зберегти</button>
 <button class="btn ghost" data-how="1">Як працює ШІ-таргетолог</button>`;
const keyView=()=>()=>`<h2 style="margin-top:6px">Ключ Meta</h2><div class="card"><div class="h2s" style="margin:0 0 10px">Встав ключ доступу системного користувача targetolog. Він зберігається тільки в твоєму Telegram і використовується лише цим застосунком.</div>
 <textarea id="mk" class="in mono" rows="4" placeholder="EAA…"></textarea></div><button class="btn" data-savekey="1">Підключити</button>`;
const howView=()=>`<h2 style="margin-top:6px">Як працює ШІ-таргетолог</h2><p class="h2s">Від тебе креативи й «так» на рішення. Решту робить сам.</p>
<div class="card"><div class="flowmap">
<div class="fs"><div class="dotc">🔍</div><b>Щопонеділка дивиться конкурентів</b><small>О 06:13 збирає рекламу з бібліотеки Meta за запитами твоєї ніші, відсіює чуже (курси, CRM, інші ніші) і залишає ту, що крутиться 2+ тижні, тобто окупається. ШІ (Claude, а якщо він недоступний, Gemini) розбирає, чим вона чіпляє і що взяти собі. Після оновлення пише тобі в Telegram.</small></div>
<div class="fs"><div class="dotc">✍️</div><b>Пише сценарії</b><small>Нові ідеї для зйомки з'являються у вкладці «Ідеї». Кнопкою можна попросити ще три, з урахуванням твоєї статистики.</small></div>
<div class="fs"><div class="dotc">🎯</div><b>Кампанії під різні цілі</b><small>Переписки в Direct, заявки через форму, переходи в Telegram чи на сайт. У кожної свій бюджет, аудиторія, плейсменти, за бажанням ретаргет на тих, хто тебе вже знає.</small></div>
<div class="fs"><div class="dotc">🚀</div><b>Креатив за хвилину</b><small>Фото чи відео (4:5 і 9:16), до трьох текстів. ШІ напише тексти й розбере креатив до запуску, зокрема ризик відхилення Meta. Запущений текст можна змінити, статистика збережеться.</small></div>
<div class="fs"><div class="dotc">📊</div><b>Щоранку звіт у Telegram</b><small>О 07:47: вчора й за тиждень, ціна результату проти норми, відхилені оголошення з причиною, рішення: що вимкнути, де додати бюджет. Детальний звіт по днях, віку, статі й плейсментах у вкладці «Звіт».</small></div>
<div class="fs"><div class="dotc">💳</div><b>Рахує справжніх клієнтів</b><small>Дзвінки й оплати з таблиці клієнтів або ручних відміток. Видно ціну клієнта й скільки повертає кожна гривня реклами.</small></div>
<div class="fs"><div class="dotc">✅</div><b>Ти вирішуєш</b><small>Без твого «так» нічого не змінюється. Нову рекламу ШІ оцінює, лише коли вона витратила дві норми ціни результату або набрала 3 результати, тож на малому бюджеті чекає довше. Бюджет додає по 20%, а наступний крок робить, коли група витратить ще три норми за новим бюджетом (2–7 днів). Ключі Meta та ШІ зберігаються лише у твоєму Telegram.</small></div>
</div></div><button class="btn" data-back="1">Зрозуміло</button>`;

/* ───── Норми: юніт-економіка замість «60 грн з повітря» ───── */
const NIN0={check:15000,share:15,chat:10,lead:7,click:12};
const calcN=i=>{const cac=i.check*i.share/100,conv=cac*i.chat/100;return {cac,conv:Math.round(conv),lead:Math.round(cac*i.lead/100),link:Math.max(1,Math.round(conv*i.click/100))}};
let nd=null;
const normsView=()=>()=>{const i=nd,c=calcN(i),f=(k,l,h,suf)=>`<div class="sec"><div class="l">${l}</div><div style="display:flex;align-items:center;gap:8px"><input class="in" data-nin="${k}" inputmode="numeric" value="${i[k]}" style="margin:0;max-width:130px"><span style="color:var(--mut)">${suf}</span></div><div class="h2s" style="margin:4px 0 0">${h}</div></div>`;
 return `<h2 style="margin-top:6px">Норми ціни результату</h2><p class="h2s">Таргетолог не бере норму з повітря: рахує, скільки можна віддати за одного клієнта, і множить на те, яка частка переписок стає клієнтами ${q('norm')}</p>
 <div class="card">${f('check','Скільки приносить один клієнт','Чек або прибуток з одного клієнта, що тобі зручніше. Головне, щоб відсоток нижче був саме від цього числа.','₴')}
 ${f('share','Скільки з цієї суми готовий віддати на рекламу','Зазвичай 10–20% для послуг. Більше, і реклама з\'їдає прибуток.','%')}
 ${f('chat','Зі 100 переписок стають клієнтами','Якщо не знаєш, почни з 5–10%. Потім уточниш із таблиці клієнтів.','%')}
 ${f('lead','Зі 100 заявок з форми стають клієнтами','Заявки з форми зазвичай холодніші за переписки.','%')}
 ${f('click','Зі 100 переходів пишуть тобі','Для Telegram чи сайту зазвичай 5–15%.','%')}</div>
 <div class="card hero" id="nres">${nres(c)}</div>
 <button class="btn" data-nsave="1">Зберегти норми</button>
 <button class="btn ghost" data-nai="1">${L$.ai?'✨ ШІ перевірить, чи реалістично для ніші':'✨ Перевірка ШІ: додай ключ у налаштуваннях'}</button><div id="naiout"></div>
 <p class="h2s" style="margin-top:10px">Норми свої для кожного кабінету Meta: їх бачить і застосунок, і щоранковий звіт у Telegram. Новий власник бота задає свої.</p>`};
const nres=c=>`<div class="lab">Можна віддати за одного клієнта <span class="pro">max CAC</span></div><div class="big">${usd(c.cac)}</div>
 <div class="mg" style="margin:10px 0 0"><div class="m"><span>Переписка</span><b>${usd(c.conv)}</b></div><div class="m"><span>Заявка</span><b>${usd(c.lead)}</b></div><div class="m"><span>Перехід</span><b>${usd(c.link)}</b></div></div>
 <div class="h2s" style="margin:8px 0 0">Переписка = ${usd(c.cac)} × ${nd.chat}%. Дорожче за це, і реклама не окупається.</div>`;
document.addEventListener('input',e=>{const k=e.target.dataset?.nin;if(!k||!nd)return;nd[k]=+String(e.target.value).replace(/[^\d.]/g,'')||0;const el=$('#nres');if(el)el.innerHTML=nres(calcN(nd))});
async function saveNorms(){const c=calcN(nd);L$.norms={conv:c.conv,lead:c.lead,link:c.link};L$.nin=nd;await CS.set('norms',JSON.stringify(L$.norms));await CS.set('norms_in',JSON.stringify(nd));
 /* щоб щоранковий звіт на GitHub бачив ті самі норми, зберігаємо їх міткою в кабінеті Meta */
 if(tok())try{const j=await gget(`${ACT()}/adlabels?fields=id,name&limit=100`);for(const l of (j.data||[]).filter(l=>/^ai_norms /.test(l.name)))try{await fetch(`${GV}/${l.id}?access_token=${encodeURIComponent(L$.token)}`,{method:'DELETE'})}catch(e){}
  await gpost(`${ACT()}/adlabels`,{name:`ai_norms conv=${c.conv} lead=${c.lead} link=${c.link}`})}catch(e){toast('Норми збережено тут, але не в Meta: '+e.message.slice(0,60))}}

/* ───── Знання таргетолога, які ШІ застосовує в усіх відповідях ───── */
const SKILLS=`Правила роботи таргетолога (застосовуй, коли доречно):
- Рішення приймай за ціною результату проти норми, а не за CTR чи охопленням. Норма = середній чек × частка на рекламу × конверсія в клієнта.
- Навчання Meta: ~50 результатів за тиждень після останньої суттєвої зміни. Нове оголошення не оцінювати, поки не витратило 2 норми або не набрало 3 результати (мінімум 2 доби); кількість днів залежить від бюджету: ≈ 2 норми ÷ денний бюджет на оголошення.
- Вимикати: витрачено ≥2 норми без результату, або ціна >1,5 норми після ≥3 результатів. Єдине оголошення в групі не вимикати без заміни.
- Бюджет міняти не більше ніж на 20% за раз (більша зміна перезапускає навчання). Наступна зміна, коли група витратила ще ~3 норми за новим бюджетом: від 2 до 7 днів залежно від бюджету.
- Малий бюджет (до ~300 ₴/день): одна кампанія, одна група, Advantage+ аудиторія й автоплейсменти, 2–4 креативи. Не дробити на багато груп.
- Креатив важливіший за таргетинг: тестуй різні кути (біль, результат, кейс, ціна, процес), а не кольори кнопки. Хук у перші 3 секунди.
- Частота >3 за тиждень означає втому креативу. CPM росте: аудиторія вузька або креатив слабкий.
- Переписки в Direct дешевші, але холодніші за заявки з форми; переходи найдешевші й найхолодніші. Порівнюй за ціною клієнта, а не результату.
- Ретаргет на тих, хто взаємодіяв з профілем, зазвичай дає найдешевших клієнтів, але аудиторія мала.
- Правила Meta: без звертань до особистих рис, без «до/після», без гарантій результату.`;
let askQ='',askA='',askBusy=false;
const askView=()=>()=>`<h2 style="margin-top:6px">Спитати таргетолога</h2><p class="h2s">ШІ бачить твої кампанії, витрати за 7 днів, норми й конкурентів і відповідає за правилами таргетолога.</p>
 <div class="chips" style="margin-bottom:10px">${['Що зараз змінити в рекламі?','Чому дорогі переписки?','Яку кампанію запустити першою?','Скільки креативів тестувати?'].map(x=>`<button data-askq="${esc(x)}">${x}</button>`).join('')}</div>
 <div class="card"><textarea id="askt" class="in" rows="3" placeholder="Твоє питання">${esc(askQ)}</textarea><button class="btn sm" data-ask="1">${askBusy?'<span class="spin"></span> Думаю…':'Спитати'}</button></div>
 ${askA?`<div class="card" style="white-space:pre-wrap">${esc(askA)}</div>`:''}`;
function acctCtx(){const camps=L$.camps.map(c=>{const g=GOALS[goalOfCamp(c.id)],i=campIns(c.id),b=setsOf(c.id).reduce((a,s)=>a+(dB(s)||0),0);return `- «${c.name}» (${g.name}, ${c.effective_status}, ${b} ₴/день): витрати 7 дн ${Math.round(i.spend)} ₴, ${i[g.res]} ${RES[g.res][2]}, ціна ${cost(i,g.res)?Math.round(cost(i,g.res))+' ₴':'—'}, норма ${g.norm} ₴`}).join('\n')||'- кампаній ще нема';
 const all=[...L$.marks,...L$.sheet];return `Кабінет:\n${camps}\nКреативів у застосунку: ${L$.crs.length}, оголошень у Meta: ${L$.ads.length}. За 90 днів витрачено ${Math.round(L$.sp90)} ₴, дзвінків ${all.filter(m=>m.t==='call').length}, оплат ${all.filter(m=>m.t==='paid').length}. Норми: переписка ${NR('conv')} ₴, заявка ${NR('lead')} ₴, перехід ${NR('link')} ₴.`}

/* ───── ШІ-дії ───── */
async function aiTexts(){keepDraft();const gk=draft.camp?goalOfCamp(draft.camp):(L$.camps[0]?goalOfCamp(L$.camps[0].id):'direct');const car=isCar(draft);
 let imgs=[],vis='';
 if(car){const cs=draft.cards;const per=cs.length<=4?3:cs.length<=7?2:1;for(const c of cs)imgs.push(...await fileImgs(c.file,c.file.type.startsWith('video')?per:1,768));
  vis=`\n\nЦе КАРУСЕЛЬ з ${cs.length} карток. Картинки додано по порядку карток (для відео-карток по кілька кадрів поспіль). Спершу роздивись усю історію: що на кожній картці, який меседж веде від першої до останньої, текст на картках. Основний текст має працювати на всю карусель і спонукати гортати, а не описувати одну картку. Для кожної картки дай короткий заголовок до 40 символів, який підсилює саме її, не повторює дослівно текст на ній.`}
 else if(draft.file){imgs=await fileImgs(draft.file,6);const v=imgs[0]?.video;
  if(imgs.length)vis=v?`\n\nДодано ${imgs.length} кадрів з відео тривалістю ~${imgs[0].dur} с, рівномірно від початку до кінця (секунди: ${imgs.map(x=>x.t).join(', ')}). Звуку ти не чуєш. Спершу відтвори сюжет: що відбувається, титри, як розвивається меседж, чим закінчується. Перший кадр — це те, що людина бачить перші секунди, хук тексту має з ним працювати. Текст продовжує саме це відео, не переказує його і не суперечить.`
   :`\n\nДо повідомлення додано картинку креативу, під який пишеш. Спершу роздивись: що на ній, який меседж, текст на зображенні, для кого це. Текст оголошення має продовжувати саме цей креатив: хук перегукується з тим, що людина бачить, не повторює дослівно текст з картинки й не суперечить їй.`;
  if(imgs.length)vis+=` Якщо креатив не про наш продукт, все одно пиши про продукт, але зв'язуй з тим, що бачиш.`}
 const t=await ai(SYSf(),`${aiCtx()}${vis}\n\nНапиши 3 різні варіанти тексту оголошення для Instagram. Мета: ${GOALS[gk].name}.${draft.topic?' Про що реклама: '+draft.topic+'.':''}
Кожен варіант з іншим хуком (перше речення) і кутом подачі. 300–600 символів, абзаци, в кінці заклик до дії під мету (${gk==='direct'?'написати в Direct':gk==='lead'?'залишити заявку':'перейти за посиланням'}).
Формат: {"headline":"заголовок до 40 символів","variants":["текст A","текст B","текст C"]${car?',"cards":["заголовок картки 1","…"]':''}}`,imgs);const j=pj(t);
 Object.assign(draft,{headline:draft.headline||j.headline||'',text:j.variants[0]||'',text2:j.variants[1]||'',text3:j.variants[2]||''});
 if(car&&Array.isArray(j.cards))draft.cards.forEach((c,i)=>{if(!c.title&&j.cards[i])c.title=String(j.cards[i]).slice(0,40)})}
async function aiReview(c){let img=c.thumb?[{url:c.thumb}]:[];
 if(c.kind==='carousel'){img=[];const hs=c.cards.filter(x=>x.k==='i').map(x=>x.r);let urls={};if(hs.length)try{(await gget(`${ACT()}/adimages?hashes=${encodeURIComponent(JSON.stringify(hs))}&fields=hash,url`)).data.forEach(x=>urls[x.hash]=x.url)}catch(e){}
  for(const x of c.cards){const u=x.k==='i'?urls[x.r]:await videoReady(x.r).catch(()=>'');if(u)img.push({url:u})}}
 const t=await ai(SYSf(),`${aiCtx()}\n\nРозбери мій креатив перед запуском${img.length?' (зображення додано)':''}. Тип: ${c.kind==='carousel'?`карусель з ${c.cards.length} карток, зображення по порядку; заголовки карток: ${c.cards.map((x,i)=>(i+1)+'. '+(x.t||'—')).join('; ')}. Оціни ще, чи тягне перша картка гортати далі`:c.kind==='video'?'відео (бачиш лише обкладинку)':'фото'}.
Заголовок: ${c.headline||'—'}\nТекст(и):\n${c.texts.map((x,k)=>LET[k]+': '+x).join('\n---\n')}
Оціни як таргетолог: чи зупинить скрол, чи зрозуміла пропозиція за 3 секунди, що виправити в першу чергу, чи є ризик відхилення правилами Meta.
Формат: {"score":1-10,"hook":"1-2 речення","offer":"1-2 речення","fix":["до 4 конкретних правок"],"risk":"порожньо, якщо ризику нема"}`,img);
 const j=pj(t);c.review={score:+j.score||0,hook:String(j.hook||'').slice(0,300),offer:String(j.offer||'').slice(0,300),fix:(j.fix||[]).map(x=>String(x).slice(0,200)),risk:String(j.risk||'').slice(0,250)}}
async function aiIdeas(){const t=await ai(SYSf(),`${aiCtx()}\n\nЗапропонуй 3 нові ідеї реклами, яких ще нема серед цих: ${allIdeas().map(c=>c.concept).join('; ')}.
Кожна для іншої аудиторії з ніші. Бери механіку в конкурентів, але слова й пропозиція мої. Враховуй, що працює в моїй рекламі.
Формат: {"ideas":[{"concept":"назва до 70 символів","persona":"для кого","format":"формат","offer":"що пропонуємо","hypothesis":"чому має спрацювати","hooks":["3 варіанти перших 3 секунд"],"primary_text":"текст оголошення до 500 символів","headline":"до 40 символів","script":[{"t":"0–3с","frame":"що в кадрі","on_screen":"текст на екрані"}]}]}`,null,true);
 const j=pj(t);const idx=await CSj('idea_index',[]);let n=Math.max(0,...idx)+1;
 for(const x of (j.ideas||[]).slice(0,3)){const c={concept:x.concept,persona:x.persona,format:x.format,offer:x.offer,hypothesis:x.hypothesis,hooks:(x.hooks||[]).slice(0,3),primary_text:String(x.primary_text||'').slice(0,700),headline:x.headline,script:(x.script||[]).slice(0,5)};
  let s=JSON.stringify(c);while(s.length>3900&&c.script.length){c.script.pop();s=JSON.stringify(c)}await CS.set('idea_'+n,s);idx.unshift(n);n++}
 await CS.set('idea_index',JSON.stringify(idx.slice(0,12)));await loadIdeas()}

/* ───── Події ───── */
async function act(d){
 if(await recClick(d)||await audClick(d))return;
 // кампанії
 if(d.camp){go(campView(d.camp));return}
 if(d.newcamp){if(!tok()){go(keyView());return}const a=await CSj('aud',null),lid=stack.at(-1)?.lid||d.lid||null;nc={goal:'direct',budget:+(await CS.get('def_budget'))||LC.budget,aud:{...defAud(),...(a||{}),place:[]},link:'',form:'',name:'',lid};L$.forms=null;go(Object.assign(newCampView(),{k:'new'}));return}
 if(d.ngoal){keepNc();nc.goal=d.ngoal;nc.link=d.ngoal==='tg'?L$.links.tg||'':d.ngoal==='site'?L$.links.site||'':'';if(d.ngoal==='lead'&&L$.forms==null)loadForms();reView();return}
 if(d.nbud){keepNc();nc.budget=+d.nbud;reView();return}
 if(d.nform){keepNc();nc.form=d.nform;reView();return}
 if(d.naud){keepNc();go(Object.assign(nAudView(),{k:'naud'}));return}
 if(d.ncreate){keepNc();toast('Створюю кампанію…');try{const cid=await createCamp(nc);okHap();toast('✓ Кампанію створено');await liveLoad();stack=[];tab='ads';
   if(nc.lid){launchFor=cid;go(Object.assign(launchView(nc.lid),{lid:nc.lid}))}else go(campView(cid))}catch(e){err(e)}return}
 if(d.cpause||d.cresume){const id=d.cpause||d.cresume;confirmDo(d.cpause?'Зупинити всю кампанію?':'Увімкнути кампанію?',async()=>{try{await gpost(id,{status:d.cpause?'PAUSED':'ACTIVE'});toast(d.cpause?'⏸ Кампанію зупинено':'▶ Кампанію увімкнено');await liveLoad()}catch(e){err(e)}});return}
 if(d.rt){confirmDo('Створити групу ретаргету з бюджетом 50 ₴/день?',async()=>{toast('Створюю ретаргет…');try{await makeRt(d.rt);okHap();toast('✓ Ретаргет запущено');await liveLoad()}catch(e){err(e)}});return}
 // групи
 if(d.set2){budVal=null;sd=null;go(setView(d.set2));return}
 if(d.bstep||d.bset){budVal=d.bset?+d.bset:Math.max(MINB,budVal+(+d.bstep));hap('soft');re(setView(sd.id));return}
 if(d.bsave){const v=budVal;confirmDo(`Встановити ${usd(v)} на день?`,async()=>{try{await gpost(d.bsave,{daily_budget:String(Math.round(v*100))});ls.set('bch_'+d.bsave,Date.now());await CS.set('def_budget',String(v));okHap();toast('✓ Бюджет змінено в Meta');await liveLoad()}catch(e){err(e)}});return}
 if(d.tsave){const s=L$.sets.find(x=>x.id===d.tsave);const t=isRt(s)?buildT({...sd.a,adv:false},s.targeting.custom_audiences.map(x=>({id:x.id}))):buildT(sd.a);
  confirmDo('Змінити аудиторію й плейсменти? Meta кілька днів заново навчатиметься.',async()=>{try{await gpost(d.tsave,{targeting:JSON.stringify(t)});if(!isRt(s))await CS.set('aud',JSON.stringify({...sd.a,place:[]}));okHap();toast('✓ Збережено в Meta');await liveLoad()}catch(e){err(e)}});return}
 if(d.spause||d.sresume){const id=d.spause||d.sresume;confirmDo(d.spause?'Зупинити всі оголошення в групі?':'Увімкнути групу?',async()=>{try{await gpost(id,{status:d.spause?'PAUSED':'ACTIVE'});toast(d.spause?'⏸ Групу зупинено':'▶ Групу увімкнено');await liveLoad()}catch(e){err(e)}});return}
 // креативи
 if(d.add!==undefined){if(!tok()){go(keyView());return}draft={camp:d.addcamp||null};go(addView());return}
 if(d.useidea!==undefined){const c=allIdeas()[+d.useidea];draft={headline:c.headline,text:c.primary_text,topic:c.concept};tab='ads';stack=[];go(addView());return}
 if(d.crmode){keepDraft();draft.mode=d.crmode;re(addView());return}
 if(d.cup||d.cdown||d.cdel){keepDraft();const cs=draft.cards,i=+(d.cup||d.cdown||d.cdel);if(d.cdel)cs.splice(i,1);else{const j=d.cup?i-1:i+1;[cs[i],cs[j]]=[cs[j],cs[i]]}re(addView());return}
 if(d.aitext){if(!L$.ai){go(setView0());return}toast(draft.file?'✨ ШІ дивиться креатив і пише…':'✨ ШІ пише…');try{await aiTexts();okHap();re(addView())}catch(e){err(e)}return}
 if(d.save){keepDraft();const t=[draft.text,draft.text2,draft.text3].map(x=>(x||'').trim()).filter(Boolean);
  if(isCar(draft)){const cs=draft.cards||[];if(cs.length<2){toast('У каруселі мінімум 2 картки');return}if(!t.length){toast('Напиши текст оголошення');return}
   if(cs.some(x=>x.file.size>100*1024*1024)){toast('Файл більший за 100 МБ');return}
   try{const cards=[];let th='';for(let i=0;i<cs.length;i++){toast(`Завантажую картку ${i+1}/${cs.length}…`);const u=await upload(cs[i].file);cards.push({k:u.kind==='image'?'i':'v',r:u.ref,t:(cs[i].title||'').trim().slice(0,40)});if(!i)th=u.thumb}
    const id=(L$.crs.reduce((m,c)=>Math.max(m,c.id),0))+1;const c=normCr({id,kind:'carousel',cards,thumb:th||'',headline:draft.headline.trim(),texts:t,created:Date.now(),ads:[]});c.preview=cs[0].preview;
    L$.crs.push(c);await saveCr(c);await saveIdx();const camp=draft.camp;draft=null;stack=[];tab='ads';toast('✓ Карусель збережено');go(crView(id));if(camp){launchFor=camp}}catch(e){err(e)}return}
  if(!draft.file){toast('Вибери фото чи відео');return}if(!t.length){toast('Напиши текст оголошення');return}
  if(draft.file.size>100*1024*1024||draft.file2?.size>100*1024*1024){toast('Файл більший за 100 МБ');return}
  if(draft.file2&&draft.file2.type.slice(0,5)!==draft.file.type.slice(0,5)){toast('Обидва файли мають бути одного типу');return}
  toast('Завантажую в Meta…');try{const up=await upload(draft.file);let up2={};if(draft.file2){const u=await upload(draft.file2);up2={ref2:u.ref,thumb2:u.thumb}}
   const id=(L$.crs.reduce((m,c)=>Math.max(m,c.id),0))+1;const c=normCr({id,...up,...up2,headline:draft.headline.trim(),texts:t,created:Date.now(),ads:[]});c.preview=draft.preview;
   L$.crs.push(c);await saveCr(c);await saveIdx();const camp=draft.camp;draft=null;stack=[];tab='ads';toast('✓ Креатив збережено');go(crView(id));if(camp){launchFor=camp}}catch(e){err(e)}return}
 if(d.review){if(!L$.ai){go(setView0());return}const c=L$.crs.find(x=>x.id==d.review);toast('🧐 ШІ розбирає…');try{await aiReview(c);await saveCr(c);okHap();re(crView(c.id))}catch(e){err(e)}return}
 if(d.launch){const c=L$.crs.find(x=>x.id==d.launch);if(!L$.camps.length)return act({newcamp:1,lid:c.id});
  const free=L$.camps.filter(x=>!c.ads.some(z=>(z.camp||c.camp)===x.id));launchFor=free.length===1?free[0].id:free.some(x=>x.id===launchFor)?launchFor:null;
  go(Object.assign(launchView(c.id),{lid:c.id}));return}
 if(d.lcamp){launchFor=d.lcamp;const lid=stack.at(-1).lid;re(Object.assign(launchView(lid),{lid}));return}
 if(d.lgo){const c=L$.crs.find(x=>x.id==d.lgo),cid=launchFor,cn=L$.camps.find(x=>x.id===cid)?.name;
  confirmDo(`Запустити в «${cn}»?${c.texts.length>1?' '+c.texts.length+' варіанти тексту.':''}`,async()=>{toast('Запускаю…');try{await launchCr(c,cid);await saveCr(c);okHap();toast('🚀 Запущено, Meta перевіряє');launchFor=null;await liveLoad();stack=[];tab='ads';go(crView(c.id))}
   catch(e){c.error=e.message;await saveCr(c);err(e);stack.pop();render()}});return}
 if(d.edit){const [id,k]=d.edit.split(':');go(editView(+id,+k));return}
 if(d.aifix){const [id,k]=d.aifix.split(':').map(Number);const c=L$.crs.find(x=>x.id==id);toast('✨ ШІ переписує…');
  try{const t=await ai(SYSf(),`${aiCtx()}\n\nПерепиши текст оголошення, зберігши суть і довжину. ${c.review?'Врахуй розбір: '+c.review.fix.join('; ')+(c.review.risk?'; ризик Meta: '+c.review.risk:''):'Зроби сильніший хук і чіткішу пропозицію.'}\nТекст:\n${$('#et').value}\nФормат: {"text":"новий текст"}`);$('#et').value=pj(t).text;okHap()}catch(e){err(e)}return}
 if(d.esave){const [id,k]=d.esave.split(':').map(Number);const c=L$.crs.find(x=>x.id==id);const nt=$('#et').value.trim();if(!nt)return;
  const run=async()=>{try{c.texts[k]=nt;const ent=c.ads.filter(x=>x.k===k);const byCamp={};for(const x of ent)(byCamp[x.camp||c.camp]=byCamp[x.camp||c.camp]||[]).push(x);
   for(const [cid,xs] of Object.entries(byCamp)){const crid=await mkCreative(c,k,cid);for(const x of xs){await gpost(x.ad,{creative:JSON.stringify({creative_id:crid})});x.cr=crid}}
   await saveCr(c);okHap();toast(ent.length?'✓ Текст оновлено, Meta перевіряє':'✓ Збережено');await liveLoad();back()}catch(e){err(e)}};
  if(c.ads.some(x=>x.k===k))confirmDo('Оновити текст у Meta? Оголошення пройде повторну перевірку.',run);else run();return}
 if(d.vpause){const [id,k]=d.vpause.split(':').map(Number);const c=L$.crs.find(x=>x.id==id);confirmDo(`Вимкнути варіант ${LET[k]}?`,async()=>{try{for(const x of c.ads.filter(z=>z.k===k))await gpost(x.ad,{status:'PAUSED'});toast('⏸ Варіант вимкнено');await liveLoad()}catch(e){err(e)}});return}
 if(d.pausecr||d.resumecr){const c=L$.crs.find(x=>x.id==(d.pausecr||d.resumecr));try{for(const x of c.ads)await gpost(x.ad,{status:d.pausecr?'PAUSED':'ACTIVE'});toast(d.pausecr?'⏸ На паузі':'▶ Показ відновлено');await liveLoad()}catch(e){err(e)}return}
 if(d.delcr){L$.crs=L$.crs.filter(x=>x.id!=d.delcr);await CS.del('cr_'+d.delcr);await saveIdx();back();return}
 if(d.cr){go(crView(+d.cr));return}
 if(d.adlive){go(adLiveView(d.adlive));return}
 if(d.pause||d.resume){try{await gpost(d.pause||d.resume,{status:d.pause?'PAUSED':'ACTIVE'});toast(d.pause?'⏸ На паузі':'▶ Показ відновлено');await liveLoad()}catch(e){err(e)}return}
 // клієнти
 if(d.mark){mkDraft={t:'call',ad:'',s:0};go(markView());return}
 if(d.mt){mkDraft.t=d.mt;reMark();return}
 if(d.mad!==undefined){mkDraft.ad=d.mad;reMark();return}
 if(d.msave){if($('#msum'))mkDraft.s=+$('#msum').value||0;await addMark({t:mkDraft.t,ad:mkDraft.ad,s:mkDraft.s||0,d:Date.now()});okHap();toast('✓ Записано');back();return}
 // звіт
 if(d.rp){rp=d.rp;hap('soft');if(rp==='custom'&&!rf){const a=new Date();a.setMonth(a.getMonth()-3);rf=isoD(a);rt2=isoD(new Date())}loadRep();return}
 if(d.rgo){rf=$('#rf').value;rt2=$('#rt').value;if(!rf||!rt2||rf>rt2){toast('Перевір дати');return}loadRep();return}
 if(d.rq){const a=new Date();if(d.rq==='prev'){const b=new Date(a.getFullYear(),a.getMonth(),0);rf=isoD(new Date(b.getFullYear(),b.getMonth(),1));rt2=isoD(b)}else{const n=+d.rq;a.setMonth(a.getMonth()-n);rf=isoD(a);rt2=isoD(new Date())}loadRep();return}
 if(d.rc!==undefined){rc=d.rc;hap('soft');loadRep();return}
 if(d.rb){rb=d.rb;hap('soft');render();return}
 // ідеї
 if(d.aiideas){if(!L$.ai){go(setView0());return}if(aiBusy)return;aiBusy=true;render();try{await aiIdeas();okHap();toast('✓ 3 нові ідеї')}catch(e){err(e)}aiBusy=false;render();return}
 if(d.delidea!==undefined){const idx=await CSj('idea_index',[]);const n=idx[+d.delidea];if(n!=null){await CS.del('idea_'+n);idx.splice(+d.delidea,1);await CS.set('idea_index',JSON.stringify(idx));await loadIdeas()}back();return}
 if(d.iseg){iseg=d.iseg;hap('soft');render();return}
 if(d.idea!==undefined){bt='sum';go(ideaView(+d.idea));return}
 if(d.comp!==undefined){go(compView(+d.comp));return}
 if(d.cgrp!==undefined){const g=CG[+d.cgrp];go(g.ads.length>1?grpView(+d.cgrp):compView(g.ads[0].i));return}
 if(d.bt){bt=d.bt;hap('soft');render();return}
 if(d.copy!==undefined){const c=allIdeas()[+d.copy];try{await navigator.clipboard.writeText(c.primary_text+'\n\n'+c.headline);toast('Скопійовано ✓')}catch(x){toast('Виділи текст і скопіюй')}return}
 // норми й питання
 if(d.norms){nd={...NIN0,...(L$.nin||{})};go(normsView());return}
 if(d.nsave){await saveNorms();okHap();toast('✓ Норми збережено');back();return}
 if(d.nai){if(!L$.ai){go(setView0());return}const el=$('#naiout');el.innerHTML='<div class="card"><span class="spin"></span> ШІ рахує…</div>';const c=calcN(nd);
  try{const t=await ai(SYSf(),`${aiCtx()}\n\nМої вхідні: середній чек ${nd.check} ₴, на рекламу ${nd.share}% чека, зі 100 переписок купують ${nd.chat}, зі 100 заявок ${nd.lead}, зі 100 переходів пишуть ${nd.click}. Вийшло: клієнт до ${Math.round(c.cac)} ₴, переписка до ${c.conv} ₴, заявка до ${c.lead} ₴, перехід до ${c.link} ₴.
Оціни як таргетолог: чи реалістичні ці припущення для моєї ніші в Україні, яка зазвичай ціна переписки в схожих нішах, що б ти змінив. Коротко, 4–6 речень. Формат: {"answer":"текст"}`,null,true);el.innerHTML=`<div class="card" style="white-space:pre-wrap">${esc(pj(t).answer)}</div>`}catch(e){el.innerHTML='';err(e)}return}
 if(d.askv){go(askView());return}
 if(d.askq){askQ=d.askq;re(askView());return}
 if(d.ask){askQ=$('#askt').value.trim();if(!askQ)return;if(!L$.ai){go(setView0());return}askBusy=true;re(askView());
  try{const t=await ai(SYSf(),`${aiCtx()}\n\n${acctCtx()}\n\nПитання: ${askQ}\nВідповідай конкретно під мої цифри, простою мовою, з термінами таргетолога в дужках. До 8 речень або короткий список. Формат: {"answer":"текст"}`,null,true);askA=pj(t).answer}catch(e){err(e)}askBusy=false;re(askView());return}
 // конкуренти
 if(d.compset){if(!tok()){go(keyView());return}go(compsView());return}
 if(d.cadd){compRows.push('');re0();return}
 if(d.csave){if(!tok()){go(keyView());return}compMsg='<span class="spin"></span> Перевіряю й зберігаю…';re0();try{await saveComps();okHap()}catch(e){compMsg='⚠ '+esc(e.message)}re0();return}
 if(d.ghrun){if(!L$.gh){sheet(`<h3>Потрібен ключ GitHub</h3><div style="color:#c9c9d6;font-size:15px">Оновлення працює на GitHub, і щоб запускати його звідси, застосунку потрібен ключ GitHub (один раз):<br><br>1. github.com → фото профілю → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.<br>2. Repository access: Only select → ${esc(LC.repo)}.<br>3. Permissions → Actions: Read and write.<br>4. Скопіюй ключ і встав у ⚙ → «Ключ GitHub».</div><button class="btn" data-x="1" data-set="1">Відкрити налаштування</button>`);return}
  const r=await ghRun();toast(r===true?'🚀 Оновлення запущено, за 3–5 хв прийде в Telegram':'⚠ '+r);if(r===true)okHap();return}
 if(d.ghsave){const v=$('#ghk').value.trim();if(!v)return;await CS.set('gh_token',v);L$.gh=v;toast('✓ Ключ GitHub збережено');re(setView0());return}
 if(d.ghdel){await CS.del('gh_token');L$.gh='';re(setView0());return}
 // налаштування
 if(d.set){go(setView0());return}
 if(d.key){go(keyView());return}
 if(d.savekey){const v=$('#mk').value.trim();if(!v)return;await CS.set('meta_token',v);toast('Перевіряю…');stack=[];await liveLoad();toast(tok()?'✓ Кабінет підключено':'Ключ не підійшов');return}
 if(d.delkey){confirmDo('Відключити кабінет у цьому застосунку?',async()=>{await CS.del('meta_token');L$.token='';L$.acc=null;stack=[];render()});return}
 if(d.aisave){const v=$('#aik').value.trim();if(!v)return;await CS.set('ai_key',v);L$.ai=v;toast(aiProv()?'✓ Ключ ШІ збережено':'Ключ не схожий на Anthropic чи Gemini');re(setView0());return}
 if(d.aidel){await CS.del('ai_key');L$.ai='';re(setView0());return}
 if(d.lsave){L$.links={...L$.links,csv:$('#lcsv').value.trim(),tg:$('#ltg').value.trim(),site:$('#lsite').value.trim(),privacy:$('#lpriv').value.trim()};await CS.set('links',JSON.stringify(L$.links));toast('✓ Збережено');await loadSheet();re(setView0());return}
 if(d.how){go(howView);return}
 if(d.back){back();return}
 if(d.tab2){tab=d.tab2;stack=[];hap('soft');render();if(tab==='rep')loadRep();return}
 if(d.open){try{tg.openLink(d.open)}catch(x){window.open(d.open)}return}
 if(d.q){const g=G[d.q];sheet(`<h3>${g[0]} <span class="pro">${g[1]}</span></h3><div style="color:#c9c9d6;font-size:15px">${g[2]}</div><button class="btn ghost" data-x="1">Зрозуміло</button>`);return}}
const keepNc=()=>{if(!nc)return;if($('#nbudin'))nc.budget=Math.round(+$('#nbudin').value.replace(/\D/g,''))||nc.budget;if($('#nlink'))nc.link=$('#nlink').value.trim();if($('#nname'))nc.name=$('#nname').value.trim()};
document.addEventListener('click',async e=>{const t=e.target.closest('[data-camp],[data-newcamp],[data-ngoal],[data-nbud],[data-nform],[data-naud],[data-ncreate],[data-cpause],[data-cresume],[data-rt],[data-set2],[data-bstep],[data-bset],[data-bsave],[data-tsave],[data-spause],[data-sresume],[data-aall],[data-arm],[data-apick],[data-arad],[data-aadv],[data-aage],[data-agen],[data-pauto],[data-pl],[data-add],[data-useidea],[data-crmode],[data-cup],[data-cdown],[data-cdel],[data-compset],[data-aitext],[data-save],[data-review],[data-launch],[data-lcamp],[data-lgo],[data-edit],[data-aifix],[data-esave],[data-vpause],[data-pausecr],[data-resumecr],[data-delcr],[data-cr],[data-adlive],[data-pause],[data-resume],[data-rec],[data-recno],[data-mark],[data-mt],[data-mad],[data-msave],[data-rp],[data-rgo],[data-rq],[data-rc],[data-rb],[data-aiideas],[data-delidea],[data-iseg],[data-idea],[data-comp],[data-cgrp],[data-bt],[data-copy],[data-set],[data-cadd],[data-ghrun],[data-csave],[data-ghsave],[data-ghdel],[data-norms],[data-nsave],[data-nai],[data-askv],[data-askq],[data-ask],[data-key],[data-savekey],[data-delkey],[data-aisave],[data-aidel],[data-lsave],[data-how],[data-back],[data-tab2],[data-open],[data-q]');
 if(!t)return;if(t.dataset.q)e.stopPropagation();try{await act({...t.dataset})}catch(x){err(x)}});
render();liveLoad();
/* Telegram кешує сторінку: якщо на GitHub уже новіша збірка — перезавантажуємось */
fetch(location.pathname+'?t='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(t=>{const m=t.match(/"build": "([^"]+)"/);if(m&&m[1]!==D.build&&!location.search.includes('v='+m[1]))location.replace(location.pathname+'?v='+m[1]+location.hash)}).catch(()=>{});
}</script></body></html>"""


def build(cfg, now, stats, winners, analyses, concepts):
    """Статичні дані для застосунку: конкуренти й ідеї (оновлює щотижневий пайплайн) + налаштування кабінету."""
    launch, meta, kpi = cfg.get("launch") or {}, cfg.get("meta") or {}, cfg["kpi"]
    data = {
        "client": cfg["name"], "updated": f"{now:%d.%m.%Y}", "build": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "niche": cfg.get("niche", ""), "product": cfg.get("product", ""),
        "cur": cfg.get("currency_symbol", "₴"),
        "kpi": {"target_cpl": kpi.get("target_cpl", 60), "target_lead": kpi.get("target_lead", 150), "target_click": kpi.get("target_click", 8)},
        "winners": [{**{k: w.get(k) for k in ("ad_id", "page_id", "page_name", "days", "variants", "reuse", "text", "title", "snapshot_url")},
                     "a": analyses.get(w["ad_id"], {})}
                    for w in sorted(winners, key=lambda w: (w.get("text_source") != "body", -w["days"]))],
        "concepts": concepts or [],
        "live": ({"acc": meta["ad_account_id"], "page": launch.get("page_id"), "ig": launch.get("instagram_user_id"),
                  "ig_name": launch.get("instagram_username", ""), "repo": (cfg.get("github") or {}).get("repo", ""), "budget": launch.get("daily_budget", 135),
                  "countries": launch.get("countries", ["UA"]), "link": launch.get("link", "https://www.instagram.com/"),
                  "tg_link": launch.get("tg_link", ""), "site_link": launch.get("site_link", ""), "privacy": launch.get("privacy_url", ""),
                  "v": meta.get("api_version", "v24.0"), "ai_model": launch.get("ai_model", "claude-sonnet-5-5"),
                  "gemini_model": launch.get("gemini_model", "gemini-flash-latest"), "known": cfg.get("known_pages", {})}
                 if meta.get("ad_account_id") else None),
    }
    return APP.replace("__DATA__", json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/"))
