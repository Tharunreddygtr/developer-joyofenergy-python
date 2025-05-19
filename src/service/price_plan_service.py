
from functools import reduce

from pydantic import ValidationError
from datetime import date
from ..repository.price_plan_repository import price_plan_repository
from .electricity_reading_service import ElectricityReadingService
from .time_converter import time_elapsed_in_hours
import datetime
from datetime import timedelta

def calculate_time_elapsed(readings):
    min_time = min(map(lambda r: r.time, readings))
    max_time = max(map(lambda r: r.time, readings))
    return time_elapsed_in_hours(min_time, max_time)


class PricePlanService:
    def __init__(self, reading_repository):
        self.electricity_reading_service = ElectricityReadingService(reading_repository)

    def get_list_of_spend_against_each_price_plan_for(self, smart_meter_id, limit=None):
        readings = self.electricity_reading_service.retrieve_readings_for(smart_meter_id)
        if len(readings) < 1:
            return []

        average = self.calculate_average_reading(readings)
        time_elapsed = calculate_time_elapsed(readings)
        consumed_energy = average / time_elapsed

        price_plans = price_plan_repository.get()

        def cost_from_plan(price_plan):
            cost = {}
            cost[price_plan.name] = consumed_energy * price_plan.unit_rate
            return cost

        list_of_spend = list(map(cost_from_plan, self.cheapest_plans_first(price_plans)))

        return list_of_spend[:limit]



    def cheapest_plans_first(self, price_plans):
        return list(sorted(price_plans, key=lambda plan: plan.unit_rate))

    def calculate_average_reading(self, readings):
        sum = reduce((lambda p, c: p + c), map(lambda r: r.reading, readings), 0)
        return sum / len(readings)

    def get_unit_rate_by_price_plan_id(self,  price_plan_id):
        all_price_plans = price_plan_repository.get()
        for price_plan in all_price_plans:
            if price_plan.name == price_plan_id:
                return price_plan.unit_rate
        return None


    def get_last_week_usage_price(self, smart_meter_id, price_plan_id):
        readings = self.electricity_reading_service.retrieve_readings_for(smart_meter_id)
        unit_rate = self.get_unit_rate_by_price_plan_id(price_plan_id)
        if not (price_plan_id or unit_rate):
            raise ValidationError("No Price Plans provided for the meter readings")
        last_week_readings = []

        week_start_date = date().today() - timedelta(days=7)
        week_end_date = date().today()
        for reading in readings:
            if week_start_date <= reading.time <= week_end_date:
                last_week_readings.append(reading)
        average_readings = self.calculate_average_reading(last_week_readings)
        time_elapsed = calculate_time_elapsed(readings)
        consumed_energy = average_readings / time_elapsed
        usage_price = consumed_energy * unit_rate
        return usage_price
