"""In this module results of the tournaments are processed and computations for
the next tournament ar performed."""

from abc import ABC, abstractmethod
from rtac.ac_functionalities.config_gens import (
    DefaultConfigGen,
    RandomConfigGen
)
from rtac.ac_functionalities.ranking import trueskill
from rtac.ac_functionalities.rtac_data import (
    RTACData,
    RTACDatapp,
    Configuration,
    ACMethod,
    InterimMeaning,
    Generator
)
from rtac.ac_functionalities.logs import RTACLogs
import argparse
import random
import sys
import numpy as np
import uuid
import copy
import multiprocessing
import pickle
import time
from scipy.stats import rankdata


class Contender(object):
    """Helper object for setting trueskill ranks."""
    pass


class AbstractResultProcessing(ABC):
    """
    Abstract class with functions to process tournament results.

    Parameters
    ----------
    scenario : argparse.Namespace
        Namespace containing all settings for the RTAC.
    logs : RTACLogs
        Object containing loggers and logging functions.
    """

    def __init__(self, scenario: argparse.Namespace, logs: RTACLogs):
        """
        Initialize tournament result processing class.
        """
        self.scenario = scenario
        self.logs = logs
        self.default_config_gen = DefaultConfigGen(self.scenario)
        self.random_config_gen = RandomConfigGen(self.scenario)
        self.tourn_nr = 0
        self.contender_dict = {}
        self.huge_float = sys.float_info.max * 1e-100
        self.pool = {}
        self.time_sum = 0
        self.init_data()

    def init_data(self) -> dict[str: Configuration]:
        """
        Initialize tournament result processing data according to ReACTR
        implementation.

        Returns
        -------
        dict[str, Configuration]
            Randomly selected contenders.
        """
        if self.scenario.resume:
            # Data is loaded instead of intialized.
            pass
        elif self.scenario.pws:
            # Initialize pool of contender configurations incl. default
            default_config = self.default_config_gen.generate(0)
            self.pool[default_config.id] = default_config
            for _ in range(self.scenario.contenders - 1):
                random_config = self.random_config_gen.generate(0)
                self.pool[random_config.id] = random_config

            # Randomly initialize contender dict of first tournament
            # incl. default
            self.contender_dict[default_config.id] = default_config
            random_pick = random.sample(list(self.pool.values())[1:],
                                        self.scenario.number_cores - 1)
        else:
            # Initialize pool of contender configurations
            for _ in range(self.scenario.contenders):
                random_config = self.random_config_gen.generate(0)
                self.pool[random_config.id] = random_config

            # Randomly initialize contender dict of first tournament
            random_pick = random.sample(list(self.pool.values()),
                                        self.scenario.number_cores)

        for rp in random_pick:
            self.contender_dict[rp.id] = rp

    @abstractmethod
    def process_results(self, rtac_data: RTACData | RTACDatapp,
                        instance: str = None, tourn_nr: int = None) -> None:
        """
        Perform tournament result processing necessary to replace contenders
        in pool and select contenders for next tournament/problem instance.

        Parameters
        ----------
        rtac_data : RTACData | RTACDatapp
            Object containing data and objects necessary throughout the rtac 
            modules.
        instance : str
            ID of the problem instance. Defaults to None.
        tourn_nr : int
            Tournament number. Defaults to None.

        Returns
        -------
        None
        """

    @abstractmethod
    def manage_pool(self) -> None:
        """
        Replace contenders in pool if necessary.

        Returns
        -------
        None
        """

    @abstractmethod
    def select_contenders(self) -> None:
        """
        Select contenders for next tournament/problem instance.

        Returns
        -------
        None
        """

    def process_tourn(self, rtac_data: RTACData | RTACDatapp, 
                      instance: str = None,
                      tourn_nr: int = None) -> str | None:
        """
        Manage result processing.

        rtac_data: RTACData | RTACDatapp
            Object containing data and objects necessary throughout the RTAC 
            modules.
        instance : str
            ID of the configuration to have won the previous tournament. 
            Defaults to None.
        tourn_nr: int
            Number of the tournament that is processed.

        Returns
        -------
        str or None
            ID of the winner or None if problem instance could not be solved.
        """
        self.rtac_data = rtac_data

        if not self.scenario.baselineperf:
            self.process_results(rtac_data, instance, tourn_nr)
            if self.rtac_data.winner.value != 0:
                self.manage_pool()
            self.select_contenders()
        else:
            self.rtac_data = rtac_data
            self.rtac_data.newtime = self.rtac_data.ta_res_time[0]

        if self.rtac_data.winner.value == 0:
            winner = None
        else:
            winner = self.rtac_data.winner.value

        return winner

    def get_contender_dict(self) -> dict[str: Configuration]:
        """
        Returns contender_dict.

        Returns
        -------
        dict[str, Configuration]
            Configuration selected to run in next tournament/on next problem 
            instance. Dictionary with configuration id as key and Configuration 
            object as value.
        """
        return self.contender_dict

    def result_summary_terminal(self, results: list[float],
                                tourn_nr: int = None) -> None:
        """
        Print the sum of the winner results of all tournaments so far.

        Parameters
        ----------
        results : list[float]
            List of results of previous tournament.
        tourn_nr : int
            Number of previous tournament. Defaults to None.

        Returns
        -------
        None
        """
        if tourn_nr:
            self.tourn_nr = tourn_nr
        if self.scenario.verbosity == 2 and self.scenario.experimental:
            if not self.scenario.objective_min:
                unit = 'seconds'
            else:
                unit = 'objective value'

            self.time_sum += round(min(results), 3)
            len_str = len('Instance nr. ' + str(self.tourn_nr) + ' : ' + str(
                round(self.time_sum, 3)
            ) + f' {unit} total for solved instances')
            print('\n')
            print('-' * len_str)
            if min(results) == self.scenario.timeout:
                print('Instance nr.', self.tourn_nr, ':',
                      round(self.time_sum, 3),
                      f'{unit} total for solved instances',
                      ' *** TIMEOUT on instance')
            else:
                print('Instance nr.', self.tourn_nr, ':',
                      round(self.time_sum, 3),
                      f'{unit} total for solved instances')

            print('-' * len_str)
            print('\n')


class ResultProcessing(AbstractResultProcessing):
    """
    Processes results of previous tournament.

    Note
    ----

    Implementation based on the paper: “ReACTR: Realtime Algorithm 
    Configuration through Tournament Rankings”

    Parameters
    ----------
    scenario : argparse.Namespace
        Namespace containing all settings for the RTAC.
    logs : RTACLogs
        Object containing loggers and logging functions.
    """

    def __init__(self, scenario: argparse.Namespace, logs: RTACLogs):
        """
        Initialize tournament result processing class as necessary for
        ReACTR implementation.
        """
        super().__init__(scenario, logs)
        self.init_scores()

    def init_scores(self) -> None:
        """
        Initialize scores dict for trueskill.

        Returns
        -------
        None
        """
        self.scores = dict.fromkeys(list(self.pool.keys()), 
                                        (trueskill.INITIAL_MU,
                                         trueskill.INITIAL_SIGMA))

    def find_best(self, current_dict: list, number: int) -> list:
        """
        Find the configurations scored as best by trueskill.

        Parameters
        ----------
        current_dict : list
            Dictionary with configuration ids as key and
            trueskill scores (mu, sigma) as value.
        n_best : int
            Number of best configurations to draw.

        Returns
        -------
        list
            List of best configurations.
        """
        best_list = sorted(current_dict.items(), key=lambda kv: kv[1][1])

        return best_list[:number]

    def get_winner(self, times: list[float], res: list[float]) \
            -> tuple[int, list[int]]:
        """
        Get index of the winning configuration and ranks.

        Parameters
        ----------
        times : list[float]
            List of time results of previous tournament.
        res : list[float]
            List of objective results of previous tournament.

        Returns
        -------
        tuple
            - **winner** : int,
              Index of the winner.
            - **ranks** : list[int],
              Ranks of the contenders.
        """
        if not self.scenario.objective_min:
            winner = times.index(min(times))

        else:
            winner = res.index(min(res))

        ranks = []
        for core in range(self.scenario.number_cores):
            if core == winner:
                ranks.append(1)
            else:
                ranks.append(2)

        return winner, ranks

    def process_results(self, rtac_data: RTACData | RTACDatapp, 
                        instance: str = None,
                        tourn_nr: int = None) -> None:
        """
        Perform tournament result processing necessary to replace contenders
        in the pool and select contenders for the next tournament/problem 
        instance according to the ReACTR implementation.

        Parameters
        ----------
        rtac_data : RTACData | RTACDatapp
            Object containing data and objects necessary
            throughout the rtac modules.
        instance : str
            ID of the configuration to have won the previous tournament. 
            Defaults to None.
        tourn_nr: int
            Number of the tournament that is processed.

        Returns
        -------
        None
        """
        self.rtac_data = rtac_data
        for core in range(self.scenario.number_cores):
            # Setting timeout as time result if ta was terminated
            if self.rtac_data.ta_res[core] == self.huge_float:
                self.rtac_data.ta_res_time[core] = self.scenario.timeout

        if not self.scenario.objective_min:
            results = list(self.rtac_data.ta_res_time[:])
        else:
            results = list(self.rtac_data.ta_res[:])

        self.result_summary_terminal(results)

        times = list(self.rtac_data.ta_res_time[:])

        self.rtac_data.newtime = min(times)
        res = list(self.rtac_data.ta_res[:])
        self.rtac_data.best_res = min(res)

        winner, ranks = self.get_winner(times, res)

        if self.scenario.verbosity in (1, 2):
            res = list(self.rtac_data.ta_res[:])
            if self.scenario.gray_box:
                for core, contender in enumerate(self.contender_dict.values()):
                    contender.features = self.rtac_data.RuntimeFeatures[core]
            tourn_results = \
                [self.contender_dict, [[r, t] for r, t in zip(res, times)]]

            print('\nResults of this tournament:\n \nContender', ' ' * 19,
                  '   [Objective, Time]')
            for a in zip(*tourn_results):
                print(*a)
            print('\n')
            tr_str = ''
            for tr in tourn_results:
                tr_str += str(tr) + ' '
            self.logs.general_log(f'Results of this tournament: {tr_str}')

        # Set the results of the tournament
        individuals = [None] * self.scenario.number_cores
        contender_ids = list(self.contender_dict.keys())
        for core in range(self.scenario.number_cores):
            skill = (self.scores[contender_ids[core]][0], 
                     self.scores[contender_ids[core]][1])
            individuals[core] = Contender()
            individuals[core].skill = skill
            individuals[core].rank = ranks[core]

            if self.scenario.verbosity == 2:
                print('Contender', contender_ids[core], 'has the rank',
                      individuals[core].rank)
        print('\n')

        # Process the results of the tournament
        trueskill.AdjustPlayers(individuals)

        if self.scenario.verbosity in (1, 2):
            print('\nSkills of the contenders from tournament:\n \nContender',
                  ' ' * 31, '   (Mu', ' ' * 14, ', Sigma', ' ' * 10, ')')

        # Update Scores
        for core in range(self.scenario.number_cores):
            self.scores[contender_ids[core]] = individuals[core].skill
            if self.scenario.verbosity in (1, 2):
                print(contender_ids[core], 'skills are:',
                      individuals[core].skill)

    def manage_pool(self) -> None:
        """
        Replace contenders in pool according to Mu and Sigma (TrueSKill).

        Returns
        -------
        None
        """
        # Replace contenders in self.pool, if performance below average
        contender_ids = list(self.pool.keys())
        for core in range(self.scenario.contenders):
            # Contenders with a performance variance (sigma) <=
            # self.scenario.kill are eligible to be replaced
            if self.scores[contender_ids[core]][1] <= self.scenario.kill: 
                tournament_list = {}
                names = list(self.scores)
                for c in range(self.scenario.contenders):
                    tournament_list[c] = [names[c], self.scores[names[c]][0]]

                # Sort according to mean performance (Mu)
                best_list = \
                    self.find_best(tournament_list, self.scenario.contenders)

                # Get 5 best performing contenders for breeding
                best_five = best_list[len(best_list) - 5:]

                # Contenders which also have mean performance lower
                # than median performane are replaced by new contenders
                if self.scores[contender_ids[core]][0] \
                        < self.scores[best_list[
                            int(self.scenario.contenders / 2)][1][0]][0]:       

                    # Replace by randomly generated contender if chance
                    # is lower than self.scenario.chance
                    chance = np.random.uniform(1, 100, 1)
                    mutated_individual = \
                        self.random_config_gen.generate(self.tourn_nr)
                    if chance <= self.scenario.chance:
                        del self.pool[contender_ids[core]]
                        new_contender_id = mutated_individual.id
                        self.pool[new_contender_id]\
                            = mutated_individual
                        if self.scenario.verbosity in (1, 2):
                            print('\nReplaced contender',
                                  f'{contender_ids[core]} by randomly',
                                  'generated contender.')

                    # Else generate new contender by genetic crossover
                    elif chance > self.scenario.chance:
                        mutated = 0
                        parent_one, parent_two = \
                            random.sample([0, 1, 2, 3, 4], 2)
                        self.scenario.config_space
                        del self.pool[contender_ids[core]]
                        new_contender_id = uuid.uuid4().hex
                        self.pool[new_contender_id] = {}

                        for param in self.scenario.config_space:
                            which = np.random.uniform(0, 1, 1)

                            if 0.5 < which:
                                self.pool[new_contender_id][param] \
                                    = self.pool[
                                    best_five[parent_one][1][0]].conf[param]

                            elif 0.5 >= which:
                                self.pool[new_contender_id][param] \
                                    = self.pool[
                                    best_five[parent_two][1][0]].conf[param]

                            mutation = int(np.random.uniform(0, 100, 1))
                            if mutation <= self.scenario.mutate:
                                self.pool[new_contender_id][param]\
                                    = mutated_individual.conf[param]
                                mutated = mutated + 1

                        self.pool[new_contender_id] = \
                            Configuration(
                                new_contender_id,
                                self.pool[new_contender_id], [],
                                Generator.crossover, self.tourn_nr)
                        if self.scenario.verbosity in (1, 2):
                            print('\nReplaced contender',
                                  f'{contender_ids[core]} by contender',
                                  'generated via crossover.')
                        if self.scenario.verbosity == 2:
                            print(f'Mutation of {mutated} genes happened for',
                                  f'the new contender {new_contender_id}!\n')

                    # Delete scores of replaced contender and insert initial
                    # scores for new contender
                    del self.scores[contender_ids[core]]
                    self.scores[new_contender_id] = \
                        (trueskill.INITIAL_MU, trueskill.INITIAL_SIGMA)

    def select_contenders(self) -> None:
        """
        Select scenario.contenders == #contenders for next
        tournament/problem instance: top number of 
        'self.scenario.keeptop' and the rest randomly.

        Returns
        -------
        None
        """
        tournament_list = {}

        # Choose the two best contenders
        names = list(self.scores)
        for c in range(self.scenario.contenders):
            tournament_list[c] = [names[c], self.scores[names[c]][0]]
        best_list = self.find_best(tournament_list, self.scenario.contenders)
        self.contender_dict = {}
        for keep in range(self.scenario.keeptop):
            contender_id = best_list[self.scenario.contenders - 1 - keep][1][0]
            self.contender_dict[contender_id] = self.pool[contender_id]

        # Fill in the rest with randomly chosen contenders from pool
        temp_pool = copy.copy(self.pool)
        for contender in self.contender_dict:
            del temp_pool[contender]
        random_pick = \
            random.sample(
                list(temp_pool.keys()),
                self.scenario.number_cores - self.scenario.keeptop)
        for rp in random_pick:
            self.contender_dict[rp] = temp_pool[rp]

        if self.scenario.verbosity == 2:
            print('\nNew contender list is:',
                  *self.contender_dict, '\n', sep='\n')


class ResultProcessingpp(ResultProcessing):
    """Process results of prvious tournament."""

    def duplicates(self, ranks: list[int], rank: float) -> list[int]:
        """
        List the indices of the result in the results list.

        Parameters
        ----------
        ranks : list[int]
            List of objective results of previous tournament.
        rank : float
            A single result.

        Returns
        -------
        list[int]
            List of indices of this result in the results list.
        """
        return [i for i, x in enumerate(ranks) if x == rank]

    def get_winner(self, times: list[float], res: list[float]) \
            -> tuple[int, list[int]]:
        """
        Get index of the winning configuration including last known
        intermediate outputs to break ties. Additionally outputs complete
        ranking to compute more detailed assessment with trueskill.

        Parameters
        ----------
        times : list[float]
            List of time results of previous tournament.
        res : list[float]
            List of objective results of previous tournament.

        Returns
        -------
        tuple
            - **winner** : int,
              Index of the winner.
            - **ranks** : list[int],
              Ranks of the contenders..
        """
        if not self.scenario.objective_min:
            winner = times.index(min(times))

        else:
            winner = res.index(min(res))

        if not any(elem is None for sublist in self.rtac_data.interim
                   for elem in sublist):

            ranks = [0 for core in range(self.scenario.number_cores)]

            interim_sorted = [[self.rtac_data.interim[j][i]
                              for j in range(self.scenario.number_cores)]
                              for i, _ in enumerate(self.rtac_data.interim[0])]

            interim_sorted = np.array(interim_sorted)
            interim_sorted = interim_sorted.astype(float)

            for i, isort in enumerate(interim_sorted):
                if self.rtac_data.interim_meaning[i] is \
                        InterimMeaning.decrease:
                    interim_sorted[i] = rankdata(isort,
                                                 method='dense',
                                                 nan_policy="propagate")
                elif self.rtac_data.interim_meaning[i] is \
                        InterimMeaning.increase:
                    interim_sorted[i] = rankdata([-1 * i if i is not None
                                                  else None for i in isort],
                                                 method='dense',
                                                 nan_policy="propagate")

            for _, isort in enumerate(interim_sorted):
                for r, _ in enumerate(ranks):
                    ranks[r] += isort[r]

            if self.scenario.objective_min:
                res_ranks = rankdata(res, method='dense', nan_policy="propagate")

                duplicates = []

                for rank in sorted(set(res_ranks)):
                    duplicates.append(self.duplicates(res_ranks, rank))
                
                for duplicate in duplicates:
                    if len(duplicate) > 1:
                        interim_ranks = [ranks[dup] for dup in duplicate]
                        if not all(np.isnan(ir) for ir in interim_ranks):
                            tie_winner = \
                                duplicate[interim_ranks.index(min(interim_ranks))]
                            interim_ranks = rankdata(interim_ranks, method='dense')
                            interim_ranks -= min(interim_ranks)
                            for d, ir in zip(duplicate, interim_ranks):
                                for r, _ in enumerate(res_ranks):
                                    if d == r and r != winner and r != tie_winner:
                                        res_ranks[r] += interim_ranks[ir]
                                    elif np.isnan(max(interim_ranks)):
                                        res_ranks[r] += self.scenario.number_cores
                                    else:
                                        res_ranks[r] += max(interim_ranks)

                ranks = res_ranks

            ranks = rankdata(ranks, method='dense')

        else:
            ranks = [1 for core in range(self.scenario.number_cores)]

        ranks[winner] = 0

        return winner, ranks


class ResultProcessingCPPL(AbstractResultProcessing):
    """
    Process results of previous tournament.

    Parameters
    ----------
    scenario : argparse.Namespace
        Namespace containing all settings for the RTAC.
    logs : RTACLogs
        Object containing loggers and logging functions.
    """

    def __init__(self, scenario: argparse.Namespace, logs: RTACLogs):
        """
        Initialize tournament result processing class as necessary for
        CPPL implementation.
        """
        super().__init__(scenario, logs)
        if self.scenario.isolate_bandit:
            queue = multiprocessing.Queue()
            p = multiprocessing.Process(target=self.init_cppl,
                                        args=(self.scenario,
                                              self.pool,
                                              self.random_config_gen,
                                              self.contender_dict,
                                              queue))
            p.start()
            p.join()
            self.bandit, self.bandit_models = queue.get()
            self.sum = 0
        else:
            from rtac.ac_functionalities.ranking import cppl
            self.cppl = cppl.CPPL(scenario, self.pool, self.contender_dict)
            self.cppl.random_config_gen = self.random_config_gen
            self.bandit = self.cppl.bandit
            self.bandit_models = self.cppl.bandit_models

    def init_cppl(self, scenario: argparse.Namespace,
                  pool: dict[str, Configuration],
                  random_config_gen: RandomConfigGen,
                  contender_dict: dict[str, Configuration],
                  queue: multiprocessing.Queue) -> None:
        """
        Initialize cppl in isolated mode. The bandit functions are called and 
        executed in a separate thread so no build up in background threads of 
        libraries that numpy, scipy and sklearn depend on is possible.

        Parameters
        ----------
        scenario : argparse.Namespace
            Namespace containing all settings for the RTAC.
        pool : dict[str, Configuration]
            Initial pool of Configurations. Loaded from logas or randomly 
            generated.
        random_config_gen : RandomConfigGen
            Random configuration generator.
        contender_dict : dict[str, Configuration]
            List of contenders in the upcoming tournament. Loaded from logas or 
            randomly selected.
        queue : multiprocessing.Queue
            Queue to send data back to main thread.

        Returns
        -------
        None
        """
        from rtac.ac_functionalities.ranking import cppl

        cppl = cppl.CPPL(scenario, pool, contender_dict)
        cppl.random_config_gen = random_config_gen
        bandit = cppl.bandit
        bandit_models = cppl.bandit_models

        with open("cpplclass.pkl", "wb") as f:
            pickle.dump(cppl, f)

        queue.put((bandit, bandit_models))

    def process_tourn(self, rtac_data: RTACData | RTACDatapp,
                      instance: str = None,
                      tourn_nr: int = None) -> str:
        """
        Manage result processing.

        Parameters
        ----------
        rtac_data : RTACData | RTACDatapp
            Object containing data and objects necessary
            throughout the rtac modules.
        instance : str
            ID of the configuration to have won the previous tournament. 
            Defaults to None.
        tourn_nr: int
            Number of the tournament that is processed. Defaults to None.

        Returns
        -------
        str
            ID of the configuration to have won the previous tournament.
        """
        self.rtac_data = rtac_data

        if not self.scenario.baselineperf:
            self.process_results(rtac_data, instance, tourn_nr)
            if self.rtac_data.winner.value != 0:
                self.manage_pool()
            if not self.scenario.resume:
                self.select_contenders()
        else:
            self.rtac_data = rtac_data
            self.rtac_data.newtime = self.rtac_data.ta_res_time[0]

        if self.rtac_data.winner.value == 0:
            winner = None
        else:
            winner = self.rtac_data.winner.value

        return winner

    def cppl_process_results(self, contender_dict: dict[str, Configuration], 
                             scenario: argparse.Namespace,
                             rtac_data: RTACData | RTACDatapp,
                             instance: str, pool: dict[str, Configuration], 
                             ob: bool, queue: multiprocessing.Queue) -> None:
        """
        Perform tournament result processing necessary to replace contenders
        in the pool and select contenders for the next tournament/problem 
        instance within a separate thread.

        Parameters
        ----------
        contender_dict : dict[str, Configuration]
            List of contenders in the upcoming tournament. Loaded from logas or 
            randomly selected.
        scenario : argparse.Namespace
            Namespace containing all settings for the RTAC.
        rtac_data : RTACData | RTACDatapp
            Object containing data and objects necessary
            throughout the rtac modules.
        instance : str
            ID of the configuration to have won the previous tournament. 
            Defaults to None.
        pool : dict[str, Configuration]
            Initial pool of Configurations. Loaded from logas or randomly 
            generated.
        ob : bool
            True if scenario is objective value minimization, False if not.
        queue : multiprocessing.Queue
            Queue to send data back to main thread.

        Returns
        -------
        None
        """
        with open("cpplclass.pkl", "rb") as f:
            cppl = pickle.load(f)

        cppl.contender_dict = contender_dict
        cppl.pool = pool
        results = []
        times = []
        for core in range(scenario.number_cores):
            times.append(rtac_data.ta_res_time[core])
            results.append(rtac_data.ta_res[core])
        if not ob:
            cppl.results = times
        else:
            cppl.results = results
        cppl.instance = instance
        cppl.process_results()
        bandit = cppl.bandit
        bandit_models = cppl.bandit_models

        with open("cpplclass.pkl", "wb") as f:
            pickle.dump(cppl, f)

        queue.put((bandit, bandit_models, results, times))

    def process_results(self, rtac_data: RTACData | RTACDatapp,
                        instance: str = None,
                        tourn_nr: int = None) -> None:
        """
        Perform tournament result processing necessary to replace contenders
        in the pool and select contenders for the next tournament/problem 
        instance.

        Parameters
        ----------
        rtac_data : RTACData | RTACDatapp
            Object containing data and objects necessary
            throughout the rtac modules.
        instance : str
            ID of the configuration to have won the previous tournament. 
            Defaults to None.
        tourn_nr: int
            Number of the tournament that is processed.

        Returns
        -------
        None
        """
        self.start_time = time.time()
        results = []
        times = []
        for core in range(self.scenario.number_cores):
            times.append(rtac_data.ta_res_time[core])
            results.append(rtac_data.ta_res[core])
        if not self.scenario.objective_min:
            self.result_summary_terminal(times, tourn_nr)
        else:
            self.result_summary_terminal(results, tourn_nr)
        if self.scenario.isolate_bandit:
            queue = multiprocessing.Queue()
            p = multiprocessing.Process(target=self.cppl_process_results,
                                        args=(self.contender_dict,
                                              self.scenario, self.rtac_data,
                                              instance, self.pool, 
                                              self.scenario.objective_min,
                                              queue))
            p.start()
            p.join()
            self.bandit, self.bandit_models, results, times = queue.get()
        else:
            self.cppl.contender_dict = self.contender_dict
            self.cppl.pool = self.pool
            if not self.scenario.objective_min:
                self.cppl.results = times
            else:
                self.cppl.results = results
            self.cppl.instance = instance
            self.cppl.process_results()
            self.bandit = self.cppl.bandit
            self.bandit_models = self.cppl.bandit_models

        self.rtac_data.newtime = min(times)
        self.best_res = min(results)
        if not self.scenario.objective_min:
            self.winner = times.index(min(times))
        else:
            self.winner = results.index(min(results))
        
        res = list(self.rtac_data.ta_res[:])
        self.rtac_data.best_res = min(res)

        if self.scenario.verbosity in (1, 2):
            times = list(self.rtac_data.ta_res_time[:])
            res = list(self.rtac_data.ta_res[:])
            if self.scenario.gray_box:
                for core, contender in enumerate(self.contender_dict.values()):
                    contender.features = self.rtac_data.RuntimeFeatures[core]
            tourn_results = \
                [self.contender_dict, [[r, t] for r, t in zip(res, times)]]

            print('\nResults of this tournament:\n \nContender', ' ' * 19,
                  '   [Objective, Time]')
            for a in zip(*tourn_results):
                print(*a)
            print('\n')
            tr_str = ''
            for tr in tourn_results:
                tr_str += str(tr) + ' '
            self.logs.general_log(f'Results of this tournament: {tr_str}')

    def cppl_manage_pool(self, contender_dict: dict[str, Configuration], 
                         queue: multiprocessing.Queue) -> None:
        """
        Replace contenders in pool if necessary. Runs in separate thread.

        Parameters
        ----------
        contender_dict : dict[str, Configuration]
            List of contenders in the upcoming tournament. Loaded from logas or 
            randomly selected.
        queue : multiprocessing.Queue
            Queue to send data back to main thread.

        Returns
        -------
        None
        """
        with open("cpplclass.pkl", "rb") as f:
            cppl = pickle.load(f)

        cppl.contender_dict = contender_dict

        cppl.manage_pool()

        queue.put((cppl.pool))

        with open("cpplclass.pkl", "wb") as f:
            pickle.dump(cppl, f)

    def manage_pool(self) -> None:
        """
        Replace contenders in pool if necessary.

        Returns
        -------
        None
        """
        if self.scenario.isolate_bandit:
            queue = multiprocessing.Queue()
            p = multiprocessing.Process(target=self.cppl_manage_pool,
                                        args=(self.contender_dict, queue))
            p.start()
            p.join()

            self.pool = queue.get()

        else:
            self.cppl.manage_pool()

    def cppl_select_contenders(self, queue: multiprocessing.Queue) -> None:
        """
        Select contenders for next tournament/problem instance.

        Parameters
        ----------
        queue : multiprocessing.Queue
            Queue to send data back to main thread.

        Returns
        -------
        None
        """
        with open("cpplclass.pkl", "rb") as f:
            cppl = pickle.load(f)

        cppl.select_contenders()

        contender_dict = cppl.contender_dict

        with open("cpplclass.pkl", "wb") as f:
            pickle.dump(cppl, f)

        queue.put((contender_dict))

    def select_contenders(self) -> None:
        """
        Select contenders for next tournament/problem instance.

        Returns
        -------
        None
        """
        if self.scenario.isolate_bandit:
            queue = multiprocessing.Queue()
            p = multiprocessing.Process(target=self.cppl_select_contenders,
                                        args=(queue, ))
            p.start()
            p.join()
            self.contender_dict = queue.get()
        else:
            self.cppl.select_contenders()

            self.contender_dict = self.cppl.contender_dict

        if self.scenario.verbosity == 2:
            print('\nNew contender list is:',
                  *self.contender_dict, '\n', sep='\n')


def processing_factory(
    scenario: argparse.Namespace,
        logs: RTACLogs
) -> ResultProcessing | ResultProcessingpp | ResultProcessingCPPL:
    """
    Class factory to return the initialized class with data structures
    appropriate to the RTAC method `scenario.ac`.

    Parameters
    ----------
    scenario : argparse.Namespace
        Namespace containing all settings for the RTAC.
    logs : RTACLogs
        Object containing loggers and logging functions.

    Returns
    -------
    ResultProcessing or ResultProcessingpp or ResultProcessingCPPL
        Initialized BaseTARunner object matching the RTAC method of
        the scenario.
    """

    if scenario.ac is ACMethod.ReACTR:
        return ResultProcessing(scenario, logs)

    elif scenario.ac is ACMethod.ReACTRpp:
        return ResultProcessingpp(scenario, logs)

    elif scenario.ac is ACMethod.CPPL:
        return ResultProcessingCPPL(scenario, logs)


if __name__ == "__main__":
    pass
