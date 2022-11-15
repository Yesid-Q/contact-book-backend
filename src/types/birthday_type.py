from typing import List

class Birthday:
    day: int
    month: int
    year: int

    def __init__(self, birthday: str):
        year, month, day, = birthday.split('-')
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)

    def __sub__(self, other: 'Birthday'):
        age = self.year - other.year - (1 if self.month <= other.month and self.day < other.day else 0)
        days_year = self.is_leap_year()
        counts = - self.day - 1
        
        if self.month < other.month:
            days = days_year[self.month : other.month]
        else:
            days = days_year[self.month:] + days_year[:other.month]
        for day in days:
            counts += day
        else:
            counts += other.day
        
        return {'age': age, 'days': counts}

    
    def is_leap_year(self) -> List[int]:
        if self.year % 4 == 0 and self.year % 100 != 0 or self.year % 400 == 0:
            return [0,31,29,31,30,31,30,31,31,30,31,30,31]
        return [0,31,28,31,30,31,30,31,31,30,31,30,31]
        

    