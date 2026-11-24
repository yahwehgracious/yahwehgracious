"""
python -m targetolog update <client> [--brief] [--skip-collect] [--out path/index.html] [--notify]   # щотижня: конкуренти + ідеї → застосунок
python -m targetolog daily <client> [--no-send]                                                       # щоранку: звіт і рішення в Telegram
"""
import argparse
from datetime import datetime, timezone

from . import daily
from .pipeline import load_client, run
from .util import load_env


def main():
    load_env()
    ap = argparse.ArgumentParser(prog="targetolog")
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("update")
    u.add_argument("client")
    u.add_argument("--brief", action="store_true", help="згенерувати ідеї зараз, незалежно від розкладу")
    u.add_argument("--skip-collect", action="store_true", help="не скрапити бібліотеку реклами")
    u.add_argument("--now", help="ISO-дата (для тестів)")
    u.add_argument("--out", help="куди ще записати index.html застосунку")
    u.add_argument("--notify", action="store_true", help="написати в Telegram, що ідеї оновлено")
    d = sub.add_parser("daily")
    d.add_argument("client")
    d.add_argument("--no-send", action="store_true")
    args = ap.parse_args()

    if args.cmd == "update":
        now = datetime.fromisoformat(args.now).replace(tzinfo=timezone.utc) if args.now else None
        run(args.client, now=now, force_brief=args.brief, skip_collect=args.skip_collect, out=args.out, notify=args.notify)
    else:
        cfg, _ = load_client(args.client)
        daily.run(cfg, send=not args.no_send)


if __name__ == "__main__":
    main()
