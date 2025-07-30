from datetime import datetime
import statistics
from .indexers import _iLocIndexer, _LocIndexer
from atrax import Series
from copy import deepcopy
from collections.abc import Sequence
from .group import GroupBy

class Dataset:

    @property
    def loc(self):
        return _LocIndexer(self)

    @property
    def iloc(self):
        return _iLocIndexer(self)

    def __init__(self, data: list[dict], index=None):
        """
            Initialize a dataset.

            Parameters:

                data (list[dict] or dict[list]): either row oriented or column oriented data 
        """
        if isinstance(data, dict):
            if len(set([len(v) for v in data.values()])) != 1:
                raise ValueError("All columns must have the same length")
            
            keys = list(data.keys())
            values = zip(*data.values())
            data = [dict(zip(keys, row)) for row in values]

        self.data = data
        self.columns = list(data[0].keys()) if data else []
        self._index_name = ''
        self._index = index if index is not None else list(range(len(data)))

    def __repr__(self):
        lines = []
        lines.append('<Dataset />')
        lines.extend([', '.join(self.columns)])
        for row in self.data[:10]:
            lines.append(', '.join(str(row.get(col, '')) for col in self.columns))
        if len(self.data) > 10:
            lines.append(f"...({len(self.data)}) total rows")
        return '\n'.join(lines)
    
    def _repr_html_(self):
        if not self.data:
            return '<i>Empty Dataset</i>'
        
        from io import StringIO
        import csv, base64
        
        headers = self.columns.copy()
        show_index = self._index is not None

        # new
        if show_index and self._index_name in headers:
            headers.remove(self._index_name)
        # Header row
        index_label = self._index_name if self._index_name else ""
        header_html = f"<th>{index_label}</th>" if show_index else ""
        header_html += ''.join(f"<th>{col}</th>" for col in headers)   

        # Data rows
        body_html = ''
        for i, row in enumerate(self.data):
            idx_val = self._index[i] if self._index else i
            if isinstance(idx_val, datetime):
                idx_str = idx_val.strftime('%y-%m-%d')
            else:
                idx_str = str(idx_val)
            row_html = f"<td><strong>{idx_str}</strong></td>" if show_index else ""
            row_html += ''.join(f"<td>{row.get(col, '')}</td>" for col in headers)
            body_html += f"<tr>{row_html}</tr>" 

        # CSV export as base64
        def to_csv_string():
            buffer = StringIO()
            writer = csv.writer(buffer)
            if show_index:
                writer.writerow([index_label] + headers)
            else:
                writer.writerow(headers)
            for i, row in enumerate(self.data):
                row_vals = [row.get(col, "") for col in headers]
                if show_index:
                    row_vals = [self._index[i] if self._index else i] + row_vals
                writer.writerow(row_vals)
            return buffer.getvalue()  

        csv_bytes = to_csv_string().encode("utf-8")
        b64 = base64.b64encode(csv_bytes).decode("utf-8")
        download_link = f'''<a download="dataset.csv" href="data:text/csv;base64,{b64}" target="_blank"
            style="
               display: inline-block;
               margin-bottom: 10px;
               padding: 6px 12px;
               background-color: #007acc;
               color: white;
               text-decoration: none;
               border-radius: 5px;
               font-family: sans-serif;
               font-size: 14px;
           "
        >Download CSV</a>'''

        # Final HTML output
        return f"""
            <div>
                {download_link}
                <table>
                    <thead><tr>{header_html}</tr></thead>
                    <tbody>{body_html}</tbody>
                </table>
            </div>
        """                                  
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]
        elif isinstance(key, str):
            return Series([row.get(key) for row in self.data], name=key)
        elif isinstance(key, Series) and all(isinstance(val, bool) for val in key.data):
            # filter rows using a boolean series
            if len(key.data) != len(self.data):
                raise ValueError("Boolean Series must match the length of the dataset")
            
            filtered = [row for row, flag in zip(self.data, key.data) if flag]
            return Dataset(filtered)
        
        elif isinstance(key, list):
            # column subset
            return Dataset([{k: row[k] for k in key if k in row} for row in self.data])
        
        else:
            raise TypeError("Key must be a string (column), list of strings (subset) or Series (boolean mask)")
        
    def __setitem__(self, key, value):
        if isinstance(value, Series):
            if len(value.data) != len(self.data):
                raise ValueError("Series length must match Dataset length")
            for row, val in zip(self.data, value.data):
                row[key] = val
        elif isinstance(value, list):
            if len(value) != len(self.data):
                raise ValueError("List length must match Dataset length")
            for row, val in zip(self.data, value):
                row[key] = val
        elif callable(value):
            for row in self.data:
                row[key] = value(row)
        elif isinstance(value, (int, float, str, bool)):
            # broadcast scalar value
            for row in self.data:
                row[key] = value
        else:
            raise TypeError(f"Cannot assign value of type {type(value)} to column '{key}'")

        if key not in self.columns:
            self.columns.append(key)
    
    def head(self, n=5):
        """ Return the first n rows of the dataset."""
        return Dataset(self.data[:n])
    
    def tail(self, n = 5):
        """ Return the last n rows of the dataset."""
        return Dataset(self.data[-n:], index=self._index[-n:])
    
    def shape(self):
        return (len(self.data), len(self.columns))
    
    
    def describe(self, numeric_only=False):
        numeric_cols = {
            col: [row[col] for row in self.data if isinstance(row.get(col), (int, float))] for col in self.columns
        }
        if numeric_only:
            numeric_cols = {
                col: [row[col] for row in self.data if isinstance(row.get(col), (int, float))]
                for col in self.columns
                if any(isinstance(row.get(col), (int, float)) for row in self.data)
            }

        summary_rows = []

        def percentile(data, p):
            data = sorted(data)
            idx = int(round(p * (len(data) - 1)))
            return data[idx]
        
        for stat in ['mean', 'std', 'min', 'Q1', 'median', 'Q3', 'max', 'count']:
            row={'stat': stat}
            for col, values in numeric_cols.items():
                if not values:
                    row[col] = None
                    continue
                if stat == 'mean':
                    row[col] = round(statistics.mean(values), 2)
                elif stat == 'std':
                    row[col] = round(statistics.stdev(values), 2) if len(values) > 1 else 0.0
                elif stat == 'min':
                    row[col] = min(values)
                elif stat == 'Q1':
                    row[col] = percentile(values, 0.25)
                elif stat == 'median':
                    row[col] = round(statistics.median(values), 2)
                elif stat == 'Q3':
                    row[col] = percentile(values, 0.75)
                elif stat == 'max':
                    row[col] = max(values)
                elif stat == 'count':
                    row[col] = len(values)
            summary_rows.append(row)
        
        return Dataset(summary_rows)
    
    def info(self):
        print(f"<class 'Dataset'>")
        print(f"Range Index: {len(self.data)} entries")
        print(f"Data columns (total {len(self.columns)} columns):")
        if not self.data:
            print("   No data available")
            return

        # if self._index_name and self._index:
        #     index_sample = self._index[0]
        #     if isinstance(index_sample, datetime):
        #         dtype = 'datetime'
        #     elif isinstance(index_sample, bool):
        #         dtype = 'bool'
        #     elif isinstance(index_sample, int):
        #         dtype = 'int'
        #     elif isinstance(index_sample, float):
        #         dtype = 'float'
        #     elif isinstance(index_sample, str):
        #         dtype = 'str'
        #     else:
        #         dtype = type(index_sample).__name__

        #     print(f"Index")
        #     print(f"    name: {self._index_name}")
        #     print(f"    dtype: {dtype}")
        #     print("")

        # now print the column info
        col_stats = {}

        for col in self.columns:
            values = [row.get(col) for row in self.data]
            non_nulls = [v for v in values if v is not None]

            sample = non_nulls[0] if non_nulls else None
            dtype = 'unknown'

            if sample is None:
                dtype = 'NoneType'
            elif isinstance(sample, bool):
                dtype = 'bool'
            elif isinstance(sample, int):
                dtype = 'int'
            elif isinstance(sample, float):
                dtype = 'float'
            elif isinstance(sample, datetime):
                dtype = 'datetime'
            elif isinstance(sample, str):
                dtype = 'str'

            col_stats[col] = {
                'dtype': dtype,
                'non_null': len(non_nulls),
                'total': len(values)
            }
        print(f"{'Column':<15} | {'Dtype':<10} | {'Non-Null':<10} | {'Total':<10}")
        print(f"-" * 50)
        for col, stats in col_stats.items():
            print(f"{col:<15} | {stats['dtype']:<10} | {stats['non_null']:<10} | {stats['total']:<10}")

    def set_index(self, column, *, inplace=True, drop=True):
        """
        Set (or compute) the row index for this DataSet.

        Parameters
        ----------
        column : str | callable | Sequence
            • str   - name of an existing column to promote to the index  
            • callable - a function `f(row_dict) -> hashable` evaluated per row  
            • list/seq - explicit index values (must match len(self))
        inplace : bool, default True
            If True, mutate this DataSet.  If False, return a **new** DataSet.
        drop : bool, default True
            When `column` is a str: drop that column from the data rows.
            I think we mostly want this, so our display looks cleaner.

        Returns
        -------
        DataSet | None
            The updated DataSet (if `inplace=False`), otherwise ``None``.
        """
        from copy import deepcopy
        from collections.abc import Sequence
        from atrax import Dataset
        from atrax import Series

        # ------------------------------------------------------------------ #
        # 1. Determine the new index values (index_vals) and whether we have
        #    a column name that *might* need to be dropped.
        # ------------------------------------------------------------------ #
        if isinstance(column, str):
            if column not in self.columns:
                raise KeyError(f"Column '{column}' not found in dataset.")

            index_vals = [row[column] for row in self.data]
            index_name = column
            need_drop  = drop

        elif callable(column):
            index_vals = [column(row) for row in self.data]
            index_name = None        # anonymous index
            need_drop  = False       # nothing to drop

        elif isinstance(column, (list, tuple, Series)) or (
                isinstance(column, Sequence) and not isinstance(column, str)):
            # Accept list / tuple / Series / numpy array … anything Sequence-ish
            if len(column) != len(self.data):
                raise ValueError("Index length must match number of rows.")
            index_vals = list(column)          # materialise
            index_name = None
            need_drop  = False

        else:
            raise TypeError(
                "`column` must be a string, callable, or sequence of index values."
            )

        # ------------------------------------------------------------------ #
        # 2. Prepare the new data/columns containers
        # ------------------------------------------------------------------ #
        if inplace:
            target = self
            if need_drop:
                # remove the column from each row
                for row in target.data:
                    row.pop(column, None)
        else:
            target        = Dataset(deepcopy(self.data))  # deep-copy rows
            if need_drop:
                for row in target.data:
                    row.pop(column, None)

        # Refresh columns list if we dropped something
        if need_drop:
            target.columns = list(target.data[0].keys()) if target.data else []

        # ------------------------------------------------------------------ #
        # 3. Assign index + index name
        # ------------------------------------------------------------------ #
        target._index       = index_vals
        target._index_name  = index_name

        # ------------------------------------------------------------------ #
        # 4. Return as per `inplace`
        # ------------------------------------------------------------------ #
        if inplace:
            return None
        else:
            return target   

    def drop(self, columns=None, index=None, inplace=False):
        """
        Remove columns and/or rows.

        Parameters
        ----------
        columns : str | Sequence[str] | None
            Column name(s) to drop.
        index   : int | Sequence[int] | None
            Row position(s) to drop (by *position*, not label).
        inplace : bool, default False
            Mutate this DataSet or return a new one.

        Returns
        -------
        DataSet | None
        """
        # ------------------------------------------------------------------ #
        # 0. Normalise inputs
        # ------------------------------------------------------------------ #
        if isinstance(columns, str):
            columns = [columns]
        elif isinstance(index, int):
            index = [index]            
        if isinstance(index, (int, slice)):
            index = list(range(*index.indices(len(self.data))))  # handles slice
        elif index is not None and not isinstance(index, Sequence):
            raise TypeError("`index` must be int, slice or sequence of ints.")

        # ------------------------------------------------------------------ #
        # 1. Build working copy of rows
        # ------------------------------------------------------------------ #
        working_rows = deepcopy(self.data) if not inplace else self.data

        # ------------------------------------------------------------------ #
        # 2. Drop rows by position
        # ------------------------------------------------------------------ #
        if index:
            keep_mask    = [i not in index for i in range(len(working_rows))]
            working_rows = [r for r, keep in zip(working_rows, keep_mask) if keep]
            if hasattr(self, "_index") and self._index is not None:
                new_index = [self._index[i] for i in range(len(self._index)) if keep_mask[i]]
            else:
                new_index = None
        else:
            new_index = getattr(self, "_index", None)

        # ------------------------------------------------------------------ #
        # 3. Drop specified columns
        # ------------------------------------------------------------------ #
        if columns:
            # validation
            missing = [c for c in columns if c not in self.columns]
            if missing:
                raise KeyError(f"Column(s) not found: {missing}")
            working_rows = [
                {k: v for k, v in row.items() if k not in columns}
                for row in working_rows
            ]
            if getattr(self, "_index_name", None) in columns:
                self._index_name = None  # index column is gone

        # ------------------------------------------------------------------ #
        # 4. Finalise
        # ------------------------------------------------------------------ #
        if inplace:
            self.data    = working_rows
            self.columns = list(working_rows[0].keys()) if working_rows else []
            self._index  = new_index
            return None
        else:
            result             = Dataset(working_rows)
            result.columns     = list(working_rows[0].keys()) if working_rows else []
            result._index      = new_index
            result._index_name = getattr(self, "_index_name", None)
            return result  

    def rename(self, columns=None, inplace=False):
        """ Rename columns in the dataset.
        
        Parameters:
        ___________
            columns (dict): dictionary mapping old column names to new names
            inplace (bool): if true, modify the current dataset, otherwise return a new one
        
        Returns:
        ___________
            DataSet or None: new dataset with renamed columns, or None if inplace=True
            
        """ 
        if not columns:
            return self
        if not isinstance(columns, dict):
            raise TypeError("`columns` must be a dictionary mapping old column names to new names")
        
        new_data = []
        for row in self.data:
            new_row = {}
            for k, v in row.items():
                new_key = columns.get(k, k)
                new_row[new_key] = v
            new_data.append(new_row)

        if inplace:
            self.data = new_data
            self.columns = [columns.get(col, col) for col in self.columns]
            return None
        else:
            return Dataset(new_data)
        
    def groupby(self, by, sort=False):
        """
            Group the dataset by one more columns.

            Parameters:

                by (str or list of str): Column(s) to group by

            Returns:
                GroupBy: GroupBy object for aggregation
        """
        return GroupBy(self.data, by, sort)

    
