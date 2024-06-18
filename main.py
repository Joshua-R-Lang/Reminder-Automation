from database import *
from sqlalchemy import create_engine

def main():

    engine = createEngine()
    reminderName = sys.argv[1]
    print(getReminderRow(engine, reminderName))

if __name__ == "__main__": 
    main()


