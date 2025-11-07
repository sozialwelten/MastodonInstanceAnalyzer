#!/usr/bin/env python3
"""
Mastodon Instance Analyzer
Analysiert eine Mastodon-Instanz und erstellt detaillierte Statistiken
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import requests
from typing import Dict, List, Any


class MastodonAnalyzer:
    def __init__(self, instance_url: str, access_token: str = None):
        self.instance_url = instance_url.rstrip('/')
        self.access_token = access_token
        self.headers = {}
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'

    def _get(self, endpoint: str, params: Dict = None) -> Any:
        """API Request durchführen"""
        url = f"{self.instance_url}/api/v1/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Fehler bei API-Request: {e}", file=sys.stderr)
            return None

    def get_instance_info(self) -> Dict:
        """Basis-Informationen über die Instanz"""
        return self._get('instance')

    def get_instance_activity(self) -> List[Dict]:
        """Aktivitäts-Statistiken"""
        return self._get('instance/activity')

    def analyze_accounts(self) -> Dict:
        """Analysiert alle Accounts (benötigt Admin-Token)"""
        accounts = []
        page = 1

        # Versuche Admin-Endpoint für alle Accounts
        while True:
            data = self._get('admin/accounts', params={'page': page, 'limit': 100})
            if not data or len(data) == 0:
                break
            accounts.extend(data)
            page += 1
            if len(data) < 100:
                break

        if not accounts:
            print("Hinweis: Keine Account-Daten verfügbar. Admin-Token benötigt.", file=sys.stderr)
            return {}

        return self._analyze_account_data(accounts)

    def _analyze_account_data(self, accounts: List[Dict]) -> Dict:
        """Analysiert Account-Daten"""
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)

        stats = {
            'total': len(accounts),
            'local': 0,
            'remote': 0,
            'active_30d': 0,
            'active_90d': 0,
            'inactive': 0,
            'with_posts': 0,
            'without_posts': 0,
            'by_post_count': defaultdict(int),
            'top_posters': [],  # Neue Statistik
        }

        account_list = []

        for account in accounts:
            # Lokal vs. Remote
            if account.get('domain') is None:
                stats['local'] += 1
            else:
                stats['remote'] += 1

            # Letzte Aktivität - prüfe account-Objekt falls vorhanden
            acc_data = account.get('account', account)
            last_status_at = acc_data.get('last_status_at')

            if last_status_at:
                try:
                    last_status_at = last_status_at.replace('Z', '+00:00')
                    last_active = datetime.fromisoformat(last_status_at)
                    if last_active.tzinfo:
                        last_active = last_active.replace(tzinfo=None)

                    if last_active > thirty_days_ago:
                        stats['active_30d'] += 1
                    if last_active > ninety_days_ago:
                        stats['active_90d'] += 1
                    else:
                        stats['inactive'] += 1
                except (ValueError, AttributeError):
                    stats['inactive'] += 1
            else:
                stats['inactive'] += 1

            # Post-Statistiken
            statuses_count = acc_data.get('statuses_count', 0)
            if statuses_count > 0:
                stats['with_posts'] += 1
            else:
                stats['without_posts'] += 1

            # Für Top-Poster Liste
            account_list.append({
                'username': account.get('username', 'unknown'),
                'posts': statuses_count,
                'last_active': last_status_at
            })

            # Kategorisierung nach Post-Anzahl
            if statuses_count == 0:
                stats['by_post_count']['0'] += 1
            elif statuses_count <= 10:
                stats['by_post_count']['1-10'] += 1
            elif statuses_count <= 50:
                stats['by_post_count']['11-50'] += 1
            elif statuses_count <= 100:
                stats['by_post_count']['51-100'] += 1
            elif statuses_count <= 500:
                stats['by_post_count']['101-500'] += 1
            else:
                stats['by_post_count']['500+'] += 1

        # Top 10 Poster
        stats['top_posters'] = sorted(account_list, key=lambda x: x['posts'], reverse=True)[:10]

        return stats

    def analyze_local_timeline(self, limit: int = 100) -> Dict:
        """Analysiert die lokale Timeline"""
        # Wenn kein Token vorhanden ist oder Timeline nicht zugänglich, überspringe
        statuses = self._get('timelines/public', params={'local': 'true', 'limit': limit})

        if not statuses:
            return None  # Signalisiere, dass Timeline nicht verfügbar ist

        now = datetime.now()
        stats = {
            'total_statuses': len(statuses),
            'unique_authors': len(set(s['account']['id'] for s in statuses)),
            'with_media': sum(1 for s in statuses if s.get('media_attachments')),
            'with_cw': sum(1 for s in statuses if s.get('spoiler_text')),
            'replies': sum(1 for s in statuses if s.get('in_reply_to_id')),
            'boosts': sum(1 for s in statuses if s.get('reblog')),
        }

        return stats

    def generate_report(self, output_format: str = 'text') -> str:
        """Generiert einen vollständigen Report"""
        print("Sammle Instanz-Informationen...")
        instance_info = self.get_instance_info()

        print("Analysiere Aktivitäten...")
        activity = self.get_instance_activity()

        print("Analysiere Accounts...")
        account_stats = self.analyze_accounts()

        print("Analysiere Timeline...")
        timeline_stats = self.analyze_local_timeline()

        if output_format == 'json':
            return json.dumps({
                'instance': instance_info,
                'activity': activity,
                'accounts': account_stats,
                'timeline': timeline_stats,
                'generated_at': datetime.now().isoformat()
            }, indent=2, ensure_ascii=False)

        # Text-Format
        report = []
        report.append("=" * 70)
        report.append(f"MASTODON INSTANZ ANALYSE: {self.instance_url}")
        report.append("=" * 70)
        report.append("")

        if instance_info:
            report.append("📊 INSTANZ-INFORMATIONEN")
            report.append("-" * 70)
            report.append(f"Name:        {instance_info.get('title', 'N/A')}")
            report.append(f"Version:     {instance_info.get('version', 'N/A')}")
            report.append(f"Beschreibung: {instance_info.get('short_description', 'N/A')[:60]}...")

            stats = instance_info.get('stats', {})
            report.append(f"Nutzer:      {stats.get('user_count', 'N/A'):,}")
            report.append(f"Posts:       {stats.get('status_count', 'N/A'):,}")
            report.append(f"Domains:     {stats.get('domain_count', 'N/A'):,}")
            report.append("")

        if activity:
            report.append("📈 AKTIVITÄT (12 WOCHEN)")
            report.append("-" * 70)
            for week in activity[:3]:  # Zeige letzte 3 Wochen
                week_timestamp = week.get('week')
                try:
                    # Konvertiere Unix-Timestamp zu lesbarem Datum
                    week_date = datetime.fromtimestamp(int(week_timestamp))
                    week_str = week_date.strftime('%Y-KW%W (%d.%m.)')
                except (ValueError, TypeError):
                    week_str = str(week_timestamp)

                report.append(f"{week_str}: "
                              f"{week.get('logins', 'N/A')} Logins, "
                              f"{week.get('statuses', 'N/A')} Posts, "
                              f"{week.get('registrations', 'N/A')} Registrierungen")
            report.append("")

        if account_stats:
            report.append("👥 ACCOUNT-STATISTIKEN")
            report.append("-" * 70)
            report.append(f"Gesamt:           {account_stats['total']:,}")
            report.append(f"Lokal:            {account_stats['local']:,}")
            report.append(f"Remote:           {account_stats['remote']:,}")
            report.append(f"Aktiv (30 Tage): {account_stats['active_30d']:,}")
            report.append(f"Aktiv (90 Tage): {account_stats['active_90d']:,}")
            report.append(f"Inaktiv:          {account_stats['inactive']:,}")
            report.append(f"Mit Posts:        {account_stats['with_posts']:,}")
            report.append(f"Ohne Posts:       {account_stats['without_posts']:,}")
            report.append("")

            report.append("📝 POSTS PRO ACCOUNT")
            report.append("-" * 70)
            for category in ['0', '1-10', '11-50', '51-100', '101-500', '500+']:
                count = account_stats['by_post_count'].get(category, 0)
                report.append(f"{category:>10} Posts: {count:,} Accounts")
            report.append("")

            # Top Poster
            if account_stats.get('top_posters'):
                report.append("🏆 TOP 10 POSTER")
                report.append("-" * 70)
                for i, poster in enumerate(account_stats['top_posters'], 1):
                    last_active = poster.get('last_active', 'nie')
                    if last_active and last_active != 'nie':
                        try:
                            last_active = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
                            last_active = last_active.strftime('%Y-%m-%d')
                        except:
                            pass
                    report.append(
                        f"{i:>2}. @{poster['username']:<20} {poster['posts']:>6,} Posts (zuletzt: {last_active})")
                report.append("")

        if timeline_stats:
            report.append("🌐 LOKALE TIMELINE (letzte 100 Posts)")
            report.append("-" * 70)
            report.append(f"Posts gesamt:     {timeline_stats['total_statuses']:,}")
            report.append(f"Unique Autoren:   {timeline_stats['unique_authors']:,}")
            report.append(f"Mit Medien:       {timeline_stats['with_media']:,}")
            report.append(f"Mit CW:           {timeline_stats['with_cw']:,}")
            report.append(f"Antworten:        {timeline_stats['replies']:,}")
            report.append(f"Boosts:           {timeline_stats['boosts']:,}")
            report.append("")
        else:
            report.append("🌐 LOKALE TIMELINE")
            report.append("-" * 70)
            report.append("⚠️  Timeline nicht verfügbar (Auth-Token erforderlich)")
            report.append("")

        report.append("=" * 70)
        report.append(f"Report generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description='Analysiert eine Mastodon-Instanz',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s https://ifwo.eu
  %(prog)s https://ifwo.eu --token YOUR_TOKEN
  %(prog)s https://ifwo.eu --token YOUR_TOKEN --format json > report.json
  %(prog)s https://ifwo.eu --token YOUR_TOKEN --output report.txt

Hinweis: Für vollständige Account-Statistiken wird ein Admin-Token benötigt.
        """
    )

    parser.add_argument('instance', help='URL der Mastodon-Instanz (z.B. https://ifwo.eu)')
    parser.add_argument('--token', '-t', help='Access Token (optional, aber empfohlen für Admin-Features)')
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                        help='Output-Format (default: text)')
    parser.add_argument('--output', '-o', help='Ausgabe-Datei (optional)')

    args = parser.parse_args()

    analyzer = MastodonAnalyzer(args.instance, args.token)
    report = analyzer.generate_report(args.format)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report gespeichert: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()