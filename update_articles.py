import os

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.ingestion import run_weekly_ingestion  # noqa: E402


def main() -> None:
    result = run_weekly_ingestion(max_items_per_source=20)
    print('Ingestion summary:')
    print(f"  ABC items fetched: {result['abc_count']}")
    print(f"  CERT items fetched: {result['cert_count']}")
    print(f"  Articles processed: {result['total']}")
    print(f"  Created: {result['created']}")
    print(f"  Skipped duplicates: {result['skipped']}")


if __name__ == '__main__':
    main()
