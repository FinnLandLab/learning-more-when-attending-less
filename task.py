""" A package with the code for the main task"""

from psychopy import core
import random


class Trial:
    """ A trial in the main task"""

    class DataPoint:
        """ A DataPoint for a trial"""

        def __init__(self, character, flanker, block):
            """ Creates a DataPoint for a trial in a block

            @param str character:
            @param str flanker:
            @param Block block:
            """
            # Get the character and flanker for this trial
            self.char = character
            self.flanker = flanker

            self.user_input = None
            self.response_time = None
            self.correct = None

            self.__parent = block.to_save

            # Get the type of the trial
            if character in '23456789':
                self.type = 'numeric'
            elif character.isalpha():
                self.type = 'alphabetic'
            else:
                raise Exception("Character '{}' is not in the allowed set of characters".format(character))

            # Get the correct keys for this trial:
            if self.type == 'alphabetic':
                self.right_key = block.config.letter_key
                self.wrong_key = block.config.number_key
            else:
                self.right_key = block.config.number_key
                self.wrong_key = block.config.letter_key

            # Get whether this trial's flanker is helpful or not
            if flanker == '#':
                self.helpful = 0
            elif flanker == '@':
                if self.type == 'alphabetic':
                    self.helpful = 1 if block.config.letters_corr_at else -1
                else:
                    self.helpful = -1 if block.config.letters_corr_at else 1
            elif self.flanker == '*':
                if self.type == 'alphabetic':
                    self.helpful = -1 if block.config.letters_corr_at else 1
                else:
                    self.helpful = 1 if block.config.letters_corr_at else -1

    def __init__(self, character, flanker, block):
        """ Initializes the Trial class

        @param str character:
        @param str flanker:
        @param Block block:
        """

        self.experiment = block.experiment
        self.window = block.window
        self.config = block.config

        self.to_save = self.DataPoint(character, flanker, block)

    def feedback(self):
        """ Give the user feedback on whether they got the answer right or wrong"""
        # Show feed-back
        if self.to_save.correct:
            self.window.show_image("images/task/feedback/correct.png")
        else:
            self.window.show_image("images/task/feedback/incorrect.png")
        # Wait a little bit
        core.wait(self.config.task_feed_back_display_time)

    def run(self):
        """ Run this trial"""
        timer = core.Clock()

        text = '{1} {0} {1}'.format(self.to_save.char, self.to_save.flanker)

        legend = '{0} for  letters, {1} for numbers'.format(self.config.letter_key, self.config.number_key)

        # Experiment with size here!
        self.window.show_text(text=text, font_size=120,
                              legend=legend, legend_font_size=40)

        # Don't record responses for the first few milliseconds
        if self.config.task_no_keyboard_response_time >= 0:
            core.wait(self.config.task_no_keyboard_response_time)

        # Get the user's response
        self.to_save.user_input = self.window.wait_for_prompt(keys=[self.to_save.right_key, self.to_save.wrong_key])
        self.to_save.response_time = timer.getTime()
        self.to_save.correct = (self.to_save.user_input == self.to_save.right_key)

        # Give the user some feedback
        self.feedback()


class Block:
    """ The Block class.
    Each block has 64 trials. 32 trials are numeric, 32 are alphabetic.
    The number of flankers per block will vary.
    """

    class DataPoint:
        """ A DataPoint for a Block"""

        def __init__(self, block_num, config):
            """ Create a DataPoint for a block"""
            self.block_num = block_num
            self.trial_num = None
            self.total_trial_num = None
            self.__parent = config

    def __init__(self, experiment, type_flanker_amounts, block_num, save):

        """ Initializes the block class

        @param experiment.Experiment experiment:
        @param dict[str, dict[str, list[int]] type_flanker_amounts:
        @param int block_num:
        """
        self.experiment = experiment
        self.window = experiment.window
        self.config = experiment.config

        self.save = save

        self.to_save = self.DataPoint(block_num, self.config)

        # The numbers and letters to be included
        nums = '23456789'
        letters = 'ABCDEFGH'

        # All characters to be used in this block
        nums = list(nums * 4)
        letters = list(letters * 4)

        # Shuffle both lists
        random.shuffle(nums)
        random.shuffle(letters)

        # Get iterators for both lists
        num_gen = iter(nums)
        letter_gen = iter(letters)

        # Make a list to store the trials for the block
        self.trials = []

        # Populate the list with trials
        for flanker in type_flanker_amounts['alphabetic']:
            for _ in range(type_flanker_amounts['alphabetic'][flanker]):
                self.trials.append(Trial(next(letter_gen), flanker, self))

            for _ in range(type_flanker_amounts['numeric'][flanker]):
                self.trials.append(Trial(next(num_gen), flanker, self))

        # Randomize the trial presentation
        random.shuffle(self.trials)

    def run(self):
        """ Run this block"""
        for self.to_save.trial_num in range(len(self.trials)):
            self.to_save.total_trial_num = (self.to_save.block_num * len(self.trials)) + self.to_save.trial_num
            trial = self.trials[self.to_save.trial_num]
            trial.run()
            if self.save:
                self.experiment.push_data(trial.to_save)
            if self.config.task_interstimulus_interval >= 0:
                core.wait(self.config.task_interstimulus_interval)


def run(experiment):
    """ Run this task for the given experiment

    @param experiment.Experiment experiment:
    @return:
    """

    # Start a new section of the experiment we are in
    experiment.new_section('task')

    # Show some instructions
    experiment.window.show_image_sequence('instructions', 'start_{}_letter'.format(experiment.config.letter_key))

    # Show a practice block
    if experiment.config.practice_run:
        experiment.window.show_image_sequence('instructions', 'practice')
        practice_trial_amounts = {'alphabetic': {'$': 5}, 'numeric': {'$': 5}}
        Block(experiment, practice_trial_amounts, -1, save=False).run()

    # How many trials for each type of character and each type of flanker
    trial_amounts = {'alphabetic': {'#': [8] * 6}, 'numeric': {'#': [8] * 6}}

    # Assume that experiment.letters_corr_at is True
    # Note we know that for each character the trial amounts add up to 32
    trial_amounts['alphabetic']['@'] = [21] * 4 + [22] * 2
    random.shuffle(trial_amounts['alphabetic']['@'])
    trial_amounts['alphabetic']['*'] = [24 - i for i in trial_amounts['alphabetic']['@']]

    trial_amounts['numeric']['*'] = [21] * 4 + [22] * 2
    random.shuffle(trial_amounts['numeric']['*'])
    trial_amounts['numeric']['@'] = [24 - i for i in trial_amounts['numeric']['*']]

    # But if experiment.letters_corr_at is False, switch the occurrences
    if not experiment.config.letters_corr_at:
        trial_amounts['alphabetic'], trial_amounts['numeric'] = trial_amounts['numeric'], trial_amounts['alphabetic']

    experiment.window.show_image_sequence('instructions', 'task')
    for block_num in range(6):
        # Take only the i'th value of the trial_amounts amounts
        type_flanker_amounts = {char_type: {flanker_type: trial_amounts[char_type][flanker_type][block_num]
                                            for flanker_type in trial_amounts[char_type]}
                                for char_type in trial_amounts}

        # Run the block that is represented by the trial amounts
        Block(experiment, type_flanker_amounts, block_num, save=True).run()

        # Give them a break before the next block, unless it's the last block
        if block_num < 5:
            experiment.window.show_image_sequence('instructions', 'break')

    experiment.save_data()
