from datetime import datetime


def year(request) -> int:
    """Добавляет переменную с текущим годом."""
    cur_year = datetime.now().year
    return {
        'year': cur_year,
    }
