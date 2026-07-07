"""retail-scrape命令行入口。"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from .doctor import run_doctor
from .errors import ScraperError
from .health import list_channel_health
from .input import read_targets
from .output import write_records
from .registry import list_channels
from .runner import scrape_catalog, scrape_prices
from .scaffold import create_adapter_scaffold, scaffold_instructions
from .schema import all_schemas, record_schema, schema_markdown


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="retail-scrape",
        description="从已支持的零售渠道提取商品目录和价格。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("channels", help="列出支持的渠道")

    health = sub.add_parser("health", help="显示内置渠道的能力和维护状态")
    health.add_argument("--format", choices=("json", "markdown"), default="json")

    schema = sub.add_parser("schema", help="显示公共输出数据契约")
    schema.add_argument(
        "record", nargs="?", choices=("all", "catalog", "price", "target"), default="all"
    )
    schema.add_argument("--format", choices=("json", "markdown"), default="json")

    doctor = sub.add_parser("doctor", help="检查本地运行环境")
    doctor.add_argument("--skip-browser", action="store_true")

    scaffold = sub.add_parser("scaffold", help="生成新渠道adapter骨架")
    scaffold.add_argument("channel_id")
    scaffold.add_argument("--display-name")
    scaffold.add_argument("--country", default="XX")
    scaffold.add_argument("--with-fixtures", action="store_true")

    catalog = sub.add_parser("catalog", help="抓取渠道商品目录")
    catalog.add_argument("--channel", required=True)
    catalog.add_argument("--brand", action="append", default=[])
    catalog.add_argument("--year", action="append", type=int, default=[])
    catalog.add_argument("--max-pages", type=int)
    catalog.add_argument("--max-items", type=int)
    catalog.add_argument("--postal-code")
    catalog.add_argument("--timeout-ms", type=int, default=60_000)
    catalog.add_argument("--retries", type=int, default=2)
    catalog.add_argument("--delay-seconds", type=float, default=1.0)
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
    prices.add_argument("--timeout-ms", type=int, default=60_000)
    prices.add_argument("--retries", type=int, default=2)
    prices.add_argument("--delay-seconds", type=float, default=1.0)
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

        if args.command == "health":
            if args.format == "markdown":
                from .health import channel_health_markdown

                print(channel_health_markdown())
            else:
                print(json.dumps(list_channel_health(), ensure_ascii=False, indent=2))
            return 0

        if args.command == "schema":
            if args.format == "markdown":
                print(schema_markdown(args.record))
            elif args.record == "all":
                print(json.dumps(all_schemas(), ensure_ascii=False, indent=2))
            else:
                print(json.dumps(record_schema(args.record), ensure_ascii=False, indent=2))
            return 0

        if args.command == "doctor":
            report = asyncio.run(run_doctor(check_browser=not args.skip_browser))
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1 if report["status"] == "error" else 0

        if args.command == "scaffold":
            paths = create_adapter_scaffold(
                args.channel_id,
                display_name=args.display_name,
                country=args.country,
                with_fixtures=args.with_fixtures,
            )
            cwd = Path.cwd()
            created = [_display_path(path, cwd) for path in paths]
            print(
                json.dumps(
                    {
                        "created": created,
                        "instructions": scaffold_instructions(args.channel_id),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
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
                timeout_ms=args.timeout_ms,
                retries=args.retries,
                delay_seconds=args.delay_seconds,
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
                timeout_ms=args.timeout_ms,
                retries=args.retries,
                delay_seconds=args.delay_seconds,
            )
        write_records(records, output=args.output, output_format=args.format)
        return 0
    except (ScraperError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
