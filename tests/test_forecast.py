import unittest
from datetime import date, timedelta
import sys
import os

# Ensure the 'data' module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.forecast import project_cashflow


class TestForecastScenarios(unittest.TestCase):
    
    def setUp(self):
        # We generate test dates relative to today's date dynamically, 
        # so the test works identically no matter when it's run.
        self.today = date.today()
        self.day_1 = (self.today + timedelta(days=1)).isoformat()
        self.day_2 = (self.today + timedelta(days=2)).isoformat()
        self.day_3 = (self.today + timedelta(days=3)).isoformat()
        self.day_4 = (self.today + timedelta(days=4)).isoformat()
        self.day_5 = (self.today + timedelta(days=5)).isoformat()

    def test_scenario_1_normal_week(self):
        print("\n" + "="*50)
        print("SCENARIO 1: Normal Week")
        print("Expected: Balance declines when invoices are paid, grows when receivables arrive.")
        print("="*50)
        
        cash = 50000.0
        invoices = [
            {"id": "INV1", "amount": 10000.0, "due_date": self.day_2},
            {"id": "INV2", "amount": 5000.0, "due_date": self.day_4}
        ]
        receivables = [
            {"id": "REC1", "amount": 15000.0, "expected_date": self.day_3, "delay_probability": 0.0} 
        ]
        
        projection = project_cashflow(cash, invoices, receivables, days=5)
        for p in projection:
            print(f"{p['date']}: Balance ${p['projected_balance']:,.2f}")
            
        # Assertions
        self.assertEqual(projection[0]["projected_balance"], 50000.0)
        self.assertEqual(projection[1]["projected_balance"], 40000.0) # 50k - 10k
        self.assertEqual(projection[2]["projected_balance"], 55000.0) # 40k + 15k
        self.assertEqual(projection[3]["projected_balance"], 50000.0) # 55k - 5k
        self.assertEqual(projection[4]["projected_balance"], 50000.0)

    def test_scenario_2_delayed_receivable(self):
        print("\n" + "="*50)
        print("SCENARIO 2: Big Receivable with High Delay Risk")
        print("Expected: High probability of delay (80%) severely reduces expected cash inflow, causing later shortfall.")
        print("="*50)
        
        cash = 10000.0
        invoices = [
            {"id": "INV1", "amount": 25000.0, "due_date": self.day_4}
        ]
        receivables = [
            {"id": "REC1", "amount": 40000.0, "expected_date": self.day_2, "delay_probability": 0.8} # 80% risk!
        ]
        
        projection = project_cashflow(cash, invoices, receivables, days=5)
        for p in projection:
            print(f"{p['date']}: Balance ${p['projected_balance']:,.2f}")
            
        # Assertions
        # 80% risk means we only confidently expect 20% of 40k = 8k
        self.assertEqual(projection[0]["projected_balance"], 10000.0)
        self.assertEqual(projection[1]["projected_balance"], 18000.0) # 10k + 8k
        self.assertEqual(projection[2]["projected_balance"], 18000.0)
        self.assertEqual(projection[3]["projected_balance"], -7000.0) # 18k - 25k (Shortfall!)
        self.assertEqual(projection[4]["projected_balance"], -7000.0)

    def test_scenario_3_shortfall(self):
        print("\n" + "="*50)
        print("SCENARIO 3: Obligations > Cash Available")
        print("Expected: Function doesn't crash, and correctly projects a negative balance (shortfall).")
        print("="*50)
        
        cash = 5000.0
        invoices = [
            {"id": "INV1", "amount": 20000.0, "due_date": self.day_1},
            {"id": "INV2", "amount": 10000.0, "due_date": self.day_3}
        ]
        receivables = []
        
        projection = project_cashflow(cash, invoices, receivables, days=4)
        for p in projection:
            print(f"{p['date']}: Balance ${p['projected_balance']:,.2f}")
            
        # Assertions
        self.assertEqual(projection[0]["projected_balance"], -15000.0) # 5k - 20k
        self.assertEqual(projection[1]["projected_balance"], -15000.0)
        self.assertEqual(projection[2]["projected_balance"], -25000.0) # -15k - 10k
        self.assertEqual(projection[3]["projected_balance"], -25000.0)

if __name__ == '__main__':
    unittest.main()
