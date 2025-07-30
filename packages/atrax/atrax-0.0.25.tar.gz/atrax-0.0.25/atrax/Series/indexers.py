

class _ILoc:
    def __init__(self, series):
        self.series = series

    def __getitem__(self, key):
        from .series import Series
        if isinstance(key, slice):
            return Series(self.series.data[key], name=self.series.name, index=self.series.index[key])
        else:
            return self.series.data[key]
        
class _Loc:
    def __init__(self, series):
        self.series = series

    def __getitem__(self, key):
        from .series import Series
        if isinstance(key, list):
            index_map = {k:v for k, v in zip(self.series.index, self.series.data)}
            return Series([index_map[k] for k in key], name=self.series.name, index=key)
        elif isinstance(key, slice):
            start_label = key.start
            end_label = key.stop

            try:
                start_idx = self.series.index.index(start_label)
            except ValueError:
                raise KeyError(f'start label not found in index: {start_label}')
            
            try:
                end_idx = self.series.index.index(end_label)
            except ValueError:
                raise KeyError(f'end label not found in index: {end_label}')
            
            data = self.series.data[start_idx:end_idx+1]
            index = self.series.index[start_idx:end_idx+1]
            return Series(data, name=self.series.name, index=index)
        else:
            idx = self.series.index.index(key)
            return self.series.data[idx]