# cisco-config-backup

I got tired of not knowing if someone changed a switch config over the weekend.

This script SSHs into your Cisco devices, pulls the running config, saves a timestamped copy locally, and diffs it against the last backup so you can see exactly what changed. Optionally uploads to S3 if you want offsite copies.

## What you need

- Python 3.8+
- Network access to your devices (SSH port 22 open)
- Credentials with enough privilege to run `show running-config`
- AWS credentials configured if you're using the S3 option (`aws configure` or IAM role)

```bash
pip install -r requirements.txt
```

## Setup

Edit `devices.yaml` with your device list:

```yaml
devices:
  - name: core-sw-01
    host: 192.168.1.1
    device_type: cisco_ios
    username: admin
    password: admin
```

`device_type` uses Netmiko's naming — `cisco_ios` covers most IOS devices. Use `cisco_nxos` for Nexus.

## How to run it

Basic backup, saves to `backups/` folder:
```bash
python backup.py
```

Custom device list:
```bash
python backup.py --config /path/to/devices.yaml
```

With S3 upload:
```bash
python backup.py --s3-bucket your-bucket-name
```

Backups land in `backups/` as `devicename_YYYYMMDD_HHMMSS.txt`. The diff prints to stdout so you can see at a glance if anything changed.

## Notes

- Tested on IOS 15.x and 16.x. Older versions sometimes have SSH negotiation issues — Netmiko handles most of them but not all.
- Passwords in `devices.yaml` are plaintext — don't commit that file with real creds. Add it to `.gitignore` or use environment variables if you're putting this anywhere shared.
- The diff caps at 60 lines of output per device so it doesn't flood the terminal on large config changes.
- TODO: add email/Slack alert when a diff is detected
