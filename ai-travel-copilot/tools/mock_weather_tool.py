from typing import List


def get_weather_forecast(destination: str, days: int) -> List[str]:
    base = ["晴 26℃", "多云 24℃", "小雨 22℃", "晴转多云 25℃"]
    return [base[i % len(base)] for i in range(days)]


def get_weather_for_day(destination: str, day: int, reason: str) -> str:
    if reason.lower() == "rain":
        return "中雨 20℃"
    return get_weather_forecast(destination, day)[day - 1]
