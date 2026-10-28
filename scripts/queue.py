#!/usr/bin/env python3
"""Local, offline CSV review queue. Never accesses LinkedIn or sends messages."""
import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

CANDIDATE_FIELDS = (
    "company", "domain", "name", "title", "linkedin_url", "source_url",
    "fit_score", "fit_reason", "personalization_hook",
)
LEDGER_FIELDS = ("linkedin_url", "status", "last_action_at", "notes")
EXCLUSION_FIELDS = ("type", "value", "reason")
STATUSES = (
    "connection_sent", "message_sent", "replied_positive", "replied_negative",
    "meeting_booked", "do_not_contact", "skipped",
)


def read_rows(path, fields):
    if not path.is_file():
        raise ValueError(f"Arquivo ausente: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(fields) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Colunas ausentes em {path.name}: {', '.join(sorted(missing))}")
        return list(reader)


def profile_url(raw):
    try:
        parsed = urlparse(raw.strip())
        parts = parsed.path.strip("/").split("/")
        if parsed.scheme != "https" or parsed.hostname not in {"linkedin.com", "www.linkedin.com"}:
            return ""
        if len(parts) != 2 or parts[0].lower() != "in" or not parts[1]:
            return ""
        return "https://www.linkedin.com/in/" + parts[1].lower() + "/"
    except (ValueError, AttributeError):
        return ""


def domain(raw):
    text = raw.strip().lower()
    host = urlparse(text if "://" in text else "https://" + text).hostname or ""
    return host.removeprefix("www.")


def prepare(workdir):
    candidates = read_rows(workdir / "candidates.csv", CANDIDATE_FIELDS)
    ledger = read_rows(workdir / "ledger.csv", LEDGER_FIELDS)
    exclusions = read_rows(workdir / "exclusions.csv", EXCLUSION_FIELDS)
    blocked_urls = {profile_url(row["linkedin_url"]) for row in ledger}
    blocked_domains = set()
    for row in candidates:
        if profile_url(row["linkedin_url"]) in blocked_urls and domain(row["domain"]):
            blocked_domains.add(domain(row["domain"]))
    for row in exclusions:
        kind, value = row["type"].strip().lower(), row["value"]
        if kind == "linkedin_url":
            blocked_urls.add(profile_url(value))
        elif kind == "domain":
            blocked_domains.add(domain(value))
        else:
            raise ValueError(f"Tipo de exclusão inválido: {kind}")
    seen_urls, seen_domains, queue = set(), set(), []
    counts = {"already_contacted_or_excluded": 0, "duplicate": 0, "needs_verification": 0, "low_score": 0}
    for row in candidates:
        url, company_domain = profile_url(row["linkedin_url"]), domain(row["domain"])
        try:
            score = int(row["fit_score"])
        except (ValueError, TypeError):
            score = 0
        if url and (url in blocked_urls or company_domain in blocked_domains):
            counts["already_contacted_or_excluded"] += 1
        elif url and (url in seen_urls or (company_domain and company_domain in seen_domains)):
            counts["duplicate"] += 1
        elif (not url or not company_domain or
              urlparse(row["source_url"].strip()).scheme not in {"http", "https"} or
              not urlparse(row["source_url"].strip()).hostname or
              not row["name"].strip() or not row["title"].strip()):
            counts["needs_verification"] += 1
        elif score < 3 or score > 5 or not row["fit_reason"].strip():
            counts["low_score"] += 1
        else:
            row["linkedin_url"] = url
            row["domain"] = company_domain
            queue.append({field: row[field] for field in CANDIDATE_FIELDS})
            seen_urls.add(url)
            seen_domains.add(company_domain)
    output = workdir / "review_queue.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_FIELDS)
        writer.writeheader()
        writer.writerows(queue)
    print(f"Candidatos: {len(candidates)} | revisão: {len(queue)} | " + " | ".join(f"{k}: {v}" for k, v in counts.items()))
    print(f"Fila local: {output}")
    return queue, counts


def record(workdir, url, status, notes):
    ledger_path = workdir / "ledger.csv"
    rows = read_rows(ledger_path, LEDGER_FIELDS)
    normalized = profile_url(url)
    if not normalized:
        raise ValueError("Use uma URL pública https://www.linkedin.com/in/<identificador>/")
    if any(profile_url(r["linkedin_url"]) == normalized and r["status"] == status for r in rows):
        print("Registro idêntico já existe; nenhuma alteração.")
        return False
    row: dict[str, str] = {
        "linkedin_url": normalized, "status": status,
        "last_action_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "notes": notes,
    }
    with ledger_path.open("a", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerow([row[field] for field in LEDGER_FIELDS])
    print(f"Registrado: {normalized} → {status}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_cmd = sub.add_parser("prepare", help="Gerar fila local de revisão, sem acessar a rede")
    record_cmd = sub.add_parser("record", help="Registrar resultado confirmado manualmente")
    for command in (prepare_cmd, record_cmd):
        command.add_argument("--workdir", type=Path, required=True)
    record_cmd.add_argument("--url", required=True)
    record_cmd.add_argument("--status", required=True, choices=STATUSES)
    record_cmd.add_argument("--notes", default="")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.workdir)
        else:
            record(args.workdir, args.url, args.status, args.notes)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
