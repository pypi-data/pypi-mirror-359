try:
    from src.personalinfo import PersonalInfoSaver, FamilyDetails, VehicleDetails, EducationDetails, ProfessionalDetails, BankDetails, ContactDetails
except ImportError:
    from personalinfo import PersonalInfoSaver, ContactDetails, BankDetails, EducationDetails, FamilyDetails, ProfessionalDetails, VehicleDetails

import os

def main():
    # Create contact information
    contact = ContactDetails(
        phone_numbers=["123-456-7890"],
        email_addresses=["john@example.com"],
        native_place="Hometown",
        languages_known=["English", "Hindi"],
        communication_address="123 Main St, City, Country",
        linkedin="john-linkedin",
        facebook="john-facebook"
    )

    # Create bank account information
    bank = BankDetails(
        bank_name="Bank of Example",
        account_number="123456789",
        ifsc_code="EXAMP001",
        branch="Main Branch",
        account_type="Savings",
        upi_id="john@upi",
        pan_number="ABCDE1234F"
    )

    # Create education information
    education = EducationDetails(
        degree="B.Sc",
        institution="Example University",
        year_of_passing=2020,
        grade="A",
        specialization="Computer Science",
        board="State Board",
        school_name="Example School",
        start_year=2016,
        end_year=2020,
        location="City"
    )

    # Create family member information
    family = FamilyDetails(father="John Sr.", mother="Jane Sr.", siblings=["Jake"], spouse="Jane Doe", children=["Junior"]) 

    # Create professional information
    professional = ProfessionalDetails(
        designation="Engineer",
        company="Example Corp",
        start_date="2020-01-01",
        end_date="Present",
        location="City",
        skills=["Python", "Data Analysis"],
        responsibilities=["Development", "Testing"],
        achievements=["Employee of the Month"],
        salary=100000.0,
        employment_type="Full-time",
        currently_working=True
    )

    # Create vehicle information
    vehicle = VehicleDetails(
        vehicle_type="Car",
        make="Brand",
        model="Sedan",
        year=2018,
        registration_number="XYZ 1234",
        color="Red",
        insurance_number="INS123456",
        insurance_expiry="2026-01-01",
        mileage=15000.0,
        engine_number="EN123456",
        chassis_number="CH123456"
    )

    # Save all info using PersonalInfoSaver
    saver = PersonalInfoSaver("personal_info.json")
    saver.save_info(
        name="John Doe",
        dob="1990-01-01",
        email="john@example.com",
        height_cm=180,
        weight_kg=75,
        bio="Software engineer with a passion for open source.",
        blood_group="O+",
        family_details=family.to_dict(),
        aadhar_number="1234-5678-9012",
        address="123 Main St, City, Country",
        vehicle_details=[vehicle],
        education_details=[education],
        professional_details=[professional],
        bank_details=[bank],
        contact_details=contact.to_dict()
    )

    # Retrieve and print all info
    info = saver.get_info("John Doe")
    print("All Info:", info)

    # Ensure output directory exists
    output_dir = "extracted_info"
    os.makedirs(output_dir, exist_ok=True)

    # Export to YAML, TXT, Excel, and HTML in output directory
    saver.export_to_yaml("John Doe", os.path.join(output_dir, "John Doe_info.yaml"))
    saver.export_to_txt("John Doe", os.path.join(output_dir, "John Doe_info.txt"))
    saver.export_to_excel("John Doe", os.path.join(output_dir, "John Doe_info.xlsx"))
    saver.export_to_html("John Doe", os.path.join(output_dir, "John Doe_info.html"))
    print("Exported to YAML, TXT, Excel, and HTML in output directory.")

if __name__ == "__main__":
    main()
