import os
import visual
import config
from pandas import DataFrame


class Experiment:
    """ A general experiment class containing all the information for the experiment.
    """

    def __init__(self):
        """ Initializes a experiment class. """
        self.name = "Smiley"
        self.section = 'setup'
        self._data = []
        self._data_type = None

        self.participant, self.age_group = visual.ask_user_info(self.name)
        self.config = config.Configuration(self.participant, self.age_group)

        self.window = visual.Window(self)

    def push_data(self, data_point):
        """ Adds a data point to be saved later.

            @param lst data_point: The data point to be saved
            @rtype None
        """
        if self._data_type is None and data_point is not None:
            self._data_type = type(data_point)
        elif type(data_point) != self._data_type or data_point is None:
            raise ValueError("data_point ", data_point, "has the wrong type")

        to_save = dict(vars(data_point))
        while '_DataPoint__parent' in to_save:
            parent = to_save.pop('_DataPoint__parent')
            to_save.update(vars(parent))

        for key in to_save:
            if type(to_save[key]) is bool:
                to_save[key] = int(to_save[key])

        self._data.append(to_save)

    def new_section(self, section_name):
        """ Start a new section of the experiment"""
        self.section = section_name
        self._data = []
        self._data_type = None

    def save_data(self):
        """ Saves the data data that was pushed since the last time new section was called to:
        "{section}.csv" and resets the data to be saved

        """

        dir_loc = "{0}/{1}/".format(self.config.output_location, self.section)
        # Make sure the file directory exists
        if not os.path.exists(dir_loc):
            os.makedirs(dir_loc)

        # Get the output file
        file_loc = dir_loc + self.participant + ".csv"
        df = DataFrame(self._data)
        df.to_csv(file_loc, index=False)

    def close(self):
        """ Ends the experiment. Does not save any data"""
        self.window.close()