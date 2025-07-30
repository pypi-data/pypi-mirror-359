from datetime import datetime
import numpy as np
from .indexers import _ILoc, _Loc
from ..utils.date_accessor import _DateTimeAccessor

class Series:

    @property
    def iloc(self):
        """
            Provides integer-location based indexing

            Allows access to elements by thier integer position

            Examples:
            >>> from atrax import Series
            >>> s = Series([1,2,3], name='example', index=['a', 'b', 'c'])
            >>> s.iloc[0]
            1

            >>> s.iloc[1:3]
            b   2
            c   3
            Name: example, dtype: int64

            >>> s = Series([1,2,3,4,5,],  name="numbers", index=['a', 'b', 'c', 'd', 'e'])
            >>> s.iloc[1:4]
            b    2
            c    3
            d    4
            Name: numbers, dtype: int64   

            >>> s.iloc[::-1]
            e    5
            d    4
            c    3
            b    2
            a    1
            Name: numbers, dtype: int64                    
        """
        return _ILoc(self)
    
    @property
    def loc(self):
        """ 
            Provides label-based indexing for the Series
        
            Examples:

            >>> from atrax import Series
            >>> s = Series([1,2,3], name="example" index=['a', 'b', 'c'])
            >>> s.loc['a']
            1

            >>> s.loc['b': 'c']
            b   2
            c   3
            Name: example, dtype: int64
            
        """
        return _Loc(self)
    
    @property
    def values(self):
        """Returns the underlying data of the Series as a list.
        
        Examples:
        >>> from atrax import Atrax as tx
        >>> s = tx.Series([1, 2, 3], name='example', index=['a', 'b', 'c'])
        >>> s.values
        [1, 2, 3]
        
        >>> type(s.values)
        list"""
        return self.data

    @property
    def name(self):
        """Returns the name of the Series.

        Examples:
        >>> from atrax import Atrax as tx
        >>> s = tx.Series([1, 2, 3], name='example', index=['a', 'b', 'c'])
        >>> s.name
        'example'

        >>> s = tx.Series([1, 2, 3])
        >>> s.name
        ''
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value      
    
    @property
    def dt(self):
        """
        Provides datetime-like properties for the Series.
        
        Examples:
        >>> from atrax import Atrax as tx
        >>> test_data = [
            {
                'id': 1,
                'sale_date': '1/1/2025'
            },
            {
                'id': 2,
                'sale_date': '1/2/2025'
            },
            {
                'id': 3,
                'sale_date': '1/3/2025'
            }
        ]
        >>> ds = tx.DataSet(test_data)

        >>> ds['weekday'] = ds['sale_date'].dt.weekday
        >>> ds.head()
        id    sale_date    weekday
        1     1/1/2025     2
        2     1/2/2025     3
        3     1/3/2025     4


        >>> ds['is_weekend'] = ds['sale_date'].dt.is_weekend
        >>> ds.head()
        id    sale_date    weekday   is_weekend
        1     1/1/2025     2         False
        2     1/2/2025     3         False
        3     1/3/2025     4         False

        >>> ds['month'] = ds['sale_date'].dt.month
        >>> ds.head()
        id    sale_date    weekday   is_weekend   month
        1     1/1/2025     2         False        1
        2     1/2/2025     3         False        1
        3     1/3/2025     4         False        1

        >>> ds['day'] = ds['sale_date'].dt.day
        >>> ds.head()
        id    sale_date    weekday   is_weekend   month  day
        1     1/1/2025     2         False        1      1
        2     1/2/2025     3         False        1      2
        3     1/3/2025     4         False        1      3

        >>> ds['year'] = ds['sale_date'].dt.year
        >>> ds.head()
        id    sale_date    weekday   is_weekend   month  day  year
        1     1/1/2025     2         False        1      1    2025
        2     1/2/2025     3         False        1      2    2025
        3     1/3/2025     4         False        1      3    2025  


        """
        return _DateTimeAccessor(self)
    

    def __init__(self, data, name=None, index=None):
        """
            One-dimensional labeled array for atrax

            Parameters
            _________
                data (list): a list of values
                name (str): name of the Series
                index (list): list of indexes

            Examples:

            >>> from atrax import Series
            >>> s = Series([1, 2, 3])
            >>> s
            0    1
            1    2
            3    3
            Name: , dtype: int

            >>> s = tx.Series([1, 2, 3, 4, 5], name='numbers', index=['a', 'b', 'c'])
            >>> s
            a     1
            b     2  
            c     3
            Name: numbers, dtype: int

            >>> s = tx.Series([1.0, 2.0, 3.0], name='example', index=['a', 'b', 'c'])
            a     1.0
            b     2.0
            c     3.0
            Name: example, dtype: float

            >>> s = tx.Series(['hello', 'goodbye', 'whatsup'])
            0     hello
            1     goodbye
            2     whatsup
            Name: , dtype: str    

            >>> s = tx.Series([1, True, 'sexy', 2.5])
            0     1
            1     True
            2     sexy
            3     2.5
            Name: , dtype: object

            ##### this one is interesting and probably needs attention
            >>> s = tx.Series([True, False, True])
            0    True
            1    False
            2    True
            Name: , dtype: int                     
        """
        self.data = data
        self.name = name or ""
        # if the user didn't specify indexes, then we can infer them from the length of the data
        self.index = index or list(range(len(data)))
        # let's make sure that if the user supplied indexes that the length is correct
        if len(self.data) != len(self.index):
            raise ValueError(f"Length of index must match the length of the data, you supplied {len(self.data)} for data and {len(self.index)} for indexes")
        self.dtype = self._infer_dtype()

    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        lines = []
        lines.append(f'<Series />')
        lines.extend([f'{str(i)}    {str(d)}' for i, d in zip(self.index[0:10], self.data[0:10])])
        if len(self.data) > 10:
            lines.append(f"...({len(self.data)} total items)")
        lines.append(f'Name: {self.name}   dtype: {self.dtype}')
        return '\n'.join(lines)

    def _repr_html_(self):
        html = "<table style='border-collapse: collapse;'>"
        for idx, val in zip(self.index[:10], self.data[:10]):
            html += f"<tr><td style='text-align: 'left';'>{idx}</td>"
            html += f"<td>{val}</td></tr>"
        html += f"<tr><td colspan='2' style='font-size:14px;'>Name: {self.name}, dtype: {self.dtype}</td></tr>"
        if len(self.data) > 10:
            html += f"<tr><td colspan='2'><i>...{len(self.data)-10} more</i></td></tr>"
        html += "</table>"
        return html
        

    def _infer_dtype(self):
        if all(isinstance(x, float) for x in self.data):
            return 'float64'
        elif all(isinstance(x, bool) for x in self.data):
            return 'bool'
        elif all(isinstance(x, int) for x in self.data):
            return 'int64'
        elif all(isinstance(x, str) for x in self.data):
            return 'str'
        elif all(isinstance(x, datetime) for x in self.data):
            return 'datetime'
        else:
            return 'object'
        
    def _binary_op(self, other, op):
        if isinstance(other, Series):
            if len(self.data) != len(other.data):
                raise ValueError(f"Series must have the same length. found: {len(self.data)} and {len(other.data)}")
            return Series([op(a,b) for a,b in zip(self.data, other.data)], name=self.name)
        else:
            return Series([op(a, other) for a in self.data], name=self.name)
        
    # basic math operators
    def __add__(self, other): 
        return self._binary_op(other, lambda a, b: a + b)
    
    def __sub__(self, other): 
        return self._binary_op(other, lambda a,b: a - b)
    
    def __mul__(self, other): 
        return self._binary_op(other, lambda a,b: a * b)
    
    def __truediv__(self, other): 
        return self._binary_op(other, lambda a, b: a / b)
    
    def __floordiv__(self, other): 
        return self._binary_op(other, lambda a, b: a // b)
    
    def __mod__(self, other): 
        return self._binary_op(other, lambda a, b: a % b)
    
    def __pow__(self, other): 
        return self._binary_op(other, lambda a, b: a ** b)
    
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        from numpy import ndarray
        raw_inputs = []
        for x in inputs:
            if isinstance(x, Series):
                raw_inputs.append(x.data)
            else:
                raw_inputs.append(x)

        result = getattr(ufunc, method)(*raw_inputs, **kwargs)

        if isinstance(result, tuple):
            # for ufuncs that return multiple outputs, return tuple of series
            return tuple(Series(r, name=self.name) if isinstance(r, ndarray) else r for r in result)
        elif isinstance(result, ndarray):
            return Series(result.tolist(), name=self.name)
        else:
            return result

        
    def head(self, n=5):
        """
        Return the first n elements of the Series.

        Parameters:
        n (int): The number of elements to return. Defaults to 5.


        Returns:
        Series: A new Series containing the first n elements.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> print(s.head(3))
        0    1
        1    2
        2    3
        Name: , dtype: int
        """        
        return Series(self.data[:n], name=self.name, index=self.index[:n])
    
    def tail(self, n=5):
        """
        Return the last n elements of the Series.

        Parameters:
        n (int): The number of elements to return. Defaults to 5.

        Returns:
        Series: A new Series containing the last n elements.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> print(s.tail(3))
        2    3
        3    4 
        4    5 
        """        
        return Series(self.data[-n:], name=self.name, index=self.index[-n:])
    
    # reverse math operators
    def __radd__(self, other):
        return self._binary_op(other, lambda a, b: b + a)
    
    def __rsub__(self, other): 
        return self._binary_op(other, lambda a,b: b - a)
    
    def __rmul__(self, other): 
        return self._binary_op(other, lambda a,b: b * a)
    
    def __rtruediv__(self, other): 
        return self._binary_op(other, lambda a, b: b / a)
    
    def __rfloordiv__(self, other): 
        return self._binary_op(other, lambda a, b: b // a)
    
    def __rmod__(self, other): 
        return self._binary_op(other, lambda a, b: b % a)
    
    def __rpow__(self, other): 
        return self._binary_op(other, lambda a, b: b ** a)    
    
    # comparisons
    def __gt__(self, other):
        return Series([x > other for x in self.data], name=self.name)
    
    def __lt__(self, other):
        return Series([x < other for x in self.data], name=self.name)
    
    def __ge__(self, other):
        return Series([x >= other for x in self.data], name=self.name)
    
    def __le__(self, other):
        return Series([x <= other for x in self.data], name=self.name)
    
    def __eq__(self, other):
        return Series([x == other for x in self.data], name=self.name)
    
    def __ne__(self, other):
        return Series([x != other for x in self.data], name=self.name)
        
    # chaining
    def __and__(self, other):
        if not isinstance(other, Series):
            raise TypeError('Operand must be a Series')
        if len(other) != len(self.data):
            raise ValueError('Cannot perform operation. Series must have the same length')
        return Series([a and b for a,b in zip(self.data, other.data)], name=self.name)  

    def __or__(self, other):
        if not isinstance(other, Series):
            raise TypeError('Operand must be a Series')
        if len(other) != len(self.data):
            raise ValueError('Cannot perform operation. Series must have the same length')        
        return Series([a or b for a, b in zip(self.data, other.data)], name=self.name)      
    
    # unique
    def unique(self):
        """
        Return the unique values in the Series.

        Returns:
        Series: A new Series containing the unique values.

        Example usage:
        >>> s = tx.Series([1, 2, 2, 3, 4, 4])
        >>> unique_s = s.unique()
        >>> print(unique_s)
        0    1
        1    2
        2    3
        3    4
        Name: Unique(), dtype: int

        """        
        # the best way to do this is to create a set to remove duplicates
        uniques = list(set(self.data))
        # grab the unique values and calculate new indexes
        #return Series(uniques, name=self.name, index=list(range(len(uniques))))
        return np.array(uniques)
    
    # nunique
    def nunique(self):
        """
        Return the number of unique values in the Series.

        Returns:
        int: The number of unique values.

        Example usage:
        >>> s = tx.Series([1, 2, 2, 3, 4, 4])
        >>> num_unique = s.nunique()
        >>> print(num_unique)
        4

        """        
        uniques = list(set(self.data))
        return len(uniques)

    # apply
    def apply(self, func):
        """Apply a function to each element in the Series.
        
        Parameters:
        func (function): A function to apply to each element.   
        
        Returns:
        Series: A new Series with the function applied to each element.
        
        Example usage:
        >>> s = tx.Series([1, 2, 3])
        >>> result = s.apply(lambda x: x * 2)
        >>> print(result)
        0    2
        1    4
        2    6
        Name: , dtype: int
        
        >>> def square(x):
        >>>     return x** 2
            
        >>> result = s.apply(square)   
        >>> result
        0    1
        1    4  
        2    9
        Name: , dtype: int
        """        
        result = [func(d) for d in self.data]
        return Series(result, name=self.name)
    
    # map
    def map(self, arg):
        """
            Map values of the Series using an input mapping or function

            Parameters:

                arg (dict or function): a mapping dictionary or function to apply to each value
            
            Returns:

                Series

            Example usage:

            >>> s = Series([1,2,3], name='example', index=['a', 'b', 'c'])
            >>> mapping = {1: 'one', 2: 'two', 3: 'three'}
            >>> mapped_s = s.map(mapping)
            >>> mapped_s
            a     one
            b     two
            c     three
            Name: example, dtype: str
        """
        if callable(arg):
            mapped = [arg(x) for x in self.data]
        elif isinstance(arg, dict):
            mapped = [arg.get(x, None) for x in self.data]
        else:
            raise TypeError("Argument must be a callable of dictionary")
        return Series(mapped, name=self.name,index=self.index)
    
    # astype
    def astype(self, dtype):
        """
        Convert the Series to a specified data type.
        
        Parameters:

        dtype (type): The Python type to cast to (e.g., int, float, str)
        
        Returns:

        Series: A new Series with the converted data type.

        Example usage:
        >>> s = tx.Series(['1', '2', '3'])
        >>> i_series = s.astype(int)
        >>> i_series
        0    1
        1    2
        2    3
        Name: , dtype: int

        >>> s = tx.Series(['1', '2', '3'])
        >>> i_series = s.astype('int')
        >>> i_series
        0    1
        1    2
        2    3
        Name: , dtype: int       

        >>> s = tx.Series(['1', '2', '3'])
        >>> f_series = s.astype('float')
        >>> f_series
        0    1.0
        1    2.0
        2    3.0
        Name: , dtype: float           
        """        
        type_map = {
            'int': int,
            'float': float,
            'str': str,
            'object': lambda x: x
        }

        if isinstance(dtype, str):
            cast_fn = type_map.get(dtype)
            if cast_fn is None:
                raise ValueError(f"Unsupported dtype: {dtype}")
        else:
            cast_fn = dtype
        
        new_data = []
        for val in self.data:
            try:
                new_data.append(cast_fn(val))
            except:
                new_data.append(None)

        return Series(new_data, name=self.name, index=self.index)
    
    def to_list(self):
        """
        Convert the Series to a list.

        Returns:
        list: The data in the Series as a list.

        Example usage:
        >>> s = tx.Series([1, 2, 3])
        >>> lst = s.to_list()
        >>> print(lst)
        [1, 2, 3]

        """
        return self.data    
