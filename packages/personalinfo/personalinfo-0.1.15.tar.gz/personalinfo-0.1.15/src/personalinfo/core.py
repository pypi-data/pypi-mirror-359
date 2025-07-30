"""
PersonalInfoSaver main class for personal information management.
"""
import json
import os
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union
from .vehicle import VehicleDetails
from .education import EducationDetails
from .family import FamilyDetails
from .professional import ProfessionalDetails
from .bank import BankDetails
from .contact import ContactDetails
import yaml
import csv
import pandas as pd

class PersonalInfoSaver:
    def __init__(self, filename: str = "personal_info.json"):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return {}

    def calculate_age(self, dob: str) -> int:
        birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    def calculate_bmi(self, height_cm: float, weight_kg: float) -> float:
        height_m = height_cm / 100
        if height_m <= 0:
            return 0.0
        return round(weight_kg / (height_m ** 2), 2)

    def bmi_description(self, bmi: float) -> str:
        if bmi < 18.5:
            return "Underweight: Consider a nutritious diet."
        elif 18.5 <= bmi < 25:
            return "Normal weight: Keep up the good work!"
        elif 25 <= bmi < 30:
            return "Overweight: Consider regular exercise."
        else:
            return "Obese: Consult a healthcare provider."

    def save_info(
        self,
        name: str,
        dob: str,
        email: str,
        height_cm: float,
        weight_kg: float,
        bio: str = "",
        blood_group: str = "",
        family_details: dict = None,
        aadhar_number: str = "",
        address: str = "",
        vehicle_details: Optional[List[Union[VehicleDetails, dict]]] = None,
        education_details: Optional[List[Union[EducationDetails, dict]]] = None,
        professional_details: Optional[List[Union[ProfessionalDetails, dict]]] = None,
        bank_details: Optional[List[Union[BankDetails, dict]]] = None,
        contact_details: dict = None
    ):
        age = self.calculate_age(dob)
        bmi = self.calculate_bmi(height_cm, weight_kg)
        bmi_desc = self.bmi_description(bmi)
        if family_details is None:
            family_details = {}
        if vehicle_details is None:
            vehicle_details = []
        if contact_details is None:
            contact_details = {}
        data = {
            "dob": dob,
            "age": age,
            "email": email,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi,
            "bmi_description": bmi_desc,
            "bio": bio,
            "blood_group": blood_group,
            "family_details": family_details,
            "aadhar_number": aadhar_number,
            "address": address,
            "vehicle_details": [v.to_dict() if isinstance(v, VehicleDetails) else v for v in vehicle_details],
            "contact_details": contact_details
        }
        if education_details:
            def get_sort_year(e):
                if isinstance(e, EducationDetails):
                    return e.end_year or e.year_of_passing or 0
                return e.get("end_year") or e.get("year_of_passing") or 0
            sorted_edu = sorted(education_details, key=get_sort_year, reverse=True)
            data["education_details"] = [e.to_dict() if isinstance(e, EducationDetails) else e for e in sorted_edu]
        if professional_details:
            def get_sort_prof(e):
                if isinstance(e, ProfessionalDetails):
                    return e.end_date or e.start_date or ""
                return e.get("end_date") or e.get("start_date") or ""
            sorted_prof = sorted(professional_details, key=get_sort_prof, reverse=True)
            data["professional_details"] = [p.to_dict() if isinstance(p, ProfessionalDetails) else p for p in sorted_prof]
        if bank_details:
            data["bank_details"] = [b.to_dict() if isinstance(b, BankDetails) else b for b in bank_details]
        self.data[name] = data
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_info(self, name: str) -> Optional[Dict[str, Any]]:
        return self.data.get(name, None)

    def export_to_yaml(self, name: str, filename: str = None):
        """Export the user's data to a YAML file with grouped sections."""
        data = self.get_info(name)
        if not data:
            return False
        if not filename:
            filename = f"{name}_info.yaml"
        # Grouped structure for YAML
        grouped = {
            'Generic Info': {
                'Full Name': name,
                'DOB': data.get('dob', ''),
                'Age': data.get('age', ''),
                'Email': data.get('email', ''),
                'Height (cm)': data.get('height_cm', ''),
                'Weight (kg)': data.get('weight_kg', ''),
                'BMI': data.get('bmi', ''),
                'BMI Description': data.get('bmi_description', ''),
                'Blood Group': data.get('blood_group', ''),
                'Aadhar Number': data.get('aadhar_number', ''),
                'Address': data.get('address', ''),
                'Bio': data.get('bio', ''),
            }
        }
        if data.get('family_details'):
            grouped['Family Details'] = data['family_details']
        if data.get('contact_details'):
            grouped['Contact Details'] = data['contact_details']
        if data.get('vehicle_details'):
            grouped['Vehicle Details'] = data['vehicle_details']
        if data.get('education_details'):
            grouped['Education Details'] = data['education_details']
        if data.get('professional_details'):
            grouped['Professional Details'] = data['professional_details']
        if data.get('bank_details'):
            grouped['Bank Details'] = data['bank_details']
        with open(filename, "w", encoding="utf-8") as f:
            yaml.dump(grouped, f, allow_unicode=True, sort_keys=False)
        return True

    def export_to_txt(self, name: str, filename: str = None):
        """Export the user's data to a plain text file with grouped sections."""
        data = self.get_info(name)
        if not data:
            return False
        if not filename:
            filename = f"{name}_info.txt"
        with open(filename, "w", encoding="utf-8") as f:
            # Generic Info
            f.write("=== Generic Info ===\n")
            f.write(f"Full Name: {name}\n")
            f.write(f"DOB: {data.get('dob', '')}\n")
            f.write(f"Age: {data.get('age', '')}\n")
            f.write(f"Email: {data.get('email', '')}\n")
            f.write(f"Height (cm): {data.get('height_cm', '')}\n")
            f.write(f"Weight (kg): {data.get('weight_kg', '')}\n")
            f.write(f"BMI: {data.get('bmi', '')}\n")
            f.write(f"BMI Description: {data.get('bmi_description', '')}\n")
            f.write(f"Blood Group: {data.get('blood_group', '')}\n")
            f.write(f"Aadhar Number: {data.get('aadhar_number', '')}\n")
            f.write(f"Address: {data.get('address', '')}\n")
            f.write(f"Bio: {data.get('bio', '')}\n\n")

            # Family Details
            if data.get('family_details'):
                f.write("=== Family Details ===\n")
                for k, v in data['family_details'].items():
                    f.write(f"{k}: {v}\n")
                f.write("\n")

            # Contact Details
            if data.get('contact_details'):
                f.write("=== Contact Details ===\n")
                for k, v in data['contact_details'].items():
                    f.write(f"{k}: {v}\n")
                f.write("\n")

            # Vehicle Details
            if data.get('vehicle_details'):
                f.write("=== Vehicle Details ===\n")
                for idx, v in enumerate(data['vehicle_details'], 1):
                    f.write(f"Vehicle {idx}:\n")
                    for k, val in v.items():
                        f.write(f"  {k}: {val}\n")
                f.write("\n")

            # Education Details
            if data.get('education_details'):
                f.write("=== Education Details ===\n")
                for idx, edu in enumerate(data['education_details'], 1):
                    f.write(f"Education {idx}:\n")
                    for k, val in edu.items():
                        f.write(f"  {k}: {val}\n")
                f.write("\n")

            # Professional Details
            if data.get('professional_details'):
                f.write("=== Professional Details ===\n")
                for idx, prof in enumerate(data['professional_details'], 1):
                    f.write(f"Professional {idx}:\n")
                    for k, val in prof.items():
                        f.write(f"  {k}: {val}\n")
                f.write("\n")

            # Bank Details
            if data.get('bank_details'):
                f.write("=== Bank Details ===\n")
                for idx, bank in enumerate(data['bank_details'], 1):
                    f.write(f"Bank {idx}:\n")
                    for k, val in bank.items():
                        f.write(f"  {k}: {val}\n")
                f.write("\n")
        return True

    def export_to_excel(self, name: str, filename: str = None):
        """Export the user's data to an Excel file."""
        data = self.get_info(name)
        if not data:
            return False
        if not filename:
            filename = f"{name}_info.xlsx"
        df = pd.json_normalize(data)
        df.to_excel(filename, index=False)
        return True

    def export_to_html(self, name: str, filename: str = None):
        """Export the user's data to an HTML file using a Jinja2 template file."""
        from jinja2 import Template
        data = self.get_info(name)
        if not data:
            return False
        if not filename:
            filename = f"{name}_info.html"
        template_path = os.path.join(os.path.dirname(__file__), 'template.html')
        with open(template_path, 'r', encoding='utf-8') as tpl_file:
            template_str = tpl_file.read()
        generic_info = {
            'Full Name': name,
            'DOB': data.get('dob', ''),
            'Age': data.get('age', ''),
            'Email': data.get('email', ''),
            'Height (cm)': data.get('height_cm', ''),
            'Weight (kg)': data.get('weight_kg', ''),
            'BMI': data.get('bmi', ''),
            'BMI Description': data.get('bmi_description', ''),
            'Blood Group': data.get('blood_group', ''),
            'Aadhar Number': data.get('aadhar_number', ''),
            'Address': data.get('address', ''),
            'Bio': data.get('bio', ''),
        }
        sections = [
            ('Generic Info', generic_info),
            ('Family Details', data.get('family_details')),
            ('Contact Details', data.get('contact_details')),
            ('Vehicle Details', data.get('vehicle_details')),
            ('Education Details', data.get('education_details')),
            ('Professional Details', data.get('professional_details')),
            ('Bank Details', data.get('bank_details')),
        ]
        template = Template(template_str)
        html = template.render(name=name, sections=sections)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        return True
