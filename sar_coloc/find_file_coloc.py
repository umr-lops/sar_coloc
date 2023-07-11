"""Main module."""
from .tools import get_all_comparison_files, call_meta_class
from .intersection_tools import has_intersection
import numpy as np


class FindFileColoc:
    # Choices:
    # - Don't always use footprint for all intersection types (because sometimes it needs more processing than it
    # is necessary for a listing)
    # - Use a function to fill co-located files instead of using a property, so that it is computed once.
    def __init__(self, product_id, ds_name='SMOS', level=None, delta_time=60, listing=True):
        self.product_id = product_id
        self.ds_name = ds_name
        self.level = level
        self.listing = listing
        self.product = call_meta_class(product_id, listing=listing)
        self.delta_time = np.timedelta64(delta_time, 'm')
        self.comparison_files = self.get_comparison_files
        self.common_footprints = None
        #self.fill_footprints()
        self.colocated_files = None
        self.fill_colocated_files()

    @property
    def start_date(self):
        return self.product.start_date - np.timedelta64(self.delta_time, 'm')

    @property
    def stop_date(self):
        return self.product.stop_date + np.timedelta64(self.delta_time, 'm')

    def fill_footprints(self):
        _footprints = {}
        for file in self.comparison_files:
            opened_file = call_meta_class(file, listing=self.listing)
            if self.product.footprint.intersects(
                    opened_file.footprint(self.product.footprint, self.start_date, self.stop_date)):
                _footprints[file] = self.product.footprint \
                    .intersection(opened_file.footprint(self.product.footprint, self.start_date, self.stop_date))
            else:
                _footprints[file] = None
        # if no common values, let the footprint with the value None
        if all(value is None for value in _footprints.values()):
            pass
        else:
            self.common_footprints = _footprints

    def fill_colocated_files(self):
        _colocated_files = []
        for file in self.comparison_files:
            try:
                opened_file = call_meta_class(file)
                if has_intersection(self.product, opened_file, delta_time=self.delta_time):
                    _colocated_files.append(file)
            except FileNotFoundError:
                pass
            #print(f"The file {file} has been treated. \n Progression : {(self.comparison_files.index(file) +1 ) * 100 / len(self.comparison_files)}\n ########")
        if len(_colocated_files) > 0:
            self.colocated_files = _colocated_files

    @property
    def has_coloc(self):
        if self.colocated_files is None:
            return False
        else:
            return True

    @property
    def get_comparison_files(self):
        """
        Get all the files from the specified database that match with the start and stop dates

        Returns
        -------
        list
            Comparison files
        """
        all_comparison_files = get_all_comparison_files(self.start_date, self.stop_date, ds_name=self.ds_name,
                                                        level=self.level)
        if self.product_id in all_comparison_files:
            all_comparison_files.remove(self.product_id)
        return all_comparison_files
