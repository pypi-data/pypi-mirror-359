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
import shutil

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

    def ensure_output_dir(self):
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def export_to_yaml(self, name: str, filename: str = None):
        self.ensure_output_dir()
        data = self.get_info(name)
        if not data:
            return False
        if not filename:
            filename = os.path.join("output", f"{name}_info.yaml")
        def prettify_key(key):
            return key.replace('_', ' ').title()
        def prettify_section(data):
            if isinstance(data, dict):
                return {prettify_key(k): prettify_section(v) for k, v in data.items() if v not in (None, '', [], {})}
            elif isinstance(data, list):
                return [prettify_section(v) for v in data if v not in (None, '', [], {})]
            else:
                return data
        grouped = {
            'Personal Information': {
                'Full Name': name,
                'Date of Birth': data.get('dob', ''),
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
        grouped['Personal Information'] = {k: v for k, v in grouped['Personal Information'].items() if v not in (None, '', [], {})}
        if not grouped['Personal Information']:
            grouped.pop('Personal Information')
        if data.get('family_details') not in (None, '', [], {}):
            pretty_family = prettify_section(data['family_details'])
            if pretty_family:
                grouped['Family'] = pretty_family
        if data.get('contact_details') not in (None, '', [], {}):
            pretty_contact = prettify_section(data['contact_details'])
            if pretty_contact:
                grouped['Contact'] = pretty_contact
        if data.get('vehicle_details') not in (None, '', [], {}):
            vehicles = [prettify_section(v) for v in data['vehicle_details'] if v not in (None, '', [], {})]
            if vehicles:
                grouped['Vehicles'] = vehicles
        if data.get('education_details') not in (None, '', [], {}):
            education = [prettify_section(edu) for edu in data['education_details'] if edu not in (None, '', [], {})]
            if education:
                grouped['Education'] = education
        if data.get('professional_details') not in (None, '', [], {}):
            professional = [prettify_section(prof) for prof in data['professional_details'] if prof not in (None, '', [], {})]
            if professional:
                grouped['Professional Experience'] = professional
        if data.get('bank_details') not in (None, '', [], {}):
            bank = [prettify_section(b) for b in data['bank_details'] if b not in (None, '', [], {})]
            if bank:
                grouped['Bank Accounts'] = bank
        if not grouped:
            return False
        with open(filename, "w", encoding="utf-8") as f:
            yaml.dump(grouped, f, allow_unicode=True, sort_keys=False)
        return True

    def export_to_txt(self, name: str, filename: str = None):
        self.ensure_output_dir()
        data = self.get_info(name)
        if not data:
            return False
        if not filename:
            filename = os.path.join("output", f"{name}_info.txt")
        def prettify_key(key):
            return key.replace('_', ' ').title()
        def prettify_value(val):
            if isinstance(val, list):
                if not val:
                    return None
                if all(isinstance(v, dict) for v in val):
                    return val
                return ', '.join(str(v) for v in val)
            elif isinstance(val, dict):
                return val
            elif val not in (None, '', [], {}):
                return str(val)
            else:
                return None
        def singular_section(section_name):
            mapping = {
                'Vehicles': 'Vehicle',
                'Education': 'Education',
                'Professional Experience': 'Professional Experience',
                'Bank Accounts': 'Bank Account',
            }
            return mapping.get(section_name, section_name)
        def write_section(f, section_name, section_data):
            if not section_data:
                return
            f.write(f"=== {section_name} ===\n")
            if isinstance(section_data, dict):
                for k, v in section_data.items():
                    pretty_v = prettify_value(v)
                    if pretty_v is None:
                        continue
                    if isinstance(pretty_v, dict):
                        f.write(f"{prettify_key(k)}:\n")
                        for subk, subv in pretty_v.items():
                            sub_pretty_v = prettify_value(subv)
                            if sub_pretty_v is not None:
                                f.write(f"  {prettify_key(subk)}: {sub_pretty_v}\n")
                    elif isinstance(pretty_v, list):
                        f.write(f"{prettify_key(k)}:\n")
                        for item in pretty_v:
                            if isinstance(item, dict):
                                f.write("  - ")
                                for subk, subv in item.items():
                                    sub_pretty_v = prettify_value(subv)
                                    if sub_pretty_v is not None:
                                        f.write(f"{prettify_key(subk)}: {sub_pretty_v}; ")
                                f.write("\n")
                            else:
                                f.write(f"  - {item}\n")
                    else:
                        f.write(f"{prettify_key(k)}: {pretty_v}\n")
            elif isinstance(section_data, list):
                singular = singular_section(section_name)
                for idx, item in enumerate(section_data, 1):
                    f.write(f"{singular} {idx}:\n")
                    if isinstance(item, dict):
                        for k, v in item.items():
                            pretty_v = prettify_value(v)
                            if pretty_v is not None:
                                f.write(f"  {prettify_key(k)}: {pretty_v}\n")
                    else:
                        f.write(f"  {item}\n")
            f.write("\n")
        with open(filename, "w", encoding="utf-8") as f:
            # Personal Information
            personal_info = [
                ("Full Name", name),
                ("Date of Birth", data.get('dob', '')),
                ("Age", data.get('age', '')),
                ("Email", data.get('email', '')),
                ("Height (cm)", data.get('height_cm', '')),
                ("Weight (kg)", data.get('weight_kg', '')),
                ("BMI", data.get('bmi', '')),
                ("BMI Description", data.get('bmi_description', '')),
                ("Blood Group", data.get('blood_group', '')),
                ("Aadhar Number", data.get('aadhar_number', '')),
                ("Address", data.get('address', '')),
                ("Bio", data.get('bio', '')),
            ]
            personal_info = [(k, v) for k, v in personal_info if v not in (None, '', [], {})]
            if personal_info:
                f.write("=== Personal Information ===\n")
                for k, v in personal_info:
                    f.write(f"{k}: {v}\n")
                f.write("\n")
            # Family
            if data.get('family_details') not in (None, '', [], {}):
                pretty_family = {prettify_key(k): prettify_value(v) for k, v in data['family_details'].items() if prettify_value(v) is not None}
                write_section(f, "Family", pretty_family)
            # Contact
            if data.get('contact_details') not in (None, '', [], {}):
                pretty_contact = {prettify_key(k): prettify_value(v) for k, v in data['contact_details'].items() if prettify_value(v) is not None}
                write_section(f, "Contact", pretty_contact)
            # Vehicles
            if data.get('vehicle_details') not in (None, '', [], {}):
                vehicles = [{prettify_key(k): prettify_value(v) for k, v in veh.items() if prettify_value(v) is not None} for veh in data['vehicle_details'] if veh not in (None, '', [], {})]
                write_section(f, "Vehicles", vehicles)
            # Education
            if data.get('education_details') not in (None, '', [], {}):
                education = [{prettify_key(k): prettify_value(v) for k, v in edu.items() if prettify_value(v) is not None} for edu in data['education_details'] if edu not in (None, '', [], {})]
                write_section(f, "Education", education)
            # Professional Experience
            if data.get('professional_details') not in (None, '', [], {}):
                professional = [{prettify_key(k): prettify_value(v) for k, v in prof.items() if prettify_value(v) is not None} for prof in data['professional_details'] if prof not in (None, '', [], {})]
                write_section(f, "Professional Experience", professional)
            # Bank Accounts
            if data.get('bank_details') not in (None, '', [], {}):
                bank = [{prettify_key(k): prettify_value(v) for k, v in b.items() if prettify_value(v) is not None} for b in data['bank_details'] if b not in (None, '', [], {})]
                write_section(f, "Bank Accounts", bank)
        return True

    def export_to_excel(self, name: str, filename: str = None):
        self.ensure_output_dir()
        data = self.get_info(name)
        if not data:
            return False
        if not filename:
            filename = os.path.join("output", f"{name}_info.xlsx")
        df = pd.json_normalize(data)
        df.to_excel(filename, index=False)
        return True

    def prettify_key(self, key):
        return key.replace('_', ' ').title()

    def prettify_section(self, data):
        # Recursively prettify dict keys and skip empty/null fields
        if isinstance(data, dict):
            return {self.prettify_key(k): self.prettify_section(v) for k, v in data.items() if v not in (None, '', [], {})}
        elif isinstance(data, list):
            return [self.prettify_section(v) for v in data if v not in (None, '', [], {})]
        else:
            return data

    def export_to_html(self, name: str, filename: str = None):
        self.ensure_output_dir()
        from jinja2 import Template
        data = self.get_info(name)
        if not data:
            return False
        if not filename:
            filename = os.path.join("output", f"{name}_info.html")
        template_path = os.path.join(os.path.dirname(__file__), 'template.html')
        with open(template_path, 'r', encoding='utf-8') as tpl_file:
            template_str = tpl_file.read()
        personal_info = {
            'Full Name': name,
            'Date of Birth': data.get('dob', ''),
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
        personal_info = {k: v for k, v in personal_info.items() if v not in (None, '', [], {})}
        sections = []
        if personal_info:
            sections.append(('Personal Information', personal_info))
        if data.get('family_details') not in (None, '', [], {}):
            pretty_family = self.prettify_section(data['family_details'])
            if pretty_family:
                sections.append(('Family', pretty_family))
        if data.get('contact_details') not in (None, '', [], {}):
            pretty_contact = self.prettify_section(data['contact_details'])
            if pretty_contact:
                sections.append(('Contact', pretty_contact))
        if data.get('vehicle_details') not in (None, '', [], {}):
            vehicles = [self.prettify_section(v) for v in data['vehicle_details'] if v not in (None, '', [], {})]
            if vehicles:
                sections.append(('Vehicles', vehicles))
        if data.get('education_details') not in (None, '', [], {}):
            education = [self.prettify_section(edu) for edu in data['education_details'] if edu not in (None, '', [], {})]
            if education:
                sections.append(('Education', education))
        if data.get('professional_details') not in (None, '', [], {}):
            professional = [self.prettify_section(prof) for prof in data['professional_details'] if prof not in (None, '', [], {})]
            if professional:
                sections.append(('Professional Experience', professional))
        if data.get('bank_details') not in (None, '', [], {}):
            bank = [self.prettify_section(b) for b in data['bank_details'] if b not in (None, '', [], {})]
            if bank:
                sections.append(('Bank Accounts', bank))
        if not sections:
            return False
        template = Template(template_str)
        html = template.render(name=name, sections=sections)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        return True

    def download_html_template(self, destination_path: str = None):
        self.ensure_output_dir()
        if not destination_path:
            destination_path = os.path.join("output", "template.html")
        template_path = os.path.join(os.path.dirname(__file__), 'template.html')
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found at {template_path}")
        shutil.copyfile(template_path, destination_path)
        return destination_path
