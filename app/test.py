import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if os.path.exists("vacation_manager.db"):
    os.remove("vacation_manager.db")
    print("Old database deleted.")
else:
    print("The file does not exist")
