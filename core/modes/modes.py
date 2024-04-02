from talon import Context, Module, actions, app
from talon.grammar import Phrase
from typing import Union

mod = Module()
ctx = Context()

ctx_dictation = Context()
ctx_dictation.matches = r"""
mode: dictation
"""

ctx_sv = Context()
ctx_sv.matches = r"""
language: sv
"""

mod.list("sleep_phrase", "Phrase used to sleep Talon")
sleep_phrases = ["drowse"]
ctx.lists["user.sleep_phrase"] = {sleep_phrases[0]}
ctx_sv.lists["user.sleep_phrase"] = sleep_phrases


@ctx.action_class("user")
class UserActions:
    def command_dictation_mode_toggle():
        actions.user.dictation_mode()


@ctx_dictation.action_class("user")
class DictationUserActions:
    def command_dictation_mode_toggle():
        actions.user.command_mode()

modes = {
    "admin": "enable extra administration commands terminal (docker, etc)",
    "debug": "a way to force debugger commands to be loaded",
    "ida": "a way to force ida commands to be loaded",
    "presentation": "a more strict form of sleep where only a more strict wake up command works",
}

for key, value in modes.items():
    mod.mode(key, value)


@mod.action_class
class Actions:
    def talon_mode():
        """For windows and Mac with Dragon, enables Talon commands and Dragon's command mode."""
        actions.speech.enable()

        engine = speech_system.engine.name
        # app.notify(engine)
        if "dragon" in engine:
            if app.platform == "mac":
                actions.user.engine_sleep()
            elif app.platform == "windows":
                actions.user.engine_wake()
                # note: this may not do anything for all versions of Dragon. Requires Pro.
                actions.user.engine_mimic("switch to command mode")

    def command_mode(phrase: Union[Phrase, str] = None):
        """Enter command mode and re-evaluate phrase"""
        ctx.tags = []
        actions.mode.disable("dictation")
        actions.mode.enable("command")
        if phrase:
            actions.user.rephrase(phrase, run_async=True)

    def dictation_mode(phrase: Union[Phrase, str] = None):
        """Enter dictation mode and re-evaluate phrase"""
        actions.user.dictation_format_reset()
        actions.mode.disable("command")
        actions.mode.enable("dictation")
        if phrase:
            actions.user.rephrase(phrase, run_async=True)

    def command_dictation_mode_toggle():
        """Toggle between command and dictation mode"""

    def swedish_dictation_mode(phrase: Union[Phrase, str] = None):
        """Enter swedish dictation mode and re-evaluate phrase"""
        ctx.tags = ["user.swedish"]
        actions.user.dictation_mode(phrase)

    def mixed_mode(phrase: Union[Phrase, str] = None):
        """Enter mixed mode and re-evaluate phrase"""
        actions.user.dictation_format_reset()
        actions.mode.enable("dictation")
        if phrase:
            actions.user.rephrase(phrase, run_async=True)

    def talon_sleep():
        """Put Talon to sleep"""
        actions.speech.disable()
        actions.user.mouse_sleep()
        actions.user.notify("Talon sleeping")

    def talon_wake():
        """Wake Talon from sleep"""
        actions.user.abort_current_phrase()
        actions.speech.enable()
        actions.user.mouse_wake()
        actions.user.notify("Talon awake")
        if not actions.user.sound_microphone_enabled():
            actions.user.sound_microphone_enable(True)


def on_launch():
    """Disable not used modes and put Talon to sleep"""
    actions.mode.disable("face")
    if not actions.user.talon_was_restarted():
        actions.user.talon_sleep()


app.register("launch", on_launch)
