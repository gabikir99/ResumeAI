# test_register_login.py - Updated to work with simplified database structure
import os
import sys
import getpass
from datetime import datetime

# Fix path issues - works from testing directory or project root
current_dir = os.path.dirname(os.path.abspath(__file__))
if 'testing' in current_dir:
    # We're in the testing directory, go up one level
    project_root = os.path.dirname(current_dir)
else:
    # We're in the project root
    project_root = current_dir

sys.path.insert(0, project_root)

print(f"🔍 Current directory: {current_dir}")
print(f"📁 Project root: {project_root}")
print(f"🔎 Looking for database module in: {os.path.join(project_root, 'database')}")

# Check if database directory exists
database_path = os.path.join(project_root, 'database')
if not os.path.exists(database_path):
    print(f"❌ Database directory not found at: {database_path}")
    print("Available directories:")
    for item in os.listdir(project_root):
        if os.path.isdir(os.path.join(project_root, item)):
            print(f"   📁 {item}")
    sys.exit(1)

try:
    from database import DatabaseService, create_account, login, check_email_exists
    from database.connection import get_db_session
    from database.models import User
    print("✅ Successfully imported database modules")
except ImportError as e:
    print(f"❌ Error importing database modules: {e}")
    print(f"\n🔧 Troubleshooting:")
    print(f"1. Make sure you have the database folder in: {project_root}")
    print(f"2. Check that __init__.py exists in the database folder")
    print(f"3. Try running from the project root directory instead")
    sys.exit(1)

class UserAuth:
    def __init__(self):
        self.db_service = DatabaseService()
        self.current_user = None

    def register(self):
        """Register a new user using the simplified database structure"""
        print("\n=== REGISTRATION ===")
        
        # Get user information - matching the UI form
        name = input("Full Name: ").strip()
        email = input("Email Address: ").strip()
        
        # Get and confirm password
        while True:
            password = getpass.getpass("Password: ")
            confirm_password = getpass.getpass("Confirm Password: ")
            
            if password == confirm_password:
                break
            else:
                print("Passwords don't match. Try again.")
        
        try:
            # Use the simplified create_account function
            result = create_account(name, email, password, confirm_password)
            
            if result['success']:
                print(f"\n✅ {result['message']}")
                print(f"Welcome, {result['user']['name']}!")
                return True
            else:
                print(f"\n❌ Registration failed: {result['message']}")
                return False
                
        except ValueError as e:
            print(f"\n❌ Registration error: {str(e)}")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("🔧 This might be a database structure issue.")
            print("   Try creating a fresh database in pgAdmin 4")
            return False

    def login(self):
        """Log in a user using the simplified database structure"""
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

    def logout(self):
        """Log out the current user"""
        if self.current_user:
            name = self.current_user['name']
            self.current_user = None
            print(f"\n👋 {name} has been logged out.")
        else:
            print("\nNo user is currently logged in.")

    def is_logged_in(self):
        """Check if a user is currently logged in"""
        return self.current_user is not None
    
    def get_user_info(self):
        """Return current user information"""
        return self.current_user
    
    def check_email_availability(self):
        """Check if an email is available for registration"""
        print("\n=== CHECK EMAIL AVAILABILITY ===")
        email = input("Email to check: ").strip()
        
        try:
            exists = check_email_exists(email)
            if exists:
                print(f"❌ Email '{email}' is already registered.")
            else:
                print(f"✅ Email '{email}' is available for registration.")
        except Exception as e:
            print(f"❌ Error checking email: {str(e)}")
        
    def view_all_users(self):
        """View all registered users (for testing purposes)"""
        try:
            with get_db_session() as session:
                users = session.query(User).all()
                
                if not users:
                    print("\nNo users registered in the system.")
                    return
                    
                print("\n=== ALL REGISTERED USERS ===")
                print(f"{'ID':<5} {'Name':<25} {'Email':<35} {'Active':<8} {'Created At':<25}")
                print("-" * 98)
                
                for user in users:
                    created_str = user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "Unknown"
                    active_str = "Yes" if user.is_active else "No"
                    print(f"{user.id:<5} {user.name:<25} {user.email:<35} {active_str:<8} {created_str:<25}")
                    
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    def get_user_stats(self):
        """Get statistics for the current user"""
        if not self.current_user:
            print("❌ Please log in first.")
            return
        
        try:
            stats = self.db_service.get_user_stats(self.current_user['id'])
            print(f"\n=== USER STATISTICS FOR {self.current_user['name']} ===")
            print(f"User ID: {stats['user_id']}")
            print(f"Name: {stats['name']}")
            print(f"Email: {stats['email']}")
            print(f"Member since: {stats['member_since']}")
            print(f"Total chat sessions: {stats['total_sessions']}")
            print(f"Total messages: {stats['total_messages']}")
            print(f"Total job applications: {stats['total_job_applications']}")
        except Exception as e:
            print(f"❌ Error getting user stats: {str(e)}")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    """Display the main menu"""
    clear_screen()
    print("\n" + "="*50)
    print("    RESUME ASSISTANT - AUTH TESTING")
    print("="*50)
    print("1. Register New User")
    print("2. Login")
    print("3. Check Email Availability")
    print("4. View All Users")
    print("5. Exit")
    print("-" * 50)
    return input("Select an option (1-5): ")

def user_menu():
    """Display the user menu (when logged in)"""
    clear_screen()
    print("\n" + "="*50)
    print("    RESUME ASSISTANT - USER MENU")
    print("="*50)
    print("1. View Profile")
    print("2. View User Statistics")
    print("3. View All Users")
    print("4. Logout")
    print("5. Exit")
    print("-" * 50)
    return input("Select an option (1-5): ")

def test_database_connection():
    """Test database connection and table structure"""
    print("\n🔍 Testing database connection...")
    try:
        db_service = DatabaseService()
        print("✅ Database service initialized successfully")
        
        with get_db_session() as session:
            # Test if we can query users table
            user_count = session.query(User).count()
            print(f"✅ Database connection successful - {user_count} users found")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        if "does not exist" in str(e) or "column" in str(e):
            print("\n🔧 Database structure issue detected!")
            print("   1. Create a fresh database in pgAdmin 4")
            print("   2. Or drop all tables and let SQLAlchemy recreate them")
        return False

def main():
    """Main application flow"""
    print("🚀 Starting Resume Assistant Authentication Test")
    
    # Test database connection first
    if not test_database_connection():
        print("\n❌ Cannot continue without database connection.")
        print("Please ensure PostgreSQL is running and database is configured correctly.")
        return
    
    # Initialize user authentication
    auth = UserAuth()
    
    while True:
        if not auth.is_logged_in():
            choice = main_menu()
            
            if choice == '1':
                auth.register()
                input("\nPress Enter to continue...")
            
            elif choice == '2':
                if auth.login():
                    input("\nPress Enter to continue to user menu...")
                else:
                    input("\nPress Enter to try again...")
            
            elif choice == '3':
                auth.check_email_availability()
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                auth.view_all_users()
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                print("\n👋 Exiting the application. Goodbye!")
                break
            
            else:
                print("\n❌ Invalid option. Please try again.")
                input("\nPress Enter to continue...")
        
        else:
            choice = user_menu()
            
            if choice == '1':
                user = auth.get_user_info()
                print("\n" + "="*40)
                print("         YOUR PROFILE")
                print("="*40)
                print(f"Name: {user['name']}")
                print(f"Email: {user['email']}")
                print(f"User ID: {user['id']}")
                print(f"Account Status: {'Active' if user['is_active'] else 'Inactive'}")
                print(f"Member Since: {user['created_at']}")
                input("\nPress Enter to continue...")
            
            elif choice == '2':
                auth.get_user_stats()
                input("\nPress Enter to continue...")
            
            elif choice == '3':
                auth.view_all_users()
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                auth.logout()
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                print("\n👋 Exiting the application. Goodbye!")
                break
            
            else:
                print("\n❌ Invalid option. Please try again.")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()