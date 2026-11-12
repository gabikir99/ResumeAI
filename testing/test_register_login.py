import os
import sys
import getpass
from datetime import datetime
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Fix path issues - works from testing directory or project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) if 'testing' in current_dir else current_dir
sys.path.insert(0, project_root)

# Imports from database module
from database import DatabaseService, create_account, login, check_email_exists
from database.connection import get_db_session
from database.models import User

class UserAuth:
    def __init__(self):
        self.db_service = DatabaseService()
        self.current_user = None

    def register(self):
        print("\n=== REGISTRATION ===")
        name = input("Full Name: ").strip()
        email = input("Email Address: ").strip()
        while True:
            password = getpass.getpass("Password: ")
            confirm_password = getpass.getpass("Confirm Password: ")
            if password == confirm_password:
                break
            else:
                print("Passwords don't match. Try again.")
        try:
            result = create_account(name, email, password, confirm_password)
            if result['success']:
                print(f"\n✅ {result['message']}")
                print(f"Welcome, {result['user']['name']}!")
                return True
            else:
                print(f"\n❌ Registration failed: {result['message']}")
                return False
        except Exception as e:
            print(f"\n❌ Registration error: {str(e)}")
            return False

    def login(self):
        print("\n=== LOGIN ===")
        email = input("Email Address: ").strip()
        password = getpass.getpass("Password: ")
        try:
            result = login(email, password)
            if result['success']:
                self.current_user = result['user']
                print(f"\n✅ {result['message']}")
                print(f"Welcome back, {self.current_user['name']}!")
                return True
            else:
                print(f"\n❌ {result['message']}")
                return False
        except Exception as e:
            print(f"\n❌ Login error: {str(e)}")
            return False

    def view_all_users(self):
        try:
            with get_db_session() as session:
                users = session.query(User).all()
                if not users:
                    print("\nNo users registered in the system.")
                    return
                print("\n=== ALL REGISTERED USERS ===")
                for user in users:
                    created_str = user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "Unknown"
                    active_str = "Yes" if user.is_active else "No"
                    print(f"{user.id:<5} {user.name:<25} {user.email:<35} {active_str:<8} {created_str:<25}")
        except Exception as e:
            print(f"❌ Database error: {e}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    clear_screen()
    print("\n" + "="*50)
    print("    RESUME ASSISTANT - AUTH TESTING")
    print("="*50)
    print("1. Register New User")
    print("2. Login")
    print("3. View All Users")
    print("4. Exit")
    print("-" * 50)
    return input("Select an option (1-4): ")

def test_database_connection():
    print("\n🔍 Testing database connection...")
    try:
        db_service = DatabaseService()
        with get_db_session() as session:
            user_count = session.query(User).count()
            print(f"✅ Database connected - {user_count} users found")
            assert user_count >= 0
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        assert False

def main():
    print("🚀 Starting Resume Assistant Authentication Test")
    if not test_database_connection():
        print("\n❌ Cannot continue without database connection.")
        return
    auth = UserAuth()
    while True:
        choice = main_menu()
        if choice == '1':
            auth.register()
            input("\nPress Enter to continue...")
        elif choice == '2':
            auth.login()
            input("\nPress Enter to continue...")
        elif choice == '3':
            auth.view_all_users()
            input("\nPress Enter to continue...")
        elif choice == '4':
            print("\n👋 Exiting the application. Goodbye!")
            break
        else:
            print("\n❌ Invalid option.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
