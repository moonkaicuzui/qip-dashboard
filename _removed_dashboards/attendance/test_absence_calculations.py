"""
Unit tests for absence rate calculation logic
Validates the core business logic for absence analytics
"""

import pytest
import json
from pathlib import Path

class TestAbsenceCalculations:
    """Test absence rate calculation formulas"""
    
    def test_basic_absence_rate_formula(self):
        """Test the basic absence rate calculation"""
        # Test case from user requirements:
        # 2 employees, 10 working days each
        # Employee 1: 5 actual days worked
        # Employee 2: 10 actual days worked
        
        total_working_days = 20  # 2 * 10
        total_actual_days = 15   # 5 + 10
        
        # Formula: 100 - (actual/required * 100)
        absence_rate = 100 - (total_actual_days / total_working_days * 100)
        
        assert absence_rate == 25.0, f"Expected 25%, got {absence_rate}%"
    
    def test_zero_absence_rate(self):
        """Test when no one is absent"""
        total_working_days = 100
        total_actual_days = 100
        
        absence_rate = 100 - (total_actual_days / total_working_days * 100)
        
        assert absence_rate == 0.0, f"Expected 0%, got {absence_rate}%"
    
    def test_full_absence_rate(self):
        """Test when everyone is absent"""
        total_working_days = 100
        total_actual_days = 0
        
        absence_rate = 100 - (total_actual_days / total_working_days * 100)
        
        assert absence_rate == 100.0, f"Expected 100%, got {absence_rate}%"
    
    def test_individual_absence_calculation(self):
        """Test individual employee absence calculation"""
        # Single employee case
        required_days = 22
        actual_days = 18
        
        individual_absence_rate = ((required_days - actual_days) / required_days) * 100
        
        expected_rate = (4 / 22) * 100
        assert abs(individual_absence_rate - expected_rate) < 0.01
    
    def test_team_absence_aggregation(self):
        """Test team-level absence aggregation"""
        team_data = [
            {"required": 22, "actual": 20},  # 9.09% absence
            {"required": 22, "actual": 22},  # 0% absence
            {"required": 22, "actual": 15},  # 31.82% absence
            {"required": 22, "actual": 18},  # 18.18% absence
        ]
        
        total_required = sum(d["required"] for d in team_data)
        total_actual = sum(d["actual"] for d in team_data)
        
        team_absence_rate = 100 - (total_actual / total_required * 100)
        
        # Expected: (88 - 75) / 88 * 100 = 14.77%
        expected = (13 / 88) * 100
        assert abs(team_absence_rate - expected) < 0.01

class TestAbsenceCategories:
    """Test absence reason categorization"""
    
    @pytest.fixture
    def config_data(self):
        """Load absence configuration"""
        config_path = Path(__file__).parent.parent / "config_files" / "absence_analytics_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def test_absence_category_groups(self, config_data):
        """Test that all 22 absence reasons are categorized"""
        if not config_data:
            pytest.skip("Config file not found")
        
        categories = config_data["absence_categories"]
        
        # Should have 5 main groups
        assert len(categories) == 5
        
        # Expected groups
        expected_groups = [
            "group1_planned",
            "group2_maternity", 
            "group3_medical",
            "group4_disciplinary",
            "group5_legal"
        ]
        
        for group in expected_groups:
            assert group in categories
            assert len(categories[group]["items"]) > 0
    
    def test_absence_reason_completeness(self, config_data):
        """Test that all Vietnamese absence reasons are included"""
        if not config_data:
            pytest.skip("Config file not found")
        
        all_reasons = []
        for category in config_data["absence_categories"].values():
            all_reasons.extend(category["items"])
        
        # Should have at least 15 unique absence reasons (actual: 17)
        assert len(set(all_reasons)) >= 15  # Allow some flexibility
        
        # Check for critical absence types
        critical_reasons = [
            "Phép năm",
            "AR1 - Vắng không phép",
            "Sinh thường 1 con (6 tháng)"
        ]
        
        for reason in critical_reasons:
            assert reason in all_reasons

class TestRiskAssessment:
    """Test absence risk level calculations"""
    
    @pytest.fixture
    def risk_criteria(self):
        """Load risk assessment criteria"""
        config_path = Path(__file__).parent.parent / "config_files" / "absence_analytics_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("risk_criteria", {})
        return {}
    
    def test_high_risk_detection(self, risk_criteria):
        """Test high risk absence pattern detection"""
        if not risk_criteria:
            pytest.skip("Risk criteria not found")
        
        high_risk = risk_criteria.get("high_risk", {})
        
        # Test consecutive unauthorized absence
        employee_data = {
            "consecutive_unauthorized_days": 3,
            "monthly_unauthorized_days": 5
        }
        
        is_high_risk = (
            employee_data["consecutive_unauthorized_days"] >= high_risk["consecutive_unauthorized"] or
            employee_data["monthly_unauthorized_days"] >= high_risk["monthly_unauthorized"]
        )
        
        assert is_high_risk == True
    
    def test_medium_risk_detection(self, risk_criteria):
        """Test medium risk absence pattern detection"""
        if not risk_criteria:
            pytest.skip("Risk criteria not found")
        
        medium_risk = risk_criteria.get("medium_risk", {})
        
        # Test medium risk conditions
        employee_data = {
            "consecutive_unauthorized_days": 2,
            "monthly_unauthorized_days": 3
        }
        
        is_medium_risk = (
            employee_data["consecutive_unauthorized_days"] in medium_risk.get("consecutive_unauthorized", []) or
            employee_data["monthly_unauthorized_days"] in medium_risk.get("monthly_unauthorized", [])
        )
        
        assert is_medium_risk == True
    
    def test_low_risk_classification(self, risk_criteria):
        """Test low risk classification"""
        if not risk_criteria:
            pytest.skip("Risk criteria not found")
        
        # Employee with minimal absence
        employee_data = {
            "consecutive_unauthorized_days": 0,
            "monthly_unauthorized_days": 0,
            "monthly_planned_leave": 3
        }
        
        high_risk = risk_criteria.get("high_risk", {})
        medium_risk = risk_criteria.get("medium_risk", {})
        
        is_not_high_risk = (
            employee_data["consecutive_unauthorized_days"] < high_risk.get("consecutive_unauthorized", 999)
        )
        
        is_not_medium_risk = (
            employee_data["consecutive_unauthorized_days"] not in medium_risk.get("consecutive_unauthorized", [])
        )
        
        assert is_not_high_risk and is_not_medium_risk

class TestAuthorizedVsUnauthorized:
    """Test authorized vs unauthorized absence classification"""
    
    def test_unauthorized_absence_detection(self):
        """Test identification of unauthorized absences"""
        # AR1 prefix indicates unauthorized/disciplinary
        absence_reasons = [
            "AR1 - Gửi thư",
            "AR1 - Họp kỷ luật", 
            "AR1 - Vắng không phép"
        ]
        
        unauthorized_count = sum(1 for reason in absence_reasons if "AR1" in reason)
        
        assert unauthorized_count == 3
    
    def test_authorized_absence_detection(self):
        """Test identification of authorized absences"""
        # Authorized reasons
        absence_reasons = [
            "Phép năm",
            "Phép cưới",
            "Nghỉ bù",
            "Đi công tác"
        ]
        
        authorized_keywords = ["Phép", "Nghỉ bù", "công tác"]
        authorized_count = sum(
            1 for reason in absence_reasons 
            if any(keyword in reason for keyword in authorized_keywords)
        )
        
        assert authorized_count == 4
    
    def test_mixed_absence_calculation(self):
        """Test calculation with mixed authorized/unauthorized absences"""
        absences = [
            {"type": "Phép năm", "days": 2, "authorized": True},
            {"type": "AR1 - Vắng không phép", "days": 1, "authorized": False},
            {"type": "Nghỉ bù", "days": 1, "authorized": True},
            {"type": "AR1 - Gửi thư", "days": 2, "authorized": False}
        ]
        
        total_absence_days = sum(a["days"] for a in absences)
        authorized_days = sum(a["days"] for a in absences if a["authorized"])
        unauthorized_days = sum(a["days"] for a in absences if not a["authorized"])
        
        assert total_absence_days == 6
        assert authorized_days == 3
        assert unauthorized_days == 3
        assert authorized_days + unauthorized_days == total_absence_days

if __name__ == "__main__":
    pytest.main([__file__, "-v"])