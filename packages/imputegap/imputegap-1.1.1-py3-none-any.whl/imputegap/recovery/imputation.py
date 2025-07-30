import re
from imputegap.tools import utils
from imputegap.recovery.downstream import Downstream
from imputegap.recovery.evaluation import Evaluation

not_optimized = ["knn", "interpolation", "iterative_svd", "grouse", "dynammo", "rosl", "soft_impute", "spirit", "svt",
                 "tkcm", "deep_mvi", "brits", "mpin", "pristi", "bay_otide", "bit_graph", "gain", "grin", "hkmf_t",
                 "mice", "miss_forest", "miss_net", "trmf", "xgboost"]


class BaseImputer:
    """
    Base class for imputation algorithms.

    This class provides common methods for imputation tasks such as scoring, parameter checking,
    and optimization. Specific algorithms should inherit from this class and implement the `impute` method.

    Methods
    -------
    impute(params=None):
        Abstract method to perform the imputation.
    score(input_data, recov_data=None, downstream=None):
        Compute metrics for the imputed time series.
    _check_params(user_def, params):
        Check and format parameters for imputation.
    _optimize(parameters={}):
        Optimize hyperparameters for the imputation algorithm.
    """
    algorithm = ""
    logs = True
    verbose = True

    def __init__(self, incomp_data):
        """
        Initialize the BaseImputer with an infected time series matrix.

        Parameters
        ----------
        incomp_data : numpy.ndarray
            Matrix used during the imputation of the time series.
        """
        self.incomp_data = incomp_data
        self.recov_data = None
        self.metrics = None
        self.downstream_metrics = None
        self.downstream_plot = None
        self.parameters = None

    def impute(self, params=None):
        """
        Abstract method to perform the imputation. Must be implemented in subclasses.

        Parameters
        ----------
        params : dict, optional
            Dictionary of algorithm parameters (default is None).

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def score(self, input_data, recov_data=None, downstream=None, verbose=True):
        """
        Compute evaluation metrics for the imputed time series.
        Upstream and downstream metrics can be computed.

        Parameters
        ----------
        input_data : numpy.ndarray
            The original time series without contamination.
        recov_data : numpy.ndarray, optional
            The imputed time series (default is None).
        downstream : dict, optional
            Dictionary that calls, if active, the downstream evaluation. (default is None).
            format : {"model": "forcaster", "params": parameters}
        verbose : bool, optional
            Display the message from the evaluator (default is True).

        Returns
        -------
        None

        Example
        -------
            >>> imputer.score(ts.data, imputer.recov_data) # upstream
            >>> imputer.score(ts.data, imputer.recov_data, {"task": "forecast", "model": "hw-add", "comparator": "ZeroImputation"}) # downstream
        """
        if recov_data is not None:
            self.recov_data = recov_data

        if isinstance(downstream, dict) and downstream is not None:
            self.downstream_metrics, self.downstream_plot = Downstream(input_data, self.recov_data, self.incomp_data, self.algorithm, downstream).downstream_analysis()
        else:
            self.metrics = Evaluation(input_data, self.recov_data, self.incomp_data, self.algorithm, verbose).compute_all_metrics()

    def _check_params(self, user_def, params):
        """
        Format the parameters for optimization or imputation.

        Parameters
        ----------
        user_def : bool
            Whether the parameters are user-defined or not.
        params : dict or list
            List or dictionary of parameters.

        Returns
        -------
        tuple
            Formatted parameters as a tuple.
        """

        if params is not None:
            if not user_def:
                self._optimize(params)

                if isinstance(self.parameters, dict):
                    self.parameters = tuple(self.parameters.values())

            else:
                if isinstance(params, dict):
                    params = tuple(params.values())

                self.parameters = params

            if self.algorithm == "iim":
                if len(self.parameters) == 1:
                    learning_neighbours = self.parameters[0]
                    algo_code = "iim " + re.sub(r'[\W_]', '', str(learning_neighbours))
                    self.parameters = (learning_neighbours, algo_code)

            if self.algorithm == "mrnn":
                if len(self.parameters) == 3:
                    hidden_dim, learning_rate, iterations = self.parameters
                    _, _, _, sequence_length = utils.load_parameters(query="default", algorithm="mrnn")
                    self.parameters = (hidden_dim, learning_rate, iterations, sequence_length)

        return self.parameters

    def _optimize(self, parameters={}):
        """
        Conduct the optimization of the hyperparameters using different optimizers.

        Parameters
        ----------
        parameters : dict
            Dictionary containing optimization configurations such as input_data, optimizer, and options.

        Returns
        -------
        None
        """
        from imputegap.recovery.optimization import Optimization

        optimizer = parameters.get('optimizer', "ray_tune")

        if self.algorithm in not_optimized and optimizer != "ray_tune":
            raise ValueError(
                f"\n\tThis algorithm '{self.algorithm}' is not optimized for this optimizer. "
                f"\n\tPlease use `run_tune` to optimize the hyperparameters for:\n\t\t {', '.join(not_optimized)}"
                "\n\tPlease use update your call :\n\t\t.impute(user_def=False, params={'input_data': ts.data, 'optimizer': 'ray_tune'})"
            )

        input_data = (
            parameters.get('input_data') if parameters.get('input_data') is not None else
            parameters.get('input') if parameters.get('input') is not None else
            parameters.get('data') if parameters.get('data') is not None else
            parameters.get('ts_input')
        )
        if input_data is None:
            raise ValueError(f"Need input_data to be able to adapt the hyper-parameters: {input_data}")

        defaults = utils.load_parameters(query="default", algorithm=optimizer)

        print("\n(OPTI) optimizer", optimizer, "has been called with", self.algorithm, "...\n")

        if optimizer.lower() in ["bayesian", "bo", "bayesopt"]:
            n_calls_d, n_random_starts_d, acq_func_d, selected_metrics_d = defaults
            options = parameters.get('options', {})

            n_calls = options.get('n_calls', n_calls_d)
            random_starts = options.get('n_random_starts', n_random_starts_d)
            func = options.get('acq_func', acq_func_d)
            metrics = options.get('metrics', selected_metrics_d)

            bo_optimizer = Optimization.Bayesian()

            optimal_params, _ = bo_optimizer.optimize(input_data=input_data,
                                                      incomp_data=self.incomp_data,
                                                      metrics=metrics,
                                                      algorithm=self.algorithm,
                                                      n_calls=n_calls,
                                                      n_random_starts=random_starts,
                                                      acq_func=func)

            if optimal_params is None:
                print("\n(OPTI) optimization does not find results for ", self.algorithm, " > load default params.\n")
                optimal_params = utils.load_parameters(query="default", algorithm=self.algorithm)

        elif optimizer.lower() in ["pso", "particle_swarm"]:
            n_particles_d, c1_d, c2_d, w_d, iterations_d, n_processes_d, selected_metrics_d = defaults
            options = parameters.get('options', {})

            n_particles = options.get('n_particles', n_particles_d)
            c1 = options.get('c1', c1_d)
            c2 = options.get('c2', c2_d)
            w = options.get('w', w_d)
            iterations = options.get('iterations', iterations_d)
            n_processes = options.get('n_processes', n_processes_d)
            metrics = options.get('metrics', selected_metrics_d)

            swarm_optimizer = Optimization.ParticleSwarm()

            optimal_params, _ = swarm_optimizer.optimize(input_data=input_data,
                                                         incomp_data=self.incomp_data,
                                                         metrics=metrics, algorithm=self.algorithm,
                                                         n_particles=n_particles, c1=c1, c2=c2, w=w,
                                                         iterations=iterations, n_processes=n_processes)

        elif optimizer.lower() in ["sh", "successive_halving"]:
            num_configs_d, num_iterations_d, reduction_factor_d, selected_metrics_d = defaults
            options = parameters.get('options', {})

            num_configs = options.get('num_configs', num_configs_d)
            num_iterations = options.get('num_iterations', num_iterations_d)
            reduction_factor = options.get('reduction_factor', reduction_factor_d)
            metrics = options.get('metrics', selected_metrics_d)

            sh_optimizer = Optimization.SuccessiveHalving()

            optimal_params, _ = sh_optimizer.optimize(input_data=input_data,
                                                      incomp_data=self.incomp_data,
                                                      metrics=metrics, algorithm=self.algorithm,
                                                      num_configs=num_configs, num_iterations=num_iterations,
                                                      reduction_factor=reduction_factor)

        elif optimizer.lower() in ["ray_tune", "ray"]:
            selected_metrics_d, n_calls_d, max_concurrent_trials_d = defaults

            options = parameters.get('options', {})
            n_calls = options.get('n_calls', n_calls_d)
            max_concurrent_trials = options.get('max_concurrent_trials', max_concurrent_trials_d)
            metrics = options.get('metrics', selected_metrics_d)

            ray_tune_optimizer = Optimization.RayTune()
            optimal_params = ray_tune_optimizer.optimize(input_data=input_data, incomp_data=self.incomp_data, metrics=metrics, algorithm=self.algorithm, n_calls=n_calls, max_concurrent_trials=max_concurrent_trials)

        else:
            n_calls_d, selected_metrics_d = defaults
            options = parameters.get('options', {})

            n_calls = options.get('n_calls', n_calls_d)
            metrics = options.get('metrics', selected_metrics_d)

            go_optimizer = Optimization.Greedy()

            optimal_params, _ = go_optimizer.optimize(input_data=input_data,
                                                      incomp_data=self.incomp_data,
                                                      metrics=metrics, algorithm=self.algorithm,
                                                      n_calls=n_calls)

        self.parameters = optimal_params

    def _check_dl_split(self, split_ratio):
        """
        Check whether the proportion of missing values in the contaminated data is acceptable
        for training a deep learning model. If more than 40% of the values are missing,
        the function returns False.

        Parameters
        ----------

        Returns
        -------
        bool
            True if the missing data ratio is less than or equal to 40%, False otherwise.
        """
        missing_ratio = utils.get_missing_ratio(self.incomp_data)

        ratio = 1 - split_ratio

        if missing_ratio <= ratio:
            return True
        else:
            print(f"\n(IMP) The proportion of missing values {missing_ratio*100}% is too high to train an effective deep learning model, limited to {int(round(ratio*100))}%.\n"
                  "Please consider reducing the contamination rate or selecting a different family of imputation methods")
            return False


class Imputation:
    """
    A class containing static methods for evaluating and running imputation algorithms on time series data.

    Methods
    -------
    evaluate_params(input_data, incomp_data, configuration, algorithm="cdrec"):
        Evaluate imputation performance using given parameters and algorithm.
    """

    def evaluate_params(input_data, incomp_data, configuration, algorithm="cdrec"):
        """
        Evaluate various metrics for given parameters and imputation algorithm.

        Parameters
        ----------
        input_data : numpy.ndarray
            The original time series without contamination.
        incomp_data : numpy.ndarray
            The time series with contamination.
        configuration : tuple
            Tuple of the configuration of the algorithm.
        algorithm : str, optional
            Imputation algorithm to use. Valid values: 'cdrec', 'mrnn', 'stmvl', 'iim' (default is 'cdrec').

        Returns
        -------
        dict
            A dictionary of computed evaluation metrics.
        """

        if isinstance(configuration, dict):
            configuration = tuple(configuration.values())

        if algorithm == 'cdrec':
            rank, epsilon, iterations = configuration
            algo = Imputation.MatrixCompletion.CDRec(incomp_data)
            algo.logs = False
            algo.impute(user_def=True, params={"rank": rank, "epsilon": epsilon, "iterations": iterations})

        elif algorithm == 'iim':
            if not isinstance(configuration, list):
                configuration = [configuration]
            learning_neighbours = configuration[0]
            alg_code = "iim " + re.sub(r'[\W_]', '', str(learning_neighbours))

            algo = Imputation.MachineLearning.IIM(incomp_data)
            algo.logs = False
            algo.impute(user_def=True, params={"learning_neighbours": learning_neighbours, "alg_code": alg_code})

        elif algorithm == 'mrnn':
            hidden_dim, learning_rate, iterations = configuration

            algo = Imputation.DeepLearning.MRNN(incomp_data)
            algo.logs = False
            algo.impute(user_def=True,
                        params={"hidden_dim": hidden_dim, "learning_rate": learning_rate, "iterations": iterations,
                                "seq_length": 7})

        elif algorithm == 'stmvl':
            window_size, gamma, alpha = configuration

            algo = Imputation.PatternSearch.STMVL(incomp_data)
            algo.logs = False
            algo.impute(user_def=True, params={"window_size": window_size, "gamma": gamma, "alpha": alpha})

        else:
            raise ValueError(f"Invalid algorithm: {algorithm}")

        algo.score(input_data)
        error_measures = algo.metrics

        return error_measures

    class Statistics:
        """
        A class containing specific imputation algorithms for statistical methods.

        Subclasses
        ----------
        ZeroImpute :
            Imputation method that replaces missing values with zeros.
        MinImpute :
            Imputation method that replaces missing values with the minimum value of the ground truth.
        MeanImputeBySeries :
            Imputation method that replaces missing values with the minimum value of the ground truth by series.
        Interpolation :
            Imputation method that replaces missing values with the Interpolation
        KNNImpute :
            Imputation method that replaces missing values with KNNImpute logic
        """

        class ZeroImpute(BaseImputer):
            """
            ZeroImpute class to impute missing values with zeros.

            Methods
            -------
            impute(self, params=None):
                Perform imputation by replacing missing values with zeros.
            """
            algorithm = "zero_impute"

            def impute(self, params=None):
                """
                Impute missing values by replacing them with zeros.
                Template for adding external new algorithm

                Parameters
                ----------
                params : dict, optional
                    Dictionary of algorithm parameters (default is None).

                Returns
                -------
                self : ZeroImpute
                    The object with `recov_data` set.
                """
                from imputegap.algorithms.zero_impute import zero_impute

                self.recov_data = zero_impute(self.incomp_data, params)

                return self

        class MeanImpute(BaseImputer):
            """
            MeanImpute class to impute missing values with the mean value of the ground truth.

            Methods
            -------
            impute(self, params=None):
                Perform imputation by replacing missing values with the mean value of the ground truth.
            """
            algorithm = "mean_impute"

            def impute(self, params=None):
                """
                Impute missing values by replacing them with the mean value of the ground truth.
                Template for adding external new algorithm

                Parameters
                ----------
                params : dict, optional
                    Dictionary of algorithm parameters (default is None).

                Returns
                -------
                self : MinImpute
                    The object with `recov_data` set.
                """
                from imputegap.algorithms.mean_impute import mean_impute

                self.recov_data = mean_impute(self.incomp_data, params)

                return self

        class MinImpute(BaseImputer):
            """
            MinImpute class to impute missing values with the minimum value of the ground truth.

            Methods
            -------
            impute(self, params=None):
                Perform imputation by replacing missing values with the minimum value of the ground truth.
            """
            algorithm = "min_impute"

            def impute(self, params=None):
                """
                Impute missing values by replacing them with the minimum value of the ground truth.
                Template for adding external new algorithm

                Parameters
                ----------
                params : dict, optional
                    Dictionary of algorithm parameters (default is None).

                Returns
                -------
                self : MinImpute
                    The object with `recov_data` set.
                """
                from imputegap.algorithms.min_impute import min_impute

                self.recov_data = min_impute(self.incomp_data, params)

                return self

        class MeanImputeBySeries(BaseImputer):
            """
            MeanImputeBySeries class to impute missing values with the mean value by series.

            Methods
            -------
            impute(self, params=None):
                Perform imputation by replacing missing values with the mean value by series
            """
            algorithm = "mean_impute"

            def impute(self, params=None):
                """
                Impute missing values by replacing them with the mean value of the series.

                Returns
                -------
                self : MeanImputeBySeries
                    The object with `recov_data` set.
                """
                from imputegap.algorithms.mean_impute_by_series import mean_impute_by_series

                self.recov_data = mean_impute_by_series(self.incomp_data, logs=self.logs, verbose=self.verbose)

                return self

        class Interpolation(BaseImputer):
            """
            Interpolation class to impute missing values with interpolation-based algorithm

            Methods
            -------
            impute(self, params=None):
                Perform imputation by replacing missing values with interpolation-based algorithm
            """
            algorithm = "interpolation"

            def impute(self, user_def=True, params=None):
                """
                Impute missing values by replacing them with the interpolation-based algorithm

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the interpolation algorithm, if None, default ones are loaded.

                Returns
                -------
                self : Interpolation
                    The object with `recov_data` set.

                Example
                -------
                    >>> interpolation_imputer = Imputation.Statistics.Interpolation(incomp_data)
                    >>> interpolation_imputer.impute()  # default parameters for imputation > or
                    >>> interpolation_imputer.impute(user_def=True, params={"method":"linear", "poly_order":2})  # user-defined > or
                    >>> interpolation_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = interpolation_imputer.recov_data
                """
                from imputegap.algorithms.interpolation import interpolation

                if params is not None:
                    method, poly_order = self._check_params(user_def, params)
                else:
                    method, poly_order = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = interpolation(incomp_data=self.incomp_data, method=method, poly_order=poly_order, logs=self.logs, verbose=self.verbose)

                return self


        class KNNImpute(BaseImputer):
            """
            KNNImpute class to impute missing values with K-Nearest Neighbor algorithm

            Methods
            -------
            impute(self, params=None):
                Perform imputation by replacing missing values with K-Nearest Neighbor
            """
            algorithm = "knn_impute"

            def impute(self, user_def=True, params=None):
                """
                Impute missing values by replacing them with the K-Nearest Neighbor value

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the KNNImpute algorithm, if None, default ones are loaded.

                    **Algorithm parameters:**

                        k : int, optional
                            Number of nearest neighbor (default is 5).
                        weights : str, optional
                            "uniform" for mean, "distance" for inverse-distance weighting.

                Returns
                -------
                self : KNNImpute
                    The object with `recov_data` set.

                Example
                -------
                    >>> knn_imputer = Imputation.Statistics.KNNImpute(incomp_data)
                    >>> knn_imputer.impute()  # default parameters for imputation > or
                    >>> knn_imputer.impute(user_def=True, params={'k': 5, 'weights': "uniform"})  # user-defined > or
                    >>> knn_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = knn_imputer.recov_data
                """
                from imputegap.algorithms.knn import knn

                if params is not None:
                    k, weights = self._check_params(user_def, params)
                else:
                    k, weights = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                k = utils.compute_rank_check(M=self.incomp_data.shape[0], rank=k, verbose=self.verbose)

                self.recov_data = knn(incomp_data=self.incomp_data, k=k, weights=weights, logs=self.logs, verbose=self.verbose)

                return self





    class MatrixCompletion:
        """
        A class containing imputation algorithms for matrix decomposition methods.

        Subclasses
        ----------
        CDRec :
            Imputation method using Centroid Decomposition.
        IterativeSVD :
            Imputation method using Iterative Singular Value Decomposition.
        GROUSE :
            Imputation method using Grassmannian Rank-One Update Subspace Estimation.
        ROSL :
            Imputation method using Robust Online Subspace Learning.
        SoftImpute :
            Imputation method using Soft Impute algorithm.
        SPIRIT :
            Imputation method using Streaming Pattern Discovery in Multiple Time-Series.
        SVT :
            Imputation method using Singular Value Thresholding algorithm.
        TRMF :
            Imputation method using Temporal Regularized Matrix Factorization.
        """

        class CDRec(BaseImputer):
            """
            CDRec class to impute missing values using Centroid Decomposition (CDRec).

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the CDRec algorithm.
            """

            algorithm = "cdrec"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the CDRec algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the CDRec algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                        rank : int
                            Rank of matrix reduction, which should be higher than 1 and smaller than the number of series.
                        epsilon : float
                            The learning rate used for the algorithm.
                        iterations : int
                            The number of iterations to perform.

                    **Auto-ML parameters:**

                        input_data : numpy.ndarray
                            The original time series dataset without contamination.
                        optimizer : str
                            The optimizer to use for parameter optimization. Valid values are "bayesian", "greedy", "pso", or "sh".
                        options : dict, optional
                            Optional parameters specific to the optimizer.

                        **Bayesian:**

                            n_calls : int, optional
                                Number of calls to the objective function. Default is 3.
                            metrics : list, optional
                                List of selected metrics to consider for optimization. Default is ["RMSE"].
                            n_random_starts : int, optional
                                Number of initial calls to the objective function, from random points. Default is 50.
                            acq_func : str, optional
                                Acquisition function to minimize over the Gaussian prior. Valid values: 'LCB', 'EI', 'PI', 'gp_hedge' (default is 'gp_hedge').

                        **Greedy:**

                            n_calls : int, optional
                                Number of calls to the objective function. Default is 3.
                            metrics : list, optional
                                List of selected metrics to consider for optimization. Default is ["RMSE"].

                        **PSO:**

                            n_particles : int, optional
                                Number of particles used.
                            c1 : float, optional
                                PSO learning coefficient c1 (personal learning).
                            c2 : float, optional
                                PSO learning coefficient c2 (global learning).
                            w : float, optional
                                PSO inertia weight.
                            iterations : int, optional
                                Number of iterations for the optimization.
                            n_processes : int, optional
                                Number of processes during optimization.

                        **Successive Halving (SH):**

                            num_configs : int, optional
                                Number of configurations to try.
                            num_iterations : int, optional
                                Number of iterations to run the optimization.
                            reduction_factor : int, optional
                                Reduction factor for the number of configurations kept after each iteration.


                        **RAY TUNE (ray_tune):**

                            n_calls : int, optional
                                Number of calls to the objective function (default is 10).
                            max_concurrent_trials : int, optional
                                Number of trials run in parallel, related to your total memory / cpu / gpu (default is 2).
                                Please increase the value if you have more resources

                Returns
                -------
                self : CDRec
                    CDRec object with `recov_data` set.

                Example
                -------
                    >>> cdrec_imputer = Imputation.MatrixCompletion.CDRec(incomp_data)
                    >>> cdrec_imputer.impute()  # default parameters for imputation > or
                    >>> cdrec_imputer.impute(user_def=True, params={'rank': 5, 'epsilon': 0.01, 'iterations': 100})  # user-defined > or
                    >>> cdrec_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "bayesian", "options": {"n_calls": 2}})  # automl with bayesian
                    >>> recov_data = cdrec_imputer.recov_data

                References
                ----------
                Khayati, M., Cudré-Mauroux, P. & Böhlen, M.H. Scalable recovery of missing blocks in time series with high and low cross-correlations. Knowl Inf Syst 62, 2257–2280 (2020). https://doi.org/10.1007/s10115-019-01421-7
                """
                from imputegap.algorithms.cdrec import cdrec

                if params is not None:
                    rank, epsilon, iterations = self._check_params(user_def, params)
                else:
                    rank, epsilon, iterations = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=False)

                rank = utils.compute_rank_check(M=self.incomp_data.shape[0], rank=rank, verbose=self.verbose)

                self.recov_data = cdrec(incomp_data=self.incomp_data, truncation_rank=rank, iterations=iterations, epsilon=epsilon, logs=self.logs, verbose=self.verbose)

                return self

        class IterativeSVD(BaseImputer):
            """
            IterativeSVD class to impute missing values using Iterative SVD.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the Iterative SDV algorithm.
            """

            algorithm = "iterative_svd"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the Iterative SVD algorithm.

                Parameters
                ----------
                 user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the Iterative SVD algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                        rank : int
                            Rank of matrix reduction, which should be higher than 1 and smaller than the number of series.


                Returns
                -------
                self : IterativeSVD
                    IterativeSVD object with `recov_data` set.

                Example
                -------
                    >>> i_svd_imputer = Imputation.MatrixCompletion.IterativeSVD(incomp_data)
                    >>> i_svd_imputer.impute()  # default parameters for imputation > or
                    >>> i_svd_imputer.impute(params={'rank': 5}) # user-defined  > or
                    >>> i_svd_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = i_svd_imputer.recov_data

                References
                ----------
                Olga Troyanskaya, Michael Cantor, Gavin Sherlock, Pat Brown, Trevor Hastie, Robert Tibshirani, David Botstein, Russ B. Altman, Missing value estimation methods for DNA microarrays , Bioinformatics, Volume 17, Issue 6, June 2001, Pages 520–525, https://doi.org/10.1093/bioinformatics/17.6.520
                """
                from imputegap.algorithms.iterative_svd import iterative_svd

                if params is not None:
                    rank  = self._check_params(user_def, params)[0]
                else:
                    rank = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                rank = utils.compute_rank_check(M=self.incomp_data.shape[0], rank=rank, verbose=self.verbose)

                self.recov_data = iterative_svd(incomp_data=self.incomp_data, truncation_rank=rank, logs=self.logs, verbose=self.verbose)

                return self

        class GROUSE(BaseImputer):
            """
            GROUSE class to impute missing values using GROUSE.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the GROUSE algorithm.
            """

            algorithm = "grouse"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the GROUSE algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the GROUSE algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                        max_rank : int
                            Max rank of matrix reduction, which should be higher than 1 and smaller than the number of series.


                Returns
                -------
                self : GROUSE
                    GROUSE object with `recov_data` set.

                Example
                -------
                    >>> grouse_imputer = Imputation.MatrixCompletion.GROUSE(incomp_data)
                    >>> grouse_imputer.impute()  # default parameters for imputation > or
                    >>> grouse_imputer.impute(params={'max_rank': 5}) # user-defined  > or
                    >>> grouse_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = grouse_imputer.recov_data

                References
                ----------
                D. Zhang and L. Balzano. Global convergence of a grassmannian gradient descent algorithm for subspace estimation. In Proceedings of the 19th International Conference on Artificial Intelligence and Statistics, AISTATS 2016, Cadiz, Spain, May 9-11, 2016, pages 1460–1468, 2016.
                """
                from imputegap.algorithms.grouse import grouse

                if params is not None:
                    max_rank  = self._check_params(user_def, params)[0]
                else:
                    max_rank = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                max_rank = utils.compute_rank_check(M=self.incomp_data.shape[0], rank=max_rank, verbose=self.verbose)

                self.recov_data = grouse(incomp_data=self.incomp_data, max_rank=max_rank, logs=self.logs, verbose=self.verbose)

                return self

        class ROSL(BaseImputer):
            """
            ROSL class to impute missing values using Robust Online Subspace Learning algorithm.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the ROSL algorithm.
            """

            algorithm = "rosl"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the ROSL algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the ROSL algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                         rank : int
                            The rank of the low-dimensional subspace for matrix decomposition.
                            Must be greater than 0 and less than or equal to the number of columns in the matrix.
                         regularization : float
                            The regularization parameter to control the trade-off between reconstruction accuracy and robustness.
                            Higher values enforce sparsity or robustness against noise in the data.

                Returns
                -------
                self : ROSL
                    ROSL object with `recov_data` set.

                Example
                -------
                    >>> rosl_imputer = Imputation.MatrixCompletion.ROSL(incomp_data)
                    >>> rosl_imputer.impute()  # default parameters for imputation > or
                    >>> rosl_imputer.impute(params={'rank': 5, 'regularization': 10}) # user-defined  > or
                    >>> rosl_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = rosl_imputer.recov_data

                References
                ----------
                X. Shu, F. Porikli, and N. Ahuja. Robust orthonormal subspace learning: Efficient recovery of corrupted low-rank matrices. In 2014 IEEE Conference on Computer Vision and Pattern Recognition, CVPR 2014, Columbus, OH, USA, June 23-28, 2014, pages 3874–3881, 2014.
                """
                from imputegap.algorithms.rosl import rosl

                if params is not None:
                    rank, regularization = self._check_params(user_def, params)
                else:
                    rank, regularization = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                rank = utils.compute_rank_check(M=self.incomp_data.shape[0], rank=rank, verbose=self.verbose)

                self.recov_data = rosl(incomp_data=self.incomp_data, rank=rank, regularization=regularization, logs=self.logs, verbose=self.verbose)

                return self

        class SoftImpute(BaseImputer):
            """
            SoftImpute class to impute missing values using Soft Impute algorithm.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the Soft Impute algorithm.
            """

            algorithm = "soft_impute"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the Soft Impute algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the Soft Impute algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                         max_rank : int
                            The max rank of the low-dimensional subspace for matrix decomposition.
                            Must be greater than 0 and less than or equal to the number of columns in the matrix.

                Returns
                -------
                self : SoftImpute
                    SoftImpute object with `recov_data` set.

                Example
                -------
                    >>> soft_impute_imputer = Imputation.MatrixCompletion.SoftImpute(incomp_data)
                    >>> soft_impute_imputer.impute()  # default parameters for imputation > or
                    >>> soft_impute_imputer.impute(params={'max_rank': 5}) # user-defined  > or
                    >>> soft_impute_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = soft_impute_imputer.recov_data

                References
                ----------
                R. Mazumder, T. Hastie, and R. Tibshirani. Spectral regularization algorithms for learning large incomplete matrices. Journal of Machine Learning Research, 11:2287–2322, 2010.
                """
                from imputegap.algorithms.soft_impute import soft_impute

                if params is not None:
                    max_rank = self._check_params(user_def, params)[0]
                else:
                    max_rank = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                max_rank = utils.compute_rank_check(M=self.incomp_data.shape[0], rank=max_rank, verbose=self.verbose)

                self.recov_data = soft_impute(incomp_data=self.incomp_data, max_rank=max_rank, logs=self.logs, verbose=self.verbose)

                return self


        class SPIRIT(BaseImputer):
            """
            SPIRIT class to impute missing values using SPIRIT algorithm.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the SPIRIT algorithm.
            """

            algorithm = "spirit"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the SPIRIT algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the SPIRIT algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                        k : int
                            The number of eigencomponents (principal components) to retain for dimensionality reduction.
                            Example: 2, 5, 10.
                        w : int
                            The window size for capturing temporal dependencies.
                            Example: 5 (short-term), 20 (long-term).
                        lambda_value : float
                            The forgetting factor controlling how quickly past data is "forgotten".
                            Example: 0.8 (fast adaptation), 0.95 (stable systems).

                Returns
                -------
                self : SPIRIT
                    SPIRIT object with `recov_data` set.

                Example
                -------
                    >>> spirit_imputer = Imputation.MatrixCompletion.SPIRIT(incomp_data)
                    >>> spirit_imputer.impute()  # default parameters for imputation > or
                    >>> spirit_imputer.impute(params={'k': 2, 'w': 5, 'lambda_value': 0.85}) # user-defined  > or
                    >>> spirit_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = spirit_imputer.recov_data

                References
                ----------
                S. Papadimitriou, J. Sun, and C. Faloutsos. Streaming pattern discovery in multiple time-series. In Proceedings of the 31st International Conference on Very Large Data Bases, Trondheim, Norway, August 30 - September 2, 2005, pages 697–708, 2005.
                """
                from imputegap.algorithms.spirit import spirit

                if params is not None:
                    k, w, lambda_value = self._check_params(user_def, params)
                else:
                    k, w, lambda_value = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = spirit(incomp_data=self.incomp_data, k=k, w=w, lambda_value=lambda_value, logs=self.logs, verbose=self.verbose)

                return self

        class SVT(BaseImputer):
            """
            SVT class to impute missing values using Singular Value Thresholding algorithm.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the SVT algorithm.
            """

            algorithm = "svt"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the SVT algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the SVT algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                        tau : float
                            The thresholding parameter for singular values. Controls how singular values are shrunk during the decomposition process.
                            Larger values encourage a sparser, lower-rank solution, while smaller values retain more detail.


                Returns
                -------
                self : SVT
                    SVT object with `recov_data` set.

                Example
                -------
                    >>> svt_imputer = Imputation.MatrixCompletion.SVT(incomp_data)
                    >>> svt_imputer.impute()  # default parameters for imputation > or
                    >>> svt_imputer.impute(params={'tau': 1}) # user-defined  > or
                    >>> svt_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = svt_imputer.recov_data

                References
                ----------
                J. Cai, E. J. Candès, and Z. Shen. A singular value thresholding algorithm for matrix completion. SIAM Journal on Optimization, 20(4):1956–1982, 2010. [8] J. Cambronero, J. K. Feser, M. J. Smith, and
                """
                from imputegap.algorithms.svt import svt

                if params is not None:
                    tau = self._check_params(user_def, params)[0]
                else:
                    tau = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = svt(incomp_data=self.incomp_data, tau=tau, logs=self.logs, verbose=self.verbose)

                return self

        class TRMF(BaseImputer):
            """
            TRMF class to impute missing values using Temporal Regularized Matrix Factorization.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the TRMF algorithm.
            """

            algorithm = "trmf"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the TRMF algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the TRMF algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                        lags : array-like, optional
                            Set of lag indices to use in model.
                        K : int, optional
                            Length of latent embedding dimension
                        lambda_f : float, optional
                            Regularization parameter used for matrix F.
                        lambda_x : float, optional
                            Regularization parameter used for matrix X.
                        lambda_w : float, optional
                            Regularization parameter used for matrix W.
                        alpha : float, optional
                            Regularization parameter used for make the sum of lag coefficient close to 1.
                            That helps to avoid big deviations when forecasting.
                        eta : float, optional
                            Regularization parameter used for X when undercovering autoregressive dependencies.
                        max_iter : int, optional
                            Number of iterations of updating matrices F, X and W.
                        logs : bool, optional
                            Whether to log the execution time (default is True).


                Returns
                -------
                self : TRMF
                    TRMF object with `recov_data` set.

                Example
                -------
                    >>> trmf_imputer = Imputation.MatrixCompletion.TRMF(incomp_data)
                    >>> trmf_imputer.impute()
                    >>> trmf_imputer.impute(params={"lags":[], "K":-1, "lambda_f":1.0, "lambda_x":1.0, "lambda_w":1.0, "eta":1.0, "alpha":1000.0, "max_iter":100})
                    >>> trmf_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})
                    >>> recov_data = trmf_imputer.recov_data

                References
                ----------
                H.-F. Yu, N. Rao, and I. S. Dhillon, "Temporal Regularized Matrix Factorization for High-dimensional Time Series Prediction," in *Advances in Neural Information Processing Systems*, vol. 29, 2016. [Online]. Available: https://proceedings.neurips.cc/paper_files/paper/2016/file/85422afb467e9456013a2a51d4dff702-Paper.pdf
                """
                from imputegap.algorithms.trmf import trmf

                if params is not None:
                    lags, K, lambda_f, lambda_x, lambda_w, eta, alpha, max_iter = self._check_params(user_def, params)
                else:
                    lags, K, lambda_f, lambda_x, lambda_w, eta, alpha, max_iter = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = trmf(incomp_data=self.incomp_data, lags=lags, K=K, lambda_f=lambda_f, lambda_x=lambda_x, lambda_w=lambda_w, eta=eta, alpha=alpha, max_iter=max_iter, logs=self.logs, verbose=self.verbose)

                return self





    class MachineLearning:
        """
        A class containing imputation algorithms for pattern-based methods.

        Subclasses
        ----------
        MissForest :
            Imputation method using Miss Forest (MissForest)
        MICE :
            Imputation method using Multivariate imputation of chained equations (MICE).
        IIM :
            Imputation method using Iterative Imputation with Metric Learning (IIM).
        XGBOOST :
            Imputation method using Scalable Tree Boosting System (XGBOOST).
        """

        class MissForest(BaseImputer):
            """
            MissForest class to impute missing values with Miss Forest.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the Miss Forest algorithm.
            """
            algorithm = "miss_forest"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the Miss Forest algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the miss forest algorithm, if None, default ones are loaded.

                    **Algorithm parameters:**

                        alpha : float, optional
                            Trade-off parameter controlling the contribution of contextual matrix
                            and time-series. If alpha = 0, network is ignored. (default 0.5)
                        beta : float, optional
                            Regularization parameter for sparsity. (default 0.1)
                        L : int, optional
                            Hidden dimension size. (default 10)
                        n_cl : int, optional
                            Number of clusters. (default 1)
                        max_iteration : int, optional
                            Maximum number of iterations for convergence. (default 20)
                        tol : float, optional
                            Tolerance for early stopping criteria.  (default 5)
                        random_init : bool, optional
                            Whether to use random initialization for latent variables. (default False)

                Returns
                -------
                self : MissForest
                    The object with `recov_data` set.

                Example
                -------
                    >>> mf_imputer = Imputation.MachineLearning.MissForest(incomp_data)
                    >>> mf_imputer.impute()  # default parameters for imputation > or
                    >>> mf_imputer.impute(user_def=True, params={"n_estimators":10, "max_iter":3, "max_features":"sqrt", "seed": 42})  # user defined > or
                    >>> mf_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = mf_imputer.recov_data

                References
                ----------
                Daniel J. Stekhoven, Peter Bühlmann, MissForest—non-parametric missing value imputation for mixed-type data, Bioinformatics, Volume 28, Issue 1, January 2012, Pages 112–118, https://doi.org/10.1093/bioinformatics/btr597
                https://github.com/yuenshingyan/MissForest
                https://pypi.org/project/MissForest/
                """
                from imputegap.algorithms.miss_forest import miss_forest

                if params is not None:
                    n_estimators, max_iter, max_features, seed = self._check_params(user_def, params)
                else:
                    n_estimators, max_iter, max_features, seed = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = miss_forest(incomp_data=self.incomp_data, n_estimators=n_estimators, max_iter=max_iter, max_features=max_features, seed=seed, logs=self.logs, verbose=self.verbose)

                return self


        class MICE(BaseImputer):
            """
            MICE class to impute missing values with Multivariate imputation of chained equations (MICE).

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the MICE algorithm.
            """
            algorithm = "mice"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the MICE algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True). \n
                params : dict, optional
                    Parameters of the MICE algorithm, if None, default ones are loaded. \n

                    **Algorithm parameters:**

                        max_iter : int, optional
                            Maximum number of imputation rounds to perform before returning the imputations computed during the final round. (default is 3). \n
                        tol : float, optional
                            Tolerance of the stopping condition. (default is 0.001). \n
                        initial_strategy : str, optional
                            Which strategy to use to initialize the missing values. {‘mean’, ‘median’, ‘most_frequent’, ‘constant’} (default is "means"). \n
                        seed : int, optional
                            The seed of the pseudo random number generator to use. Randomizes selection of estimator features (default is 42). \n

                Returns
                -------
                    self : MICE
                        The object with `recov_data` set.

                Example
                -------
                    >>> mice_imputer = Imputation.MachineLearning.MICE(incomp_data)
                    >>> mice_imputer.impute()  # default parameters for imputation > or
                    >>> mice_imputer.impute(user_def=True, params={"max_iter":3, "tol":0.001, "initial_strategy":"mean", "seed": 42})  # user defined > or
                    >>> mice_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = mice_imputer.recov_data

                References
                ----------
                P. Royston and I. R. White. Multiple Imputation by Chained Equations (MICE): Implementation in Stata. Journal of Statistical Software, 45(4):1–20, 2011. Available: https://www.jstatsoft.org/index.php/jss/article/view/v045i04.
                Stef van Buuren, Karin Groothuis-Oudshoorn (2011). “mice: Multivariate Imputation by Chained Equations in R”. Journal of Statistical Software 45: 1-67.
                S. F. Buck, (1960). “A Method of Estimation of Missing Values in Multivariate Data Suitable for use with an Electronic Computer”. Journal of the Royal Statistical Society 22(2): 302-306.
                https://scikit-learn.org/stable/modules/generated/sklearn.impute.IterativeImputer.html#sklearn.impute.IterativeImputer
                """
                from imputegap.algorithms.mice import mice

                if params is not None:
                    max_iter, tol, initial_strategy, seed = self._check_params(user_def, params)
                else:
                    max_iter, tol, initial_strategy, seed = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = mice(incomp_data=self.incomp_data, max_iter=max_iter, tol=tol, initial_strategy=initial_strategy, seed=seed, logs=self.logs, verbose=self.verbose)

                return self

        class XGBOOST(BaseImputer):
            """
            XGBOOST class to impute missing values with Extreme Gradient Boosting (XGBOOST).

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the XGBOOST algorithm.
            """
            algorithm = "xgboost"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the XGBOOST algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the xgboost algorithm, if None, default ones are loaded.

                    **Algorithm parameters:**

                        n_estimators : int, optional
                            The number of trees in the Random Forest model used for imputation (default is 10).
                        seed : int, optional
                            The seed of the pseudo random number generator to use. Randomizes selection of estimator features (default is 42).

                Returns
                -------
                self : XGBOOST
                    The object with `recov_data` set.

                Example
                -------
                    >>> mxgboost_imputer = Imputation.MachineLearning.XGBOOST(incomp_data)
                    >>> mxgboost_imputer.impute()  # default parameters for imputation > or
                    >>> mxgboost_imputer.impute(user_def=True, params={"n_estimators":3, "seed": 42})  # user defined > or
                    >>> mxgboost_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = mxgboost_imputer.recov_data

                References
                ----------
                Tianqi Chen and Carlos Guestrin. 2016. XGBoost: A Scalable Tree Boosting System. In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16). Association for Computing Machinery, New York, NY, USA, 785–794. https://doi.org/10.1145/2939672.2939785
                https://dl.acm.org/doi/10.1145/2939672.2939785
                https://medium.com/@tzhaonj/imputing-missing-data-using-xgboost-802757cace6d
                """
                from imputegap.algorithms.xgboost import xgboost

                if params is not None:
                    n_estimators, seed = self._check_params(user_def, params)
                else:
                    n_estimators, seed = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = xgboost(incomp_data=self.incomp_data, n_estimators=n_estimators, seed=seed, logs=self.logs, verbose=self.verbose)

                return self

        class IIM(BaseImputer):
            """
            IIM class to impute missing values using Iterative Imputation with Metric Learning (IIM).

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the IIM algorithm.
            """
            algorithm = "iim"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the IIM algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the IIM algorithm, if None, default ones are loaded.

                    **Algorithm parameters:**

                        learning_neighbours : int
                            Number of nearest neighbors for learning.
                        algo_code : str
                            Unique code for the algorithm configuration.

                Returns
                -------
                self : IIM
                    The object with `recov_data` set.

                Example
                -------
                    >>> iim_imputer = Imputation.MachineLearning.IIM(incomp_data)
                    >>> iim_imputer.impute()  # default parameters for imputation > or
                    >>> iim_imputer.impute(user_def=True, params={'learning_neighbors': 10})  # user-defined  > or
                    >>> iim_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "bayesian", "options": {"n_calls": 2}})  # automl with bayesian
                    >>> recov_data = iim_imputer.recov_data

                References
                ----------
                A. Zhang, S. Song, Y. Sun and J. Wang, "Learning Individual Models for Imputation," 2019 IEEE 35th International Conference on Data Engineering (ICDE), Macao, China, 2019, pp. 160-171, doi: 10.1109/ICDE.2019.00023.
                keywords: {Data models;Adaptation models;Computational modeling;Predictive models;Numerical models;Aggregates;Regression tree analysis;Missing values;Data imputation}
                """
                from imputegap.algorithms.iim import iim

                if params is not None:
                    learning_neighbours, algo_code = self._check_params(user_def, params)
                else:
                    learning_neighbours, algo_code = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = iim(incomp_data=self.incomp_data, number_neighbor=learning_neighbours,
                                      algo_code=algo_code, logs=self.logs, verbose=self.verbose)

                return self





    class PatternSearch:
        """
        A class containing imputation algorithms for pattern-based methods.

        Subclasses
        ----------
        STMVL :
            Imputation method using Spatio-Temporal Matrix Variational Learning (STMVL).

        DynaMMo :
            Imputation method using Dynamic Multi-Mode modeling with Missing Observations algorithm (DynaMMo).

        TKCM :
            TKCM class to impute missing values using Tensor Kernelized Coupled Matrix Completion algorithm. (TKCM).
        """

        class STMVL(BaseImputer):
            """
            STMVL class to impute missing values using Spatio-Temporal Matrix Variational Learning (STMVL).

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the STMVL algorithm.
            """
            algorithm = "stmvl"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the STMVL algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the STMVL algorithm, if None, default ones are loaded.

                    - window_size : int
                        The size of the temporal window for imputation.
                    - gamma : float
                        Smoothing parameter for temporal weights.
                    - alpha : float
                        Power for spatial weights.

                Returns
                -------
                self : STMVL
                    The object with `recov_data` set.

                Example
                -------
                    >>> stmvl_imputer = Imputation.PatternSearch.STMVL(incomp_data)
                    >>> stmvl_imputer.impute()  # default parameters for imputation > or
                    >>> stmvl_imputer.impute(user_def=True, params={'window_size': 7, 'learning_rate':0.01, 'gamma':0.85, 'alpha': 7})  # user-defined  > or
                    >>> stmvl_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "bayesian", "options": {"n_calls": 2}})  # automl with bayesian
                    >>> recov_data = stmvl_imputer.recov_data

                References
                ----------
                Yi, X., Zheng, Y., Zhang, J., & Li, T. ST-MVL: Filling Missing Values in Geo-Sensory Time Series Data.
                School of Information Science and Technology, Southwest Jiaotong University; Microsoft Research; Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences.
                """
                from imputegap.algorithms.stmvl import stmvl

                if params is not None:
                    window_size, gamma, alpha = self._check_params(user_def, params)
                else:
                    window_size, gamma, alpha = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = stmvl(incomp_data=self.incomp_data, window_size=window_size, gamma=gamma,
                                        alpha=alpha, logs=self.logs, verbose=self.verbose)

                return self

        class DynaMMo(BaseImputer):
            """
            DynaMMo class to impute missing values using Dynamic Multi-Mode modeling with Missing Observations algorithm.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the DynaMMo algorithm.
            """

            algorithm = "dynammo"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the DynaMMo algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the DynaMMo algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                        h : int
                            The time window (H) parameter for modeling temporal dynamics.
                        max_iteration : int
                            The maximum number of iterations for the imputation process.
                        approximation : bool
                            If True, enables faster approximate processing.

                Returns
                -------
                self : DynaMMo
                    DynaMMo object with `recov_data` set.

                Example
                -------
                    >>> dynammo_imputer = Imputation.PatternSearch.DynaMMo(incomp_data)
                    >>> dynammo_imputer.impute()  # default parameters for imputation > or
                    >>> dynammo_imputer.impute(params={'h': 5, 'max_iteration': 100, 'approximation': True}) # user-defined  > or
                    >>> dynammo_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = dynammo_imputer.recov_data

                References
                ----------
                L. Li, J. McCann, N. S. Pollard, and C. Faloutsos. Dynammo: mining and summarization of coevolving sequences with missing values. In Proceedings of the 15th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, Paris, France, June 28 - July 1, 2009, pages 507–516, 2009.
                """
                from imputegap.algorithms.dynammo import dynammo

                if params is not None:
                    h, max_iteration, approximation = self._check_params(user_def, params)
                else:
                    h, max_iteration, approximation = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = dynammo(incomp_data=self.incomp_data, h=h, max_iteration=max_iteration, approximation=approximation, logs=self.logs, verbose=self.verbose)

                return self

        class TKCM(BaseImputer):
            """
            TKCM class to impute missing values using Tensor Kernelized Coupled Matrix Completion algorithm.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the TKCM algorithm.
            """

            algorithm = "tkcm"

            def impute(self, user_def=True, params=None):
                """
                Perform imputation using the TKCM algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the TKCM algorithm or Auto-ML configuration, if None, default ones are loaded.

                    **Algorithm parameters:**

                        rank : int
                            The rank for matrix decomposition (must be greater than 1 and smaller than the number of series).

                Returns
                -------
                self : TKCM
                    TKCM object with `recov_data` set.

                Example
                -------
                    >>> tkcm_imputer = Imputation.PatternSearch.TKCM(incomp_data)
                    >>> tkcm_imputer.impute()  # default parameters for imputation > or
                    >>> tkcm_imputer.impute(params={'rank': 5})  # user-defined > or
                    >>> tkcm_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = tkcm_imputer.recov_data

                References
                ----------
                K. Wellenzohn, M. H. Böhlen, A. Dignös, J. Gamper, and H. Mitterer. Continuous imputation of missing values in streams of pattern-determining time series. In Proceedings of the 20th International Conference on Extending Database Technology, EDBT 2017, Venice, Italy, March 21-24, 2017., pages 330–341, 2017.
                """
                from imputegap.algorithms.tkcm import tkcm

                if params is not None:
                    rank = self._check_params(user_def, params)[0]
                else:
                    rank = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                rank = utils.compute_rank_check(M=self.incomp_data.shape[0], rank=rank, verbose=self.verbose)

                self.recov_data = tkcm(incomp_data=self.incomp_data, rank=rank, logs=self.logs, verbose=self.verbose)

                return self

    class DeepLearning:
        """
        A class containing imputation algorithms for deep learning-based methods.

        Subclasses
        ----------
        MRNN :
            Imputation method using Multi-directional Recurrent Neural Networks (MRNN).
        BRITS :
            Imputation method using Bidirectional Recurrent Imputation for Time Series.
        DeepMVI :
            Imputation method using Deep Multivariate Imputation.
        MPIN :
            Imputation method using Multi-attribute Sensor Data Streams via Message Propagation.
        PRISTI :
            Imputation method using A Conditional Diffusion Framework for Spatiotemporal Imputation.
        MissNet :
            Imputation method using Mining of Switching Sparse Networks for Missing Value Imputation.
        GAIN :
            Imputation method using Generative Adversarial Nets for missing data imputation.
        GRIN :
            Imputation method using Graph Neural Networks for Multivariate Time Series Imputation.
        BayOTIDE :
            Imputation method using Bayesian Online Multivariate Time Series Imputation with functional decomposition.
        HKMF_T :
            Imputation method using Hankel Matrix Factorization to recover from blackouts in tagged time series.
        """


        class MRNN(BaseImputer):
            """
            MRNN class to impute missing values using Multi-directional Recurrent Neural Networks (MRNN).

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the MRNN algorithm.
            """
            algorithm = "mrnn"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using the MRNN algorithm.

                Parameters
                ----------

                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the MRNN algorithm, if None, default ones are loaded.
                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).

                    **Algorithm parameters:**

                        hidden_dim : int
                            The number of hidden units in the neural network.
                        learning_rate : float
                            Learning rate for training the neural network.
                        iterations : int
                            Number of iterations for training.
                        sequence_length : int
                            The length of the sequences used in the recurrent neural network.

                Returns
                -------
                self : MRNN
                    The object with `recov_data` set.

                Example
                -------
                    >>> mrnn_imputer = Imputation.DeepLearning.MRNN(incomp_data)
                    >>> mrnn_imputer.impute()  # default parameters for imputation > or
                    >>> mrnn_imputer.impute(user_def=True, params={'hidden_dim': 10, 'learning_rate':0.01, 'iterations':50, 'sequence_length': 7})  # user-defined > or
                    >>> mrnn_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "bayesian", "options": {"n_calls": 2}})  # automl with bayesian
                    >>> recov_data = mrnn_imputer.recov_data

                References
                ----------
                J. Yoon, W. R. Zame and M. van der Schaar, "Estimating Missing Data in Temporal Data Streams Using Multi-Directional Recurrent Neural Networks," in IEEE Transactions on Biomedical Engineering, vol. 66, no. 5, pp. 1477-1490, May 2019, doi: 10.1109/TBME.2018.2874712. keywords: {Time measurement;Interpolation;Estimation;Medical diagnostic imaging;Correlation;Recurrent neural networks;Biomedical measurement;Missing data;temporal data streams;imputation;recurrent neural nets}
                """
                from imputegap.algorithms.mrnn import mrnn

                if not (self._check_dl_split(split_ratio=tr_ratio)):
                    self.recov_data = self.incomp_data
                    return

                if params is not None:
                    hidden_dim, learning_rate, iterations, sequence_length = self._check_params(user_def, params)
                else:
                    hidden_dim, learning_rate, iterations, sequence_length = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = mrnn(incomp_data=self.incomp_data, hidden_dim=hidden_dim,
                                       learning_rate=learning_rate, iterations=iterations,
                                       sequence_length=sequence_length, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)

                return self

        class BRITS(BaseImputer):
            """
            BRITS class to impute missing values using Bidirectional Recurrent Imputation for Time Series

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the BRITS algorithm.
            """
            algorithm = "brits"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using the BRITS algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the BRITS algorithm, if None, default ones are loaded.
                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).

                    **Algorithm parameters:**

                        model : str
                            Specifies the type of model to use for the imputation. Options may include predefined models like 'brits', 'brits-i' or 'brits_i_univ'.
                        epoch : int
                            Number of epochs for training the model. Determines how many times the algorithm processes the entire dataset during training.
                        batch_size : int
                            Size of the batches used during training. Larger batch sizes can speed up training but may require more memory.
                        nbr_features : int
                            Number of features, dimension in the time series.
                        hidden_layer : int
                            Number of units in the hidden layer of the model. Controls the capacity of the neural network to learn complex patterns.
                        num_workers: int, optional
                            Number of worker for multiprocess (default is 0).

                Returns
                -------
                self : BRITS
                    The object with `recov_data` set.

                Example
                -------
                    >>> brits_imputer = Imputation.DeepLearning.BRITS(incomp_data)
                    >>> brits_imputer.impute()  # default parameters for imputation > or
                    >>> brits_imputer.impute(params={"model": "brits", "epoch": 2, "batch_size": 10, "nbr_features": 1, "hidden_layer": 64, "num_workers":0})  # user-defined > or
                    >>> brits_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = brits_imputer.recov_data

                References
                ----------
                Cao, W., Wang, D., Li, J., Zhou, H., Li, L. & Li, Y. BRITS: Bidirectional Recurrent Imputation for Time Series. Advances in Neural Information Processing Systems, 31 (2018). https://proceedings.neurips.cc/paper_files/paper/2018/file/734e6bfcd358e25ac1db0a4241b95651-Paper.pdf
                """
                from imputegap.algorithms.brits import brits

                if not (self._check_dl_split(split_ratio=0.8)):
                    self.recov_data = self.incomp_data
                    return

                if params is not None:
                    model, epoch, batch_size, nbr_features, hidden_layer, num_workers = self._check_params(user_def, params)
                else:
                    model, epoch, batch_size, nbr_features, hidden_layer, num_workers = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                seq_length = self.incomp_data.shape[1]

                self.recov_data = brits(incomp_data=self.incomp_data, model=model, epoch=epoch, batch_size=batch_size, nbr_features=nbr_features, hidden_layers=hidden_layer, seq_length=seq_length, num_workers=num_workers, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)
                return self

        class DeepMVI(BaseImputer):
            """
            DeepMVI class to impute missing values using Deep Multivariate Imputation

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the DeepMVI algorithm.
            """
            algorithm = "deep_mvi"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using the DeepMVI algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the DeepMVI algorithm, if None, default ones are loaded.
                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).

                    **Algorithm parameters:**

                        max_epoch : int, optional
                            Limit of training epoch (default is 1000)

                        patience : int, optional
                            Number of threshold error that can be crossed during the training (default is 2)

                        lr : float, optional
                            Learning rate of the training (default is 0.001)

                Returns
                -------
                self : DeepMVI
                    The object with `recov_data` set.

                Example
                -------
                    >>> deep_mvi_imputer = Imputation.DeepLearning.DeepMVI(incomp_data)
                    >>> deep_mvi_imputer.impute()  # default parameters for imputation > or
                    >>> deep_mvi_imputer.impute(params={"max_epoch": 10, "patience": 2, "lr":0.001})  # user-defined > or
                    >>> deep_mvi_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = deep_mvi_imputer.recov_data

                References
                ----------
                P. Bansal, P. Deshpande, and S. Sarawagi. Missing value imputation on multidimensional time series. arXiv preprint arXiv:2103.01600, 2023
                https://github.com/pbansal5/DeepMVI
                """
                from imputegap.algorithms.deep_mvi import deep_mvi

                if not (self._check_dl_split(split_ratio=0.8)):
                    self.recov_data = self.incomp_data
                    return

                if params is not None:
                    max_epoch, patience, lr = self._check_params(user_def, params)
                else:
                    max_epoch, patience, lr = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = deep_mvi(incomp_data=self.incomp_data, max_epoch=max_epoch, patience=patience, lr=lr, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)
                return self

        class MPIN(BaseImputer):
            """
            MPIN class to impute missing values using Multi-attribute Sensor Data Streams via Message Propagation algorithm.
            Need torch-cluster to work.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the MPIN algorithm.
            """
            algorithm = "mpin"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using the MPIN algorithm.
                Need torch-cluster to work.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the MPIN algorithm, if None, default ones are loaded.
                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).

                    **Algorithm parameters:**

                        incre_mode : str, optional
                            The mode of incremental learning. Options are: 'alone',  'data', 'state', 'state+transfer', 'data+state', 'data+state+transfer' (default is "alone").
                        window : int, optional
                            The size of the sliding window for processing data streams (default is 2).
                        k : int, optional
                            The number of neighbors to consider during message propagation (default is 10).
                        lr : float, optional
                            The learning rate for optimizing the message propagation algorithm (default is 0.01).
                        weight_decay : float, optional
                            The weight decay (regularization) term to prevent overfitting during training (default is 0.1).
                        epochs : int, optional
                            The number of epochs to run the training process (default is 200).
                        num_of_iteration : int, optional
                            The number of iteration of the whole training (default is 5).
                        thre : float, optional
                            The threshold for considering a missing value as imputed (default is 0.25).
                        base : str, optional
                            The base model used for graph representation and message propagation. Common options include "SAGE" and "GCN" (default is "SAGE").


                Returns
                -------
                self : MPIN
                    The object with `recov_data` set.

                Example
                -------
                    >>> mpin_imputer = Imputation.DeepLearning.MPIN(incomp_data)
                    >>> mpin_imputer.impute()  # default parameters for imputation > or
                    >>> mpin_imputer.impute(params={"incre_mode": "data+state", "window": 1, "k": 15, "learning_rate": 0.001, "weight_decay": 0.2, "epochs": 6, "num_of_iteration": 6, "threshold": 0.50, "base": "GCN"})  # user-defined > or
                    >>> mpin_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = mpin_imputer.recov_data

                References
                ----------
                Li, X., Li, H., Lu, H., Jensen, C.S., Pandey, V. & Markl, V. Missing Value Imputation for Multi-attribute Sensor Data Streams via Message Propagation (Extended Version). arXiv (2023). https://arxiv.org/abs/2311.07344
                https://github.com/XLI-2020/MPIN
                """
                from imputegap.algorithms.mpin import mpin

                if params is not None:
                    incre_mode, window, k, learning_rate, weight_decay, epochs, num_of_iteration, threshold, base = self._check_params(user_def, params)
                else:
                    incre_mode, window, k, learning_rate, weight_decay, epochs, num_of_iteration, threshold, base = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                k = utils.compute_rank_check(M=self.incomp_data.shape[0], rank=k, verbose=self.verbose)

                self.recov_data = mpin(incomp_data=self.incomp_data, incre_mode=incre_mode, window=window, k=k, lr=learning_rate, weight_decay=weight_decay, epochs=epochs, num_of_iteration=num_of_iteration, thre=threshold, base=base, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)
                return self

        class PRISTI(BaseImputer):
            """
            PRISTI class to impute missing values using A Conditional Diffusion Framework for Spatiotemporal Imputation algorithm.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the PRISTI algorithm.
            """
            algorithm = "pristi"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using the PRISTI algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the PRISTI algorithm, if None, default ones are loaded.
                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).

                    **Algorithm parameters:**

                        target_strategy : str, optional
                            The strategy to use for targeting missing values. Options include: "hybrid", "random", "historical" (default is "hybrid").
                        unconditional : bool, optional
                            Whether to use an unconditional imputation model (default is True).
                            If False, conditional imputation models are used, depending on available data patterns.
                        seed : int, optional
                            Random seed for reproducibility (default is 42).
                        batch_size : int, optional
                            Size of the batch to train the deep learning model (-1 means compute automatically based on the dataset shape).
                        embedding : int, optional
                            Size of the embedding used to train the deep learning model (-1 means compute automatically based on the dataset shape).
                        num_workers: int, optional
                             Number of worker for multiprocess (default is 0).


                Returns
                -------
                self : PRISTI
                    The object with `recov_data` set.

                Example
                -------
                    >>> pristi_imputer = Imputation.DeepLearning.PRISTI(incomp_data)
                    >>> pristi_imputer.impute()  # default parameters for imputation > or
                    >>> pristi_imputer.impute(params={"target_strategy":"hybrid", "unconditional":True, "batch_size":-1, "embedding":-1, "num_workers":0, "seed":42})  # user-defined > or
                    >>> pristi_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # automl with ray_tune
                    >>> recov_data = pristi_imputer.recov_data

                References
                ----------
                M. Liu, H. Huang, H. Feng, L. Sun, B. Du and Y. Fu, "PriSTI: A Conditional Diffusion Framework for Spatiotemporal Imputation," 2023 IEEE 39th International Conference on Data Engineering (ICDE), Anaheim, CA, USA, 2023, pp. 1927-1939, doi: 10.1109/ICDE55515.2023.00150.
                https://github.com/LMZZML/PriSTI
                """
                from imputegap.algorithms.pristi import pristi

                if params is not None:
                    target_strategy, unconditional, batch_size, embedding, num_workers, seed = self._check_params(user_def, params)
                else:
                    target_strategy, unconditional, batch_size, embedding, num_workers, seed = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = pristi(incomp_data=self.incomp_data, target_strategy=target_strategy, unconditional=unconditional, batch_size=batch_size, embedding=embedding, num_workers=num_workers, tr_ratio=tr_ratio, seed=seed, logs=self.logs, verbose=self.verbose)
                return self

        class MissNet(BaseImputer):
            """
            MissNet class to impute missing values using Mining of Switching Sparse Networks for Missing Value
             Imputation in Multivariate Time Series.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the MissNet algorithm.
            """
            algorithm = "miss_net"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using the MissNet algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).
                params : dict, optional
                    Parameters of the MissNet algorithm, if None, default ones are loaded.
                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).

                    **Algorithm parameters:**

                        alpha : float, optional
                            Trade-off parameter controlling the contribution of contextual matrix
                            and time-series. If alpha = 0, network is ignored. (default 0.5)
                        beta : float, optional
                            Regularization parameter for sparsity. (default 0.1)
                        L : int, optional
                            Hidden dimension size. (default 10)
                        n_cl : int, optional
                            Number of clusters. (default 1)
                        max_iteration : int, optional
                            Maximum number of iterations for convergence. (default 20)
                        tol : float, optional
                            Tolerance for early stopping criteria.  (default 5)
                        random_init : bool, optional
                            Whether to use random initialization for latent variables. (default False)

                Returns
                -------
                self : MissNet
                    The object with `recov_data` set.

                Example
                -------
                    >>> miss_net_imputer = Imputation.DeepLearning.MissNet(incomp_data)
                    >>> miss_net_imputer.impute()  # default parameters for imputation > or
                    >>> miss_net_imputer.impute(user_def=True, params={'alpha': 0.5, 'beta':0.1, 'L':10, 'n_cl': 1, 'max_iteration':20, 'tol':5, 'random_init':False})  # user-defined > or
                    >>> miss_net_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # auto-ml with ray_tune
                    >>> recov_data = miss_net_imputer.recov_data

                References
                ----------
                Kohei Obata, Koki Kawabata, Yasuko Matsubara, and Yasushi Sakurai. 2024. Mining of Switching Sparse Networks for Missing Value Imputation in Multivariate Time Series. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '24). Association for Computing Machinery, New York, NY, USA, 2296–2306. https://doi.org/10.1145/3637528.3671760
                https://github.com/KoheiObata/MissNet/tree/main
                """
                from imputegap.algorithms.miss_net import miss_net

                if params is not None:
                    alpha, beta, L, n_cl, max_iteration, tol, random_init = self._check_params(user_def, params)
                else:
                    alpha, beta, L, n_cl, max_iteration, tol, random_init = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = miss_net(incomp_data=self.incomp_data, alpha=alpha, beta=beta, L=L, n_cl=n_cl, max_iteration=max_iteration, tol=tol, random_init=random_init, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)

                return self


        class GAIN(BaseImputer):
            """
            GAIN class to impute missing values using Missing Data Imputation using Generative Adversarial Nets,

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the GAIN algorithm.
            """

            algorithm = "gain"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using the GAIN algorithm.

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the GAIN algorithm or Auto-ML configuration, if None, default ones are loaded.

                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).


                    **Algorithm parameters:**

                        batch_size : int, optional
                            Number of samples in each mini-batch during training. Default is 32.
                        hint_rate : float, optional
                            Probability of providing hints for the missing data during training. Default is 0.9.
                        alpha : float, optional
                            Hyperparameter that controls the balance between the adversarial loss and the reconstruction loss. Default is 10.
                        epoch : int, optional
                            Number of training epochs. Default is 100.
                        logs : bool, optional


                Returns
                -------
                self : GAIN
                    GAIN object with `recov_data` set.

                Example
                -------
                    >>> gain_imputer = Imputation.DeepLearning.GAIN(incomp_data)
                    >>> gain_imputer.impute()  # default parameters for imputation > or
                    >>> gain_imputer.impute(user_def=True, params={"batch_size":32, "hint_rate":0.9, "alpha":10, "epoch":100})  # user defined> or
                    >>> gain_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # auto-ml with ray_tune
                    >>> recov_data = gain_imputer.recov_data

                References
                ----------
                J. Yoon, J. Jordon, and M. van der Schaar, "GAIN: Missing Data Imputation using Generative Adversarial Nets," CoRR, vol. abs/1806.02920, 2018. Available: http://arxiv.org/abs/1806.02920.
                """

                from imputegap.algorithms.gain import gain

                if params is not None:
                    batch_size, hint_rate, alpha, epoch = self._check_params(user_def, params)
                else:
                    batch_size, hint_rate, alpha, epoch = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = gain(incomp_data=self.incomp_data, batch_size=batch_size, hint_rate=hint_rate, alpha=alpha, epoch=epoch, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)

                return self


        class GRIN(BaseImputer):
            """
            GRIN class to impute missing values using MULTIVARIATE TIME SERIES IMPUTATION BY GRAPH NEURAL NETWORKS.

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the GRIN
            """

            algorithm = "grin"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using the Multivariate Time Series Imputation by Graph Neural Networks

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the GRIN algorithm or Auto-ML configuration, if None, default ones are loaded.

                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).


                    **Algorithm parameters:**

                        d_hidden : int, optional, default=32
                            The number of hidden units in the model's recurrent and graph layers.

                        lr : float, optional, default=0.001
                            Learning rate for the optimizer.

                        batch_size : int, optional, default=32
                            The number of samples per training batch.

                        window : int, optional, default=10
                            The size of the time window used for modeling temporal dependencies.

                        alpha : float, optional, default=10.0
                            The weight assigned to the adversarial loss term during training.

                        patience : int, optional, default=4
                            Number of epochs without improvement before early stopping is triggered.

                        epochs : int, optional, default=20
                            The maximum number of training epochs.

                        workers : int, optional, default=2
                            The number of worker processes for data loading.


                Returns
                -------
                self : GRIN
                    GRIN object with `recov_data` set.

                Example
                -------
                    >>> grin_imputer = Imputation.DeepLearning.GRIN(incomp_data)
                    >>> grin_imputer.impute()  # default parameters for imputation > or
                    >>> grin_imputer.impute(user_def=True, params={"d_hidden":32, "lr":0.001, "batch_size":32, "window":1, "alpha":10.0, "patience":4, "epochs":20, "workers":2})  # user defined> or
                    >>> grin_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # auto-ml with ray_tune
                    >>> recov_data = grin_imputer.recov_data

                References
                ----------
                A. Cini, I. Marisca, and C. Alippi, "Multivariate Time Series Imputation by Graph Neural Networks," CoRR, vol. abs/2108.00298, 2021
                https://github.com/Graph-Machine-Learning-Group/grin
                """
                from imputegap.algorithms.grin import grin

                if params is not None:
                    d_hidden, lr, batch_size, window, alpha, patience, epochs, workers = self._check_params(user_def, params)
                else:
                    d_hidden, lr, batch_size, window, alpha, patience, epochs, workers = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = grin(incomp_data=self.incomp_data, d_hidden=d_hidden, lr=lr, batch_size=batch_size, window=window, alpha=alpha, patience=patience, epochs=epochs, workers=workers, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)

                return self

        class BayOTIDE(BaseImputer):
            """
            BayOTIDE class to impute missing values using Bayesian Online Multivariate Time series Imputation with functional decomposition

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the BayOTIDE

            References
            ----------
            https://arxiv.org/abs/2308.14906
            https://github.com/xuangu-fang/BayOTIDE
            """

            algorithm = "bay_otide"

            def impute(self, user_def=True, params=None, tr_ratio=0.6):
                """
                Perform imputation using the Multivariate Time Series Imputation by Deep Learning

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the BayOTIDE algorithm or Auto-ML configuration, if None, default ones are loaded.

                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).


                    **Algorithm parameters:**

                        K_trend : int, (optional) (default: 20)
                            Number of trend factors.

                        K_season : int, (optional) (default: 2)
                            Number of seasonal factors.

                        n_season : int, (optional) (default: 5)
                            Number of seasonal components per factor.

                        K_bias : int, (optional) (default: 1)
                            Number of bias factors.

                        time_scale : float, (optional) (default: 1)
                            Time scaling factor.

                        a0 : float, (optional) (default: 0.6)
                            Hyperparameter for prior distribution.

                        b0 : float, (optional) (default: 2.5)
                            Hyperparameter for prior distribution.

                        v : float, (optional) (default: 0.5)
                            Variance parameter.

                        num_workers: int, optional
                             Number of worker for multiprocess (default is 0).

                        config : dict, (optional) (default: None)
                            Dictionary containing all configuration parameters, that will replace all other parameters (see documentation).

                        args : object, (optional) (default: None)
                            Arguments containing all configuration parameters, that will replace all other parameters (see documentation).


                Returns
                -------
                self : BayOTIDE
                    BayOTIDE object with `recov_data` set.

                Example
                -------
                    >>> bay_otide_imputer = Imputation.DeepLearning.BayOTIDE(incomp_data)
                    >>> bay_otide_imputer.impute()  # default parameters for imputation > or
                    >>> bay_otide_imputer.impute(user_def=True, params={"K_trend":20, "K_season":2, "n_season":5, "K_bias":1, "time_scale":1, "a0":0.6, "b0":2.5, "v":0.5, "num_workers":0, "tr_ratio":0.6})  # user defined> or
                    >>> bay_otide_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # auto-ml with ray_tune
                    >>> recov_data = bay_otide_imputer.recov_data

                References
                ----------
                S. Fang, Q. Wen, Y. Luo, S. Zhe, and L. Sun, "BayOTIDE: Bayesian Online Multivariate Time Series Imputation with Functional Decomposition," CoRR, vol. abs/2308.14906, 2024. [Online]. Available: https://arxiv.org/abs/2308.14906.
                https://github.com/xuangu-fang/BayOTIDE
                """
                from imputegap.algorithms.bayotide import bay_otide

                if not (self._check_dl_split(split_ratio=0.8)):
                    self.recov_data = self.incomp_data
                    return

                if params is not None:
                    K_trend, K_season, n_season, K_bias, time_scale, a0, b0, v, num_workers, tr_ratio = self._check_params(user_def, params)
                else:
                    K_trend, K_season, n_season, K_bias, time_scale, a0, b0, v, num_workers, tr_ratio = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = bay_otide(incomp_data=self.incomp_data, K_trend=K_trend, K_season=K_season, n_season=n_season, K_bias=K_bias, time_scale=time_scale, a0=a0, b0=b0, v=v, num_workers=num_workers, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)

                return self



        class HKMF_T(BaseImputer):
            """
            HKMF-T class to impute missing values using Recover From Blackouts in Tagged Time Series With Hankel Matrix Factorization

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the HKMF-T
            """

            algorithm = "hkmf_t"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using Recover From Blackouts in Tagged Time Series With Hankel Matrix Factorization

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the HKMF-T algorithm or Auto-ML configuration, if None, default ones are loaded.

                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).


                    **Algorithm parameters:**

                        tags : numpy.ndarray, optional
                            An array containing tags that provide additional structure or metadata about
                            the input data. If None, no tags are used (default is None).

                        data_names : list of str, optional
                            List of names corresponding to each row or column of the dataset for interpretability.
                            If None, names are not used (default is None).

                        epoch : int, optional
                            The maximum number of training epochs for the Hankel Matrix Factorization algorithm.
                            If convergence is reached earlier, the process stops (default is 10).

                Returns
                -------
                self : HKMF-T
                    HKMF-T object with `recov_data` set.

                Example
                -------
                    >>> hkmf_t_imputer = Imputation.DeepLearning.HKMF_T(incomp_data)
                    >>> hkmf_t_imputer.impute()  # default parameters for imputation > or
                    >>> hkmf_t_imputer.impute(user_def=True, params={"tags":None, "data_names":None, "epoch":5})  # user defined> or
                    >>> hkmf_t_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # auto-ml with ray_tune
                    >>> recov_data = hkmf_t_imputer.recov_data

                References
                ----------
                L. Wang, S. Wu, T. Wu, X. Tao and J. Lu, "HKMF-T: Recover From Blackouts in Tagged Time Series With Hankel Matrix Factorization," in IEEE Transactions on Knowledge and Data Engineering, vol. 33, no. 11, pp. 3582-3593, 1 Nov. 2021, doi: 10.1109/TKDE.2020.2971190. keywords: {Time series analysis;Matrix decomposition;Market research;Meteorology;Sparse matrices;Indexes;Software;Tagged time series;missing value imputation;blackouts;hankel matrix factorization}
                https://github.com/wangliang-cs/hkmf-t?tab=readme-ov-file
                """
                from imputegap.algorithms.hkmf_t import hkmf_t

                if params is not None:
                    tags, data_names, epoch = self._check_params(user_def, params)
                else:
                    tags, data_names, epoch = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                if not tags:
                    tags = None
                if not data_names:
                    data_names = None

                self.recov_data = hkmf_t(incomp_data=self.incomp_data, tags=tags, data_names=data_names, epoch=epoch, tr_ratio=tr_ratio, logs=self.logs, verbose=self.verbose)

                return self

        class BitGraph(BaseImputer):
            """
            BitGraph class to impute missing values using BIASED TEMPORAL CONVOLUTION GRAPH NETWORK FOR TIME SERIES FORECASTING WITH MISSING VALUES

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the BitGraph
            """

            algorithm = "bit_graph"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using BIASED TEMPORAL CONVOLUTION GRAPH NETWORK FOR TIME SERIES FORECASTING WITH MISSING VALUES

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the BitGraph algorithm or Auto-ML configuration, if None, default ones are loaded.

                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).


                    **Algorithm parameters:**

                        node_number : int, optional
                            The number of nodes (time series variables) in the dataset. If not provided,
                            it is inferred from `incomp_data`.

                        kernel_set : list, optional
                            Set of kernel sizes used in the model for graph convolution operations (default: [1]).

                        dropout : float, optional
                            Dropout rate applied during training to prevent overfitting (default: 0.1).

                        subgraph_size : int, optional
                            The size of each subgraph used in message passing within the graph network (default: 5).

                        node_dim : int, optional
                            Dimensionality of the node embeddings in the graph convolution layers (default: 3).

                        seq_len : int, optional
                            Length of the input sequence for temporal modeling (default: 1).

                        lr : float, optional
                            Learning rate for model optimization (default: 0.001).

                        epoch : int, optional
                            Number of training epochs (default: 10).

                        num_workers: int, optional
                            Number of worker for multiprocess (default is 0).

                        seed : int, optional
                            Random seed for reproducibility (default: 42).

                Returns
                -------
                self : BitGraph
                    BitGraph object with `recov_data` set.

                Example
                -------
                    >>> bit_graph_imputer = Imputation.DeepLearning.BitGraph(incomp_data)
                    >>> bit_graph_imputer.impute()  # default parameters for imputation > or
                    >>> bit_graph_imputer.impute(user_def=True, params={"node_number":-1, "kernel_set":[1], "dropout":0.1, "subgraph_size":5, "node_dim":3, "seq_len":1, "lr":0.001, "batch_size": 32, "epoch":10, "num_workers":0, "seed":42})  # user defined> or
                    >>> bit_graph_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # auto-ml with ray_tune
                    >>> recov_data = bit_graph_imputer.recov_data

                References
                ----------
                X. Chen1, X. Li, T. Wu, B. Liu and Z. Li, BIASED TEMPORAL CONVOLUTION GRAPH NETWORK FOR TIME SERIES FORECASTING WITH MISSING VALUES
                https://github.com/chenxiaodanhit/BiTGraph
                """

                from imputegap.algorithms.bit_graph import bit_graph

                if params is not None:
                    node_number, kernel_set, dropout, subgraph_size, node_dim, seq_len, lr, batch_size, epoch, num_workers, seed = self._check_params(user_def, params)
                else:
                    node_number, kernel_set, dropout, subgraph_size, node_dim, seq_len, lr, batch_size, epoch, num_workers, seed = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = bit_graph(incomp_data=self.incomp_data, node_number=node_number, kernel_set=kernel_set, dropout=dropout, subgraph_size=subgraph_size, node_dim=node_dim, seq_len=seq_len, lr=lr, epoch=epoch, num_workers=num_workers, tr_ratio=tr_ratio, seed=seed, logs=self.logs, verbose=self.verbose)

                return self

    class LLMs:
        """
        A class containing specific imputation algorithms for Pre-trained Language Models (LLMs)
        """

        class NuwaTS(BaseImputer):
            """
            NuwaTS class to impute missing values using Foundation Model Mending Every Incomplete Time Series

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the NuwaTS
            """

            algorithm = "nuwats"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using Foundation Model Mending Every Incomplete Time Series

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the BitGraph algorithm or Auto-ML configuration, if None, default ones are loaded.

                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).


                    **Algorithm parameters:**

                        incomp_data : numpy.ndarray
                            The input matrix with contamination (missing values represented as NaNs).

                        seq_length : int, optional
                            Length of the input sequence for the encoder. If -1, it will be automatically determined (default: -1).

                        patch_size : int, optional
                            Patch size used for segmenting the sequence in the NuwaTS model (default: -1).

                        batch_size : int, optional
                            Number of samples per batch during training/inference. If -1, it will be auto-set (default: -1).

                        pred_length : int, optional
                            Length of the output prediction window (default: -1).

                        label_length : int, optional
                            Length of the label segment used during decoding (default: -1).

                        enc_in : int, optional
                            Number of input features for the encoder (default: 10).

                        dec_in : int, optional
                            Number of input features for the decoder (default: 10).

                        c_out : int, optional
                            Number of output features of the model (default: 10).

                        gpt_layers : int, optional
                            Number of layers in the transformer/generator component (default: 6).

                        num_workers: int, optional
                            Number of worker for multiprocess (default is 0).

                        seed : int, optional
                            Random seed for reproducibility (default: 42).

                        logs : bool, optional
                            Whether to print/log execution time and key events (default: True).

                        verbose : bool, optional
                            Whether to print detailed output information during execution (default: True).


                Returns
                -------
                self : NuwaTS
                    NuwaTS object with `recov_data` set.

                Example
                -------
                    >>> nuwats_imputer = Imputation.LLMs.NuwaTS(incomp_data)
                    >>> nuwats_imputer.impute()  # default parameters for imputation > or
                    >>> nuwats_imputer.impute(user_def=True, params={"seq_length":-1, "patch_size":-1, "batch_size":-1, "pred_length":-1, "label_length":-1, "enc_in":10, "dec_in":10, "c_out": 10, "gpt_layers":6, "num_workers":0, "seed":42})  # user defined> or
                    >>> nuwats_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # auto-ml with ray_tune
                    >>> recov_data = nuwats_imputer.recov_data

                References
                ----------
                Cheng, Jinguo and Yang, Chunwei and Cai, Wanlin and Liang, Yuxuan and Wen, Qingsong and Wu, Yuankai: "NuwaTS: Mending Every Incomplete Time Series", arXiv'2024
                https://github.com/Chengyui/NuwaTS/tree/master
                """

                from imputegap.algorithms.nuwats import nuwats

                if params is not None:
                    seq_length, patch_size, batch_size, pred_length, label_length, enc_in, dec_in, c_out, gpt_layers, num_workers, seed = self._check_params(user_def, params)
                else:
                    seq_length, patch_size, batch_size, pred_length, label_length, enc_in, dec_in, c_out, gpt_layers, num_workers, seed = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = nuwats(incomp_data=self.incomp_data, seq_length=seq_length, patch_size=patch_size, batch_size=batch_size, pred_length=pred_length, label_length=label_length, enc_in=enc_in, dec_in=dec_in, c_out=c_out, gpt_layers=gpt_layers, num_workers=num_workers, tr_ratio=tr_ratio, seed=seed, logs=self.logs, verbose=self.verbose)

                return self


        class GPT4TS(BaseImputer):
            """
            GPT4TS class to impute missing values using Foundation Model Mending Every Incomplete Time Series
            (Model used from the NuwaTS repository)

            Methods
            -------
            impute(self, user_def=True, params=None):
                Perform imputation using the GPT4TS
            """

            algorithm = "gpt4ts"

            def impute(self, user_def=True, params=None, tr_ratio=0.9):
                """
                Perform imputation using GPT4TS (Foundation Model Mending Every Incomplete Time Series)

                Parameters
                ----------
                user_def : bool, optional
                    Whether to use user-defined or default parameters (default is True).

                params : dict, optional
                    Parameters of the BitGraph algorithm or Auto-ML configuration, if None, default ones are loaded.

                tr_ratio: float, optional
                    Split ratio between training and testing sets (default is 0.9).


                    **Algorithm parameters:**

                        incomp_data : numpy.ndarray
                            The input matrix with contamination (missing values represented as NaNs).

                        seq_length : int, optional
                            Length of the input sequence for the encoder. If -1, it will be automatically determined (default: -1).

                        patch_size : int, optional
                            Patch size used for segmenting the sequence in the NuwaTS model (default: -1).

                        batch_size : int, optional
                            Number of samples per batch during training/inference. If -1, it will be auto-set (default: -1).

                        pred_length : int, optional
                            Length of the output prediction window (default: -1).

                        label_length : int, optional
                            Length of the label segment used during decoding (default: -1).

                        enc_in : int, optional
                            Number of input features for the encoder (default: 10).

                        dec_in : int, optional
                            Number of input features for the decoder (default: 10).

                        c_out : int, optional
                            Number of output features of the model (default: 10).

                        gpt_layers : int, optional
                            Number of layers in the transformer/generator component (default: 6).

                        num_workers: int, optional
                            Number of worker for multiprocess (default is 00).

                        seed : int, optional
                            Random seed for reproducibility (default: 42).

                        logs : bool, optional
                            Whether to print/log execution time and key events (default: True).

                        verbose : bool, optional
                            Whether to print detailed output information during execution (default: True).


                Returns
                -------
                self : GPT4TS
                    GPT4TS object with `recov_data` set.

                Example
                -------
                    >>> gpt4ts_imputer = Imputation.LLMs.GPT4TS(incomp_data)
                    >>> gpt4ts_imputer.impute()  # default parameters for imputation > or
                    >>> gpt4ts_imputer.impute(user_def=True, params={"seq_length":-1, "patch_size":-1, "batch_size":-1, "pred_length":-1, "label_length":-1, "enc_in":10, "dec_in":10, "c_out": 10, "gpt_layers":6, "num_workers":0, "seed":42})  # user defined> or
                    >>> gpt4ts_imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})  # auto-ml with ray_tune
                    >>> recov_data = gpt4ts_imputer.recov_data

                References
                ----------
                Cheng, Jinguo and Yang, Chunwei and Cai, Wanlin and Liang, Yuxuan and Wen, Qingsong and Wu, Yuankai: "NuwaTS: Mending Every Incomplete Time Series", arXiv'2024
                https://github.com/Chengyui/NuwaTS/tree/master
                """

                from imputegap.algorithms.gpt4ts import gpt4ts

                if params is not None:
                    seq_length, patch_size, batch_size, pred_length, label_length, enc_in, dec_in, c_out, gpt_layers, num_workers, seed = self._check_params(user_def, params)
                else:
                    seq_length, patch_size, batch_size, pred_length, label_length, enc_in, dec_in, c_out, gpt_layers, num_workers, seed = utils.load_parameters(query="default", algorithm=self.algorithm, verbose=self.verbose)

                self.recov_data = gpt4ts(incomp_data=self.incomp_data,  seq_length=seq_length, patch_size=patch_size, batch_size=batch_size, pred_length=pred_length, label_length=label_length, enc_in=enc_in, dec_in=dec_in, c_out=c_out, gpt_layers=gpt_layers, num_workers=num_workers, tr_ratio=tr_ratio, seed=seed, logs=self.logs, verbose=self.verbose)

                return self


