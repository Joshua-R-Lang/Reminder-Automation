from database import *

def main():
    engine = create_db_engine()
    if engine:
        reminder_name = str(input("What is the reminder name to fetch data for: "))
        reminder_row = get_reminder_row(engine, reminder_name)
        if reminder_row is not None:
            print(reminder_row.to_string())
        else:
            print("No reminder found or an error occurred.")
        
        delete = str(input("Would you like to delete a reminder yes or no: "))
        if delete == "yes":
            reminder_name = str(input("What is the reminder name: "))
            delete_reminder_row(engine, reminder_name)
    
    formatted_string = format_reminder_to_string(reminder_row)

    subject = "Reminder"
    recipients = ["reminderautomation@outlook.com"]

    send_email(subject, formatted_string, recipients)

if __name__ == "__main__":
    main()
