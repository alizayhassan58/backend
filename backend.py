"""
MediTrack - Healthcare Management System
Simple medicine and appointment tracker
"""

import json
import os
from datetime import datetime, timedelta, date
import sys
from typing import Dict, List, Optional

DATABASE_FILE = "meditrack_simple.json"

class Appointment:
    """Appointment class"""
    def __init__(self, title: str, doctor: str, date_str: str, time_str: str, location: str = ""):
        self.title = title
        self.doctor = doctor
        self.date = date_str
        self.time = time_str
        self.location = location
        self.completed = False
    
    def days_until(self) -> int:
        """Calculate days until appointment"""
        appt_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        today = date.today()
        return (appt_date - today).days
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'doctor': self.doctor,
            'date': self.date,
            'time': self.time,
            'location': self.location,
            'completed': self.completed
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Appointment':
        """Create from dictionary"""
        appointment = Appointment(
            title=data['title'],
            doctor=data['doctor'],
            date_str=data['date'],
            time_str=data['time'],
            location=data.get('location', '')
        )
        appointment.completed = data.get('completed', False)
        return appointment

class Medicine:
    """Medicine class"""
    def __init__(self, name: str, dosage: str, frequency: str, start_date: str, end_date: str, stock: int = 30):
        self.name = name
        self.dosage = dosage
        self.frequency = frequency
        self.start_date = start_date
        self.end_date = end_date
        self.stock = stock
        self.taken_today = 0
        self.missed_today = 0
    
    def take_dose(self) -> bool:
        """Record dose as taken"""
        if self.stock <= 0:
            return False
        self.stock -= 1
        self.taken_today += 1
        return True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'stock': self.stock,
            'taken_today': self.taken_today,
            'missed_today': self.missed_today
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Medicine':
        """Create from dictionary"""
        medicine = Medicine(
            name=data['name'],
            dosage=data['dosage'],
            frequency=data['frequency'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            stock=data['stock']
        )
        medicine.taken_today = data.get('taken_today', 0)
        medicine.missed_today = data.get('missed_today', 0)
        return medicine

class User:
    """User class"""
    def __init__(self, username: str, password: str, name: str):
        self.username = username
        self.password = password  # Simple password storage (not for production)
        self.name = name
        self.medicines: List[Medicine] = []
        self.appointments: List[Appointment] = []
        self.emergency_contact = ""
        self.emergency_phone = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'medicines': [m.to_dict() for m in self.medicines],
            'appointments': [a.to_dict() for a in self.appointments],
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'User':
        """Create from dictionary"""
        user = User(
            username=data['username'],
            password=data['password'],
            name=data['name']
        )
        user.medicines = [Medicine.from_dict(m) for m in data.get('medicines', [])]
        user.appointments = [Appointment.from_dict(a) for a in data.get('appointments', [])]
        user.emergency_contact = data.get('emergency_contact', '')
        user.emergency_phone = data.get('emergency_phone', '')
        return user

class Database:
    """Simple database handler"""
    @staticmethod
    def load_data() -> Dict:
        """Load data from JSON file"""
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    @staticmethod
    def save_data(data: Dict) -> None:
        """Save data to JSON file"""
        with open(DATABASE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def save_user(user: User) -> None:
        """Save user data"""
        data = Database.load_data()
        data['users'] = data.get('users', {})
        data['users'][user.username] = user.to_dict()
        Database.save_data(data)
    
    @staticmethod
    def load_user(username: str) -> Optional[User]:
        """Load user by username"""
        data = Database.load_data()
        users = data.get('users', {})
        if username in users:
            return User.from_dict(users[username])
        return None
    
    @staticmethod
    def user_exists(username: str) -> bool:
        """Check if user exists"""
        data = Database.load_data()
        return username in data.get('users', {})

class MediTrackApp:
    """Main application class"""
    def __init__(self):
        self.current_user: Optional[User] = None
    
    def clear_screen(self) -> None:
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self, title: str = "") -> None:
        """Display application header"""
        self.clear_screen()
        print("=" * 60)
        print("           💊 MEDITRACK - HEALTHCARE SYSTEM")
        print("=" * 60)
        if self.current_user:
            print(f"👤 User: {self.current_user.name}")
        if title:
            print(f"\n{title}")
            print("-" * 60)
        print()
    
    def register_user(self) -> None:
        """Register new user"""
        self.display_header("📝 REGISTER NEW USER")
        
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            input("Press Enter to continue...")
            return
        
        if Database.user_exists(username):
            print("❌ Username already exists")
            input("Press Enter to continue...")
            return
        
        name = input("Full Name: ").strip()
        if not name:
            print("❌ Name cannot be empty")
            input("Press Enter to continue...")
            return
        
        password = input("Password: ").strip()
        if not password:
            print("❌ Password cannot be empty")
            input("Press Enter to continue...")
            return
        
        confirm = input("Confirm Password: ").strip()
        if password != confirm:
            print("❌ Passwords don't match")
            input("Press Enter to continue...")
            return
        
        emergency_contact = input("Emergency Contact Name (optional): ").strip()
        emergency_phone = input("Emergency Contact Phone (optional): ").strip()
        
        user = User(username, password, name)
        user.emergency_contact = emergency_contact
        user.emergency_phone = emergency_phone
        
        Database.save_user(user)
        print("\n✅ Registration successful!")
        print(f"Welcome to MediTrack, {name}!")
        input("\nPress Enter to login...")
    
    def login_user(self) -> None:
        """Login existing user"""
        self.display_header("🔐 USER LOGIN")
        
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        user = Database.load_user(username)
        if user and user.password == password:
            self.current_user = user
            print(f"\n✅ Welcome back {user.name}!")
            self.check_notifications()
            input("\nPress Enter to continue...")
        else:
            print("\n❌ Invalid username or password")
            input("Press Enter to continue...")
    
    def check_notifications(self) -> None:
        """Check and display notifications"""
        if not self.current_user:
            return
        
        today = date.today()
        notifications = []
        
        for appointment in self.current_user.appointments:
            days = appointment.days_until()
            if days == 0 and not appointment.completed:
                notifications.append(f"🚨 {appointment.title} with Dr. {appointment.doctor} is TODAY!")
            elif 1 <= days <= 3 and not appointment.completed:
                notifications.append(f"📅 {appointment.title} with Dr. {appointment.doctor} in {days} days")
        
        for medicine in self.current_user.medicines:
            if medicine.stock <= 5:
                notifications.append(f"⚠️  {medicine.name} low stock: {medicine.stock} doses left")
        
        if notifications:
            print("\n🔔 NOTIFICATIONS:")
            for note in notifications:
                print(f"  • {note}")
    
    def add_medicine(self) -> None:
        """Add new medicine"""
        self.display_header("➕ ADD NEW MEDICINE")
        
        name = input("Medicine Name: ").strip()
        if not name:
            print("❌ Name required")
            input("Press Enter to continue...")
            return
        
        dosage = input("Dosage (e.g., 500mg): ").strip()
        if not dosage:
            print("❌ Dosage required")
            input("Press Enter to continue...")
            return
        
        print("\nFrequency Options:")
        print("1. Once daily")
        print("2. Twice daily")
        print("3. Three times daily")
        print("4. Four times daily")
        
        choice = input("\nSelect (1-4): ").strip()
        frequencies = ['Once daily', 'Twice daily', 'Three times daily', 'Four times daily']
        if choice.isdigit() and 1 <= int(choice) <= 4:
            frequency = frequencies[int(choice) - 1]
        else:
            frequency = 'Once daily'
        
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date_input = input(f"End Date (YYYY-MM-DD) [{(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}]: ").strip()
        end_date = end_date_input if end_date_input else (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            stock = int(input("Initial stock [30]: ").strip() or "30")
        except ValueError:
            stock = 30
        
        medicine = Medicine(name, dosage, frequency, start_date, end_date, stock)
        self.current_user.medicines.append(medicine)
        Database.save_user(self.current_user)
        
        print(f"\n✅ {name} added successfully!")
        print(f"   Dosage: {dosage}")
        print(f"   Frequency: {frequency}")
        print(f"   Stock: {stock} doses")
        input("\nPress Enter to continue...")
    
    def add_appointment(self) -> None:
        """Add new appointment"""
        self.display_header("📅 ADD NEW APPOINTMENT")
        
        title = input("Appointment Title: ").strip()
        if not title:
            print("❌ Title required")
            input("Press Enter to continue...")
            return
        
        doctor = input("Doctor's Name: ").strip()
        if not doctor:
            print("❌ Doctor required")
            input("Press Enter to continue...")
            return
        
        date_str = input("Date (YYYY-MM-DD): ").strip()
        time_str = input("Time (HH:MM) [10:00]: ").strip() or "10:00"
        location = input("Location (optional): ").strip()
        
        appointment = Appointment(title, doctor, date_str, time_str, location)
        self.current_user.appointments.append(appointment)
        Database.save_user(self.current_user)
        
        days = appointment.days_until()
        print(f"\n✅ Appointment added!")
        print(f"   Title: {title}")
        print(f"   Doctor: Dr. {doctor}")
        print(f"   Date: {date_str} ({'TODAY!' if days == 0 else f'in {days} days'})")
        print(f"   Time: {time_str}")
        input("\nPress Enter to continue...")
    
    def mark_medicine_taken(self) -> None:
        """Mark medicine as taken"""
        self.display_header("✅ MARK MEDICINE AS TAKEN")
        
        if not self.current_user.medicines:
            print("❌ No medicines")
            input("Press Enter to continue...")
            return
        
        print("Your Medicines:")
        for i, med in enumerate(self.current_user.medicines, 1):
            print(f"{i}. {med.name} - {med.dosage} ({med.frequency})")
        
        try:
            choice = int(input("\nSelect medicine: ").strip())
            if 1 <= choice <= len(self.current_user.medicines):
                medicine = self.current_user.medicines[choice - 1]
                if medicine.take_dose():
                    Database.save_user(self.current_user)
                    print(f"\n✅ {medicine.name} marked as taken")
                    print(f"   Remaining stock: {medicine.stock} doses")
                    
                    if medicine.stock <= 5:
                        print("⚠️  Low stock! Please refill soon")
                else:
                    print("❌ Out of stock!")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Invalid input")
        
        input("\nPress Enter to continue...")
    
    def mark_appointment_completed(self) -> None:
        """Mark appointment as completed"""
        self.display_header("✅ MARK APPOINTMENT COMPLETED")
        
        if not self.current_user.appointments:
            print("❌ No appointments")
            input("Press Enter to continue...")
            return
        
        upcoming = [a for a in self.current_user.appointments if a.days_until() >= 0 and not a.completed]
        
        if not upcoming:
            print("❌ No upcoming appointments")
            input("Press Enter to continue...")
            return
        
        print("Upcoming Appointments:")
        for i, appt in enumerate(upcoming, 1):
            print(f"{i}. {appt.title} with Dr. {appt.doctor} on {appt.date}")
        
        try:
            choice = int(input("\nSelect appointment: ").strip())
            if 1 <= choice <= len(upcoming):
                appointment = upcoming[choice - 1]
                appointment.completed = True
                Database.save_user(self.current_user)
                print(f"\n✅ {appointment.title} marked as completed")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Invalid input")
        
        input("\nPress Enter to continue...")
    
    def view_weekly_summary(self) -> None:
        """View weekly summary"""
        self.display_header("📊 WEEKLY SUMMARY")
        
        taken_today = sum(m.taken_today for m in self.current_user.medicines)
        missed_today = sum(m.missed_today for m in self.current_user.medicines)
        total_medicines = len(self.current_user.medicines)
        
        upcoming_appointments = sum(1 for a in self.current_user.appointments if a.days_until() >= 0 and not a.completed)
        low_stock = sum(1 for m in self.current_user.medicines if m.stock <= 5)
        
        print("📅 This Week's Summary:")
        print(f"   ✅ Doses Taken: {taken_today}")
        print(f"   ❌ Doses Missed: {missed_today}")
        print(f"   💊 Active Medicines: {total_medicines}")
        print(f"   📅 Upcoming Appointments: {upcoming_appointments}")
        
        if low_stock > 0:
            print(f"   ⚠️  Low Stock Medicines: {low_stock}")
        
        if total_medicines > 0:
            total_doses = taken_today + missed_today
            if total_doses > 0:
                adherence = (taken_today / total_doses) * 100
                print(f"   📈 Adherence Rate: {adherence:.1f}%")
        
        input("\nPress Enter to continue...")
    
    def change_password(self) -> None:
        """Change user password"""
        self.display_header("🔐 CHANGE PASSWORD")
        
        current = input("Current Password: ").strip()
        if current != self.current_user.password:
            print("❌ Current password incorrect")
            input("Press Enter to continue...")
            return
        
        new_password = input("New Password: ").strip()
        if not new_password:
            print("❌ Password cannot be empty")
            input("Press Enter to continue...")
            return
        
        confirm = input("Confirm Password: ").strip()
        if new_password != confirm:
            print("❌ Passwords don't match")
            input("Press Enter to continue...")
            return
        
        self.current_user.password = new_password
        Database.save_user(self.current_user)
        
        print("\n✅ Password changed successfully!")
        input("Press Enter to continue...")
    
    def emergency_mode(self) -> None:
        """Emergency mode"""
        self.display_header("🚨 EMERGENCY MODE")
        
        print("🚨 CRITICAL INFORMATION - FOR EMERGENCY USE")
        print("=" * 60)
        
        print(f"\n👤 PATIENT INFORMATION:")
        print(f"   Name: {self.current_user.name}")
        
        if self.current_user.emergency_contact:
            print(f"   Emergency Contact: {self.current_user.emergency_contact}")
            print(f"   Contact Phone: {self.current_user.emergency_phone}")
        else:
            print("   ⚠️  No emergency contact set")
        
        critical_meds = [m for m in self.current_user.medicines if m.stock <= 2]
        if critical_meds:
            print(f"\n⚠️  CRITICAL MEDICATIONS (LOW STOCK):")
            for med in critical_meds:
                print(f"   • {med.name}: {med.stock} doses left")
        
        urgent_appts = [a for a in self.current_user.appointments if a.days_until() <= 3 and not a.completed]
        if urgent_appts:
            print(f"\n📅 URGENT APPOINTMENTS:")
            for appt in urgent_appts:
                print(f"   • {appt.title} with Dr. {appt.doctor}")
        
        print("\n" + "=" * 60)
        print("In a real emergency, share this information with responders")
        input("\nPress Enter to continue...")
    
    def view_medicines(self) -> None:
        """View all medicines"""
        self.display_header("💊 YOUR MEDICINES")
        
        if not self.current_user.medicines:
            print("No medicines added yet")
            input("Press Enter to continue...")
            return
        
        for i, med in enumerate(self.current_user.medicines, 1):
            status = "🟢" if med.stock > 10 else "🟡" if med.stock > 5 else "🔴"
            print(f"{i}. {med.name} - {med.dosage}")
            print(f"   Frequency: {med.frequency}")
            print(f"   Stock: {status} {med.stock} doses")
            if med.stock <= 5:
                print(f"   ⚠️  Low stock! Please refill soon")
            print()
        
        input("Press Enter to continue...")
    
    def view_appointments(self) -> None:
        """View all appointments"""
        self.display_header("📅 YOUR APPOINTMENTS")
        
        if not self.current_user.appointments:
            print("No appointments scheduled")
            input("Press Enter to continue...")
            return
        
        upcoming = [a for a in self.current_user.appointments if a.days_until() >= 0]
        past = [a for a in self.current_user.appointments if a.days_until() < 0]
        
        if upcoming:
            print("📅 UPCOMING APPOINTMENTS:")
            for i, appt in enumerate(upcoming, 1):
                status = "✅" if appt.completed else "📅"
                days = appt.days_until()
                day_str = "TODAY!" if days == 0 else f"in {days} days"
                print(f"{i}. {status} {appt.title} with Dr. {appt.doctor}")
                print(f"   Date: {appt.date} ({day_str})")
                if appt.location:
                    print(f"   Location: {appt.location}")
                print()
        
        if past:
            print("📅 PAST APPOINTMENTS:")
            for i, appt in enumerate(past, 1):
                status = "✅" if appt.completed else "❌"
                days = abs(appt.days_until())
                print(f"{i}. {status} {appt.title} with Dr. {appt.doctor}")
                print(f"   Date: {appt.date} ({days} days ago)")
                print()
        
        input("Press Enter to continue...")
    
    def main_menu(self) -> None:
        """Main application menu"""
        while True:
            self.display_header()
            
            if not self.current_user:
                print("MAIN MENU")
                print("-" * 60)
                print("1. 🔐 Login")
                print("2. 📝 Register")
                print("3. 🚪 Exit")
                print("-" * 60)
                
                choice = input("Select (1-3): ").strip()
                
                if choice == "1":
                    self.login_user()
                elif choice == "2":
                    self.register_user()
                elif choice == "3":
                    print("\n👋 Thank you for using MediTrack!")
                    sys.exit(0)
                else:
                    print("❌ Invalid choice")
                    input("Press Enter to continue...")
            else:
                print(f"MAIN MENU - Welcome {self.current_user.name}")
                print("-" * 60)
                print("📊 DASHBOARD")
                print("1. 📊 View Weekly Summary")
                print("2. 🔔 Check Notifications")
                
                print("\n💊 MEDICINES")
                print("3. 💊 View All Medicines")
                print("4. ➕ Add New Medicine")
                print("5. ✅ Mark Medicine Taken")
                
                print("\n📅 APPOINTMENTS")
                print("6. 📅 View Appointments")
                print("7. ➕ Add Appointment")
                print("8. ✅ Mark Appointment Completed")
                
                print("\n⚙️  SETTINGS")
                print("9. 🔐 Change Password")
                print("10. 🚨 Emergency Mode")
                
                print("\n🔐 ACCOUNT")
                print("11. 🚪 Logout")
                print("12. 🚪 Exit Program")
                print("-" * 60)
                
                choice = input("Select (1-12): ").strip()
                
                if choice == "1":
                    self.view_weekly_summary()
                elif choice == "2":
                    self.display_header()
                    self.check_notifications()
                    input("\nPress Enter to continue...")
                elif choice == "3":
                    self.view_medicines()
                elif choice == "4":
                    self.add_medicine()
                elif choice == "5":
                    self.mark_medicine_taken()
                elif choice == "6":
                    self.view_appointments()
                elif choice == "7":
                    self.add_appointment()
                elif choice == "8":
                    self.mark_appointment_completed()
                elif choice == "9":
                    self.change_password()
                elif choice == "10":
                    self.emergency_mode()
                elif choice == "11":
                    print(f"\n👋 Goodbye {self.current_user.name}!")
                    self.current_user = None
                    input("Press Enter to continue...")
                elif choice == "12":
                    print("\n👋 Thank you for using MediTrack!")
                    sys.exit(0)
                else:
                    print("❌ Invalid choice")
                    input("Press Enter to continue...")

def main():
    app = MediTrackApp()
    app.main_menu()

if __name__ == "__main__":
    main()