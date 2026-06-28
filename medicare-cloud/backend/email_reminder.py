# ===== MEDICARE CLOUD - EMAIL REMINDER SERVICE =====
# Level 3: Automated email reminders using Azure Communication Services
# Run this file separately on Azure App Service as a background job
#
# Install: pip install azure-communication-email schedule pyodbc
#
# Set these environment variables in Azure App Service:
#   AZURE_COMM_CONNECTION_STRING = your Azure Communication Services connection string
#   AZURE_SQL_CONNECTION_STRING  = your Azure SQL connection string
#   SENDER_EMAIL                 = donotreply@your-azure-domain.azurecomm.net

import schedule
import time
import os
import pyodbc
from datetime import datetime
from azure.communication.email import EmailClient

# ── Azure Connections ───────────────────────────────────────────
COMM_CONN_STR = os.environ.get('AZURE_COMM_CONNECTION_STRING', '')
SQL_CONN_STR  = os.environ.get('AZURE_SQL_CONNECTION_STRING',  '')
SENDER_EMAIL  = os.environ.get('SENDER_EMAIL', 'donotreply@medicarecloud.azurecomm.net')


def get_db_connection():
    """Connect to Azure SQL Database"""
    return pyodbc.connect(SQL_CONN_STR)


def send_reminder_email(to_email, to_name, medicine_name, dosage, instructions):
    """Send medicine reminder email via Azure Communication Services"""
    try:
        client  = EmailClient.from_connection_string(COMM_CONN_STR)
        message = {
            "senderAddress": SENDER_EMAIL,
            "recipients": {
                "to": [{"address": to_email, "displayName": to_name}]
            },
            "content": {
                "subject": f"💊 Medicine Reminder: Time to take {medicine_name}",
                "html": f"""
                <html>
                <body style="font-family:Arial,sans-serif;max-width:500px;margin:0 auto;padding:20px;">
                  <div style="background:#0078d4;padding:20px;border-radius:12px 12px 0 0;text-align:center;">
                    <h2 style="color:white;margin:0;">🏥 MediCare Cloud</h2>
                    <p style="color:rgba(255,255,255,0.85);margin:6px 0 0;font-size:14px;">Medicine Reminder</p>
                  </div>
                  <div style="background:#f8f9fa;padding:24px;border-radius:0 0 12px 12px;border:1px solid #dee2e6;">
                    <p style="font-size:16px;color:#333;">Hello <strong>{to_name}</strong>,</p>
                    <p style="color:#555;">This is your scheduled medicine reminder from MediCare Cloud.</p>
                    <div style="background:white;border:1px solid #dee2e6;border-radius:8px;padding:16px;margin:16px 0;">
                      <p style="margin:0;font-size:18px;"><strong>💊 {medicine_name}</strong></p>
                      <p style="margin:6px 0 0;color:#0078d4;font-weight:500;">Dosage: {dosage}</p>
                      {f'<p style="margin:6px 0 0;color:#666;font-size:14px;">{instructions}</p>' if instructions else ''}
                    </div>
                    <p style="color:#555;">Please take your medicine now. Stay healthy!</p>
                    <a href="https://sayyadasanafatima.github.io/medicare-cloud/dashboard.html"
                       style="display:inline-block;background:#0078d4;color:white;padding:10px 24px;
                              border-radius:6px;text-decoration:none;font-weight:500;margin-top:8px;">
                      Open Dashboard
                    </a>
                    <hr style="border:none;border-top:1px solid #dee2e6;margin:20px 0;">
                    <p style="font-size:12px;color:#aaa;margin:0;">
                      MediCare Cloud | SITER Academy Summer Internship 2026 | Cloud Computing Domain<br>
                      Powered by Microsoft Azure Communication Services
                    </p>
                  </div>
                </body>
                </html>
                """,
                "plainText": f"Hello {to_name}, time to take {medicine_name} {dosage}. {instructions or ''}"
            }
        }
        poller = client.begin_send(message)
        result = poller.result()
        print(f"[EMAIL SENT] To: {to_email} | Medicine: {medicine_name} | Status: {result.status}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def check_and_send_reminders():
    """Check database for medicines due now and send reminders"""
    try:
        now          = datetime.now()
        current_time = now.strftime('%H:%M')
        print(f"[REMINDER CHECK] Time: {current_time}")

        conn   = get_db_connection()
        cursor = conn.cursor()

        # Get all active medicines with their user emails
        # that have a reminder time matching current time
        query = """
            SELECT u.name, u.email, m.medicine_name, m.dosage, m.reminder_times, m.instructions
            FROM Medicines m
            JOIN Users u ON m.user_id = u.user_id
            WHERE m.is_active = 1
              AND m.reminder_times LIKE ?
        """
        cursor.execute(query, f'%{current_time}%')
        rows = cursor.fetchall()

        print(f"[REMINDER CHECK] Found {len(rows)} reminders to send")

        for row in rows:
            name, email, medicine_name, dosage, reminder_times, instructions = row
            send_reminder_email(email, name, medicine_name, dosage, instructions or '')

        conn.close()

    except Exception as e:
        print(f"[DB ERROR] {e}")
        # Fallback: use in-memory demo data if DB not connected
        demo_check()


def demo_check():
    """Demo mode: prints reminder without DB or email"""
    now          = datetime.now()
    current_time = now.strftime('%H:%M')
    print(f"[DEMO MODE] Reminder check at {current_time} - No DB connected")
    print("[DEMO MODE] In production: connects to Azure SQL and sends email via Azure Communication Services")


# ── Schedule reminders every minute ────────────────────────────
schedule.every(1).minutes.do(check_and_send_reminders)

print("=" * 50)
print("  MediCare Cloud - Email Reminder Service")
print("  Powered by Microsoft Azure")
print("  Running... (checks every minute)")
print("=" * 50)

# Run once immediately on startup
check_and_send_reminders()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(30)
