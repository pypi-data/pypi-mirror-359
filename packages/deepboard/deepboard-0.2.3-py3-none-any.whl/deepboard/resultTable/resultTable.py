import sys
from typing import *
from enum import Enum
from pathlib import PurePath
import os
from glob import glob
from datetime import datetime
import warnings
import shutil
import sqlite3
import hashlib
import pandas as pd
import shlex
from PIL import Image
from io import BytesIO

from .logwritter import LogWriter
from .cursor import Cursor
from .utils import get_last_commit, get_diff
from .table_schema import create_database

class NoCommitAction(Enum):
    """
    How to notify the user when there are changes that are not committed and a new run is started not in DEBUG mode
    - `NOP`: No action
    - `WARN`: Show a warning
    - `RAISE`: Raise an exception
    """
    NOP = "NOP"
    WARN = "WARN"
    RAISE = "RAISE"


class ResultTable:
    """
    This class represents all the results. There are a lot of method to interact with the resultTable (the database).

    All actions performed by the GUI (DeepBoard) are available by public methods to get a programmatic access.

    How to use:

    - First, specify a path the result table. If the db was not created, it will be created automatically.

    - Then, create a run with all the specific parameters describing the run. A unique run_id will be generated.
    Note that each run must be unique. This security allows more reproducible runs. If one run perform better than
    the others, you can run the code again with all the parameters in the result table and you should get the same
    results.

    - If you simply want to test your code, you can create a debug run. It won't create a permanent entry in the
    table. You will still be able to see the logged scalars in the GUI with the run_id -1 that is reserved for
    debug runs. This run will be overwritten by the next debug run.

    - Finally, you can interact with the table with the different available methods.
    """
    def __init__(self, db_path: str = "results/result_table.db", nocommit_action: NoCommitAction = NoCommitAction.WARN):
        """
        :param db_path: The path to the databse file
        :param nocommit_action: What to do if changes are not committed
        """
        if not os.path.exists(db_path):
            self._create_database(db_path)
        db_path = PurePath(db_path) if not isinstance(db_path, PurePath) else db_path

        # The configuration files will be back up there
        self.configs_path = db_path.parent / "configs"
        if not os.path.exists(self.configs_path):
            os.mkdir(self.configs_path)

        self.db_path = db_path
        self.nocommit_action = nocommit_action

    def new_run(self, experiment_name: str,
                config_path: Union[str, PurePath],
                cli: dict,
                comment: Optional[str] = None,
                flush_each: int = 10,
                keep_each: int = 1,
                auto_log_plt: bool = True,
                disable: bool = False
                ) -> LogWriter:
        """
        Create a new logwritter object bound to a run entry in the table. Think of it as a socket.
        :param experiment_name: The name of the current experiment
        :param config_path: The path to the configuration path
        :param cli: The cli arguments
        :param comment: The comment, if any
        :param flush_each: Every how many logs does the logger save them to the database?
        :param keep_each: If the training has a lot of steps, it might be preferable to not log every step to save space and speed up the process. This parameter controls every how many step we store the log. 1 means we save at every steps. 10 would mean that we drop 9 steps to save 1.
        :param auto_log_plt: If True, automatically detect if matplotlib figures were generated and log them. Note that it checks only when a method on the socket is called. It is better to log them manually because you can set the appropriate step, epoch and split.
        :param disable: If true, disable the logwriter, meaning that nothing will be written to the database.
        :return: The log writer
        """
        diff = get_diff()
        if diff is not None and len(diff) > 0:
            if self.nocommit_action == NoCommitAction.RAISE:
                raise RuntimeError("You have uncommitted changes. Please commit your changes before running the experiment in prod mode.")
            elif self.nocommit_action == NoCommitAction.WARN:
                warnings.warn("You have uncommitted changes. Please commit your changes before running the experiment in prod mode.", RuntimeWarning)

        commit = get_last_commit()
        start = datetime.now()
        config_str = str(config_path)
        config_hash = self.get_file_hash(config_path)
        comment = "" if comment is None else comment
        cli = " ".join([f'{key}={value}' for key, value in cli.items()])
        command = " ".join(shlex.quote(arg) for arg in sys.argv)
        if not disable:
            with self.cursor as cursor:
                # Step 1: Check if the configuration already exists
                cursor.execute("""
                        SELECT * FROM Experiments
                        WHERE experiment = ?
                          AND config = ?
                          AND config_hash = ?
                          AND cli = ?
                          AND comment = ?
                """, (experiment_name, config_str, config_hash, cli, comment))
                result = cursor.fetchall()
                if result is not None:
                    status = [res[8] for res in result]
                    run_id = [res[0] for res in result]

                    # We ignore debug runs
                    status = [status for i, status in enumerate(status) if run_id[i] != -1]
                    run_id = [runID for i, runID in enumerate(run_id) if runID != -1]
                    if len(status) == 0:
                        # If here, only a debug run exists. So we need to create a new one
                        run_id = None
                        status = None
                    else:
                        # If here, the run does exist. So we will not create a new one
                        run_id = run_id[0]
                        status = status[0]

                    if status is not None and status != "failed":
                        # If here, the run does exist and is not failed. So we will not create a new one
                        raise RuntimeError(f"Configuration has already been run with runID {run_id}. Consider changing "
                                           f"parameter to avoid duplicate runs or add a comment.")
                    elif run_id is not None and status == "failed":
                        # If here, the run does exist, but failed. So we will retry it
                        self._create_run_with_id(run_id, experiment_name, config_str, config_hash, cli, command, comment, start, commit, diff)

                    elif run_id is None:
                        # Only a debug run exists. So we need to create a new one
                        run_id = self._create_run(experiment_name, config_str, config_hash, cli, command, comment, start, commit, diff)

                else:
                    run_id = self._create_run(experiment_name, config_str, config_hash, cli, command, comment, start, commit, diff)

            if not isinstance(config_path, PurePath):
                config_path = PurePath(config_path)
            config_name = config_path.name
        else:
            run_id = -2 # If disabled and not debug, we use -2 to indicate that it is a disabled run
            if not isinstance(config_path, PurePath):
                config_path = PurePath(config_path)
            config_name = config_path.name

        extension = config_name.split(".")[-1]
        shutil.copy(config_path, self.configs_path / f'{run_id}.{extension}')

        return LogWriter(self.db_path, run_id, datetime.now(), flush_each=flush_each, keep_each=keep_each,
                         disable=disable, auto_log_plt=auto_log_plt)

    def new_debug_run(self, experiment_name: str,
                config_path: Union[str, PurePath],
                cli: dict,
                comment: Optional[str] = None,
                flush_each: int = 10,
                keep_each: int = 1,
                auto_log_plt: bool = True,
                disable: bool = False
                ) -> LogWriter:
        """
        Create a new DEBUG socket to log the results. The results will be entered in the result table, but as the runID -1.
        This means that everytime you run the same code, it will overwrite the previous one. This is useful to avoid
        adding too many rows to the table when testing the code or debugging.

        Note:
            It will not log the git diff or git hash
        :param experiment_name: The name of the current experiment
        :param config_path: The path to the configuration path
        :param cli: The cli arguments
        :param comment: The comment, if any
        :param flush_each: Every how many logs does the logger save them to the database?
        :param keep_each: If the training has a lot of steps, it might be preferable to not log every step to save space and speed up the process. This parameter controls every how many step we store the log. 1 means we save at every steps. 10 would mean that we drop 9 steps to save 1.
        :param auto_log_plt: If True, automatically detect if matplotlib figures were generated and log them. Note that it checks only when a method on the socket is called. It is better to log them manually because you can set the appropriate step, epoch and split.
        :param disable: If true, disable the logwriter, meaning that nothing will be written to the database.
        :return: The log writer
        """

        start = datetime.now()
        config_str = str(config_path)
        config_hash = self.get_file_hash(config_path)
        comment = "" if comment is None else comment
        cli = " ".join([f'{key}={value}' for key, value in cli.items()])
        command = " ".join(shlex.quote(arg) for arg in sys.argv)
        if not disable:
            self._create_run_with_id(-1, experiment_name, config_str, config_hash, cli, command, comment, start, None, None)

        if not isinstance(config_path, PurePath):
            config_path = PurePath(config_path)
        config_name = config_path.name

        extension = config_name.split(".")[-1]
        shutil.copy(config_path, self.configs_path / f'{-1}.{extension}')

        return LogWriter(self.db_path, -1, datetime.now(), flush_each=flush_each, keep_each=keep_each, disable=disable,
                         auto_log_plt=auto_log_plt)

    def load_config(self, run_id: int) -> str:
        """
        Load the configuration file of a given run id
        :param run_id: The run id
        :return: The path to the configuration file
        """
        valid_files = glob(str(self.configs_path / f"{run_id}.*"))
        if len(valid_files) > 1:
            print(f"Warning: More than one configuration file found for run {run_id}. ")
        with open(valid_files[0], 'r') as f:
            content = f.read()
        return content

    def load_run(self, run_id) -> LogWriter:
        """
        Load a specific run's LogWriter in read-only mode.
        :param run_id: The run id
        :return: The logWriter bound to the run
        """
        logwriter = LogWriter(self.db_path, run_id, datetime.now())
        logwriter.enabled = False  # We cannot log with a used writer
        return logwriter

    def hide_run(self, run_id: int):
        """
        Instead of deleting runs and lose information, you can hide it. It will not be visible in the default view of
        the result Table, however, it can be unhidden if it was a mistake.
        :param run_id: The run id to hide
        :return: None
        """
        with self.cursor as cursor:
            cursor.execute("UPDATE Experiments SET hidden=1 WHERE run_id=?", (run_id,))

    def show_run(self, run_id: int):
        """
        This method unhide a run that has been hidden. It undo the operation performed by `hide_run`.
        :param run_id: The run id to show
        :return:
        """
        with self.cursor as cursor:
            cursor.execute("UPDATE Experiments SET hidden=0 WHERE run_id=?", (run_id,))

    def get_hidden_runs(self) -> List[int]:
        """
        Get the list of all hidden run ids.
        :return: A list of run ids associated to hidden runs.
        """
        with self.cursor as cursor:
            cursor.execute("SELECT run_id FROM Experiments WHERE hidden>0")
            runs = cursor.fetchall()
            return [r[0] for r in runs]

    def fetch_experiment(self, run_id: int) -> Dict[str, Any]:
        """
        Load the row of an experiment. It will return a dictionary with the keys being the column names and the values
        the actual values. Note that this does not perform any other operations than fetch in the database. This means
        that it will also show columns that were hidden.
        :param run_id: The run id to fetch
        :return: The raw row of an experiment
        """
        with self.dict_cursor as cursor:
            cursor.execute("SELECT * FROM Experiments WHERE run_id=?", (run_id,))
            row = cursor.fetchone()
            return row

    def set_column_order(self, columns: Dict[str, Optional[int]]):
        """
        Set the order of the column in the result table. If order is None, it will be set to NULL
        :param columns: A dict of column name and their order. The order is the index of the column in the table. If the order is None, it will be set to NULL and be hidden
        :return: None
        """
        with self.cursor as cursor:
            # Batch update
            for column, order in columns.items():
                cursor.execute("UPDATE ResultDisplay SET display_order=? WHERE Name=?", (order, column))

    def set_column_alias(self, columns: Dict[str, str]):
        """
        Set the alias of the column in the result table.
        :param columns: A dict of column name and their alias. The alias is the name displayed in the table.
        :return: None
        """
        with self.cursor as cursor:
            # Batch update
            for column, alias in columns.items():
                cursor.execute("UPDATE ResultDisplay SET alias=? WHERE Name=?", (alias, column))

    def hide_column(self, column: str):
        """
        Hide a column in the result table.
        :param column: The column name to hide.
        :return: None
        """
        with self.cursor as cursor:
            cursor.execute("UPDATE ResultDisplay SET display_order=NULL WHERE Name=?", (column,))
            # Change the order of every other columns such that they are continuous
            cursor.execute("""
            UPDATE ResultDisplay 
                SET display_order=(
                    SELECT COUNT(*) FROM ResultDisplay AS R2
                    WHERE R2.display_order < ResultDisplay.display_order
                    ) + 1
                WHERE display_order IS NOT NULL;""", )

    def show_column(self, column: str, order: int = -1):
        """
        Show a column in the result table.
        If order is -1, it will be set to the last column.
        """
        # If the column is already at this order, do nothing
        current = {col_id: order for col_id, (order, alias) in self.result_columns.items()}[column]
        if current == order:
            return
        with self.cursor as cursor:
            # Get the max order
            cursor.execute("SELECT MAX(display_order) FROM ResultDisplay")
            max_order = cursor.fetchone()[0]
            if max_order is None:
                max_order = 0
            else:
                max_order += 1

            if order == -1:
                order = max_order

            # Update all display orders
            cursor.execute("""
                UPDATE ResultDisplay
                SET display_order = display_order + 1
                WHERE display_order >= ?
            """, (order,))
            # print(self.result_columns)
            # Insert the column
            cursor.execute("UPDATE ResultDisplay SET display_order=? WHERE Name=?", (order, column))

    def get_results(self, run_id: Optional[int] = None, show_hidden: bool = False) -> Tuple[List[str], List[str], List[List[Any]]]:
        """
        This function will build the result table and return it as a list. It will also return the column names and
        their unique id. It will not return the columns that were hidden and will format the table to respect the
        column order. By default, it does not include hidden runs, but they can be included by setting the show_hidden.
        You can also get a single row by passing a run_id to the method.
        :param run_id: the run id. If none is specified, it fetches all results
        :param show_hidden: Show hidden runs.
        :return: A list of columns names, a list of column ids and a list of rows
        """
        out = {}
        exp_info = {}
        with self.cursor as cursor:
            command = "SELECT E.run_id, E.experiment, E.config, E.config_hash, E.cli, E.command, E.comment, E.start, E.status, E.commit_hash, E.diff, E.hidden, R.metric, R.value " \
                        "FROM Experiments E LEFT JOIN Results R ON E.run_id = R.run_id"
            params = []
            if run_id is not None:
                command += " WHERE E.run_id = ?"
                params.append(run_id)
            if not show_hidden:
                command += " WHERE E.hidden = 0"

            cursor.execute(command, params)
            rows = cursor.fetchall()

        for row in rows:
            run_id, metric, value = row[0], row[-2], row[-1]
            if run_id not in out:  # Run id already stored
                out[run_id] = {}
                exp_info[run_id] = dict(
                    run_id=run_id,
                    experiment=row[1],
                    config=row[2],
                    config_hash=row[3],
                    cli=row[4],
                    command=row[5],
                    comment=row[6],
                    start=datetime.fromisoformat(row[7]),
                    status=row[8],
                    commit_hash=row[9],
                    diff=row[10],
                    hidden=row[11]
                )
            out[run_id][metric] = value

        # Merge them together:
        for run_id, metrics in out.items():
            exp_info[run_id].update(metrics)

        # Sort the columns of the result table
        columns = [(col_id, col_order, col_alias) for col_id, (col_order, col_alias) in self.result_columns.items() if
                   col_order is not None]
        columns.sort(key=lambda x: x[1])

        table = [[row.get(col[0]) for col in columns] for key, row in exp_info.items()]
        return [col[2] for col in columns], [col[0] for col in columns], table

    def get_image_by_id(self, image_id: int) -> Optional[Image.Image]:
        """
        If the image_id is valid, it will return the image as a PIL Image object.
        :param image_id: The id of the image to fetch.
        :return: The image as a PIL Image object or None if the image_id is not valid.
        """
        with self.cursor as cursor:
            cursor.execute("SELECT image FROM Images WHERE id_=?", (image_id,))
            row = cursor.fetchone()
            if row is None:
                return None

            # get raw bytes
            image_data = row[0]

            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data))
            return image

    def to_pd(self, get_hidden: bool = False) -> pd.DataFrame:
        """
        Export the table to a pandas dataframe.
        :param get_hidden: If True, it will include the hidden runs.
        :return: The table as a pandas dataframe.
        """

        columns, col_ids, data = self.get_results(show_hidden=get_hidden)
        df = pd.DataFrame(data, columns=columns)
        if "run_id" in col_ids:
            idx = col_ids.index("run_id")
            colname = columns[idx]
            df.set_index(colname, inplace=True)
        return df

    @property
    def runs(self) -> List[int]:
        """
        Get all the runs in the result table. It will return a list of run ids.
        :return: A list of run ids.
        """
        with self.cursor as cursor:
            cursor.execute("SELECT run_id FROM Experiments")
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    @property
    def result_columns(self) -> Dict[str, Tuple[Optional[int], str]]:
        """
        Get all the columns in the result table that can be shown. It will return a dictionary where the keys are the
        columns ids and the values a tuple containing the column position (order) and its name (alias).
        {col_id: (order, alias), ...}
        :return: The available columns.
        """
        with self.cursor as cursor:
            cursor.execute("SELECT Name, display_order, alias FROM ResultDisplay")
            rows = cursor.fetchall()
            return {row[0]: (row[1], row[2]) for row in rows}

    @property
    def cursor(self):
        """
        Get access to the cursor to interact with the db. It is usable in a with statement.
        """
        return Cursor(self.db_path)

    @property
    def dict_cursor(self):
        """
        Get access to the cursor to interact with the db, but it returns the data as a dict. It is usable in a with
        statement.
        """
        return Cursor(self.db_path, format_as_dict=True)


    def _create_run_with_id(self, run_id: int, experiment_name: str, config_str: str, config_hash: str, cli: str, command: str,
                            comment: str, start: datetime, commit: Optional[str], diff: Optional[str]):
        self._delete_run(run_id)

        with self.cursor as cursor:
            cursor.execute("""
                                    INSERT INTO Experiments (run_id, experiment, config, config_hash, cli, command, comment, start, commit_hash, diff) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                                    """,
                           (run_id, experiment_name, config_str, config_hash, cli, command, comment, start, commit, diff))

    def _create_run(self, experiment_name: str, config_str: str, config_hash: str, cli: str, command: str,
                            comment: str, start: datetime, commit: str, diff: str):

        with self.cursor as cursor:
            cursor.execute("""
                                    INSERT INTO Experiments (experiment, config, config_hash, cli, command, comment, start, commit_hash, diff) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                                    """,
                           (experiment_name, config_str, config_hash, cli, command, comment, start, commit, diff))
            return cursor.lastrowid

    def _delete_run(self, run_id: int):
        """
        Delete the run with the given run_id from the database.

        IMPORTANT: You should not call this method directly.
        The result Table is supposed to be immutable.
        """
        with self.cursor as cursor:
            # Delete the failed run and replace it with the new one
            cursor.execute("DELETE FROM Experiments WHERE run_id=?", (run_id,))
            # Delete logs
            cursor.execute("DELETE FROM Logs WHERE run_id=?", (run_id,))
            cursor.execute("DELETE FROM Images WHERE run_id=?", (run_id,))
            cursor.execute("DELETE FROM Fragments WHERE run_id=?", (run_id,))
            # Delete results
            cursor.execute("DELETE FROM Results WHERE run_id=?", (run_id,))

    @staticmethod
    def get_file_hash(file_path: str, hash_algo: str = 'sha256') -> str:
        """Returns the hash of the file at file_path using the specified hashing algorithm."""
        hash_func = hashlib.new(hash_algo)  # Create a new hash object for the specified algorithm

        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):  # Read the file in chunks to avoid memory overflow
                hash_func.update(chunk)  # Update the hash with the current chunk

        return hash_func.hexdigest()

    @staticmethod
    def _create_database(db_path):
        create_database(db_path)