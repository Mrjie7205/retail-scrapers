"""retail-scrape命令行入口。"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .errors import ScraperError
from .input import read_targets
from .output import write_records
from .registry import list_channels
from .runner import scrape_catalog, scrape_prices


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="retail-scrape",
        description="从已支持的零售渠道提取商品目录和价格。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("channels", help="列出支持的渠道")

    catalog = sub.add_parser("catalog", help="抓取渠道商品目录")
    catalog.add_argument("--channel", required=True)
    catalog.add_argument("--brand", action="append", default=[])
    catalog.add_argument("--year", action="append", type=int, default=[])
    catalog.add_argument("--max-pages", type=int)
    catalog.add_argument("--max-items", type=int)
    catalog.add_argument("--postal-code")
    catalog.add_argument("--output", "-o")
    catalog.add_argument("--format", choices=("jsonl", "csv"), default="jsonl")
    catalog.add_argument("--no-strict", action="store_true")
    catalog.add_argument("--headed", action="store_true")

    prices = sub.add_parser("prices", help="按用户输入的URL清单抓价格")
    prices.add_argument("--channel", required=True)
    prices.add_argument("--input", "-i", required=True)
    prices.add_argument("--output", "-o")
    prices.add_argument("--format", choices=("jsonl", "csv"), default="jsonl")
    prices.add_argument("--concurrency", type=int, default=3)
    prices.add_argument("--min-success-rate", type=float, default=0.8)
    prices.add_argument("--postal-code")
    prices.add_argument("--no-strict", action="store_true")
    prices.add_argument("--headed", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    # Windows 中文环境常用 GBK；统一 UTF-8，避免渠道名和商品标题输出失败。
    for stream in (sys.stdout, sys.stderr):
        try:
            reconfigure = getattr(stream, "reconfigure", None)
            if callable(reconfigure):
                reconfigure(encoding="utf-8")
        except OSError:
            pass
    args = _parser().parse_args(argv)
    try:
        if args.command == "channels":
            print(json.dumps(list_channels(), ensure_ascii=False, indent=2))
            return 0

        if args.command == "catalog":
            records: list[Any] = scrape_catalog(
                args.channel,
                brands=args.brand,
                years=args.year,
                max_pages=args.max_pages,
                max_items=args.max_items,
                strict=not args.no_strict,
                headless=not args.headed,
                postal_code=args.postal_code,
            )
        else:
            records = scrape_prices(
                args.channel,
                read_targets(args.input),
                concurrency=args.concurrency,
                min_success_rate=args.min_success_rate,
                strict=not args.no_strict,
                headless=not args.headed,
                postal_code=args.postal_code,
            )
        write_records(records, output=args.output, output_format=args.format)
        return 0
    except (ScraperError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
