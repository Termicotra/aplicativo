# Weekly article ingestion

## Linux cron example
Run every Monday at 03:00:

```cron
0 3 * * 1 cd /path/to/aplicativo && /path/to/aplicativo/.venv/bin/python update_articles.py >> /path/to/aplicativo/logs/update_articles.log 2>&1
```

## Windows Task Scheduler example
Program/script:

```text
C:\Users\feder\OneDrive\Escritorio\Trabajos\Tesis\aplicativo\.venv\Scripts\python.exe
```

Arguments:

```text
update_articles.py
```

Start in:

```text
C:\Users\feder\OneDrive\Escritorio\Trabajos\Tesis\aplicativo
```

Schedule: Weekly, Monday, 03:00 AM.
