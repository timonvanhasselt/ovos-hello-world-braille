import threading
import time
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_workshop.intents import IntentBuilder
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
import os
import sys

# Append the directory to sys.path
sys.path.append('/usr/lib/python3/dist-packages/')
import brlapi

DEFAULT_SETTINGS = {
    "log_level": "WARNING"
}

class HelloWorldSkillBraille(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.override = True

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=False,
            gui_before_load=False,
            requires_internet=False,
            requires_network=False,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=True,
            no_gui_fallback=True,
        )
    
    def initialize(self):
        self.settings.merge(DEFAULT_SETTINGS, new_only=True)
        self.settings_change_callback = self.on_settings_changed
        self.add_event("hello.world", self.handle_hello_world_intent)
        self.my_var = "hello world"

    def on_settings_changed(self):
        LOG.info("Settings changed!")

    @property
    def log_level(self):
        return self.settings.get("log_level", "INFO")

    @intent_handler(IntentBuilder("ThankYouIntent").require("ThankYouKeyword"))
    def handle_thank_you_intent(self, message):
        text_to_display = self.dialog_renderer.render("thank.you")  # Get text from dialog file
        self.speak_and_display(text_to_display)


    @intent_handler("HowAreYou.intent")
    def handle_how_are_you_intent(self, message):
        text_to_display = self.dialog_renderer.render("how.are.you")  # Get text from dialog file
        self.speak_and_display(text_to_display)


    @intent_handler(IntentBuilder("HelloWorldIntent").require("HelloWorldKeyword"))
    def handle_hello_world_intent(self, message):
        text_to_display = self.dialog_renderer.render("hello.world")  # Get text from dialog file
        self.speak_and_display(text_to_display)

    def display_text(self, text):
        self.display_in_braille(text)
        LOG.info("Text successfully displayed: '{}'".format(text))

    def display_in_braille(self, text):
        tty_number = 1  # Set the TTY number to 1
        try:
            handle = brlapi.Connection()  # Connect to BrlAPI
            handle.enterTtyMode(tty_number)  # Enter TTY mode
            chunks = [text[i:i+40] for i in range(0, len(text), 40)]
            for chunk in chunks:
                handle.writeText(chunk)  # Write chunk of text to the display
                time.sleep(5)
        except Exception as e:
            LOG.error("Error during BrlAPI operations:", e)
        finally:
            try:
                handle.leaveTtyMode()  # Leave TTY mode
            except Exception as e:
                LOG.error("Error leaving TTY mode:", e)
            handle.closeConnection()  # Close connection

    def speak_and_display(self, text):
        # Define functions for speech output and Braille display
        def speak_text(text):
            self.speak(text)

        def display_braille(text):
            self.display_text(text)

        # Create threads for speech output and Braille display
        speech_thread = threading.Thread(target=speak_text, args=(text,))
        braille_thread = threading.Thread(target=display_braille, args=(text,))

        # Start the threads
        speech_thread.start()
        braille_thread.start()

        # Wait for both threads to finish
        speech_thread.join()
        braille_thread.join()

    def stop(self):
        pass
