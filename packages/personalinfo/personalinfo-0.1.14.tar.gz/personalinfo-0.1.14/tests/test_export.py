import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from personalinfo import PersonalInfoSaver, VehicleDetails

class TestPersonalInfoSaverExport(unittest.TestCase):
    def setUp(self):
        self.saver = PersonalInfoSaver(filename="test_personal_info.json")
        self.name = "TestUser"
        self.saver.save_info(
            name=self.name,
            dob="1990-01-01",
            email="test@example.com",
            height_cm=170,
            weight_kg=70,
            bio="Test bio",
            blood_group="O+",
            family_details={},
            aadhar_number="123456789012",
            address="123 Test St",
            vehicle_details=[VehicleDetails(vehicle_type="Car", make="Toyota", model="Corolla", year=2015)],
            education_details=None,
            professional_details=None,
            bank_details=None,
            contact_details={}
        )

    def tearDown(self):
        for ext in ["json", "yaml", "txt", "xlsx"]:
            fname = f"{self.name}_info.{ext}"
            if os.path.exists(fname):
                os.remove(fname)
        if os.path.exists("test_personal_info.json"):
            os.remove("test_personal_info.json")

    def test_export_to_yaml(self):
        self.assertTrue(self.saver.export_to_yaml(self.name))
        self.assertTrue(os.path.exists(f"{self.name}_info.yaml"))

    def test_export_to_txt(self):
        self.assertTrue(self.saver.export_to_txt(self.name))
        self.assertTrue(os.path.exists(f"{self.name}_info.txt"))

    def test_export_to_excel(self):
        self.assertTrue(self.saver.export_to_excel(self.name))
        self.assertTrue(os.path.exists(f"{self.name}_info.xlsx"))

if __name__ == "__main__":
    unittest.main()
