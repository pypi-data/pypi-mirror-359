# PersonalInfoSaver

A comprehensive Python utility to save and retrieve all personal, family, professional, vehicle, education, bank, and contact information to/from a local JSON file.

## 🔗 Project Homepage

For the latest updates, issues, and source code, visit the official GitHub repository:

[https://github.com/prabaharanpython/personalinfo](https://github.com/prabaharanpython/personalinfo)

## 📁 File: `personal_info.json`
This file is automatically created in the same directory to store the data in JSON format.

## ✅ Features
- Save user information: name, date of birth (dob), email, height (cm), weight (kg), bio, blood group, aadhar number, address
- Auto-calculates age from dob
- Auto-calculates BMI from height and weight
- Provides a BMI health description
- Store detailed family information (father, mother, siblings, spouse, children)
- Store detailed vehicle information (type, make, model, year, registration, insurance, mileage, engine/chassis, etc.)
- Store detailed education information (schooling, college, degree, board, years, grades, specialization, location)
- Store professional/career information (designation, company, dates, skills, responsibilities, achievements, salary, employment type)
- Store bank details (bank name, account, IFSC, branch, account type, UPI, PAN, nominee, etc.)
- Store contact and communication details (phones, emails, native, languages, addresses, social, guardian, emergency contacts)
- Retrieve saved information by name
- Automatically loads and updates the data file
- Export data to YAML, TXT, Excel, or HTML formats

## 📦 Requirements

This package requires the following dependencies:
- Python's built-in `json`, `os`, and `datetime` modules
- `pyyaml` (for YAML export)
- `pandas` (for Excel export)
- `openpyxl` (Excel engine for pandas)
- `jinja2` (for HTML export)

Install all requirements with:

```bash
pip install personalinfo pyyaml pandas openpyxl jinja2
```

## 🛠️ Usage

```bash
pip install personalinfo
```

```python
from personalinfo import PersonalInfoSaver, FamilyDetails, VehicleDetails, EducationDetails, ProfessionalDetails, BankDetails, ContactDetails

# Create vehicle details
car = VehicleDetails(
    vehicle_type="Car",
    make="Toyota",
    model="Camry",
    year=2020,
    registration_number="TN01AB1234",
    color="White",
    insurance_number="INS123456789",
    insurance_expiry="2026-05-31",
    mileage=15000.5,
    engine_number="ENG987654321",
    chassis_number="CHS123456789"
)
bike = VehicleDetails(
    vehicle_type="Bike",
    make="Honda",
    model="CBR",
    year=2018,
    registration_number="TN01XY5678",
    color="Red",
    insurance_number="INS987654321",
    insurance_expiry="2025-12-31",
    mileage=22000.0,
    engine_number="ENG123456789",
    chassis_number="CHS987654321"
)

# Create education details
schooling = EducationDetails(
    degree="SSLC",
    institution="ABC Matriculation School",
    year_of_passing=2011,
    grade="92%",
    board="State Board",
    school_name="ABC Matriculation School",
    start_year=2001,
    end_year=2011,
    location="Chennai"
)
ug = EducationDetails(
    degree="B.Tech",
    institution="IIT Madras",
    year_of_passing=2017,
    grade="8.9 CGPA",
    specialization="Computer Science",
    start_year=2013,
    end_year=2017,
    location="Chennai"
)

# Create professional details
prof = ProfessionalDetails(
    designation="Software Engineer",
    company="Google",
    start_date="2018-07-01",
    end_date="2022-12-31",
    location="Bangalore",
    skills=["Python", "ML"],
    responsibilities=["Developed ML models"],
    achievements=["Employee of the Year 2020"],
    salary=2500000.0,
    employment_type="Full-time",
    currently_working=False
)

# Create bank details
bank = BankDetails(
    bank_name="SBI",
    account_number="1234567890",
    ifsc_code="SBIN0001234",
    branch="Chennai Main",
    account_type="Savings",
    upi_id="peter@sbi",
    pan_number="ABCDE1234F",
    nominee="Lakshmi"
)

# Create contact details
contact = ContactDetails(
    phone_numbers=["+91-9876543210"],
    email_addresses=["peter@example.com"],
    native_place="Chennai",
    languages_known=["Tamil", "English"],
    communication_address="123 Main St, Chennai",
    whatsapp_number="+91-9876543210"
)

# Create family details (father as string, mother as PersonalInfoSaver)
mother = PersonalInfoSaver()
mother.save_info(
    "Lakshmi", "1972-02-02", "lakshmi@example.com", 160, 60,
    bio="Homemaker.",
    blood_group="B+",
    aadhar_number="2222-3333-4444",
    address="456 Park Ave, New York, NY",
)
family = FamilyDetails(father="Shiva", mother=mother)

# Create the saver object and save user information
saver = PersonalInfoSaver()
saver.save_info(
    "Peter", "1996-06-15", "peter@example.com", 180, 75,
    bio="Data scientist from India.",
    blood_group="B+",
    family_details=family.to_dict(),
    aadhar_number="1234-5678-9012",
    address="123 Main St, New York, NY",
    vehicle_details=[car, bike],
    education_details=[ug, schooling],
    professional_details=[prof],
    bank_details=[bank],
    contact_details=contact.to_dict()
)

# Retrieve user information
info = saver.get_info("Peter")
print(info)
# Output example:
# {
#   'dob': '1996-06-15',
#   'age': 29,
#   'email': 'peter@example.com',
#   'height_cm': 180,
#   'weight_kg': 75,
#   'bmi': 23.15,
#   'bmi_description': 'Normal weight: Keep up the good work!',
#   'bio': 'Data scientist from India.',
#   'blood_group': 'B+',
#   'family_details': { ... },
#   'aadhar_number': '1234-5678-9012',
#   'address': '123 Main St, New York, NY',
#   'vehicle_details': [ ... ],
#   'education_details': [ ... ],
#   'professional_details': [ ... ],
#   'bank_details': [ ... ],
#   'contact_details': { ... }
# }

## 📤 Exporting Data

You can easily export a user's data to YAML, TXT, Excel, or HTML with a single line:

```python
saver.export_to_yaml("Peter")   # ➡️ Creates Peter_info.yaml
saver.export_to_txt("Peter")    # ➡️ Creates Peter_info.txt
saver.export_to_excel("Peter")  # ➡️ Creates Peter_info.xlsx
saver.export_to_html("Peter")   # ➡️ Creates Peter_info.html (requires Jinja2)
```

### ✨ Example Export Outputs

#### YAML Export (`Peter_info.yaml`)
```yaml
Personal Information:
  Full Name: Peter
  Date of Birth: '1996-06-15'
  Age: 29
  Email: peter@example.com
  Height (cm): 180
  Weight (kg): 75
  BMI: 23.15
  BMI Description: Normal weight: Keep up the good work!
  Blood Group: B+
  Aadhar Number: 1234-5678-9012
  Address: 123 Main St, New York, NY
  Bio: Data scientist from India.
Family:
  Father: Shiva
  Mother:
    Full Name: Lakshmi
    Date of Birth: '1972-02-02'
    ...
Contact:
  Phone Numbers:
    - +91-9876543210
  Email Addresses:
    - peter@example.com
  Native Place: Chennai
  Languages Known:
    - Tamil
    - English
  Communication Address: 123 Main St, Chennai
Vehicles:
  - Vehicle Type: Car
    Make: Toyota
    Model: Camry
    Year: 2020
    ...
Education:
  - Degree: B.Tech
    Institution: IIT Madras
    Year Of Passing: 2017
    ...
Professional Experience:
  - Designation: Software Engineer
    Company: Google
    Start Date: 2018-07-01
    ...
Bank Accounts:
  - Bank Name: SBI
    Account Number: 1234567890
    ...
```

#### TXT Export (`Peter_info.txt`)
```
=== Personal Information ===
Full Name: Peter
Date of Birth: 1996-06-15
Age: 29
Email: peter@example.com
Height (cm): 180
Weight (kg): 75
BMI: 23.15
BMI Description: Normal weight: Keep up the good work!
Blood Group: B+
Aadhar Number: 1234-5678-9012
Address: 123 Main St, New York, NY
Bio: Data scientist from India.

=== Family ===
Father: Shiva
Mother:
  Full Name: Lakshmi
  Date of Birth: 1972-02-02
  ...

=== Contact ===
Phone Numbers: +91-9876543210
Email Addresses: peter@example.com
Native Place: Chennai
Languages Known: Tamil, English
Communication Address: 123 Main St, Chennai

=== Vehicles ===
Vehicle 1:
  Vehicle Type: Car
  Make: Toyota
  Model: Camry
  Year: 2020
  ...

=== Education ===
Education 1:
  Degree: B.Tech
  Institution: IIT Madras
  Year Of Passing: 2017
  ...

=== Professional Experience ===
Professional Experience 1:
  Designation: Software Engineer
  Company: Google
  Start Date: 2018-07-01
  ...

=== Bank Accounts ===
Bank Account 1:
  Bank Name: SBI
  Account Number: 1234567890
  ...
```

#### 🌐 HTML Export
The HTML export uses a beautiful, modern template with sections, icons, and a download-to-PDF button. You can fully customize the template at `src/personalinfo/template.html`.


**Note:**
- The HTML export requires the `jinja2` package. Install it with:
  ```bash
  pip install jinja2
  ```
- If you see a `jinja2.exceptions.UndefinedError: 'enumerate' is undefined`, update your template as shown in the latest package version (see `src/personalinfo/template.html`).

---

MIT License
