from random import choice, random


class MultipleChoiceQuestion:
    """ A class for asking multiple choice questions"""

    class DataPoint:
        """ A DataPoint for this multiple choice question"""

        def __init__(self, question, options, config):
            """ Initialize a DataPoint
            @param str question:
            @param list of str options:
            @param config.Configuration config:
            """
            self.question = question
            self.options = options
            self.__parent = config
            self.user_response = None

    def __init__(self, experiment, question, options, prompt_font_size=120):
        """ Initializes this Question
        @param experiment.Experiment experiment:
        @param str question:
        @param list of str options:
        """
        self.experiment = experiment
        self.window = experiment.window
        self.config = experiment.config

        self.prompt_font_size = prompt_font_size

        self.to_save = self.DataPoint(question, options, self.config)

    def ask(self):
        """ Ask this question and record the response"""
        self.to_save.user_response = self.experiment.window.wait_for_choice(self.to_save.question,
                                                                            self.to_save.options,
                                                                            prompt_font_size=self.prompt_font_size)
        self.experiment.push_data(self.to_save)


class OpenEndedQuestion:
    """ A class for asking open ended questions"""

    class DataPoint:
        """ A DataPoint for this multiple choice question"""

        def __init__(self, question, config):
            """ Initialize a DataPoint
            @param str question:
            @param config.Configuration config: """
            self.question = question
            self.__parent = config
            self.user_response = None

    def __init__(self, experiment, question):
        """ Initializes this Question class with question {question},
        for the experiment {experiment}
        @param experiment.Experiment experiment:
        @param str question:
        """
        self.experiment = experiment
        self.window = experiment.window
        self.config = experiment.config

        self.to_save = self.DataPoint(question, self.config)

    def ask(self):
        """ Ask this question and record the response"""
        self.to_save.user_response = self.window.get_input_text(self.to_save.question, prompt_font_size=24)
        self.experiment.push_data(self.to_save)


def random_number():
    """ Return a random number char allowed in this task (from 2 to 8 inclusive)"""
    return choice("2345678")


def random_letter():
    """ Return a random upper-case letter char allowed in this task (A - H inclusive)"""
    return choice("ABCDEFGH")


def run(experiment):
    """ Run the post-task for this experiment"""
    # Start a new section of the experiment we are in
    experiment.new_section('post-task')

    # Show some slides before the post-task
    experiment.window.show_image_sequence('instructions', 'start')

    # The answers that people can give
    yes_no_answer = ["Yes", "No"]
    quantity_answer = ["Very little", "A bit", "A lot"]

    prompt = "Did you notice any relationship between the symbols and the letters?"
    noticed_relationship = MultipleChoiceQuestion(experiment, prompt, yes_no_answer, prompt_font_size=24)

    prompt = "Do you have any thoughts on the experiment?"
    open_ended = OpenEndedQuestion(experiment, prompt)

    # Create the number questions and alphabetic questions
    number_questions = [MultipleChoiceQuestion(experiment, "{0} {1} {0}".format(c, random_number()), quantity_answer)
                        for c in "#@*"]
    alpha_questions = [MultipleChoiceQuestion(experiment, "{0} {1} {0}".format(c, random_letter()), quantity_answer)
                       for c in "#@*"]

    # Half the time number questions should come first,
    # the other half alphabetic questions
    questions = number_questions + alpha_questions if random() > 0.5 else alpha_questions + number_questions

    # Ask if they noticed any relationships
    noticed_relationship.ask()

    # Ask for thoughts
    open_ended.ask()

    # Show some images before the correlation questions
    experiment.window.show_image_sequence('instructions', 'before_corr_questions')

    # Ask the remaining questions
    for question in questions:
        question.ask()

    # Show some slides after the experiment ends
    experiment.window.show_image_sequence('instructions', 'end')

    # Save the gathered data
    experiment.save_data()
