import time


class Configuration:
    """ The configuration for an experiment """
    def __init__(self, participant, age_group):
        """ Creates a configuration with the following values"""
        self.output_location = "data"
        self.practice_run = True

        self.task_no_keyboard_response_time = 0.150
        self.task_interstimulus_interval = 0
        self.task_feed_back_display_time = 0.500

        # ===================== Below variables are generated! ==========================
        # Save the age group and participant
        self.participant = participant
        self.age_group = age_group

        # Get the numbers from the participant_id string
        self.participant_num = int("".join([c for c in self.participant if c.isdigit()]))

        self.date = time.strftime('%c')
        self.condition = self.participant_num % 4  # can be 0, 1, 2, or 3

        # True in half of the trials, in which letter will occur more often with the '@'
        self.letters_corr_at = self.condition % 2 == 0

        # True in half of the trials, when false pair them with 'k'
        self.letter_pair_condition = self.condition // 2 == 0

        # More useful version of above variable to use in code
        self.letter_key = 'j' if self.letter_pair_condition else 'f'
        self.number_key = 'f' if self.letter_pair_condition else 'j'
