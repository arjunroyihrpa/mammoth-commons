__mammoth_progress_callback = lambda progress, message: print(
    message + " " + "█" * int(progress * 10), end="\r"
)
__mammoth_progress_end = lambda: print(" " * 80, end="\r")


def register_progress_callback(callback, end=None):
    global __mammoth_progress_callback
    global __mammoth_progress_end

    def do_nothing():
        pass

    __mammoth_progress_callback = callback
    __mammoth_progress_end = do_nothing if end is None else end


def notify_progress(progress, message):
    global __mammoth_progress_callback
    __mammoth_progress_callback(progress, message)
    if progress >= 1:
        notify_end()
        return


def notify_end():
    global __mammoth_progress_end
    __mammoth_progress_end()
