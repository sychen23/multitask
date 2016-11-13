"""
Analysis of general properties of tasks
"""

from __future__ import division

import os
import numpy as np
import pickle
import time
import copy
from collections import OrderedDict
import scipy.stats as stats
from scipy.optimize import curve_fit, minimize
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn.apionly as sns # If you don't have this, then some colormaps won't work
from task import *
from run import Run

color_rules = np.array([
            [240,163,255],[0,117,220],[153,63,0],[76,0,92],[25,25,25],[0,92,49],
            [43,206,72],[255,204,153],[128,128,128],[148,255,181],[143,124,0],
            [157,204,0],[194,0,136],[0,51,128],[255,164,5],[255,168,187],[66,102,0],
            [255,0,16],[94,241,242],[0,153,143],[224,255,102],[116,10,255],
            [153,0,0],[255,255,128],[255,255,0],[255,80,5]])/255.

def plot_trainingprogress(save_addon, rule_plot=None, save=True):
    # Plot Training Progress
    with open('data/config'+save_addon+'.pkl', 'rb') as f:
        config = pickle.load(f)

    trials      = config['trials']
    times       = config['times']
    cost_tests  = config['cost_tests']
    perf_tests  = config['perf_tests']

    fig = plt.figure(figsize=(5,3))
    d1, d2 = 0.01, 0.35
    ax1 = fig.add_axes([0.15,0.5+d1,   0.5,d2])
    ax2 = fig.add_axes([0.15,0.5-d1-d2,0.5,d2])
    lines = list()
    labels = list()

    x_plot = np.array(trials)/1000.
    if rule_plot == None:
        rule_plot = cost_tests.keys()

    for i, rule in enumerate(rule_plot):
        line = ax1.plot(x_plot, np.log10(cost_tests[rule]),color=color_rules[i%26])
        ax2.plot(x_plot, perf_tests[rule],color=color_rules[i%26])
        lines.append(line[0])
        labels.append(rule_name[rule])

    ax1.tick_params(axis='both', which='major', labelsize=7)
    ax2.tick_params(axis='both', which='major', labelsize=7)

    ax2.set_ylim([-0.05, 1.05])
    ax2.set_xlabel('Total trials (1,000)',fontsize=7)
    ax2.set_ylabel('performance',fontsize=7)
    ax1.set_ylabel('log(cost)',fontsize=7)
    ax1.set_xticklabels([])
    ax1.set_title('Training time {:0.0f} s'.format(times[-1]),fontsize=7)
    lg = fig.legend(lines, labels, title='Rule',ncol=1,bbox_to_anchor=(0.65,0.5),
                    fontsize=7,labelspacing=0.3,loc=6)
    plt.setp(lg.get_title(),fontsize=7)
    if save:
        plt.savefig('figure/Training_Progress'+config['save_addon']+'.pdf', transparent=True)
    plt.show()

def plot_finalperformance(save_type='tf'):
    # Initialization. Dictionary comprehension.
    HDIM, N_RING = 500, 16
    save_addon = save_type+'_'+str(HDIM)
    with open('data/config'+save_addon+'.pkl','rb') as f:
        config = pickle.load(f)
    cost_tests  = config['cost_tests']
    perf_tests  = config['perf_tests']

    final_cost = {k: [] for k in cost_tests}
    final_perf = {k: [] for k in cost_tests}
    HDIM_plot = list()
    training_time_plot = list()
    # Recording performance and cost for networks
    HDIMs = range(1000)
    for HDIM in HDIMs:
        save_addon = save_type+'_'+str(HDIM)
        fname = 'data/config'+save_addon+'.pkl'
        if not os.path.isfile(fname):
            continue
        with open(fname,'rb') as f:
            config = pickle.load(f)
        cost_tests = config['cost_tests']
        perf_tests = config['perf_tests']
        if perf_tests[DMCGO][-1] > 0.1:
            for key in perf_tests.keys():
                final_perf[key] += [float(perf_tests[key][-1])]
                final_cost[key]        += [float(cost_tests[key][-1])]
            HDIM_plot.append(HDIM)
            training_time_plot.append(config['times'][-1])

    n_trial = config['trials'][-1]
    x_plot = np.array(HDIM_plot)
    rule_plot = None
    if rule_plot == None:
        rule_plot = perf_tests.keys()

    fig = plt.figure(figsize=(5,3))
    d1, d2 = 0.01, 0.35
    ax1 = fig.add_axes([0.15,0.5+d1,   0.5,d2])
    ax2 = fig.add_axes([0.15,0.5-d1-d2,0.5,d2])
    lines = list()
    labels = list()
    for i, rule in enumerate(rule_plot):
        line = ax1.plot(x_plot,np.log10(final_cost[rule]),color=color_rules[i%26])
        ax2.plot(x_plot,final_perf[rule],color=color_rules[i%26])
        lines.append(line[0])
        labels.append(rule_name[rule])

    ax1.tick_params(axis='both', which='major', labelsize=7)
    ax2.tick_params(axis='both', which='major', labelsize=7)

    ax2.set_ylim(top=1.05)
    ax2.set_xlabel('Number of Recurrent Units',fontsize=7)
    ax2.set_ylabel('performance',fontsize=7)
    ax1.set_ylabel(r'$log_{10}$(cost)',fontsize=7)
    ax1.set_xticklabels([])
    ax1.set_title('After {:.1E} trials'.format(n_trial),fontsize=7)
    lg = fig.legend(lines, labels, title='Rule',ncol=1,bbox_to_anchor=(0.65,0.5),
                    fontsize=7,labelspacing=0.3,loc=6)
    plt.setp(lg.get_title(),fontsize=7)
    plt.savefig('figure/FinalCostPerformance_'+save_type+'.pdf', transparent=True)
    plt.show()

    x_plot = np.array(HDIM_plot)/100.
    y_plot = np.array(training_time_plot)/3600.
    fig = plt.figure(figsize=(5,1.5))
    ax  = fig.add_axes([0.15, 0.25, 0.5, 0.7])
    p = np.polyfit(x_plot[x_plot<5], y_plot[x_plot<5], 2) # Temporary
    #p = np.polyfit(x_plot, y_plot, 2)
    ax.plot(x_plot, p[0]*x_plot**2+p[1]*x_plot+p[2], color='black')
    ax.plot(x_plot, y_plot, color=sns.xkcd_palette(['cerulean'])[0])
    ax.text(0.05, 0.7, 'Number of Hours = \n {:0.2f}$(N/100)^2$+{:0.2f}$(N/100)$+{:0.2f}'.format(*p), fontsize=7, transform=ax.transAxes)
    ax.set_xlabel('Number of Recurrent Units $N$ (100)',fontsize=7)
    ax.set_ylabel('Training time (hours)',fontsize=7)
    ax.tick_params(axis='both', which='major', labelsize=7)
    plt.savefig('figure/FinalTrainingTime_'+save_type+'.pdf', transparent=True)
    plt.show()

def psychometric_choice(save_addon, **kwargs):
    print('Starting standard analysis of the CHOICE task...')
    with Run(save_addon) as R:
        n_tar_loc = 120
        n_tar = 7
        batch_size = n_tar_loc * n_tar
        batch_shape = (n_tar_loc,n_tar)
        ind_tar_loc, ind_tar = np.unravel_index(range(batch_size),batch_shape)

        tar1_locs = 2*np.pi*ind_tar_loc/n_tar_loc
        tar2_locs = (tar1_locs+np.pi)%(2*np.pi)

        tar_str_range = 0.2
        tar1_strengths = (1-tar_str_range/2)+tar_str_range*ind_tar/(n_tar-1)
        tar2_strengths = 2 - tar1_strengths

        ydatas = list()
        tar_times = [200, 400, 800]
        for tar_time in tar_times:
            params = {'tar1_locs' : tar1_locs,
                      'tar2_locs' : tar2_locs,
                      'tar1_strengths' : tar1_strengths,
                      'tar2_strengths' : tar2_strengths,
                      'tar_time'    : tar_time}

            task  = generate_onebatch(CHOICE_MOD1, R.config, 'psychometric', params=params)
            y_loc_sample = R.f_y_loc_from_x(task.x)
            y_loc_sample = np.reshape(y_loc_sample[-1], batch_shape)

            tar1_locs_ = np.reshape(tar1_locs, batch_shape)
            tar2_locs_ = np.reshape(tar2_locs, batch_shape)

            choose1 = (get_dist(y_loc_sample - tar1_locs_) < 0.3*np.pi).sum(axis=0)
            choose2 = (get_dist(y_loc_sample - tar2_locs_) < 0.3*np.pi).sum(axis=0)
            ydatas.append(choose1/(choose1 + choose2))

        xdatas = [tar_str_range*(-1+2*np.arange(n_tar)/(n_tar-1))] * len(tar_times)

    plot_psychometric_choice(xdatas, ydatas,
                              labels=[str(t) for t in tar_times],
                              colors=sns.dark_palette("light blue", 3, input="xkcd"),
                              legtitle='Stim. time (ms)',rule=CHOICE_MOD1, **kwargs)

def psychometric_delaychoice(save_addon, **kwargs):
    print('Starting standard analysis of the CHOICEDELAY task...')
    with Run(save_addon) as R:
        n_tar_loc = 120
        n_tar = 7
        batch_size = n_tar_loc * n_tar
        batch_shape = (n_tar_loc,n_tar)
        ind_tar_loc, ind_tar = np.unravel_index(range(batch_size),batch_shape)

        tar1_locs = 2*np.pi*ind_tar_loc/n_tar_loc
        tar2_locs = (tar1_locs+np.pi)%(2*np.pi)

        tar_str_range = 0.75
        tar1_strengths = (1-tar_str_range/2)+tar_str_range*ind_tar/(n_tar-1)
        tar2_strengths = 2 - tar1_strengths

        tar1_ons = 200
        tar1_offs = 400

        dtars = [200,1500,3000] # tar1 offset and tar2 onset time difference
        # dtars = [2800,3000,3200] # tar1 offset and tar2 onset time difference
        ydatas = list()
        for dtar in dtars:
            tar2_ons  = tar1_offs + dtar
            tar2_offs = tar2_ons + 200
            params = {'tar1_locs'    : tar1_locs,
                      'tar2_locs'    : tar2_locs,
                      'tar1_strengths' : tar1_strengths,
                      'tar2_strengths' : tar2_strengths,
                      'tar1_ons'     : tar1_ons,
                      'tar1_offs'    : tar1_offs,
                      'tar2_ons'     : tar2_ons,
                      'tar2_offs'    : tar2_offs,
                      }

            task  = generate_onebatch(CHOICEDELAY_MOD1, R.config, 'psychometric', params=params)
            y_loc_sample = R.f_y_loc_from_x(task.x)
            y_loc_sample = np.reshape(y_loc_sample[-1], batch_shape)

            tar1_locs_ = np.reshape(tar1_locs, batch_shape)
            tar2_locs_ = np.reshape(tar2_locs, batch_shape)

            choose1 = (get_dist(y_loc_sample - tar1_locs_) < 0.3*np.pi).sum(axis=0)
            choose2 = (get_dist(y_loc_sample - tar2_locs_) < 0.3*np.pi).sum(axis=0)
            print(choose1)
            print(choose2)
            ydatas.append(choose1/(choose1 + choose2))

        xdatas = [tar_str_range*(-1+2*np.arange(n_tar)/(n_tar-1))] * len(dtars)

    plot_psychometric_choice(xdatas, ydatas,
                              labels=[str(t) for t in dtars],
                              colors=sns.dark_palette("light blue", 3, input="xkcd"),
                              legtitle='Delay (ms)',rule=CHOICEDELAY_MOD1, **kwargs)

def psychometric_choiceattend(save_addon, **kwargs):
    print('Starting standard analysis of the CHOICEATTEND task...')
    with Run(save_addon) as R:

        from task import get_dist

        n_tar_loc = 12 # increase repeat by increasing this
        n_tar = 7
        batch_size = n_tar_loc * n_tar**2
        batch_shape = (n_tar_loc,n_tar,n_tar)
        ind_tar_loc, ind_tar_mod1, ind_tar_mod2 = np.unravel_index(range(batch_size),batch_shape)

        tar1_locs = 2*np.pi*ind_tar_loc/n_tar_loc
        tar2_locs = (tar1_locs+np.pi)%(2*np.pi)

        tar_str_range = 0.25
        tar1_mod1_strengths = (1-tar_str_range/2)+tar_str_range*ind_tar_mod1/(n_tar-1)
        tar2_mod1_strengths = 2 - tar1_mod1_strengths
        tar1_mod2_strengths = (1-tar_str_range/2)+tar_str_range*ind_tar_mod2/(n_tar-1)
        tar2_mod2_strengths = 2 - tar1_mod2_strengths

        params = {'tar1_locs' : tar1_locs,
                  'tar2_locs' : tar2_locs,
                  'tar1_mod1_strengths' : tar1_mod1_strengths,
                  'tar2_mod1_strengths' : tar2_mod1_strengths,
                  'tar1_mod2_strengths' : tar1_mod2_strengths,
                  'tar2_mod2_strengths' : tar2_mod2_strengths,
                  'tar_time'    : 800}

        task  = generate_onebatch(CHOICEATTEND_MOD1, R.config, 'psychometric', params=params)
        y_loc_sample = R.f_y_loc_from_x(task.x)
        y_loc_sample = np.reshape(y_loc_sample[-1], batch_shape)

        tar1_locs_ = np.reshape(tar1_locs, batch_shape)
        tar2_locs_ = np.reshape(tar2_locs, batch_shape)

        choose1 = (get_dist(y_loc_sample - tar1_locs_) < 0.3*np.pi).sum(axis=0)
        choose2 = (get_dist(y_loc_sample - tar2_locs_) < 0.3*np.pi).sum(axis=0)
        prop1s = choose1/(choose1 + choose2)

        xdatas = [tar_str_range*(-1+2*np.arange(n_tar)/(n_tar-1))]*2
        ydatas = [prop1s.mean(axis=k) for k in [1,0]]

        plot_psychometric_choice(xdatas, ydatas,
                                  labels=['Attend', 'Ignore'],
                                  colors=sns.color_palette("Set2",2),
                                  legtitle='Modality',rule=CHOICEATTEND_MOD1, **kwargs)

def psychometric_choiceattend_varytime(save_addon, **kwargs):
    print('Starting second analysis of the CHOICEATTEND task...')
    with Run(save_addon) as R:

        from task import get_dist

        n_tar_loc = 12 # increase repeat by increasing this
        n_tar = 7
        batch_size = n_tar_loc * n_tar**2
        batch_shape = (n_tar_loc,n_tar,n_tar)
        ind_tar_loc, ind_tar_mod1, ind_tar_mod2 = np.unravel_index(range(batch_size),batch_shape)

        tar1_locs = 2*np.pi*ind_tar_loc/n_tar_loc
        tar2_locs = (tar1_locs+np.pi)%(2*np.pi)

        tar_str_range = 0.25
        tar1_mod1_strengths = (1-tar_str_range/2)+tar_str_range*ind_tar_mod1/(n_tar-1)
        tar2_mod1_strengths = 2 - tar1_mod1_strengths
        tar1_mod2_strengths = (1-tar_str_range/2)+tar_str_range*ind_tar_mod2/(n_tar-1)
        tar2_mod2_strengths = 2 - tar1_mod2_strengths

        xdatas = list()
        ydatas = list()
        tar_times = [200, 400, 800, 1200]
        for tar_time in tar_times:
            params = {'tar1_locs' : tar1_locs,
                      'tar2_locs' : tar2_locs,
                      'tar1_mod1_strengths' : tar1_mod1_strengths,
                      'tar2_mod1_strengths' : tar2_mod1_strengths,
                      'tar1_mod2_strengths' : tar1_mod2_strengths,
                      'tar2_mod2_strengths' : tar2_mod2_strengths,
                      'tar_time'    : tar_time}

            task  = generate_onebatch(CHOICEATTEND_MOD1, R.config, 'psychometric', params=params)
            y_loc_sample = R.f_y_loc_from_x(task.x)
            y_loc_sample = np.reshape(y_loc_sample[-1], batch_shape)

            tar1_locs_ = np.reshape(tar1_locs, batch_shape)
            tar2_locs_ = np.reshape(tar2_locs, batch_shape)

            choose1 = (get_dist(y_loc_sample - tar1_locs_) < 0.3*np.pi).sum(axis=0)
            choose2 = (get_dist(y_loc_sample - tar2_locs_) < 0.3*np.pi).sum(axis=0)
            prop1s = choose1/(choose1 + choose2)

            xdatas.extend([tar_str_range*(-1+2*np.arange(n_tar)/(n_tar-1))])
            ydatas.extend([prop1s.mean(axis=k) for k in [1]])

        plot_psychometric_choice(xdatas, ydatas,
                                 labels=[str(t) for t in tar_times],
                                 colors=sns.dark_palette("light blue", len(tar_times), input="xkcd"),
                                 legtitle='Stim. time (ms)',rule=CHOICEATTEND_MOD1,
                                 savename_append='2', **kwargs)

def psychometric_choiceint(save_addon, **kwargs):
    print('Starting standard analysis of the CHOICEINT task...')
    with Run(save_addon) as R:


        n_tar_loc = 100 # increase repeat by increasing this
        n_tar = 7
        batch_size = n_tar_loc * n_tar
        batch_shape = (n_tar_loc,n_tar)
        ind_tar_loc, ind_tar1_strength = np.unravel_index(range(batch_size),batch_shape)

        tar1_locs = 2*np.pi*ind_tar_loc/n_tar_loc
        tar2_locs = (tar1_locs+np.pi)%(2*np.pi)

        tar_str_range = 0.1
        tar1_strengths = (1-tar_str_range/2)+tar_str_range*ind_tar1_strength/(n_tar-1)
        tar2_strengths = 2 - tar1_strengths

        xdatas = list()
        ydatas = list()
        for mod_strength in [(1,0), (0,1), (1,1)]:
            params = {'tar1_locs' : tar1_locs,
                      'tar2_locs' : tar2_locs,
                      'tar1_mod1_strengths' : tar1_strengths*mod_strength[0],
                      'tar2_mod1_strengths' : tar2_strengths*mod_strength[0],
                      'tar1_mod2_strengths' : tar1_strengths*mod_strength[1],
                      'tar2_mod2_strengths' : tar2_strengths*mod_strength[1],
                      'tar_time'    : 800}

            task  = generate_onebatch(CHOICE_INT, R.config, 'psychometric', params=params)
            y_loc_sample = R.f_y_loc_from_x(task.x)
            y_loc_sample = np.reshape(y_loc_sample[-1], batch_shape)

            tar1_locs_ = np.reshape(tar1_locs, batch_shape)
            tar2_locs_ = np.reshape(tar2_locs, batch_shape)

            choose1 = (get_dist(y_loc_sample - tar1_locs_) < 0.3*np.pi).sum(axis=0)
            choose2 = (get_dist(y_loc_sample - tar2_locs_) < 0.3*np.pi).sum(axis=0)
            prop1s = choose1/(choose1 + choose2)

            xdatas.append(tar_str_range*(-1+2*np.arange(n_tar)/(n_tar-1)))
            ydatas.append(prop1s)

        fits = plot_psychometric_choice(
            xdatas,ydatas, labels=['1 only', '2 only', 'both'],
            colors=sns.color_palette("Set2",3),
            legtitle='Modality',rule=CHOICE_INT, **kwargs)
        sigmas = [fit[1] for fit in fits]
        print('Fit sigmas:')
        print(sigmas)

def psychometric_intrepro(save_addon):
    with Run(save_addon) as R:

        n_tar_loc = 360
        # intervals = [700]
        # intervals = [500, 600, 700, 800, 900, 1000]
        intervals = np.linspace(500, 1000, 10)
        mean_sample_intervals = list()
        for interval in intervals:
            batch_size = n_tar_loc
            tar_mod1_locs  = 2*np.pi*np.arange(n_tar_loc)/n_tar_loc

            params = {'tar_mod1_locs'  : tar_mod1_locs,
                      'interval'       : interval}

            task  = generate_onebatch(INTREPRO, R.config, 'psychometric', params=params)
            h_test = R.f_h(task.x)
            y = R.f_y(h_test)

            sample_intervals = list() # sampled interval test
            for i_batch in range(batch_size):
                try: ##TODO: Temporary solution
                    # Setting the threshold can be tricky, but doesn't impact the overall results
                    sample_interval = np.argwhere(y[:,i_batch,0]<0.3)[0]-task.epochs['tar2'][1]
                    sample_intervals.append(sample_interval)
                except IndexError:
                    # print i_batch
                    pass
            mean_sample_intervals.append(np.mean(sample_intervals))

        fig = plt.figure(figsize=(2,1.5))
        ax = fig.add_axes([0.25,0.25,0.65,0.65])
        ax.plot(intervals, mean_sample_intervals, 'o-', markersize=3.5, color=sns.xkcd_palette(['blue'])[0])
        ax.plot(intervals, intervals, color=sns.xkcd_palette(['black'])[0])
        plt.xlim([intervals[0]-50,intervals[-1]+50])
        plt.ylim([intervals[0]-50,intervals[-1]+50])
        plt.xlabel('Sample Interval (ms)',fontsize=7)
        plt.ylabel('Production interval (ms)',fontsize=7)
        plt.title('Rule '+rule_name[INTREPRO], fontsize=7)
        plt.locator_params(nbins=5)
        ax.tick_params(axis='both', which='major', labelsize=7)

        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        plt.savefig('figure/analyze_'+rule_name[INTREPRO].replace(' ','')+'_performance.pdf', transparent=True)
        plt.show()

def plot_psychometric_choice(xdatas, ydatas, labels, colors, **kwargs):
    '''
    For the class of choice tasks, plot the psychometric function for a list of
    xdatas and ydatas
    '''
    fig = plt.figure(figsize=(2,1.5))
    ax = fig.add_axes([0.25,0.25,0.65,0.65])
    fits = list()
    for i in range(len(xdatas)):
        # Analyze performance of the choice tasks
        cdf_gaussian = lambda x, mu, sigma : stats.norm.cdf(x, mu, sigma)

        xdata = xdatas[i]
        ydata = ydatas[i]
        (mu,sigma), _ = curve_fit(cdf_gaussian, xdata, ydata, bounds=([-0.5,0.01],[0.5,1]))
        fits.append((mu,sigma))
        x_plot = np.linspace(xdata[0],xdata[-1],100)
        ax.plot(x_plot, cdf_gaussian(x_plot,mu,sigma), label=labels[i],
                linewidth=1, color=colors[i])
        ax.plot(xdata, ydata, 'o', markersize=3.5, color=colors[i])

    plt.xlabel('Target 1 - Target 2',fontsize=7)
    plt.ylim([-0.05,1.05])
    plt.xlim([xdata[0]*1.1,xdata[-1]*1.1])
    plt.yticks([0,0.5,1])
    if 'no_ylabel' in kwargs and kwargs['no_ylabel']:
        plt.yticks([0,0.5,1],['','',''])
    else:
        plt.ylabel('Proportion of choice 1',fontsize=7)
    plt.title(rule_name[kwargs['rule']], fontsize=7)
    plt.locator_params(axis='x', nbins=5)
    ax.tick_params(axis='both', which='major', labelsize=7)

    if len(xdatas)>1:
        if len(kwargs['legtitle'])>10:
            bbox_to_anchor = (0.6, 1.1)
        else:
            bbox_to_anchor = (0.5, 1.1)
        leg = plt.legend(title=kwargs['legtitle'],fontsize=7,frameon=False,
                         bbox_to_anchor=bbox_to_anchor,labelspacing=0.3)
        plt.setp(leg.get_title(),fontsize=7)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    savename = 'figure/analyze_'+rule_name[kwargs['rule']].replace(' ','') + '_performance'
    if 'savename_append' in kwargs:
        savename += kwargs['savename_append']

    #plt.savefig(savename+'.pdf', transparent=True)
    plt.show()
    return fits


# plot_trainingprogress('tf_latest_400')
# plot_finalperformance('tf_latest')

psychometric_choice('tf_choiceonly_100')
# psychometric_choiceattend('tf_latest_400')
# psychometric_choiceattend_varytime('tf_latest_400')
# psychometric_choiceint('tf_latest_400')
# psychometric_delaychoice('tf_500')


