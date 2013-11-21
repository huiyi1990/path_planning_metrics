#!/usr/bin/python

import roslib; roslib.load_manifest('path_planning_ruler')
import rospy
from path_planning_ruler import *
from path_planning_ruler.scenario import Scenario
from path_planning_ruler.move_base import *
from path_planning_ruler.parameterization import *
import sys
import argparse
import os, errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def param_keys(s1, s2=None):
    a1 = s1.split('/')
    ns1 = a1[-1]
    if s2 is None:
        return ns1

    a2 = s2.split('/')
    ns2 = a2[-1]

    if ns1 != ns2:
        return ns1, ns2

    i=2
    while i <= len(a1) and i <= len(a2):
        b1 = a1[-i]
        b2 = a2[-i]
        if b1 == b2:
            i+=1
        else:
            return "%s_%s"%(b1, ns1), "%s_%s"%(b2, ns2)

    return '_'.join(a1), '_'.join(a2)

basedir = '/home/dlu/Desktop/path_data'

def parameterize(var1, var2, set1, set2):
    if var1 or set1:
        if var1:
            param1, N_str = var1
            parameterizations = multiply(parameterizations, param1, N_str)
        else:
            param1, val1, N_str = set1
            val1 = int(val1)
            N = int(N_str)
            newp = []
            for p in parameterizations:
                newm = {param1: (N, val1)}
                newm.update(p)
                newp.append(newm)
            parameterizations = newp

        if var2 or set2:
            if var2:
                param2, N_str = var2
                parameterizations = multiply(parameterizations, param2, N_str)
            else:
                param2, val2, N_str = set2
                val12= int(val2)
                N = int(N_str)
                newp = []
                for p in parameterizations:
                    newm = {param2: (N, val2)}
                    newm.update(p)
                    newp.append(newm)
                parameterizations = newp

            key1, key2 = param_keys(param1, param2)
            directory = '%(root)s/twoD/%(algorithm)s-%(key1)s-%(key2)s'
            pattern = '%(scenario_key)s-%(value1)s-%(value2)s-%%03d.bag'
        else:
            key1 = param_keys(param1)
            directory = '%(root)s/oneD/%(algorithm)s-%(key1)s'
            pattern = '%(scenario_key)s-%(value1)s-%%03d.bag'
    else:
        directory = '%(root)s/core'
        pattern = '%(scenario_key)s-%(algorithm)s-%%03d.bag'

    return parameterizations, directory, pattern, param1, key1, param2, key2


def run_one_set(algorithm_fn, scenarios, n, parameterizations, directory, pattern, param1, key1, param2, key2, clean, quiet):
    m = MoveBaseInstance(quiet=quiet)
    scenarios = [Scenario(filename) for filename in scenarios]

    for parameterization in parameterizations:
        values = m.configure(algorithm_fn, parameterization)
        if param1:
            value1 = values[param1]
        if param2:
            value2 = values[param2]
        if len(parameterizations)>1:
            s = ', '.join(['%s: %s'%(str(k),str(v)) for k,v in values.iteritems()])
            rospy.loginfo(s)

        algorithm = rospy.get_param('/nav_experiments/algorithm')
        root = basedir

        for scenario in scenarios:
            scenario_key = scenario.key
            thedir = directory % locals()
            thepattern = pattern % locals()
            
            mkdir_p(thedir)
            full_pattern = '%s/%s'%(thedir, thepattern )
            run_batch_scenario(m, scenario, n, full_pattern, clean, quiet)
    
if __name__=='__main__':
    rospy.init_node('batch_trials_script')

    parser = argparse.ArgumentParser()
    parser.add_argument('algorithm', metavar='algorithm.cfg')
    parser.add_argument('scenario', metavar='scenario.yaml', nargs='+')
    parser.add_argument('-v', dest='variables', nargs="+", type=str)
    parser.add_argument('-c', dest='constants', nargs="+", type=str)
    parser.add_argument("-n", "--num_trials", dest="n", help='Number of trials per configuration', metavar='N', type=int, default=10)
    parser.add_argument('--clean', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')

    """    if '-b' in sys.argv:
        p2 = argparse.ArgumentParser()
        p2.add_argument('-b', '--batch', dest="batchfile")
        p2.add_argument('-q', '--quiet', action='store_true')
        p2.add_argument('-c', '--clean', action='store_true')
        a2 = p2.parse_args()
        f = open(a2.batchfile, 'r')
        for line in f.readlines():
            if len(line.strip())==0:
                continue
            args = parser.parse_args(line.split())
            parameterizations, directory, pattern, param1, key1, param2, key2 = parameterize(args.var1, args.var2, args.set1, args.set2)
            run_one_set(args.algorithm, args.scenarios, args.n, parameterizations, directory, pattern, param1, key1, param2, key2, args.clean or a2.clean, a2.quiet or args.quiet)
        f.close()        
    else:"""
    if True:
        args = parser.parse_args()
        parameterization = Parameterization(args.algorithm, args.variables, args.constants)

        print parameterization.get_folder()
        for p in parameterization.parameterizations:
            print parameterization.get_filename('scenario', p, 0)

        #run_one_set(args.algorithm, args.scenarios, args.n, parameterizations, directory, pattern, param1, key1, param2, key2, args.clean, args.quiet)



