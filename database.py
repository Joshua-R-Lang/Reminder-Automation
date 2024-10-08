import pandas as pd
import logging
from sqlalchemy import create_engine as sqlalchemy_create_engine
import pymysql
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('reminder_automation.log')
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

DB_URL = os.getenv("DATABASE_URL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")

def create_db_engine():
    try:
        engine = sqlalchemy_create_engine(DB_URL)
        logging.info("Database engine created successfully.")
        return engine
    except Exception as e:
        logging.error(f"Error creating engine: {e}")
        return None

def get_reminder_row(engine, reminder_name):
    query = "SELECT * FROM Reminder_Config WHERE Reminder_Name = %s"
    try:
        reminder_row = pd.read_sql(query, engine, params=(reminder_name,))
        logging.info(f"Reminder row fetched for {reminder_name}.")
        return reminder_row
    except Exception as e:
        logging.error(f"An error occurred while fetching reminder: {e}")
        return None

def delete_reminder_row(engine, reminder_name):
    delete_query = "DELETE FROM Reminder_Config WHERE Reminder_Name = %s"
    try:
        with engine.connect() as connection:
            result = connection.execute(delete_query, (reminder_name,))
            logging.info(f"Deleted rows: {result.rowcount} for reminder {reminder_name}.")
            return result.rowcount
    except Exception as e:
        logging.error(f"An error occurred while deleting reminder: {e}")
        return None
    
def create_reminder_row(engine, reminder_name, reminder_description, event_start, event_end):
    df = pd.DataFrame([{
        'Reminder_Name': reminder_name,
        'Reminder_Description': reminder_description,
        'Event_Start': event_start,
        'Event_End': event_end
    }])
    try: 
        df.to_sql('Reminder_Config', engine, if_exists='append', index=False)
        logging.info(f"Reminder '{reminder_name}' inserted into the database.")
    except Exception as e:
        logging.error(f"An error occurred while creating reminder: {e}")
        return None
    
def update_reminder_row(engine, reminder_name, reminder_description=None, event_start=None, event_end=None):
    try:
        query = "SELECT * FROM Reminder_Config WHERE Reminder_Name = %s"
        reminder_df = pd.read_sql(query, engine, params=(reminder_name,))

        if reminder_df.empty:
            logging.info(f"No reminder found with name {reminder_name}.")
            return None
        
        if reminder_description:
            reminder_df['Reminder_Description'] = reminder_description
        if event_start:
            reminder_df['Event_Start'] = event_start
        if event_end:
            reminder_df['Event_End'] = event_end
        
        with engine.connect() as connection:
            update_query = """
            UPDATE Reminder_Config
                SET Reminder_Description = %s, Event_Start = %s, Event_End = %s
                WHERE Reminder_Name = %s
            """
            params = (reminder_df['Reminder_Description'].values[0], 
                        reminder_df['Event_Start'].values[0],
                        reminder_df['Event_End'].values[0],
                        reminder_name)
            connection.execute(update_query, params)
            
        logging.info(f"Reminder '{reminder_name}' updated successfully.")
        return True

    except Exception as e:
        logging.error(f"An error occurred while updating reminder: {e}")
        return None
    
def list_all_reminders(engine):
    query = "SELECT * FROM Reminder_Config"
    try:
        reminders_df = pd.read_sql(query, engine)
        
        if reminders_df.empty:
            logging.info("No reminders found.")
            print("No reminders found.")
            return
        
        for index, reminder_row in reminders_df.iterrows():
            formatted_reminder = format_reminder_to_string(reminders_df.loc[[index]])
            print(formatted_reminder)

    except Exception as e:
        logging.error(f"An error occurred while listing all reminders: {e}")
        print("An error occurred while listing reminders.")
    
def schedule_reminder(reminder_name, event_start, formatted_string, recipients):
    try:
        scheduler = BackgroundScheduler()
        event_start_time = datetime.strptime(event_start, "%Y-%m-%d %H:%M:%S")
        trigger_24h = DateTrigger(run_date=event_start_time - timedelta(minutes=1440))
        trigger_1h = DateTrigger(run_date=event_start_time - timedelta(minutes=60))
        scheduler.add_job(send_scheduled_reminder, trigger_24h, args=[f"Reminder for {reminder_name}", formatted_string, recipients])
        scheduler.add_job(send_scheduled_reminder, trigger_1h, args=[f"Reminder for {reminder_name}", formatted_string, recipients])
        scheduler.start()
        logging.info(f"Reminder '{reminder_name}' scheduled for 24h and 1h before {event_start_time}.")
    except Exception as e:
        logging.error(f"Failed to schedule reminder '{reminder_name}': {e}")

def send_scheduled_reminder(reminder_name, event_start, formatted_string, recipients):
    subject = f"Reminder for {reminder_name}" 
    try:
        send_email(subject, formatted_string, recipients)
        logging.info(f"Scheduled reminder '{reminder_name}' sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send scheduled reminder '{reminder_name}': {e}")

def send_email(subject, body, recipients):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = ', '.join(recipients)
    
    try:
        with smtplib.SMTP('smtp.office365.com', 587) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp_server.sendmail(EMAIL_SENDER, recipients, msg.as_string())
            logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def format_reminder_to_string(reminder_row):
    if reminder_row.empty:
        logging.info("No reminder found.")
        return "No reminder found."

    reminder = reminder_row.iloc[0].to_dict()
    
    formatted_string = (
        f"Reminder Name: {reminder['Reminder_Name']}\n"
        f"Description: {reminder['Reminder_Description']}\n"
        f"Start Time: {reminder['Event_Start']}\n"
        f"End Time: {reminder['Event_End']}"
    )
    
    logging.info(f"Formatted reminder: {formatted_string}")
    
    return formatted_string