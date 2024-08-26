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
            if reminder_row is not None:
                delete_reminder_row(engine, reminder_name)
            else:
                print("No reminder found or an error occurred.")
    
    formatted_string = format_reminder_to_string(reminder_row)

    subject = "Reminder"
    body = formatted_string
    sender = "reminderautomation@outlook.com"
    recipients = ["reminderautomation@outlook.com"]
    password = "Darfoklutz11!"
    
    send_email(subject, body, sender, recipients, password)



    

if __name__ == "__main__":
    main()



