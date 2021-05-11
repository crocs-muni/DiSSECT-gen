#!/usr/bin/env python3

import argparse
import json
import logging
import os
from sage.all import ZZ
from job_manager.manager import ParallelRunner, Task, TaskResult
from standards.utils.utils import seed_update

try:
    import coloredlogs

    coloredlogs.install(level=logging.INFO)
except ModuleNotFoundError:
    print("E: Package coloredlogs is not installed. No logs will be displayed")

logger = logging.getLogger(__name__)


def get_file_name(params: list, result_dir=None) -> str:
    """Determines the file name of the results"""
    file_name = "%s.json" % ("_".join(map(str, params)),)
    return file_name if result_dir is None else os.path.join(result_dir, file_name)


def load_parameters(standard: str, config_path: str, num_bits: int, cofactor: int, total_count: int, count: int,
                    offset: int, result_dir=None) -> dict:
    """Loads the parameters from the config file (prime,seed)"""
    with open(config_path, "r") as f:
        params = json.load(f)
        p, std_seed = params["%s" % num_bits]
    curve_seed = seed_update(std_seed, offset, standard)
    while total_count > 0:
        c = total_count if total_count < count else count
        f = get_file_name([c, ZZ(p).nbits(), curve_seed], result_dir)
        yield {"count": count, "prime": p, "seed": curve_seed, "outfile": f, "cofactor": cofactor, 'std_seed': std_seed}
        total_count -= count
        curve_seed = seed_update(curve_seed, count, standard)


def check_config_file(config_file, bits):
    """Checks the config file if suitable parameters are present"""
    with open(config_file, "r") as f:
        params = json.load(f)
    if not str(bits) in params:
        new_bits = list(params.keys())[0]
        print(f"Bit-size {str(bits)} is not in {config_file}! Taking {new_bits} instead.")
        return new_bits
    return bits


def main():
    parser = argparse.ArgumentParser(description="Are you in a dire need of some standardized curves? Use DiSSECT-gen!")
    parser.add_argument('standard', help='which standard do you want to simulate')
    parser.add_argument("--tasks", type=int, default=10, help="Number of tasks to run in parallel")
    parser.add_argument("-i", "--interpreter", default="python3", help="Sage or python?")
    parser.add_argument("-c", "--count", type=int, default=16, help="")
    parser.add_argument("-t", "--total_count", dest="total_count", type=int, default=32, help="")
    parser.add_argument("-b", "--bits", type=int, default=0, help="")
    parser.add_argument('-u', '--cofactor', type=int, default=0, help="If equal to 1, the cofactor is forced to 1")
    parser.add_argument("-o", "--offset", type=int, default=0, help="")
    parser.add_argument("-p", "--config_path", default=None, help="")
    parser.add_argument("-r", "--result_dir", default='results', help="Where to store experiment results")
    args = parser.parse_args()
    print(args)

    standard = args.standard
    config_path = args.config_path
    if config_path is None:
        config_path = os.path.join('standards', 'parameters', f"parameters_{standard}.json")
    bits = check_config_file(config_path, args.bits)
    result_dir = os.path.join(args.result_dir, standard, str(bits))
    os.makedirs(result_dir, exist_ok=True)
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    wrapper_path = os.path.join(script_path, 'standards', f'{standard}_wrapper.py')

    pr = ParallelRunner()
    pr.parallel_tasks = args.tasks

    def feeder():
        """Generates computing jobs"""
        for p in load_parameters(args.standard, config_path, bits, args.cofactor, args.total_count, args.count,
                                 args.offset, result_dir):
            cli = " ".join(["--%s=%s" % (k, p[k]) for k in p.keys()])
            yield Task(args.interpreter, "%s %s" % (wrapper_path, cli))

    def prerun(j: Task):
        """Function executed just after the Task is taken out from the queue and before executing by a worker."""
        logger.info("Going to start task %s" % (j.idx,))

    def on_finished(r: TaskResult):
        """Called when task completes with log info"""
        logger.info("Task %s finished, code: %s, fails: %s" % (r.job.idx, r.ret_code, r.job.failed_attempts))
        if r.ret_code != 0 and r.job.failed_attempts < 3:
            pr.enqueue(r.job)

    pr.job_feeder = feeder
    pr.cb_job_prerun = prerun
    pr.cb_job_finished = on_finished
    pr.work()


if __name__ == "__main__":
    main()
