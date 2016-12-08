#-----------------------------------------------------------------------------
# Copyright (c) 2016, Machiavellian Project.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------

import copy
from functools import partial

import numpy as np
import pandas as pd

import machivellian.effects as eff


def summarize_power(power_summary, sim_num, test, colors):
    """Generates a dataframe describing a power calculation run

    Please note, this function is primarily designed for use with the
    simulation notebooks.

    Parameters
    ----------
    power_summary : dict
        A dictionary summarizing the power simulation outputs generated in
        the monte_carlo_power simulation notebooks.
    sim_num : int
        Idenifier for the simulation
    test : str
        The name of the test applied
    colors : dictionary
        A dictionary linking the counts to the colors to be used in regression
        and residual gradient plots

    Returns
    -------
    ndarray
        The summary of the power analysis where each row contains data from a
        single observation. Columns include `counts`, `traditional`
        (distribution-based power), `empirical` (empirically based power),
        `sim_position` (a unique identifier for each simulation), `test`,
        `alpha` (the critical value), `sim_num` (the simulation id), and
        `colors`,
    """

    # Builds the initia data frame
    run_summary = _build_summary_frame(power_summary)

    #  Adds static information
    run_summary['test'] = test
    run_summary['ori_alpha'] = power_summary['alpha']
    run_summary['alpha'] = power_summary['alpha_adj'] * power_summary['alpha']
    run_summary['alpha_adj'] = power_summary['alpha_adj']
    run_summary['sim_num'] = sim_num
    run_summary['p_all'] = power_summary['original_p']
    run_summary['statistic'] = power_summary['statistic']

    # Includes the count values to be plotted
    run_summary['colors'] = run_summary['counts'].apply(lambda x: colors[x])

    run_summary['index'] = (
        run_summary['test'] + '.' +
        run_summary['sim_num'].apply(lambda x: '%i' % x) + '.' +
        run_summary['sim_position'].apply(lambda x: '%i' % x)
        )
    run_summary.set_index("index", inplace=True)

    return run_summary


# def modify_effect_size(df, drop_index, dists=None, num_groups=2):
#     """Calculates a modified effect size based on dropped values

#     Parameters
#     ----------
#     df : DataFrame
#         The output of `summarize_power` or a concatenated description of the
#         output of summarize power
#     drop_index : list, ndarray or Index
#         The observations to be excluded from the calculations
#     dists : list
#         The list of distributions to be used to calculate effect sizes and
#         power.
#     num_groups : int, optional
#         The number of groups included, to be used with the F distribution

#     Returns
#     -------
#     DataFrame
#         Summarizes the recalculated effect sizes and power. Columns include
#         `counts`, `traditional` (distribution-based power),
#         `empirical` (empirically based power), `sim_position` (a unique
#         idenifier for each simulation), `test`, `alpha` (the critical value),
#         `sim_num` (the simulation id), `colors`, and the corresponding
#         `effect` and `power` for each distribution specified in `dists.`
#     """
#     copy_cols = ['empirical', 'traditional', 'counts', 'color', 'simulation',
#                  'sim_pos', 'test', 'alpha']
#     copy_cols.extend(['%s_effect' % d for d in dists])
#     df_mod = copy.deepcopy(df)
#     df_mod.loc[drop_index, ['%s_effect' % d for d in dists]] = np.nan
#     _calculate_power(df_mod, dists, num_groups)

#     return df_mod


def calc_z_effect(x, col2='empirical', num_groups=2):
    """Wraps the z-based power calculation for pandas `apply`"""
    effect = eff.z_effect([x['counts']],
                          [x[col2]],
                          alpha=x['alpha'])[0]
    return effect


def calc_z_power(x, col2, num_groups=2):
    """Wraps the z-based power calulation"""
    power = eff.z_power(counts=x['counts'],
                        effect=x[col2],
                        alpha=x['alpha'])
    return power


def _build_summary_frame(sim):
    """Builds the intial dataframe summarizing the run"""
    counts = sim['counts']
    empirical = sim['emperical']

    # Determines the number of samples handled in the summary
    (empr_r, empr_c) = empirical.shape

    # Draws the traditional power
    if ('traditional' in sim.keys() and
            (sim['traditional'] is not None)):
        traditional = sim['traditional']
    else:
        traditional = np.nan * np.ones(counts.shape)

    # Sets up the summary dictionary
    run_summary = pd.DataFrame.from_dict(
        {'counts': np.hstack(np.array([counts] * empr_r)),
         'empirical': np.hstack(empirical),
         'traditional':
            np.hstack(np.array([traditional] * empr_r)),
         'sim_position': np.hstack([np.arange(empr_c) + i * 10
                                    for i in np.arange(empr_r)]),
         })

    return run_summary


# def _calculate_effect_size(df, distributions, num_groups=2):
#     """Adds the effect sizes to the dataframe"""
#     for dist in distributions:
#         if dist == 'f2':
#             ng = 2
#         else:
#             ng = num_groups
#         f_ = partial(effect_lookup[dist], col2='empirical',
#                      num_groups=ng)
#         df['%s_effect' % dist] = df.apply(f_, axis=1)


# def _calculate_power(df, distributions, num_groups=2):
#     """Adds power calculations to the dataframe"""
#     mean_lookup = (df.groupby('sim_num').mean()
#                    [['%s_effect' % d for d in distributions]])
#     for d in distributions:
#         mean_lookup.loc[mean_lookup['%s_effect' % d] < 0.1,
#                         '%s_effect' % d] = np.nan
#     mean_lookup = mean_lookup.to_dict()

#     for dist in distributions:
#         df['%s_mean' % dist] = \
#             df['sim_num'].replace(mean_lookup['%s_effect' % dist])
#         if dist == 'f2':
#             ng = 2
#         else:
#             ng = num_groups
#         f_ = partial(power_lookup[dist],
#                      col2='%s_mean' % dist,
#                      num_groups=ng)
#         df['%s_power' % dist] = df.apply(f_, axis=1)
