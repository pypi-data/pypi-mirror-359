"""This module contains classes implementing problem instance solving
tournaments by differently configured target algorithms according to the RTAC
method utilized."""

from abc import ABC, abstractmethod
import multiprocessing as mp
import subprocess
import os
import uuid
import time
import signal
from rtac.utils.process_affinity import set_affinity_recursive
from rtac.ac_functionalities.config_gens import DefaultConfigGen
from rtac.ac_functionalities.rtac_data import (
    TournamentStats,
    TARun,
    TARunStatus
)
from rtac.ac_functionalities.ta_runner import BaseTARunner
from rtac.ac_functionalities.rtac_data import (
    Configuration,
    RTACData,
    ACMethod,
    RTACDatapp
)
from rtac.ac_functionalities.logs import RTACLogs
import argparse


class AbstractTournament(ABC):
    """
    Abstract class for tournaments.

    Parameters
    ----------
    scenario : argparse.Namespace
        Namespace containing all settings for the RTAC.
    ta_runner : BaseTARunner
        Target algorithm runner object.
    rtac_data : RTACData | RTACDatapp
        Object containing data and objects necessary throughout the RTAC 
        modules.
    logs : RTACLogs
        Object containing loggers and logging functions.
    """

    def __init__(self, scenario: argparse.Namespace, ta_runner: BaseTARunner,
                 rtac_data: RTACData | RTACDatapp, logs: RTACLogs):
        """
        Initializes the tournament class for ReACTR tournaments.

        If `self.scenario.baselineperf` is set, the configuration used is the
        default configuration according to the configuration space definition 
        JSON.
        """
        self.scenario = scenario
        self.ta_runner_class = ta_runner
        self.rtac_data = rtac_data
        self.logs = logs
        
        if self.scenario.baselineperf:
            self.dcg = DefaultConfigGen(self.scenario)

        if self.scenario.gray_box:
            self.gb_model = None
    
    @abstractmethod
    def start_tournament(self, instance: str,
                         contender_dict: dict[str: Configuration],
                         tourn_nr: int) -> None:
        """
        Sets up tournament data and information and starts the tournament with
        `scenario.number_cores` configured target algorithms running in parallel,
        using settings according to the RTAC method.

        Parameters
        ----------
        instance : str
            Path to the problem instance to solve.
        contender_dict : dict[str, Configuration]
            Dictionary containing configurations to run in the tournament, with
            configuration IDs as keys and Configuration objects as values.
        tourn_nr : int
            Number of the tournament during this RTAC run.

        Returns
        -------
        None
        """

    @abstractmethod
    def watch_tournament(self) -> None:
        """
        Function to observe the tournament and enforce the timelimit
        scenario.timeout if reached according to the RTAC method used.

        Returns
        -------
        None
        """

    def close_tournament(self) -> None:
        """
        Initiates termination of all target algorithm runs.

        Returns
        -------
        None
        """
        self.rtac_data.ev.set()
        self.rtac_data.event = 1
        print(f'\nClosing tournament Nr. {self.tourn_nr}',
              f'(Tournament ID: {self.tourn_id})',
              f'due to timeout ({self.scenario.timeout}s) at ',
              f'{self.currenttime}s.\n')
        if self.scenario.objective_min:
            time.sleep(1)  # extra time for TAs to shut down and print results
        for core in range(self.scenario.number_cores):
            if self.rtac_data.status[core] not in (2, 3):
                self.rtac_data.status[core] = 5
            self.terminate_run(core, self.rtac_data.process[core])

    def terminate_run(self, core: int, process: subprocess.Popen) -> None:
        """
        Enforces termination of a target algorithm run.

        Parameters
        ----------
        core : int
            Index of the process in the list of processes.
        process : subprocess.Popen
            Target algorithm run process to terminate.

        Returns
        -------
        None
        """
        if core not in self.terminated_configs:
            if self.scenario.verbosity == 2:             
                print('Terminating configuration', self.conf_id_list[core],
                      'running on core', core, 'in tournament', self.tourn_id,
                      '( tournament Nr.', self.tourn_nr, ').')
            if self.pid_alive(self.rtac_data.pids[core]):
                try:
                    os.kill(self.rtac_data.pids[core], signal.SIGKILL)
                except Exception as e:
                    message = \
                        f'Tried killing pid {self.rtac_data.pids[core]} - ' \
                        + str(e) \
                        + ' - It was run with configuration' + \
                        f' {self.conf_id_list[core]}'
                    self.logs.general_log(message)
            if process.is_alive():
                process.terminate()
                process.join()

            self.terminated_configs.append(core)

    def pid_alive(self, pid) -> None:
        """Checks if process is till alive using PID.

        Parameters
        ----------
        pid : int
            Unique identifier for process.

        Returns
        -------
        None
        """
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


class Tournament(AbstractTournament):
    """
    Tournament class with functions needed for ReACTR method tournaments.
    """

    def start_tournament(self, instance: str,
                         contender_dict: dict[str: Configuration],
                         tourn_nr: int, cores_start: list[int]) -> None:
        """
        Sets up tournament data and starts the tournament with
        `scenario.number_cores` configured target algorithms running in 
        parallel according to the ReACTR method.

        Parameters
        ----------
        instance : str
            Path to the problem instance to solve.
        contender_dict : dict[str, Configuration]
            Dictionary containing configurations to run in the tournament, with
            configuration IDs as keys and Configuration objects as values.
        tourn_nr : int
            Number of the tournament during this RTAC run.
        cores_start : list[int]
            List of cores which to start the contenders on.

        Returns
        -------
        None
        """
        self.terminated_configs = []
        self.instance = instance
        self.tourn_nr = tourn_nr
        if self.scenario.baselineperf:
            def_conf = self.dcg.generate()
            contender_dict = {def_conf.id: def_conf}
        self.config_list = \
            [list(contender_dict.values())[i]
             if i in cores_start else None
             for i in range(self.scenario.number_cores)]
        self.conf_id_list = \
            [list(contender_dict.keys())[i]
             if i in cores_start else None
             for i in range(self.scenario.number_cores)]
        self.tourn_id = uuid.uuid4().hex
        self.rtac_data.tournID = self.tourn_id
        log_message = f'Starting tournament {self.tourn_id}' \
                      + f' (nr. {self.tourn_nr}) on instance {self.instance}'
        self.logs.general_log(log_message)
        self.tournamentstats = \
            TournamentStats(self.tourn_id, tourn_nr, self.conf_id_list, None,
                            [], [], [], [], {})

        self.sync_event = mp.Event()

        for core in cores_start:
            self.ta_runner = \
                self.ta_runner_class(self.scenario, self.logs, core)
            contender = self.config_list[core]
            self.tournamentstats.TARuns[contender.id] = \
                TARun(contender.id, contender.conf, 0, 0, TARunStatus.running)

            translated_config = self.ta_runner.translate_config(contender)

            self.rtac_data.process[core] = \
                mp.Process(target=self.ta_runner.run,
                           args=[self.instance, translated_config,
                                 self.rtac_data, self.sync_event])

        # Starting processes
        for core in cores_start:  # range(self.scenario.number_cores):
            self.rtac_data.process[core].start()

        self.sync_event.set()
        time.sleep(0.01)

        for core in cores_start:
            set_affinity_recursive(self.rtac_data.process[core], core)

    def fill_tournament(self, cores_start: list[int]) -> None:
        """
        Fills up the remaining cores to be used in an early started tournament.

        Parameters
        ----------
        cores_start : list[int]
            List of cores which to start the contenders on.

        Returns
        -------
        None
        """
        for core in cores_start:
            self.ta_runner = \
                self.ta_runner_class(self.scenario, self.logs, core)
            contender = self.config_list[core]
            self.tournamentstats.TARuns[contender.id] = \
                TARun(contender.id, contender.conf, 0, 0, TARunStatus.running)

            translated_config = self.ta_runner.translate_config(contender)

            self.rtac_data.process[core] = \
                mp.Process(target=self.ta_runner.run,
                           args=[self.instance, translated_config,
                                 self.rtac_data, self.sync_event])

        self.rtac_data.start = time.time()

        # Starting processes
        for core in cores_start:
            self.rtac_data.process[core].start()

        for core in cores_start:
            set_affinity_recursive(self.rtac_data.process[core], core)

    def watch_tournament(self) -> None:
        """
        Function to observe the tournament and enforce the timelimit
        scenario.timeout if reached.

        Returns
        -------
        None
        """

        while any(proc.is_alive() for proc in self.rtac_data.process):
            time.sleep(1)  # Timeout is int, so checking every second is enough
            currenttime = time.time() - self.rtac_data.start

            if currenttime >= self.scenario.timeout:
                self.currenttime = currenttime
                self.close_tournament()


class Tournament_GB:
    """
    Class that contains gray-box tournament functions to be inserted into 
    tournament classes if scenario.gray_box is True.
    """

    def watch_tournament_gray_box(self, early_tournament=False) -> None:
        """
        Function to observe the tournament and enforce the timelimit
        scenario.timeout if reached.

        Parameters
        ----------
        early_tournament : bool
            True if tournament is early starter, False if not.

        Returns
        -------
        None
        """

        gb_check_time = time.time()
        self.gb_pw_inst_archive = []
        self.pw_cores = []
        self.mtp = {}
        self.s_instances = []
        self.term_list = []

        while any(isinstance(p, mp.Process) and p.is_alive()
                  for p in self.rtac_data.process):
            time.sleep(self.scenario.gb_read_time)
            currenttime = time.time() - self.rtac_data.start

            if not early_tournament and not self.terminated_configs:

                X_pw, cores, self.s_instances, self.gb_pw_inst_archive, \
                    self.mtp, self.pw_cores = \
                    self.gray_box.prepare_predict_data(self.rtac_data.rec_data, 
                                                       self.s_instances,
                                                       self.gb_pw_inst_archive,
                                                       self.mtp, self.pw_cores)

                if self.gb_model is not None and len(X_pw) > 2 and \
                        time.time() \
                        - gb_check_time >= self.scenario.gb_read_time:

                    pred = self.gray_box.classify_configs(
                        X_pw, self.scenario.number_cores, self.gb_model
                    )
                    if pred is not None:
                        self.term_list = self.tournamentstats.kills = \
                            self.gray_box.term_list(pred, cores,
                                                    self.scenario.verbosity)
                        if self.term_list:

                            self.tm.early_start(currenttime)
                    
                gb_check_time = time.time()

            if currenttime >= self.scenario.timeout:
                self.currenttime = currenttime
                self.close_tournament()


class Tournamentpp(Tournament):
    """
    Tournament class with functions needed for ReACTR method tournaments.
    """


def tournament_factory(scenario: argparse.Namespace, ta_runner: BaseTARunner,
                       rtac_data: RTACData | RTACDatapp, logs: RTACLogs
                       ) -> Tournament | Tournamentpp:
    """
    Class factory to return the initialized TournamentManager class
    appropriate to the RTAC method `scenario.ac`.

    Parameters
    ----------
    scenario : argparse.Namespace
        Namespace containing all settings for the RTAC.
    ta_runner : BaseTARunner
        Target algorithm runner object.
    rtac_data : RTACData | RTACDatapp
        Object containing data and objects necessary throughout the RTAC 
        modules.
    logs : RTACLogs
        Object containing loggers and logging functions.

    Returns
    -------
    Tournament or Tournamentpp
        Initialized Tournament object matching the RTAC method of the scenario.
    """
    if scenario.ac in (ACMethod.ReACTR, ACMethod.CPPL):
        tournament = Tournament
    elif scenario.ac is ACMethod.ReACTRpp:
        tournament = Tournamentpp

    if scenario.gray_box:
        tournament.watch_tournament = Tournament_GB.watch_tournament_gray_box

    return tournament(scenario, ta_runner, rtac_data, logs)


if __name__ == '__main__':
    pass
