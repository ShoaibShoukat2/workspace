# Cron Automation System - Complete Guide

## Overview
Automated scheduled tasks for compliance checks, reminders, email summaries, payout notifications, aur stale job management.

---

## 🤖 Key Features

- **Daily Compliance Expiry Check** - Auto-detect expiring/expired documents
- **Pending Jobs Reminder** - Daily reminders for unassigned/overdue jobs
- **Daily Summary Email** - Comprehensive daily metrics to FM/Admin
- **Payout Reminders** - Bi-weekly payout processing reminders
- **Auto Close Stale Jobs** - Automatically close inactive jobs
- **Email Notifications** - Automatic email alerts
- **In-App Notifications** - Real-time system notifications

---

## 📋 Management Commands

### 1. Compliance Expiry Check
**Command:** `python manage.py check_compliance_expiry`
**Schedule:** Daily at 6:00 AM
**Purpose:** Check for expiring and expired compliance documents

**What it does:**
- Finds documents expiring within 30 days
- Updates status to `EXPIRING_SOON`
- Finds expired documents
- Updates status to `EXPIRED`
- Sends notifications to contractors
- Sends email alerts

**Output:**
```
Starting compliance expiry check...
Compliance check complete: 3 expiring, 2 expired
```

**Manual Test:**
```bash
python manage.py check_compliance_expiry
```

---

### 2. Pending Jobs Reminder
**Command:** `python manage.py send_pending_jobs_reminder`
**Schedule:** Weekdays at 8:00 AM (Mon-Fri)
**Purpose:** Remind FM/Admin about pending jobs

**What it does:**
- Finds unassigned jobs
- Finds jobs approaching due date (within 7 days)
- Finds overdue jobs
- Sends summary to all FM and Admin users
- Creates in-app notifications
- Sends email reminders

**Email Content:**
```
📋 UNASSIGNED JOBS: 5
  • JOB-000123: Bathroom Renovation
  • JOB-000124: Kitchen Remodel
  ...

⏰ APPROACHING DUE DATE: 3
  • JOB-000125: Plumbing Repair (Due in 2 days)
  ...

🚨 OVERDUE JOBS: 2
  • JOB-000120: Painting (5 days overdue)
  ...
```

**Manual Test:**
```bash
python manage.py send_pending_jobs_reminder
```

---

### 3. Daily Summary Email
**Command:** `python manage.py send_daily_summary`
**Schedule:** Weekdays at 9:00 AM (Mon-Fri)
**Purpose:** Send comprehensive daily summary to FM/Admin

**What it does:**
- Calculates yesterday's activity metrics
- Shows current system status
- Highlights items requiring attention
- Sends to all FM and Admin users

**Email Content:**
```
Daily Summary Report - January 15, 2024
==================================================

📊 YESTERDAY'S ACTIVITY (January 14, 2024):
  • New Jobs Created: 5
  • Jobs Completed: 3
  • New Estimates: 4
  • Payouts Processed: 2 ($5,000.00)
  • Revenue Generated: $12,500.00

📈 CURRENT STATUS:
  • Total Jobs: 150
  • Pending Jobs: 20
  • Active Jobs: 35
  • Pending Estimates: 8
  • Pending Completions: 5

⚠️ REQUIRES ATTENTION:
  • 3 unassigned jobs
  • 2 overdue jobs
  • 5 job completions awaiting verification
```

**Manual Test:**
```bash
python manage.py send_daily_summary
```

---

### 4. Payout Reminders
**Command:** `python manage.py send_payout_reminders`
**Schedule:** Monday & Thursday at 10:00 AM
**Purpose:** Remind admins about pending payouts

**What it does:**
- Finds pending payout requests
- Finds jobs ready for payout
- Sends reminders to admins
- Notifies contractors with old pending requests (>7 days)

**Email to Admin:**
```
Payout Reminder:

📋 PENDING PAYOUT REQUESTS: 5

Top 5 Pending Requests:
  • PAY-REQ-001: contractor@example.com - $2,500.00
  • PAY-REQ-002: contractor2@example.com - $3,200.00
  ...

💰 READY FOR PAYOUT: 8

Top 5 Ready for Payout:
  • JOB-000123: contractor@example.com - $1,800.00
  • JOB-000124: contractor3@example.com - $2,100.00
  ...
```

**Manual Test:**
```bash
python manage.py send_payout_reminders
```

---

### 5. Auto Close Stale Jobs
**Command:** `python manage.py auto_close_stale_jobs`
**Schedule:** Sunday at 2:00 AM
**Purpose:** Automatically close inactive jobs

**Options:**
- `--days=90` - Number of days of inactivity (default: 90)
- `--dry-run` - Show what would be closed without closing

**What it does:**
- Finds jobs inactive for X days
- Changes status to `CANCELLED`
- Adds note about auto-closure
- Notifies assigned contractor
- Notifies job creator
- Sends email alerts

**Dry Run Test:**
```bash
python manage.py auto_close_stale_jobs --dry-run
```

**Output:**
```
Checking for stale jobs (inactive for 90+ days)...
Found 3 stale jobs
DRY RUN - No jobs will be closed
  • JOB-000100: Old Bathroom Job (95 days inactive)
  • JOB-000101: Abandoned Kitchen (120 days inactive)
  • JOB-000102: Stale Plumbing (100 days inactive)
```

**Actual Run:**
```bash
python manage.py auto_close_stale_jobs --days=90
```

**Output:**
```
Checking for stale jobs (inactive for 90+ days)...
Found 3 stale jobs
  ✓ Closed: JOB-000100 (95 days inactive)
  ✓ Closed: JOB-000101 (120 days inactive)
  ✓ Closed: JOB-000102 (100 days inactive)
Auto-closed 3 stale jobs
```

---

## ⚙️ Setup Instructions

### Linux/Mac Setup (Crontab)

1. **Open crontab editor:**
```bash
crontab -e
```

2. **Add cron entries:**
```bash
# Daily Compliance Check (6:00 AM)
0 6 * * * cd /path/to/project && /path/to/venv/bin/python manage.py check_compliance_expiry >> /var/log/cron_compliance.log 2>&1

# Pending Jobs Reminder (8:00 AM weekdays)
0 8 * * 1-5 cd /path/to/project && /path/to/venv/bin/python manage.py send_pending_jobs_reminder >> /var/log/cron_reminders.log 2>&1

# Daily Summary (9:00 AM weekdays)
0 9 * * 1-5 cd /path/to/project && /path/to/venv/bin/python manage.py send_daily_summary >> /var/log/cron_summary.log 2>&1

# Payout Reminders (10:00 AM Mon & Thu)
0 10 * * 1,4 cd /path/to/project && /path/to/venv/bin/python manage.py send_payout_reminders >> /var/log/cron_payouts.log 2>&1

# Auto Close Stale Jobs (2:00 AM Sunday)
0 2 * * 0 cd /path/to/project && /path/to/venv/bin/python manage.py auto_close_stale_jobs --days=90 >> /var/log/cron_stale_jobs.log 2>&1
```

3. **Save and exit**

4. **Verify crontab:**
```bash
crontab -l
```

---

### Windows Setup (Task Scheduler)

#### Method 1: GUI

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create New Task**
   - Click "Create Basic Task"
   - Name: "Daily Compliance Check"
   - Trigger: Daily at 6:00 AM
   - Action: Start a program
   - Program: `python.exe`
   - Arguments: `manage.py check_compliance_expiry`
   - Start in: `C:\path\to\project`

3. **Repeat for each command**

#### Method 2: Command Line

```powershell
# Daily Compliance Check
schtasks /create /tn "ComplianceCheck" /tr "python C:\path\to\project\manage.py check_compliance_expiry" /sc daily /st 06:00

# Pending Jobs Reminder (Weekdays)
schtasks /create /tn "PendingJobsReminder" /tr "python C:\path\to\project\manage.py send_pending_jobs_reminder" /sc weekly /d MON,TUE,WED,THU,FRI /st 08:00

# Daily Summary (Weekdays)
schtasks /create /tn "DailySummary" /tr "python C:\path\to\project\manage.py send_daily_summary" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:00

# Payout Reminders (Mon & Thu)
schtasks /create /tn "PayoutReminders" /tr "python C:\path\to\project\manage.py send_payout_reminders" /sc weekly /d MON,THU /st 10:00

# Auto Close Stale Jobs (Sunday)
schtasks /create /tn "AutoCloseStaleJobs" /tr "python C:\path\to\project\manage.py auto_close_stale_jobs --days=90" /sc weekly /d SUN /st 02:00
```

---

## 📧 Email Configuration

### Django Settings

Add to `settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@yourcompany.com'
```

### Gmail Setup

1. Enable 2-Factor Authentication
2. Generate App Password
3. Use App Password in settings

### Testing Email

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email.',
    'noreply@yourcompany.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

---

## 📊 Monitoring & Logs

### View Logs

**Linux/Mac:**
```bash
# View compliance log
tail -f /var/log/cron_compliance.log

# View all cron logs
tail -f /var/log/cron_*.log
```

**Windows:**
```powershell
# View Task Scheduler history
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | Select-Object -First 10
```

### Log Rotation

Create `/etc/logrotate.d/django-cron`:

```
/var/log/cron_*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue: Cron not running**
```bash
# Check cron service
sudo service cron status

# Restart cron
sudo service cron restart

# Check cron logs
grep CRON /var/log/syslog
```

**Issue: Python not found**
```bash
# Use full path to Python
/usr/bin/python3 manage.py command_name

# Or activate virtual environment
cd /path/to/project && source venv/bin/activate && python manage.py command_name
```

**Issue: Emails not sending**
- Check EMAIL_HOST settings
- Verify SMTP credentials
- Check firewall/port 587
- Test with manual send_mail()

**Issue: Permission denied**
```bash
# Make sure user has permissions
chmod +x manage.py

# Check log directory permissions
sudo chmod 755 /var/log
```

---

## 🎯 Best Practices

### Scheduling
1. **Stagger tasks** - Don't run all at same time
2. **Off-peak hours** - Run heavy tasks at night
3. **Weekday vs Weekend** - Adjust based on business hours
4. **Time zones** - Consider server timezone

### Monitoring
1. **Check logs daily** - Review for errors
2. **Set up alerts** - Email on failures
3. **Track metrics** - Monitor execution time
4. **Test regularly** - Run manual tests monthly

### Maintenance
1. **Update schedules** - Adjust based on usage
2. **Clean old logs** - Implement log rotation
3. **Review thresholds** - Adjust days/counts as needed
4. **Backup configs** - Save crontab/task configs

---

## 📈 Customization

### Adjust Thresholds

**Compliance expiry warning:**
```python
# In check_compliance_expiry.py
expiry_threshold = today + timedelta(days=30)  # Change 30 to desired days
```

**Stale job threshold:**
```bash
# In crontab
python manage.py auto_close_stale_jobs --days=60  # Change 90 to 60
```

**Pending request age:**
```python
# In send_payout_reminders.py
old_threshold = timezone.now() - timedelta(days=7)  # Change 7 to desired days
```

### Add Custom Commands

Create new command:
```bash
python manage.py startapp myapp
mkdir -p myapp/management/commands
touch myapp/management/commands/my_custom_command.py
```

Template:
```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of command'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting...')
        # Your logic here
        self.stdout.write(self.style.SUCCESS('Done!'))
```

---

## 🚀 Production Deployment

### Using Celery (Recommended)

For production, consider using Celery Beat for scheduled tasks:

```python
# celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('workspace')

app.conf.beat_schedule = {
    'check-compliance-daily': {
        'task': 'workspace.tasks.check_compliance_expiry',
        'schedule': crontab(hour=6, minute=0),
    },
    'send-daily-summary': {
        'task': 'workspace.tasks.send_daily_summary',
        'schedule': crontab(hour=9, minute=0, day_of_week='1-5'),
    },
}
```

### Using Supervisor

Monitor cron jobs with Supervisor:

```ini
[program:django-cron]
command=/path/to/venv/bin/python manage.py runcrons
directory=/path/to/project
autostart=true
autorestart=true
stderr_logfile=/var/log/django-cron.err.log
stdout_logfile=/var/log/django-cron.out.log
```

---

## 📝 Testing Checklist

Before deploying to production:

- [ ] Test each command manually
- [ ] Verify email sending works
- [ ] Check notification creation
- [ ] Review log output
- [ ] Test with dry-run options
- [ ] Verify timezone settings
- [ ] Check database connections
- [ ] Test error handling
- [ ] Verify permissions
- [ ] Monitor first few runs

---

## 📞 Support

### Command Help

```bash
# Get help for any command
python manage.py command_name --help

# Example
python manage.py auto_close_stale_jobs --help
```

### Debug Mode

Add verbose output:
```python
self.stdout.write(self.style.WARNING('Debug info here'))
```

---

**Cron Automation Status:** Production Ready
**Last Updated:** December 6, 2024
**Version:** 1.0
**Total Commands:** 5
