import os
import pytest
from personalinfo.core import PersonalInfoSaver

def test_export_to_html(tmp_path):
    # Setup
    saver = PersonalInfoSaver(filename=os.path.join(tmp_path, 'test.json'))
    name = "John Doe"
    saver.save_info(
        name=name,
        dob="1990-01-01",
        email="john@example.com",
        height_cm=180,
        weight_kg=75,
        bio="A sample bio.",
        blood_group="O+",
        family_details={"Spouse": "Jane Doe", "Child": "Baby Doe"},
        aadhar_number="1234-5678-9012",
        address="123 Main St, City",
        vehicle_details=[{"Type": "Car", "Model": "Toyota"}],
        education_details=[{"Degree": "BSc", "Year": 2012}],
        professional_details=[{"Company": "Acme Corp", "Role": "Engineer"}],
        bank_details=[{"Bank": "BankName", "Account": "123456"}],
        contact_details={"Phone": "1234567890"}
    )
    html_file = os.path.join(tmp_path, f"{name}_info.html")
    # Act
    result = saver.export_to_html(name, filename=html_file)
    # Assert
    assert result is True
    assert os.path.exists(html_file)
    with open(html_file, encoding="utf-8") as f:
        html = f.read()
        assert "John Doe" in html
        assert "Generic Info" in html
        assert "Family Details" in html
        assert "Acme Corp" in html
        assert "Toyota" in html
        assert "1234567890" in html
        assert "BankName" in html


if __name__ == "__main__":
    unittest.main()
