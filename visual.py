""" A package that focuses on the user interaction"""

import sys
from glob import glob

import psychopy.tools.monitorunittools
from psychopy import visual, event, gui, core


def ask_user_info(title):
    """ A method used to ask the user for their participant id and their age group.
        Will quit if the user presses 'cancel'

        @param str title: The title of the pop-up box
        @return (str, str): A tuple with of (participant id, age group)
    """
    info = {'Participant': '', 'Age group': ''}

    # Store info about the experiment session
    dialogue = gui.DlgFromDict(dictionary=info, title=title)

    # User pressed cancel, so quit!
    if dialogue.OK is False:
        sys.exit()

    # Return the results
    return info['Participant'], info['Age group']


def pt_to_cm(pt):
    """ Convert from pt to cm
    @param float pt: pt to be converted
    @return float: cm equivalent
    """
    return pt * 0.035277778


class Window:
    """ A class used to interface the interaction with the user"""

    def __init__(self, experiment):
        """ Initializes the window class"""
        self.experiment = experiment
        # Create the window object we'll use
        self._window = visual.Window(fullscr=True, monitor="testMonitor", units="norm", color=1)

        self._instruction_image = visual.ImageStim(win=self._window, units='norm', size=(2, 2))

    def norm_to_cm(self, point):
        x = psychopy.tools.monitorunittools.pix2cm(point[0] * self._window.size[0] / 2.0, self._window.monitor)
        y = psychopy.tools.monitorunittools.pix2cm(point[1] * self._window.size[1] / 2.0, self._window.monitor)
        return x, y

    def px_to_cm(self, point):
        x = psychopy.tools.monitorunittools.pix2cm(point[0], self._window.monitor)
        y = psychopy.tools.monitorunittools.pix2cm(point[1], self._window.monitor)
        return x, y

    def px_to_norm(self, point):
        x = 2.0 * point[0] / self._window.size[0]
        y = 2.0 * point[1] / self._window.size[1]
        return x, y

    def scalar_norm_to_cm(self, scalar):
        return self.norm_to_cm((scalar, 0))[0]

    def scalar_px_to_cm(self, scalar):
        return self.px_to_cm((scalar, 0))[0]

    def show_image_sequence(self, genre, subgenre='', task=None, extension='.png'):
        """ Shows all the images which follow the pattern
        'image/{task}/{genre}/{subgenre}/*{extension}', in ascending order.

        @param genre:
        @param subgenre:
        @param task:
        @param extension:
        @return:
        """
        if task is None:
            task = self.experiment.section
        image_paths = glob("images/{0}/{1}/{2}/*{3}".format(task, genre, subgenre, extension))
        image_paths.sort()

        for image_path in image_paths:
            self.show_image(image_path)
            self.wait_for_prompt()

    def show_image(self, path):
        """ Show the image at the given path.

        @param str path: the path of the image to be shown
        @rtype: None
        """
        self._instruction_image.image = path
        self._instruction_image.draw()
        self._window.flip()

    def show_text(self, text, font_size=24, legend=None, legend_font_size=24):
        """ Shows the text text on the main screen. font size in pt. Optionally shows a legend beneath the text"""
        # convert size to cm
        font_size_cm = pt_to_cm(font_size)
        text_element = visual.TextStim(self._window, text=text, wrapWidth=None, color=-1,
                                       font='Times New Roman', units='cm', height=font_size_cm)
        text_element.draw()

        if legend is not None:
            legend_font_size_cm = pt_to_cm(legend_font_size)
            text_element = visual.TextStim(self._window, text=legend, wrapWidth=None, color=-1, font='Times New Roman',
                                           units='cm', height=legend_font_size_cm, alignVert='bottom',
                                           pos=self.norm_to_cm((0, -1)))
            text_element.draw()
        self._window.flip()

    def wait_for_choice(self, prompt, choices, prompt_font_size=24, instruction_font_size=20, choice_font_size=20):
        """ Displays the given choices in lst choices with the given str prompt,
            and waits until one is picked. """
        # Calculate font sizes in cm
        prompt_font_size = pt_to_cm(prompt_font_size)
        instruction_font_size = pt_to_cm(instruction_font_size)
        choice_font_size = pt_to_cm(choice_font_size)

        # Calculate maximum size of each button
        button_max_width = self.scalar_norm_to_cm(2 / (len(choices) + 1.0))
        buttons = []

        # Keep track of the maximum text height
        max_button_height = 0

        for i in range(len(choices)):
            # Figure out where to place the button using norm units
            x_loc = 2 * ((i + 1.0) / (len(choices) + 1)) - 1
            y_loc = -0.5

            # Convert to cm
            x_loc, y_loc = self.norm_to_cm((x_loc, y_loc))

            # Create and draw the text to display on the button
            text = visual.TextStim(self._window, text=choices[i], wrapWidth=button_max_width - 1,
                                   color=-1, font='Times New Roman', units='cm',
                                   pos=(x_loc, y_loc), height=choice_font_size)
            text.draw()

            # Find the dimensions of the text's bounding box in cm
            text_width, text_height = self.px_to_cm(text.boundingBox)

            # Calculate the size of the button we'll draw
            button_width = min(1 + text_width, button_max_width)
            button_height = 1 + text_height

            # Keep track of the maximum button height
            max_button_height = max(button_height, max_button_height)

            # Create and draw the box that will represent this button
            rect = visual.Rect(self._window, button_width, button_height, lineColor=-1,
                               pos=(x_loc, y_loc), units='cm')
            rect.draw()

            # Add the rectangle to the set of rectangles to check for input
            buttons += [rect]

        # Create and display the prompt
        text = visual.TextStim(self._window, text=prompt, wrapWidth=self.scalar_norm_to_cm(2), color=-1,
                               font='Times New Roman', units='cm', height=prompt_font_size)
        text.draw()

        # Get the height of the prompt text
        x_loc = self.scalar_norm_to_cm(-0.9)
        y_loc = (instruction_font_size + prompt_font_size) / 2

        # Tell the user to use their mouse
        text = visual.TextStim(self._window, text="Use your mouse to click:", wrapWidth=self.scalar_norm_to_cm(2),
                               color=-1, font='Times New Roman', alignHoriz='left',
                               pos=(x_loc, y_loc),
                               units='cm', height=instruction_font_size)
        text.draw()

        self._window.flip()

        mouse = event.Mouse(win=self._window)
        # Wait for the user to click on one of them
        while True:
            for i in range(len(buttons)):
                if mouse.isPressedIn(buttons[i], buttons=[0]):
                    return choices[i]

            if len(event.getKeys(keyList=["escape"])) != 0:
                self.experiment.save_data()
                sys.exit()

            core.wait(0.01, hogCPUperiod=0)

    def wait_for_prompt(self, timer=None, keys='space'):
        """ Waits indefinitely until a key in keys is pressed. Return the key that was pressed.

            If a timer is provided, will wait for prompt until the timer runs out. If the timer runs out,
            None will be returned.

            @rtype: str|None
        """
        # Clear the key's buffer:
        event.clearEvents()

        if isinstance(keys, str):
            keys = [keys]

        keys = [k.lower() for k in keys] + [k.upper() for k in keys]

        # Wait for input
        while timer is None or timer.getTime() >= 0:
            # Get the keys that were pressed that we are watching
            keys_pressed = event.getKeys(keyList=keys)
            if len(keys_pressed) != 0:
                return keys_pressed[0]

            if len(event.getKeys(keyList=["escape"])) != 0:
                self.experiment.save_data()
                sys.exit()

        return None

    def close(self):
        """ Closes this window"""
        self._window.close()

    def get_input_text(self, prompt=None, prompt_font_size=24, input_font_size=20):
        """ Gets user input as text. The prompt

        @return: The text the user inputted until they pressed the key '0'
        @rtype: str
        """
        # Calculate font sizes in cm
        prompt_font_size = pt_to_cm(prompt_font_size)
        input_font_size = pt_to_cm(input_font_size)

        # Clear the keys buffer
        event.getKeys()

        # Set up the prompt's textbox's text
        prompt = "" if prompt is None or prompt == "" else prompt + ". "
        text = prompt + "Please type in your answer, press the key '0' to submit it:"

        # Make the prompt textbox
        text_instr = visual.TextStim(win=self._window, text=text, color=-1, wrapWidth=self.scalar_norm_to_cm(1.8),
                                     alignHoriz='left', alignVert='top', units='cm',
                                     pos=self.norm_to_cm((-.9, .9)), height=prompt_font_size)

        # Set up a textbox for user input
        input_text = ""

        input_box = visual.TextStim(win=self._window, text=input_text, color=-1, units='cm', height=input_font_size,
                                    wrapWidth=self.scalar_norm_to_cm(1.8), alignHoriz='left', alignVert='top',
                                    pos=self.norm_to_cm((-.9, 0)))
        input_box.draw()

        # Get user input
        inputting = True

        while inputting:
            # Get the keys that were pressed
            keys = event.getKeys()

            # Handle each key. Some key presses have special meaning
            for key in keys:
                if key == '0':
                    # 0 means we submit the captured text
                    inputting = False
                    break
                elif key == 'escape':
                    # escape means we exit the experiment
                    self.experiment.save_data()
                    core.quit()
                elif key == 'space':
                    # space means we add a blank
                    input_text += ' '
                elif key == 'backspace':
                    # backspace means we delete a char
                    if len(input_text) > 0:
                        input_text = input_text[:-1]
                elif key == 'return':
                    # return means we add a newline
                    input_text += '\n'
                elif key == 'comma':
                    input_text += ','
                elif key == 'period':
                    input_text += '.'
                elif len(key) == 1 and key.isalnum():
                    # Regular character to be inputted
                    input_text += key

            # Draw what the user wrote and the instructions to the screen
            input_box.text = input_text
            input_box.draw()
            text_instr.draw()
            self._window.flip()

            # Only check evey 100 ms
            core.wait(0.1, 0)

        return input_text
