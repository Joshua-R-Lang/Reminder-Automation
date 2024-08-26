import pandas as pd
from sqlalchemy import create_engine as sqlalchemy_create_engine
import pymysql
import smtplib
from email.mime.text import MIMEText

def create_db_engine():
    db_url = "mysql+pymysql://root:Darfoklutz11!@localhost/reminders"
    try:
        engine = sqlalchemy_create_engine(db_url)
        return engine
    except Exception as e:
        print(f"Error creating engine: {e}")
        return None

def get_reminder_row(engine, reminder_name):
    query = "SELECT * FROM Reminder_Config WHERE Reminder_Name = %s"
    try:
        reminder_row = pd.read_sql(query, engine, params=(reminder_name,))
        return reminder_row
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def delete_reminder_row(engine, reminder_name):
    delete_query = "DELETE FROM Reminder_Config WHERE Reminder_Name = %s"
    try:
        with engine.connect() as connection:
            result = connection.execute(delete_query, (reminder_name, ))
            print(f"Deleted rows: {result.rowcount}")
            return result.rowcount
    except Exception as e:
        print(f"An error occurred: {e}")
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
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    
    with smtplib.SMTP('smtp.office365.com', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent.")


def format_reminder_to_string(reminder_row):
    if reminder_row.empty:
        return "No reminder found."

    reminder = reminder_row.iloc[0].to_dict()
    
    formatted_string = (
        f"Reminder Name: {reminder['Reminder_Name']}\n"
        f"Description: {reminder['Reminder_Description']}\n"
        f"Start Time: {reminder['Event_Start']}\n"
        f"End Time: {reminder['Event_End']}"
    )
    
    return formatted_string

