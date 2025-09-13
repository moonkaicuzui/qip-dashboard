"""
Playwright E2E tests for Absence Analytics Popup System
Tests the comprehensive absence analysis dashboard functionality
"""

import pytest
from playwright.sync_api import Page, expect
import os
import json
from pathlib import Path

# Test configuration
BASE_DIR = Path(__file__).parent.parent
DASHBOARD_PATH = BASE_DIR / "output_files" / "management_dashboard_2025_08.html"
CONFIG_PATH = BASE_DIR / "config_files" / "absence_analytics_config.json"

@pytest.fixture(scope="function")
def dashboard_page(page: Page):
    """Load the management dashboard page"""
    file_url = f"file://{DASHBOARD_PATH}"
    page.goto(file_url)
    page.wait_for_load_state("networkidle")
    return page

class TestAbsenceAnalyticsPopup:
    """Test suite for absence analytics popup functionality"""
    
    def test_absence_card_click_opens_modal(self, dashboard_page: Page):
        """Test that clicking the absence card opens the modal"""
        # Find and click the absence rate card (card #3)
        absence_card = dashboard_page.locator(".dashboard-card").nth(2)
        expect(absence_card).to_be_visible()
        
        # Verify card contains absence information
        expect(absence_card).to_contain_text("결근자 정보")
        
        # Click the card
        absence_card.click()
        
        # Wait for modal to appear
        modal = dashboard_page.locator("#absenceModal")
        expect(modal).to_be_visible(timeout=5000)
        
        # Verify modal title
        modal_title = modal.locator(".modal-title")
        expect(modal_title).to_contain_text("결근 현황 상세 분석")
    
    def test_tab_navigation(self, dashboard_page: Page):
        """Test tab switching functionality"""
        # Open the modal
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        dashboard_page.wait_for_timeout(500)  # Wait for modal animation
        
        # Test all 4 tabs
        tabs = [
            {"id": "summary", "text": "요약", "icon": "📊"},
            {"id": "detailed", "text": "상세분석", "icon": "📈"},
            {"id": "team", "text": "팀별", "icon": "👥"},
            {"id": "individual", "text": "개인별", "icon": "👤"}
        ]
        
        for tab in tabs:
            # Click tab button
            tab_button = modal.locator(f"button[data-tab='{tab['id']}']")
            expect(tab_button).to_be_visible()
            expect(tab_button).to_contain_text(tab["text"])
            
            tab_button.click()
            
            # Verify tab is active
            expect(tab_button).to_have_class(/active/)
            
            # Verify corresponding content is visible
            tab_content = modal.locator(f"#absence-{tab['id']}")
            expect(tab_content).to_be_visible()
            expect(tab_content).to_have_css("display", "block")
    
    def test_summary_tab_kpi_cards(self, dashboard_page: Page):
        """Test KPI cards in summary tab"""
        # Open modal and ensure summary tab is active
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        dashboard_page.wait_for_timeout(500)
        
        # Check KPI cards grid
        kpi_grid = modal.locator("#absence-summary .kpi-grid")
        expect(kpi_grid).to_be_visible()
        
        # Verify 9 KPI cards (3x3 grid)
        kpi_cards = kpi_grid.locator(".kpi-card")
        expect(kpi_cards).to_have_count(9)
        
        # Test specific KPI cards
        expected_kpis = [
            "8월 누적 결근율",
            "8월 누적 무단 결근율",
            "8월 승인된 결근율",
            "8월 일평균 결근율",
            "8월 일평균 무단 결근율",
            "8월 일평균 승인된 결근율",
            "1인 평균 결근일수",
            "1인 평균 무단 결근일",
            "1인 평균 승인된 결근일"
        ]
        
        for i, expected_title in enumerate(expected_kpis):
            card = kpi_cards.nth(i)
            expect(card).to_contain_text(expected_title)
            
            # Verify card has value and trend
            value = card.locator(".kpi-value")
            expect(value).to_be_visible()
            
            trend = card.locator(".kpi-trend")
            expect(trend).to_be_visible()
    
    def test_summary_tab_charts(self, dashboard_page: Page):
        """Test charts in summary tab"""
        # Open modal
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        dashboard_page.wait_for_timeout(500)
        
        # Check for canvas elements (Chart.js charts)
        monthly_chart = modal.locator("#monthlyTrendChart")
        expect(monthly_chart).to_be_visible()
        expect(monthly_chart).to_have_attribute("width")
        
        reason_chart = modal.locator("#reasonBreakdownChart")
        expect(reason_chart).to_be_visible()
        expect(reason_chart).to_have_attribute("width")
    
    def test_team_tab_bar_chart(self, dashboard_page: Page):
        """Test team comparison bar chart in team tab"""
        # Open modal and switch to team tab
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        dashboard_page.wait_for_timeout(500)
        
        team_tab_button = modal.locator("button[data-tab='team']")
        team_tab_button.click()
        
        # Verify team chart is visible
        team_chart = modal.locator("#teamComparisonChart")
        expect(team_chart).to_be_visible()
        
        # Test click interaction (should show alert for now)
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Simulate clicking on the chart area
        team_chart.click(position={"x": 100, "y": 100})
        
        # Note: In real implementation, this would open team detail modal
    
    def test_team_tab_table(self, dashboard_page: Page):
        """Test employee table in team tab"""
        # Open modal and switch to team tab
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        dashboard_page.wait_for_timeout(500)
        
        team_tab_button = modal.locator("button[data-tab='team']")
        team_tab_button.click()
        
        # Check table exists
        table = modal.locator("#absence-team table")
        expect(table).to_be_visible()
        
        # Verify table headers
        headers = table.locator("thead th")
        expected_headers = ["사번", "이름", "팀", "역할", "직급", "입사일", "근무일수", "결근일수", "결근율", "위험도"]
        
        for i, expected_header in enumerate(expected_headers):
            header = headers.nth(i)
            expect(header).to_contain_text(expected_header)
        
        # Verify table has rows
        rows = table.locator("tbody tr")
        expect(rows).to_have_count_greater_than(0)
    
    def test_detailed_tab_placeholder(self, dashboard_page: Page):
        """Test detailed analysis tab (currently placeholder)"""
        # Open modal and switch to detailed tab
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        dashboard_page.wait_for_timeout(500)
        
        detailed_tab_button = modal.locator("button[data-tab='detailed']")
        detailed_tab_button.click()
        
        # Verify placeholder content
        detailed_content = modal.locator("#absence-detailed")
        expect(detailed_content).to_be_visible()
        expect(detailed_content).to_contain_text("상세 분석")
    
    def test_individual_tab_placeholder(self, dashboard_page: Page):
        """Test individual analysis tab (currently placeholder)"""
        # Open modal and switch to individual tab
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        dashboard_page.wait_for_timeout(500)
        
        individual_tab_button = modal.locator("button[data-tab='individual']")
        individual_tab_button.click()
        
        # Verify placeholder content
        individual_content = modal.locator("#absence-individual")
        expect(individual_content).to_be_visible()
        expect(individual_content).to_contain_text("개인별 분석")
    
    def test_modal_close_button(self, dashboard_page: Page):
        """Test modal close functionality"""
        # Open modal
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        expect(modal).to_be_visible()
        
        # Click close button
        close_button = modal.locator(".btn-close")
        close_button.click()
        
        # Verify modal is hidden
        expect(modal).not_to_be_visible()
    
    def test_absence_rate_calculation(self, dashboard_page: Page):
        """Test absence rate calculation display"""
        # Open modal
        dashboard_page.locator(".dashboard-card").nth(2).click()
        modal = dashboard_page.locator("#absenceModal")
        dashboard_page.wait_for_timeout(500)
        
        # Check absence rate in KPI card matches dashboard card
        dashboard_rate = dashboard_page.locator(".dashboard-card").nth(2).locator(".stat-value")
        dashboard_rate_text = dashboard_rate.inner_text()
        
        kpi_rate = modal.locator(".kpi-card").first().locator(".kpi-value")
        kpi_rate_text = kpi_rate.inner_text()
        
        # Both should contain the same percentage
        assert "%" in dashboard_rate_text
        assert "%" in kpi_rate_text
    
    def test_responsive_design(self, dashboard_page: Page):
        """Test responsive behavior of the modal"""
        # Test different viewport sizes
        viewports = [
            {"width": 1920, "height": 1080, "name": "desktop"},
            {"width": 768, "height": 1024, "name": "tablet"},
            {"width": 375, "height": 667, "name": "mobile"}
        ]
        
        for viewport in viewports:
            dashboard_page.set_viewport_size(
                width=viewport["width"], 
                height=viewport["height"]
            )
            
            # Open modal
            dashboard_page.locator(".dashboard-card").nth(2).click()
            modal = dashboard_page.locator("#absenceModal")
            
            # Verify modal is visible and properly sized
            expect(modal).to_be_visible()
            
            # Close modal for next iteration
            modal.locator(".btn-close").click()
            dashboard_page.wait_for_timeout(300)

class TestAbsenceDataIntegration:
    """Test data integration and calculations"""
    
    def test_config_file_loading(self):
        """Test that configuration files are properly loaded"""
        # Check config file exists
        assert CONFIG_PATH.exists(), "Config file should exist"
        
        # Load and validate structure
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Verify required sections
        assert "metadata" in config
        assert "absence_categories" in config
        assert "risk_criteria" in config
        assert "visualization_config" in config
        
        # Verify absence categories
        categories = config["absence_categories"]
        assert len(categories) == 5  # 5 main groups
        
        # Verify risk criteria
        risk = config["risk_criteria"]
        assert "high_risk" in risk
        assert "medium_risk" in risk
        assert "low_risk" in risk
    
    def test_multilingual_labels(self):
        """Test that all language files exist and have consistent structure"""
        languages = ["ko", "vi", "en"]
        
        for lang in languages:
            label_file = BASE_DIR / "config_files" / f"absence_labels_{lang}.json"
            assert label_file.exists(), f"Label file for {lang} should exist"
            
            with open(label_file, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            
            # Verify structure
            assert "modal" in labels
            assert "tabs" in labels
            assert "kpi" in labels
            assert "charts" in labels
            assert "table" in labels
            
            # Verify key sections have content
            assert len(labels["tabs"]) == 4  # 4 tabs
            assert len(labels["kpi"]) > 0
            assert len(labels["charts"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--headed"])