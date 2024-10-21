# cyber_project_portal
Codebase for cyber project portal - Designed to assign slots to the library members

## Some commands

### Activate conda env

```
conda activate django
```

### Run server
```
python manage.py runserver --insecure
```

### For shell access
```
./manage.py shell_plus 
```

#### Shell commands

```
Slot.objects.filter(
            library=library,
            datetime=start_time
        ).delete()
```

```
Slot.objects.get_or_create(
            library=library,
            datetime=start_time
        )
```

## Production Setup

Directory: `/srv/cyber_portal` (contains the source, env, db, logs)

DB: `/srv/cyber_portal/db.sqlite3` (set via `/srv/cyber_portal/.env`)

Service: `/etc/systemd/system/cyber_portal.service`

Apache site: `/etc/apache2/sites-available/cyber_portal.conf`

Certs: `/etc/letsencrypt/live/portal.thecommunitylibraryproject.org/`

Permissions: Add user to group `cyber_portal`, and grant ownership to this group as well.
