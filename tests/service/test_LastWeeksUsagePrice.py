from unittest import TestCase
from unittest.mock import MagicMock

from src.repository.electricity_reading_repository import ElectricityReadingRepository
from src.service.account_service import AccountService
from src.service.electricity_reading_service import ElectricityReadingService
from src.service.price_plan_service import PricePlanService
from src.service.time_converter import iso_format_to_unix_time


class TestLastWeeksUsagePrice(TestCase):

    def setUp(self):
        self.repository = ElectricityReadingRepository()
        self.repository.store = MagicMock()
        self.electricity_reading_service = ElectricityReadingService(self.repository)


    def test_last_week_usage_price_without_price_plan(self):
        test_data = {
            "smartMeterId": "smart-meter-5",
            "electricityReadings": [
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 0.812},
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 0.23},
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 0.812},
                {"time": iso_format_to_unix_time("2025-03-02T08:55:00"), "reading": 0.23},
                {"time": iso_format_to_unix_time("2025-03-05T08:55:00"), "reading": 0.812},
                {"time": iso_format_to_unix_time("2025-03-06T08:55:00"), "reading": 0.23},
                {"time": iso_format_to_unix_time("2025-03-08T08:55:00"), "reading": 0.812},
                {"time": iso_format_to_unix_time("2025-03-10T08:55:00"), "reading": 0.23},
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 0.812},
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 0.23},
            ],
        }
        self.electricity_reading_service.store_reading(test_data)
        smart_meter_id = test_data['smartMeterId']
        self.electricity_reading_service.store_reading(test_data)
        account_service = AccountService()
        price_plan = account_service.get_price_plan(smart_meter_id)
        if not price_plan:
            self.assertEqual()


    def test_last_weeks_usage_price_with_price_plan(self):
        test_data = {
            "smartMeterId": "meter-45",
            "price-plan": "price-plan-0",
            "electricityReadings": [
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 1},
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 1},
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 1},
                {"time": iso_format_to_unix_time("2025-03-02T08:55:00"), "reading": 0.23},
                {"time": iso_format_to_unix_time("2025-03-05T08:55:00"), "reading": 0.812},
                {"time": iso_format_to_unix_time("2025-03-06T08:55:00"), "reading": 0.23},
                {"time": iso_format_to_unix_time("2025-03-08T08:55:00"), "reading": 0.812},
                {"time": iso_format_to_unix_time("2025-03-10T08:55:00"), "reading": 0.23},
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 0.812},
                {"time": iso_format_to_unix_time("2025-03-26T08:55:00"), "reading": 0.23},
            ],
        }
        smart_meter_id = test_data['smartMeterId']
        self.electricity_reading_service.store_reading(test_data)
        account_service = AccountService()
        price_plan = account_service.get_price_plan(smart_meter_id)
        price_plan_service = PricePlanService(self.repository)
        usage_price = price_plan_service.get_last_week_usage_price(smart_meter_id, price_plan)
        expected_unit_rate = 10
        expected_price = expected_unit_rate *
        self.assertEqual(usage_price, expected_price)

