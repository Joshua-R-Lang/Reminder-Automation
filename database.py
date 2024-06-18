import pandas as pd
from sqlalchemy import create_engine

def createEngine():
    # Replace 'Darfoklutz11!' with your actual MySQL password
    db_url = "mysql://root:Darfoklutz11!@localhost/reminders"
    engine = create_engine(db_url)
    return engine

def getReminderRow(engine, reminderName):
    query = f"select * from Reminder_Config where Reminder_Name = 'reminderName';"
    with engine.connect() as connection:
        try:
            reminderRow = pd.read_sql(query, engine)
            return reminderRow
        except Exception as e:
            print(f"An error occurred: {str(e)}")

            
        