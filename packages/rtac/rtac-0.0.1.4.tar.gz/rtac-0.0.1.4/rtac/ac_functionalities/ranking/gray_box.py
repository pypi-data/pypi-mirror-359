"""
Implements gray-box model based on cost-sensitive random forest from CostCla.
"""

import six
import sys
import joblib
import numpy as np
np.float = float
from sklearn import __version__ as sklearn_version
from packaging import version
from collections import Counter
import sklearn.ensemble._base as base
# Replacing/adding modules used in costcla based on deprecated sklearn modules
sys.modules['sklearn.ensemble.base'] = base
sys.modules['sklearn.externals.joblib'] = joblib
sys.modules['sklearn.externals.six'] = six
sys.modules['sklearn.externals.six.moves'] = six.moves

import multiprocessing
import costcla.models.bagging as bagging_mod


# Patching np.int to int
def _patched_partition_estimators(n_estimators, n_jobs):
    """Patched version of _partition_estimators with np.int replaced by int."""
    if n_jobs == -1:
        n_jobs = min(multiprocessing.cpu_count(), n_estimators)
    else:
        n_jobs = min(n_jobs, n_estimators)

    n_estimators_per_job = \
        (n_estimators // n_jobs) * np.ones(n_jobs, dtype=int)
    n_estimators_per_job[:n_estimators % n_jobs] += 1
    starts = np.cumsum(n_estimators_per_job)

    return n_jobs, n_estimators_per_job.tolist(), [0] + starts.tolist()


bagging_mod._partition_estimators = _patched_partition_estimators

from sklearn.utils import column_or_1d
import costcla.metrics.costs as costs_mod


# Patching np.float to float
def _patched_cost_loss(y_true, y_pred, cost_mat):
    """Patched version of cost_loss with np.float replaced by float."""
    y_true = column_or_1d(y_true)
    y_true = (y_true == 1).astype(float)
    y_pred = column_or_1d(y_pred)
    y_pred = (y_pred == 1).astype(float)
    cost = y_true * ((1 - y_pred) * cost_mat[:, 1] + y_pred * cost_mat[:, 2])
    cost += (
        (1 - y_true) * (
            y_pred * cost_mat[:, 0] + (1 - y_pred) * cost_mat[:, 3]))
    return np.sum(cost)


costs_mod.cost_loss = _patched_cost_loss

from costcla.models.bagging import BaseBagging


# Patching CostCla to work with sklearn >= 1.2
_original_init = BaseBagging.__init__


def _patched_init(self,
                  base_estimator=None,
                  n_estimators=10,
                  max_samples=1.0,
                  max_features=1.0,
                  bootstrap=True,
                  bootstrap_features=False,
                  combination='majority_voting',
                  n_jobs=1,
                  random_state=None,
                  verbose=0):
    """Patched __init__ version for the BaseBagging class."""
    # Handle estimator argument rename in sklearn >= 1.2
    if version.parse(sklearn_version) >= version.parse("1.2"):
        super(BaseBagging, self).__init__(
            estimator=base_estimator,
            n_estimators=n_estimators)
    else:
        super(BaseBagging, self).__init__(
            base_estimator=base_estimator,
            n_estimators=n_estimators)

    self.max_samples = max_samples
    self.max_features = max_features
    self.bootstrap = bootstrap
    self.bootstrap_features = bootstrap_features
    self.combination = combination
    self.n_jobs = n_jobs
    self.random_state = random_state
    self.verbose = verbose


BaseBagging.__init__ = _patched_init


from costcla.models import CostSensitiveRandomPatchesClassifier
from threadpoolctl import threadpool_limits


class Gray_Box():
    """Class containing gray-box model and data processing functions."""

    def __init__(self):
        self.gb_cla = CostSensitiveRandomPatchesClassifier
 
    def prepare_predict_data(
        self, rec_data: dict[int, list], instances: list,
            gb_pw_inst_archive: list, mtp: dict[int, int], 
            pair_cores: list[list[int]]
    ) -> tuple[list, list, list, list, int, list]:
        """
        Transform single runtime output data instances into pairwise 
        comparison data instances.

        Note
        ----

        Implementation based on the paper: “Realtime gray-box algorithm 
        configuration using cost-sensitive classification” 

        Parameters
        ----------
        rec_data : dict[int, list]
            All runtime output data recorded so far in the tournament sorted by 
            core the target algorithm runs on
        instances : list[list]
            Unique instances of recorded runtime output.
        gb_pw_inst_archive : list[list]
            All unique pairwise comparison instances.
        mtp : dict[int, int]
            Key is core, value is the last time point of the data recorded.
        pair_cores : list[list[int]]
            Core pairs corresponding to the Configurations compared in 
            gb_pw_inst_archive.

        Returns
        -------
        tuple
            - **pw_instances** : list[list],
              Pairwise comparisons of Configurations based on the most current 
              output.
            - **cores** : list[list],
              Core pairs corresponding to the Configurations compared in 
              pw_istances.
            - **instances** : bool,
              Unique instances of recorded runtime output.
            - **gb_pw_inst_archive** : list[list],
              All unique pairwise comparison instances.
            - **max_time_points** : dict[int, int],
              Key is core, value is the last time point of the data recorded.
            - **pair_cores** : list[list[int]],
              Core pairs corresponding to the Configurations compared in 
              gb_pw_inst_archive.
        """

        # Get last timepoint of recording for configs, if there were any
        max_time_points = {}
        for core, rd in rec_data.items():
            rk = rd.keys()
            if rk:
                max_time_points[core] = max(rk)

        # Do not waste time computing with unchanged records
        if mtp != max_time_points:

            mtp = max_time_points
            cores = []

            # Compute paiwise comparisons
            if len(max_time_points) > 1:
                recorded_cores = max_time_points.keys()
                pw_instances = []

                for core_i in recorded_cores:
                    for core_j in recorded_cores:
                        if core_i != core_j:
                            conf_i = rec_data[core_i][max_time_points[core_i]]
                            conf_j = rec_data[core_j][max_time_points[core_j]]

                            pw_inst = [
                                conf_i['CPUTimeExpended'],
                                *conf_i['rt_feats'],
                                conf_j['CPUTimeExpended'],
                                *conf_j['rt_feats'],
                                conf_i['CPUTimeExpended'] 
                                - conf_j['CPUTimeExpended'],
                                *[a - b for a, b 
                                  in zip(conf_i['rt_feats'],
                                         conf_j['rt_feats'])]
                            ]

                            # if pw_inst:  # not in gb_pw_inst_archive:
                            pw_instances.append(pw_inst)
                            gb_pw_inst_archive.append(pw_inst)
                            pair_cores.append(
                                [conf_i['core'], conf_j['core']])
                            instances.append([conf_i, conf_j])
                            cores.append([core_i, core_j])

                return (pw_instances, cores, instances, gb_pw_inst_archive,
                        max_time_points, pair_cores)
            else:
                return ([], [], instances, gb_pw_inst_archive, mtp,
                        pair_cores)
        else:
            return [], [], instances, gb_pw_inst_archive, mtp, pair_cores

    def prepare_train_data(
        self, X_train: list[list], data: list[list], cores: list[list],
            winner: int, res: dict[int, float], instances: list[list],
            y: list[int], cost_mat: list[list]
    ) -> tuple[list[list], list[list], list[list]]:
        """
        Adjust and add pairwise runtime output data gathered in tournament to 
        the total runtime output data gathered so far to be used it for model 
        training.

        Parameters
        ----------
        X_train : list[list]
            Total pairwise runtime output data gathered so far.
        data : list[list]
            Pairwise runtime output data gathered during last tournament.
        cores : list[list],
            Core pairs corresponding to the Configurations compared in data.
        winner : int
            Index of the winning Configuration of the last tournament.
        res : dict[int, float]
            Results of the last tournament.
        instances : list[list]
            Unique instances of recorded runtime output.
        y : list[int]
            0 signififying Configuration_0 is better, 1 signifying 
            Configuration_1 is better within the pairwise comparison 
            corresponding to instances in X_train.
        cost_mat : list[list]
            Cost matrix corresponding to instances in X_train.

        Returns
        -------
        tuple
            - **X_train** : list[list],
              Updated total pairwise runtime output data gathered so far.
            - **y** : list[list],
              0 signififying Configuration_0 is better, 1 signifying 
              Configuration_1 is better within the pairwise comparison 
              corresponding to instances in updated X_train.
            - **cost_mat** : list[list],
              Cost matrix corresponding to instances in updated X_train.
        """

        max_res = max(res)
        disregard = []

        for i, (c, X) in enumerate(zip(cores, instances)):
            if winner in (c[0], c[1]) or (
                    res[c[0]] != max_res and res[c[1]] != max_res):
                if c[0] == winner:
                    y.append(0)  # 0 -> i wins
                elif c[1] == winner:
                    y.append(1)  # 1 -> j wins
                elif res[c[0]] != max_res and res[c[1]] != max_res:
                    if res[c[0]] < res[c[1]]:
                        y.append(0)
                    else:
                        y.append(1)
                # Avoid invalid value in scalar divide (1.0 - cost / cost_base)
                # in costcla==0.6 by using epsilon instead of 0
                epsilon = 0.000001
                cost_mat.append(
                    [max([epsilon, (res[c[0]] - res[c[1]]) / max_res]),
                     max([epsilon, (res[c[1]] - res[c[0]]) / max_res]),
                     0, 0])
            else:
                disregard.append(i)

        # Delete instances that compare configurations that both timed out
        for i in reversed(disregard):
            del data[i]

        X_train.extend(data)

        return X_train, y, cost_mat

    def train_gb(
        self, X_train: list[list], y_train: list[int],
            cost_mat_train: list[list], cores: list[list]
    ) -> CostSensitiveRandomPatchesClassifier | None:
        """
        Train gray-box model.

        Parameters
        ----------
        X_train : list[list]
            Total pairwise runtime output data gathered so far.
        y_train : list[int]
            0 signififying Configuration_0 is better, 1 signifying 
            Configuration_1 is better within the pairwise comparison 
            corresponding to instances in X_train.
        cost_mat_train : list[list]
            Cost matrix corresponding to instances in X_train.
        cores : list[list],
            Core pairs corresponding to the Configurations compared in X_train.

        Returns
        -------
        CostSensitiveRandomPatchesClassifier or None
            Trained gray-box model or None, if not sufficient data for 
            training.
        """

        if len(X_train) > 2:
            with threadpool_limits(limits=cores):
                X_train, y_train, cost_mat_train = \
                    np.array(X_train), np.array(y_train), \
                    np.array(cost_mat_train)
                self.model = CostSensitiveRandomPatchesClassifier(
                    combination='weighted_voting',
                    max_samples=0.25,
                    n_estimators=20
                ).fit(X_train, y_train.ravel(), cost_mat_train)

                return self.model
        else:
            return None

    def classify_configs(self, X_pred: list[list], cores: list[list],
                         model: CostSensitiveRandomPatchesClassifier) -> list:
        """
        Classify configurations in the current tournament based o current 
        pairwise comparison features.

        Parameters
        ----------
        X_pred : list[list]
            Pairwise comparison instances from most recent outputs.
        cores : list[list]
            Core number pairs corresponding to X_pred entries.
        model : CostSensitiveRandomPatchesClassifier
            Trained gray-box model.

        Returns
        -------
        list
            0 if C_0 is predicted to be better, 1 if otherwise, corresponding 
            to cores.
        """
        with threadpool_limits(limits=cores):
            predictions = None
            # self.model = model
            if not isinstance(X_pred, np.ndarray):
                X_pred = np.array(X_pred)
            if len(X_pred) > 1:
                predictions = model.predict(X_pred)

            return predictions

    def term_list(self, pred: list, cores: list[list], verbosity: int) -> list:
        """
        Process predictions and decide if and which Configuration runs should 
        be terminated.

        Parameters
        ----------
        pred : list
            0 if C_0 is predicted to be better, 1 if otherwise, corresponding 
            to cores.
        cores : list[list]
            Core number pairs.
        verbosity : int
            Hyperparameter turning on and off additional terminal outputs.

        Returns
        -------
        list
            Core indices of Configuration runs to be terminated.
        """

        better_counts = Counter()

        for i, (a, b) in enumerate(cores):
            if pred[i] == 0:
                better_counts[a] += 1
            else:
                better_counts[b] += 1

        # Ensure all cores are represented (even with 0 count)
        all_cores = set(core for pair in cores for core in pair)
        for core in all_cores:
            better_counts.setdefault(core, 0)

        # Convert to sorted list of (core, count)
        sorted_counts = \
            sorted(better_counts.items(), key=lambda x: x[1], reverse=True)

        # Assign ranks (higher count = better rank = lower number)
        ranks = {core: rank for rank, (core, _) in enumerate(sorted_counts)}

        # Compute average of best and worst ranks
        max_rank = max(ranks.values())
        min_rank = min(ranks.values())
        avg_rank = (max_rank + min_rank) / 2

        # Select cores better than avg_rank
        worse_than_avg = \
            [core for core, rank in ranks.items() if rank >= avg_rank]

        if len(set(better_counts.values())) == 1:
            return []
        else:
            if verbosity == 2:
                print('\n\n')
                print('GRAY BOX PAIRWSE COMPARISON STATS:')
                print("Better counts:", dict(better_counts))
                print("Ranks:", ranks)
                print("Average rank:", avg_rank)
                print("Worse than average:", worse_than_avg)
            return worse_than_avg


if __name__ == '__main__':
    pass
