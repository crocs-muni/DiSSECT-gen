#!/usr/bin/env python3

import argparse
import json
import logging
import os
from dissectgen.job_manager.manager import ParallelRunner, Task, TaskResult
from dissectgen.standards.utils import seed_update

logger = logging.getLogger(__name__)


def get_file_name(params: list, result_dir=None) -> str:
    """Determines the file name of the results"""
    file_name = "%s.json" % ("_".join(map(str, params)),)
    return file_name if result_dir is None else os.path.join(result_dir, file_name)


def load_parameters(std: str, config_path: str, num_bits: int, attempts: int, tasks: int,
                    offset: int, result_dir=None) -> dict:
    """Loads the parameters from the config file (prime,seed)"""
    attempts_task = attempts // tasks + 1 * (attempts % tasks != 0)
    with open(config_path, "r") as f:
        params = json.load(f)
        try:
            p, initial_seed = params["%s" % num_bits]
        except ValueError:
            initial_seed = params["%s" % num_bits]
            p = 0
    curve_seed = seed_update(std, initial_seed, offset)
    while attempts > 0:
        a = attempts if attempts < attempts_task else attempts_task
        f = get_file_name([a, num_bits, curve_seed], result_dir)
        yield {"attempts": a, "prime": p, "seed": curve_seed, "outfile": f}
        attempts -= attempts_task

        curve_seed = seed_update(std, curve_seed, attempts)


def check_config_file(config_file, bits):
    """Checks the config file if suitable parameters are present"""
    with open(config_file, "r") as f:
        params = json.load(f)
    if not str(bits) in params:
        print(
            f"Bit-size {str(bits)} is not implemented. Edit {config_file} to extend the support. Currently supported "
            f"bit-sizes: {list(params.keys())}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="DiSSECT-gen is a tool for generating elliptic curves according to "
                                                 "popular standards or recommendations")
    parser.add_argument('standard', help='Choose a standard.')
    parser.add_argument("bits", type=int, help="Bit-size of the curve.")
    parser.add_argument("-a", "--attempts", type=int, default=1, help="Number of attempts to generate curves.")
    parser.add_argument("--tasks", type=int, default=1, help="Number of tasks to run in parallel.")
    parser.add_argument("--count", type=int, default=None, help="Number of curves to generate.")

    parser.add_argument('--cofactor_bound', type=int, default=None, help="Upper bound on the cofactor.")
    parser.add_argument("--cofactor_div", type=int, default=0,
                        help="Every prime divisor of the cofactor must divide this parameter.")

    parser.add_argument("--interpreter", default="python3", help="Sage or python?")

    parser.add_argument("-o", "--offset", type=int, default=0, help="")
    parser.add_argument("-p", "--config_path", default=None, help="")
    parser.add_argument("-r", "--results", default='results', help="Where to store experiment results")
    args = parser.parse_args()

    standard = args.standard
    config_path = args.config_path
    if config_path is None:
        config_path = os.path.join('standards', 'parameters', f"parameters_{standard}.json")
    if not check_config_file(config_path, args.bits):
        return
    result_dir = os.path.join(args.results, standard, str(args.bits))
    os.makedirs(result_dir, exist_ok=True)
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

    wrapper_name = f'{standard}_gen.py'
    wrapper_path = os.path.join(script_path, 'standards', wrapper_name)

    pr = ParallelRunner()
    pr.parallel_tasks = args.tasks

    def feeder():
        """Generates computing jobs"""
        for p in load_parameters(standard, config_path, args.bits, args.attempts, args.tasks, args.offset, result_dir):
            arguments = p
            if args.count is not None:
                arguments['count'] = args.count
            if args.cofactor_bound is not None:
                arguments['cofactor_bound'] = args.cofactor_bound
            arguments['cofactor_div'] = args.cofactor_div
            cli = " ".join(["--%s=%s" % (k, a) for k, a in arguments.items()])
            yield Task(args.interpreter, "%s %s" % (wrapper_path, cli))

    def prerun(j: Task):
        """Function executed just after the Task is taken out from the queue and before executing by a worker."""
        logger.info("Going to start task %s" % (j.idx,))

    def on_finished(r: TaskResult):
        """Called when task completes with log info"""
        logger.info("Task %s finished, code: %s, fails: %s" % (r.job.idx, r.ret_code, r.job.failed_attempts))
        if r.ret_code != 0 and r.job.failed_attempts < 3:
            pr.enqueue(r.job)
        if r.stderr != "":
            with open("error.txt", 'w') as f:
                f.write(r.stderr)

    pr.job_feeder = feeder
    pr.cb_job_prerun = prerun
    pr.cb_job_finished = on_finished
    pr.work()


if __name__ == "__main__":
    main()
