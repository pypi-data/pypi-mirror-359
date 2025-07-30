
class _LocIndexer:
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, key):
        from .dataset import Dataset
        from datetime import datetime
        from atrax import Series

        # handle (row_filter, col_filer) vs just row_filter
        if isinstance(key, tuple):
            row_filter, col_filter = key
        else:
            row_filter, col_filter = key, self.dataset.columns

        # normalize col_filter
        if isinstance(col_filter, str):
            col_filter = [col_filter]
        elif col_filter is None:
            col_filter = self.dataset.columns

        # row filtereing
        index = self.dataset._index
        data = self.dataset.data

        # single label
        if isinstance(row_filter, (str, int, float, datetime)):
            key_val = row_filter

            # smart datetime parsing if index is datetime-like
            if index and isinstance(index[0], datetime) and isinstance(row_filter, str):
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
                    try:
                        key_val = datetime.strptime(row_filter, fmt)
                        break
                    except ValueError:
                        continue
            filtered_data = [
                row for idx, row in zip(index, data)
                if idx == key_val
            ]
            new_index = [key_val] * len(filtered_data)


        # list of labels
        elif isinstance(row_filter, list) and all(not isinstance(x, bool) for x in row_filter):
            label_set = set(row_filter)
            filtered_data, new_index = zip(*[
                (row, idx) for idx, row in zip(index, data)
                if idx in label_set
            ]) if label_set else ([], [])

        # boolean mask
        elif isinstance(row_filter, list) and all(isinstance(x, bool) for x in row_filter):
            filtered_data = [row for row, keep in zip(data, row_filter) if keep]
            new_index = [idx for idx, keep in zip(index, row_filter) if keep]

        # callable
        elif callable(row_filter):
            filtered_data, new_index = zip(*[
                (row, idx) for idx, row in zip(index, data)
                if row_filter(row)
            ])

        # label slice (like 'a':'d')
        elif isinstance(row_filter, slice):
            # assume index is ordered and sliceable
            start, stop = row_filter.start, row_filter.stop
            filtered_data, new_index = zip(*[
                (row, idx) for idx, row in zip(index, data)
                if (start is None or idx >= start) and (stop is None or idx <= stop)
            ])

        # Boolean Series
        elif isinstance(row_filter, Series):
            bool_mask = row_filter.data
            filtered_data = [row for row, keep in zip(data, bool_mask) if keep]
            new_index = [idx for idx, keep in zip(index, bool_mask) if keep]

        else:
            # default: return all
            filtered_data = data
            new_index = index
        

        # column section
        result_data = [
            {col: row.get(col) for col in col_filter if col in row}
            for row in filtered_data
        ]

        return Dataset(result_data, index=list(new_index))
    
    def __setitem__(self, key, value):
        from atrax import Series


        if isinstance(key, tuple):
            row_filter, col_name = key
        else:
            row_filter = key
            col_name = None
        
        # get rows to modify
        if isinstance(row_filter, Series):
            bool_mask = row_filter.data
            rows = [row for row, keep in zip(self.dataset.data, bool_mask) if keep]

        elif isinstance(row_filter, list) and all(isinstance(b, bool) for b in row_filter):
            rows = [row for row, keep in zip(self.dataset.data, row_filter) if keep]

        elif callable(row_filter):
            rows = [row for row in self.dataset.data if row_filter(row)]

        else:
            raise TypeError("Invalid row selector for .loc")
        
        if col_name is None:
            raise ValueError("You must specify a column name for assignment with .loc")
        
        # apply assignment
        if isinstance(value, Series):
            if len(value.data) != len(rows):
                raise ValueError("Length of Series does not match number of selected rows")
            for row, val in zip(rows, value.data):
                row[col_name] = val
        elif isinstance(value, list):
            if len(value) != len(rows):
                raise ValueError("Length of list does not match number of selected rows")
            for row, val in zip(rows, value):
                row[col_name] = val
        elif callable(value):
            for row in rows:
                row[col_name] = value(row)
        else:
            for row in rows:
                row[col_name] = value  


        # Ensure the column exists in the dataset's columns list
        if col_name not in self.dataset.columns:
            self.dataset.columns.append(col_name)                     

    


class _iLocIndexer:
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, key):
        from .dataset import Dataset

        # normalize the key into (row_idx, col_idx)
        if isinstance(key, tuple): # ds.iloc[rows, cols]
            row_idx, col_idx = key
        else:                       # ds.iloc[rows] (cols=all)
            row_idx, col_idx = key, slice(None)

        # resolve rows
        if isinstance(row_idx, slice):
            rows = self.dataset.data[row_idx]
        elif isinstance(row_idx, (list, tuple)):
            rows = [self.dataset.data[i] for i in row_idx]
        else:
            rows = [self.dataset.data[row_idx]]

        # resolve columns
        if isinstance(col_idx, slice):
            column_names = self.dataset.columns[col_idx]
        elif isinstance(col_idx, (list, tuple)):
            column_names = [self.dataset.columns[i] for i in col_idx]
        else:
            column_names = [self.dataset.columns[col_idx]]

        # build filtered rows
        filtered = [
            {k: row[k] for k in column_names if k in row}
            for row in rows
        ]

        # get the index positions frmo the original dataset
        if isinstance(row_idx, slice):
            new_index = self.dataset._index[row_idx]
        elif isinstance(row_idx, (list, tuple)):
            new_index = [self.dataset._index[i] for i in row_idx]
        else:
            new_index = [self.dataset._index[row_idx]]

        return Dataset(filtered, index=new_index)

