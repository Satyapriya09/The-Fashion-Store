# The Fashion Store

A Django storefront for clothing and footwear, with catalog search, a browser-based shopping bag, checkout, and order tracking.

## Run locally

Use Python 3.12 or newer. From PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_DEBUG = "true"
$env:DJANGO_SECRET_KEY = "local-development-only"
python manage.py migrate
python manage.py runserver
```

Run the storefront tests with `python manage.py test Shop`.

For deployment, set a private `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, and provide comma-separated hostnames through `DJANGO_ALLOWED_HOSTS`. Configure persistent media storage and a production database before accepting real orders. Checkout records an order; it does not process a payment.