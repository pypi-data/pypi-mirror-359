# %% Functions

## Dependencies
from datetime import datetime
import sys
import logging
import getpass
import subprocess
import time


## Round off columns
def round_columns(df, columns, digits=2):
    """
    Rounds specified columns of a Pandas DataFrame to a given number of decimal places.

    Args:
        df: The Pandas DataFrame.
        columns: A list of column names to round.
        digits: The number of decimal places to round to.  Defaults to 2.

    Returns:
        A new Pandas DataFrame with the specified columns rounded, or the original
        DataFrame if no columns are provided or if the specified columns are not found.
        Prints a warning if some columns are not found.
    """

    if not columns:  # Handle empty column list
        return df

    df_copy = (
        df.copy()
    )  # Important: Create a copy to avoid modifying the original DataFrame

    not_found_cols = []
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].round(digits)
        else:
            not_found_cols.append(col)

    if not_found_cols:
        print(f"Warning: Columns not found: {', '.join(not_found_cols)}")

    return df_copy


## log_start
def log_start(folder_location):
    """Start logging process"""

    global file_handler, __log_name

    # Check if the logger is already set up
    if "file_handler" in globals() and file_handler is not None:
        print(
            "\nWARNING : Logging is already in progress. Call log_end() before starting a new log."
        )
        return

    class LogPrints:
        def __init__(self, logger, level=logging.INFO):
            self.logger = logger
            self.level = level
            self.linebuf = ""

        def write(self, buf):
            self.linebuf += buf
            lines = self.linebuf.split("\n")
            for line in lines[:-1]:
                self.logger.log(self.level, line)
            self.linebuf = lines[-1]

        def flush(self):
            pass

    # Define file_dt globally for demonstration purposes
    file_dt = datetime.now().strftime("%Y%m%d_%H%M%S")

    _log_name = "log_" + file_dt + ".log"
    __log_name = folder_location / _log_name

    # Create a logger only if it doesn't exist
    if "logger" not in globals():
        logger = logging.getLogger(str(getpass.getuser()))
        logger.setLevel(logging.DEBUG)

        # Create a console handler and set the level to DEBUG
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Removes previously set handlers
        logger.handlers = []

        # Create a file handler and add it to the logger
        file_handler = logging.FileHandler(__log_name, "w+", encoding="utf-8")

        # Formatting
        formatter = logging.Formatter(
            "%(asctime)s | [%(levelname)s] | %(name)s | %(message)s"
        )
        file_handler.setFormatter(formatter)

        formatter_console = logging.Formatter("%(message)s")
        console_handler.setFormatter(formatter_console)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Redirect prints to the log
        sys.stdout = LogPrints(logger, level=logging.INFO)
        sys.stderr = LogPrints(logger, level=logging.ERROR)

        print("\nNOTE: Logging started...", __log_name)
    else:
        print("\nNOTE: Logging is already in progress.")


## log_end


def log_end():
    """end logging process"""
    global file_handler

    if file_handler is not None:
        print("NOTE: Logging ended...", __log_name)
        # logger.info('NOTE: Logging ended...', __log_name)

        # Close the file handler (this will also flush the log entries to the file)
        file_handler.flush()
        file_handler.close()

        # Reset stdout and stderr to their original values
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # Set file_handler to None to indicate that logging is not in progress
        file_handler = None
    else:
        print("\nNOTE: Logging is not in progress. No action taken.")


## open_file_folder
def open_file_folder(path):
    path_adj = "explorer " + '"' + str(path) + '"'
    subprocess.Popen(path_adj)


## timer_start
def timer_start():
    """Record start time."""
    global start_time
    print("\nNOTE: Timer started...")
    # Record the start time
    start_time = time.time()


## timer_end
def timer_end():
    """Calculate overall time taken."""
    global start_time
    try:
        # Record the end time
        end_time = time.time()
        # Calculate the elapsed time
        elapsed_time_seconds = end_time - start_time

        # Extract hours, minutes, seconds, and milliseconds
        hours, remainder = divmod(elapsed_time_seconds, 3600)
        minutes, remainder = divmod(remainder, 60)
        seconds, milliseconds = divmod(remainder, 1)

        # Convert seconds to hours, minutes, and remaining seconds
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        milliseconds = int(
            milliseconds * 1000
        )  # convert fractional seconds to milliseconds

        # Print the results
        print(
            f"Execution Time: {hours} hours {minutes} minutes {seconds} seconds {milliseconds} milliseconds"
        )

        # Release
        del start_time, end_time

    except NameError:
        print("WARNING: Please run timer_start function.")
