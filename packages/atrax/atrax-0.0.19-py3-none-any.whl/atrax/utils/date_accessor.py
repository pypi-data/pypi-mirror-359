from datetime import datetime

class _DateTimeAccessor:
    def __init__(self, series):
        self.series = series

    def _convert(self, d, mode='date'):
        from .date_fns import parse_date
        if isinstance(d, str):
            date = parse_date(d)
            if mode == 'date':
                return date.weekday()
            elif mode == 'day':
                return date.day
            elif mode == 'month':
                return date.month
            elif mode == 'year':
                return date.year
            
        elif isinstance(d, datetime):
            if mode == 'date':
                return d.weekday()
            elif mode == 'day':
                return d.day
            elif mode == 'month':
                return d.month
            elif mode == 'year':
                return d.year
        else:
            raise TypeError(f"Unsupported type for date: {type(d)}")   

    @property
    def day(self):
        """
        Get the day of the month for each date in the Series.
        
        Returns:
        Series: A new Series with the day of the month.
        """
        from atrax.Series.series import Series

        return Series([self._convert(d, mode='day') for d in self.series.data], 
                      name=f"{self.series.name}_day", 
                      index=self.series.index)

    @property
    def month(self):
        """
        Get the month for each date in the Series.
        
        Returns:
        Series: A new Series with the month (1-12).
        """
        from atrax.Series.series import Series

        return Series([self._convert(d, mode='month') for d in self.series.data], 
                      name=f"{self.series.name}_month", 
                      index=self.series.index)     
    
    @property
    def year(self):
        """
        Get the year for each date in the Series.
        
        Returns:
        Series: A new Series with the year.
        """
        from atrax.Series.series import Series

        return Series([self._convert(d, mode='year') for d in self.series.data], 
                      name=f"{self.series.name}_year", 
                      index=self.series.index)

    @property
    def weekday(self):
        """
        Get the weekday of each date in the Series.
        
        Returns:
        Series: A new Series with the weekday (0=Monday, 6=Sunday).
        """
        from atrax.Series.series import Series

        return Series([self._convert(d) for d in self.series.data], 
                      name=f"{self.series.name}_weekday", 
                      index=self.series.index) 

    @property
    def is_weekend(self):
        """
        Check if each date in the Series is a weekend (Saturday or Sunday).
        
        Returns:
        Series: A new Series with int values indicating if the date is a weekend (1=yes, 0=no).
        """
        from atrax.Series.series import Series

        return Series([self._convert(d) >= 5 for d in self.series.data], 
                      name=f"{self.series.name}_is_weekend", 
                      index=self.series.index) 

    