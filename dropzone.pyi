# -*- coding: utf-8 -*-
"""
The function calls and associated type information for Dropzone's API.
Although the `official documentation on GitHub
<https://github.com/aptonic/dropzone4-actions>`_.
uses the variable name ``dz``, it's a module imported like
``import dropzone as dz`` and then added to ``__builtins__``.

"""

from typing import AnyStr, NoReturn, Optional, Iterable, overload, Literal


def add_dropbar(items: Iterable[AnyStr]) -> NoReturn:
    """
    If your action produces a file output, this method makes the output file
    available for easy dragging somewhere else. Note that **Drop Bar** just
    keeps references to files, and not the files themselves. A file needs to
    exist somewhere else on the filesystem for it to be added to and dragged
    out of **Drop Bar**.

    To add a file to **Drop Bar**, simply call the ``dz.add_dropbar`` method
    with an array of files you want to add. A new **Drop Bar** will be created
    in the *Dropzone* grid with the file(s) that you pass to this method.

    :param items: a list of filepaths to show in Drop Bar
    """
    ...

def alert(title: AnyStr, message: AnyStr) -> NoReturn:
    """
    Shows a popup alert box with the given ``title`` and ``message``. It must
    be dismissed by the user clicking "OK" before progress will continue.

    :param title: the title text of the notification
    :param message: the body text of the notification
    """
    ...

def begin(message: AnyStr) -> NoReturn:
    """
    Tells *Dropzone* to show a new task status progress bar in the grid and to
    set the label above the progress bar to the specified message. You can call
    this method multiple times as your action runs to update the displayed text.

    :param message: a message to display over the new progress bar
    """
    ...

def determinate(value: bool) -> NoReturn:
    """
    ``True`` indicates that you will be providing progress information to
    *Dropzone* from your script as a percent, and ``False`` means that no
    progress information will be provided.

    :param value: ``True`` if this task will provide progress updates or not
    """
    ...

def error(title: AnyStr, message: AnyStr) -> NoReturn:
    """
    Shows a popup error box with the given ``title`` and ``message``.

    :param title: the title text of the notification
    :param message: the body text of the notification
    """
    ...

def fail(message: AnyStr) -> NoReturn:
    """
    Shows a notification center notification that the task failed. Also
    terminates the task and makes a cross show in the status item to indicate
    task failure. If you call this you don't need to call ``dz.url`` or
    ``dz.text`` after.

    :param message: descriptive error message that will appear in a notification
                    box to the user
    """
    ...

def finish(message: AnyStr) -> NoReturn:
    """
    Shows a notification center notification that the task is finishing with
    the given message. To actually end the task and remove the task status bar
    from the grid you have to call ``dz.url`` after this.

    :param message: the body text for the "Custom Task Completed" notification
    """
    ...

def inputbox(title: AnyStr, prompt_text: AnyStr,
             field_name: Optional[AnyStr] = "Filename") -> AnyStr:
    """
    Shows an input box with the given ``title`` and prompt ``text``. If no
    input is entered or the Cancel button is clicked the script exits and
    calls ``dz.fail`` with an appropriate message. The ``field_name`` parameter
    is optional, and is used if the user doesn't enter any input to show a
    '{field_name} cannot be empty.' ``dz.fail`` message. The ``field_name``
    parameter defaults to 'Filename'.

    :param title: the title text of the notification
    :param prompt_text: the label for the text field of this input box
    :param field_name: a helpful name for what it is the user is inputting
    """
    ...

def percent(value: float) -> NoReturn:
    """
    *Dropzone* updates the task progress bar to reflect this value. You only
    need to call this method when in determinate mode.

    :param value: an integer value between 0 and 100
    """
    ...

def read_clipboard() -> AnyStr:
    """
    Returns the user's clipboard's current contents.

    :return: the current value the user has in their clipboard
    """
    ...

def remove_value(value_name) -> NoReturn:
    """
    Remove values stored for a grid action.

    :param value_name: the name of setting to delete
    """
    ...

def save_value(value_name: AnyStr, value: AnyStr) -> NoReturn:
    """
    Store string values in the *Dropzone* database. This is useful for storing
    configuration for your action - e.g. when your action first runs you could
    use Pashua to prompt for a setting and then store the result. When your
    action is next run, all saved values are set as environment variables and
    can be accessed using ``os.environ['stored_value_name']``. You can see
    which variables were set in the debug console each time your action is run.
    If the user has multiple instances of your action setup in the grid, the
    stored values are unique to each instance.

    :param value_name: the name you want to use when retrieving this value from
                       os.environ
    :param value: the value you wish to store
    """
    ...

def temp_folder() -> AnyStr:
    """
    A path that is writeable by both the sandboxed and unsandboxed versions
    of Dropzone

    :return: a path to a directory you can read and write files to
    """
    ...

def text(message: AnyStr) -> NoReturn:
    """
    You can use this in place of ``dz.url``. It behaves exactly the same except
    that it does not attempt to encode the argument as a URL so you can place
    raw strings of text on the pasteboard.

    :param message: the raw text to place in the user's clipboard
    """
    ...

@overload
def url(value: Literal[False]) -> NoReturn:
    ...

@overload
def url(value: AnyStr) -> NoReturn:
    ...

def url(value: AnyStr, title: Optional[AnyStr] = None) -> NoReturn:
    """
    Sets a **URL** to be placed on the pasteboard. This is useful for writing
    actions that result in content being made available at a URL so a user can
    quickly paste the URL into other applications. You can optionally provide a
    title for the URL that will be shown in the *Recently Shared* popup menu.
    If you don't specify a title, then the first dragged filename will be used
    or the truncated text if text was dragged.

    If you do **not** wish to specify a URL, **you must still call either this
    method with false as the argument or** ``dz.text``. Calling this method causes the task status bar to be removed from the grid and the task resources to be cleaned up. You should only call this method once and it should be the last method your action calls.

    :param value: a URL to add to the clipboard or False to signify no clipboard
                  value should be added
    :param title: optional title for the Recently Shared popup menu
    """
    ...


def pashua(config: AnyStr):
    ...
