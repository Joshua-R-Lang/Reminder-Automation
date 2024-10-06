import argparse
from database import *

def main():
    engine = create_db_engine()
    if not engine():
        print("Failed to create database engine.")
        return

    parser = argparse.ArgumentParser(description="Reminder Automation CLI")
    subparsers = parser.add_subparsers(dest='command')
    
    #Fetch Reminder
    fetch_parser = subparsers.add_parser('fetch', help='Fetch a reminder by name')
    fetch_parser.add_argument('reminder_name', type=str, help='The name of the reminder to fetch')

    #Create Reminder
    create_parser = subparsers.add_parser('create', help='Create a new reminder')
    create_parser.add_argument('reminder_name', type=str, help='The name of the reminder')
    create_parser.add_argument('reminder_description', type=str, help='Description of the reminder')
    create_parser.add_argument('event_start', type=str, help='Event start time (format: YYYY-MM-DD HH:MM:SS)')
    create_parser.add_argument('event_end', type=str, help='Event end time (format: YYYY-MM-DD HH:MM:SS)')

    #Delete Reminder
    delete_parser = subparsers.add_parser('delete', help='Delete an existing reminder by name')
    delete_parser.add_argument('reminder_name', type=str, help='The name of the reminder to delete')

    #Schedule Reminder
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a reminder to be sent')
    schedule_parser.add_argument('reminder_name', type=str, help='The name of the reminder to schedule')
    schedule_parser.add_argument('event_start', type=str, help='Event start time (format: YYYY-MM-DD HH:MM:SS)')

    #Send Email
    send_email_parser = subparsers.add_parser('send_email', help='Send an email reminder')
    send_email_parser.add_argument('subject', type=str, help='Email subject')
    send_email_parser.add_argument('body', type=str, help='Email body')
    send_email_parser.add_argument('recipients', type=str, nargs='+', help='Email recipients')

    #List Reminders
    list_parser = subparsers.add_parser('list', help='List all reminders')

    #Update Reminder
    update_parser = subparsers.add_parser('update', help='Update a reminder')
    update_parser.add_argument('reminder_name', type=str, help='The name of the reminder to update')
    update_parser.add_argument('new_description', type=str, help='New description of the reminder')
    update_parser.add_argument('new_event_start', type=str, help='New event start time (format: YYYY-MM-DD HH:MM:SS)')
    update_parser.add_argument('new_event_end', type=str, help='New event end time (format: YYYY-MM-DD HH:MM:SS)')

    args = parser.parse_args()

    #Command Handling
    if args.command =='fetch':
        reminder_row = get_reminder_row(engine, args.reminder_name)
        if reminder_row is not None:
            print(format_reminder_to_string(reminder_row))
        else:
            print("No reminder found or an error occurred.")

    elif args.command == 'create':
        create_reminder_row(engine, args.reminder_name, args.reminder_description, args.event_start, args.event_end)
        print(f"Reminder '{args.reminder_name}' created successfully.")
    
    elif args.command == 'delete':
        deleted_count = delete_reminder_row(engine, args.reminder_name)
        if deleted_count:
            print(f"Deleted {deleted_count} reminder(s) named '{args.reminder_name}'.")
        else:
            print("No reminder found or an error occurred.")
    
    elif args.command == 'schedule':
        reminder_row = get_reminder_row(engine, args.reminder_name)
        if reminder_row:
            formatted_string = format_reminder_to_string(reminder_row)
            schedule_reminder(args.reminder_name, args.event_start, formatted_string, ["recipient@example.com"])
            print(f"Reminder '{args.reminder_name}' scheduled for {args.event_start}.")
        else:
            print("No reminder found to schedule.")

    elif args.command == 'send_email':
        send_email(args.subject, args.body, args.recipients)
        print(f"Email sent successfully to {', '.join(args.recipients)}.")

    elif args.command == 'list':
        reminders = list_all_reminders(engine)
        if reminders:
            for reminder in reminders:
                print(reminder.to_string())
        else:
            print("No reminders found.")

    elif args.command == 'update':
        updated_count = update_reminder_row(engine, args.reminder_name, args.new_description, args.new_event_start, args.new_event_end)
        if updated_count:
            print(f"Updated {updated_count} reminder(s) named '{args.reminder_name}'.")
        else:
            print("No reminder found or an error occurred.")


if __name__ == "__main__":
    main()
