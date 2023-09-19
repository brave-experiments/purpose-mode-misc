# Purpose Mode backend

This service accepts and stores incoming POST requests targeting the `/submit`
path.  To compile the service, run:

    make

## Helper Scripts
### show participant status

    cd scripts
    python user_overview.py active

### export interview data

    cd scripts
    python export_esm.py {pid} {#week}