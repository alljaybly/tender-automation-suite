# Deployment Guide

This guide shows how to deploy the project on an Ubuntu server or VPS.

It uses:

- Ubuntu
- Python virtual environment
- Uvicorn
- systemd
- optional Nginx reverse proxy

## Deployment Model

Recommended simple production layout:

1. keep the app code in a dedicated directory
2. create a Python virtual environment
3. install OCR dependencies
4. run the app with Uvicorn behind `systemd`
5. optionally expose it through Nginx

## Server Requirements

- Ubuntu 22.04 or newer recommended
- Python 3.11+
- `python3-venv`
- `tesseract-ocr`
- `poppler-utils`
- network access for pip installs

## 1. Create An App Directory

Example:

```bash
sudo mkdir -p /opt/tender_system
sudo chown "$USER":"$USER" /opt/tender_system
cd /opt/tender_system
```

Copy the project files into that directory.

## 2. Install System Packages

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip tesseract-ocr tesseract-ocr-eng poppler-utils nginx
```

If you do not want Nginx yet, remove it from the command.

## 3. Create And Populate The Virtual Environment

From the project directory:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Or use the project script:

```bash
bash setup.sh
```

## 4. Configure Environment Variables

At minimum, decide whether you want Groq cloud pricing.

Example:

```bash
export GROQ_API_KEY="gsk_your_key_here"
```

For persistent production use, store environment values in a protected file such as:

```bash
sudo mkdir -p /etc/tender-system
sudo nano /etc/tender-system/tender-system.env
```

Example contents:

```bash
GROQ_API_KEY=gsk_your_key_here
```

The app auto-loads a local `.env` file when it starts. For production, a systemd `EnvironmentFile` is still the better option because it keeps deployment configuration outside the code directory.

## 5. Test The App Manually

```bash
source venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Visit:

- `http://server-ip:8000`

Stop the process after confirming it starts correctly.

## 6. Create A systemd Service

Create:

```bash
sudo nano /etc/systemd/system/tender-system.service
```

Use this service file:

```ini
[Unit]
Description=Tender System FastAPI Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/tender_system
EnvironmentFile=-/etc/tender-system/tender-system.env
ExecStart=/opt/tender_system/venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Important:

- adjust `WorkingDirectory` if your app lives elsewhere
- ensure `www-data` can read the project directory and write to `workspace/`

Grant permissions if needed:

```bash
sudo chown -R www-data:www-data /opt/tender_system
```

Then enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tender-system
sudo systemctl start tender-system
sudo systemctl status tender-system
```

## 7. Configure Nginx

Create:

```bash
sudo nano /etc/nginx/sites-available/tender-system
```

Use:

```nginx
server {
    listen 80;
    server_name your-domain-or-server-ip;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/tender-system /etc/nginx/sites-enabled/tender-system
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Optional HTTPS With Let's Encrypt

If you have a real domain name:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.example.com
```

## 9. Verify The Deployment

Check:

```bash
curl http://127.0.0.1:8000/api/models
curl http://127.0.0.1/api/models
sudo systemctl status tender-system
sudo journalctl -u tender-system -n 100 --no-pager
```

## File And Folder Considerations

The app writes data to:

- `workspace/uploads`
- `workspace/outputs`
- `workspace/history`
- `workspace/merged`

Make sure the service user can write to those directories.

The app also expects:

- `templates/`
- `static/`

Those are created automatically if missing, but they still need to be present in the deployed project tree.

## Production Notes

- the current app runs with permissive CORS in `app.py`
- output files and uploads are stored on local disk
- there is no authentication layer yet
- generated files may contain sensitive tender content
- web-searched rate data should be manually validated

If you deploy this publicly, consider adding:

- authentication
- upload size limits
- log rotation
- backup for `workspace/`
- a stronger process manager strategy

## Updating The App

From the deployment directory:

```bash
cd /opt/tender_system
source venv/bin/activate
python -m pip install -r requirements.txt
sudo systemctl restart tender-system
```

If code changed significantly, also verify:

```bash
sudo systemctl status tender-system
sudo journalctl -u tender-system -n 100 --no-pager
```

## Rollback Strategy

Simple approach:

1. keep a backup copy of the previous release directory
2. restore the previous code
3. restart the service

Example:

```bash
sudo systemctl stop tender-system
cp -r /opt/tender_system_previous /opt/tender_system
sudo systemctl start tender-system
```

## Troubleshooting

### Service Will Not Start

Check:

```bash
sudo systemctl status tender-system
sudo journalctl -u tender-system -n 200 --no-pager
```

### OCR Fails On The Server

Check that these exist:

```bash
which tesseract
which pdftoppm
```

If not:

```bash
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
```

### Permission Errors In `workspace/`

Fix ownership:

```bash
sudo chown -R www-data:www-data /opt/tender_system
```

### WebSocket Issues Behind Nginx

Confirm the `/ws/` location block includes:

- `proxy_set_header Upgrade $http_upgrade;`
- `proxy_set_header Connection "upgrade";`

## Related Files

- [README.md](file:///c:/Users/allan/OneDrive/Documents/tender_system/README.md)
- [README_QUICKSTART.md](file:///c:/Users/allan/OneDrive/Documents/tender_system/README_QUICKSTART.md)
- [.env.example](file:///c:/Users/allan/OneDrive/Documents/tender_system/.env.example)
