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
