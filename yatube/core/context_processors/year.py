import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    day_today = dt.datetime.today()
    return {
        'year': day_today.year,
    }
