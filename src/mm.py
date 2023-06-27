import logging
import sys

import numpy as np
import tvm
import time
import os

from tvm import autotvm, te, testing

map_order = {
    0: "ijk", 1: "ikj", 2: "jik", 3: "jki", 4: "kij", 5: "kji"
}

def get_best_time(log, ms=True):
    import json

    best_avg, best_std, best_cfg = 9999.0, 0.0, ""
    f = open(log, "r")
    for line in f.readlines():
        data = json.loads(line)
        r = np.mean(data["result"][0])
        if (best_avg > r):
            best_avg = r
            best_std = np.std(data["result"][0])
            best_cfg = data["config"]["entity"]
    f.close()

    if ms: # convet to ms
        best_avg *= 1000
        best_std *= 1000
    return best_avg, best_std, best_cfg

def mm(N, L, M, dtype="float32"):
    A = te.placeholder((N, L), name="A", dtype=dtype)
    B = te.placeholder((L, M), name="B", dtype=dtype)
    
    k = te.reduce_axis((0, L), name="k")
    C = te.compute((N, M), lambda i, j: te.sum(A[i, k] * B[k, j], axis=k), name="C")

    return A, B, C

@autotvm.template("template_matmul")
def matmul(N, L, M, search_space, target="llvm", dtype="float"):
    A, B, C = mm(N, L, M, dtype)
    s = te.create_schedule(C.op)

    # schedule
    y, x = s[C].op.axis
    k = s[C].op.reduce_axis[0]

    # get the config object
    cfg = autotvm.get_config()

    # define search space
    cfg.define_knob("tile_i", search_space)
    cfg.define_knob("tile_j", search_space)
    cfg.define_knob("tile_k", search_space)      

    # schedule according to config
    x0, x1 = s[C].split(x, cfg["tile_i"].val)
    y0, y1 = s[C].split(y, cfg["tile_j"].val)
    k0, k1 = s[C].split(k, cfg["tile_k"].val)

    cfg.define_knob("order", [0, 1, 2, 3])

    if cfg["order"].val == 0: # "ijk"
        s[C].reorder(x0, x1, y0, y1, k0, k1)
    elif cfg["order"].val == 1: #" ikj"
        s[C].reorder(x0, x1, k0, k1, y0, y1)
    elif cfg["order"].val == 2: # "jik"
        s[C].reorder(y0, y1, x0, x1, k0, k1)
    elif cfg["order"].val == 3: # "jki"
        s[C].reorder(y0, y1, k0, k1, x0, x1)

    if target == "cuda":
        # Bind GPU thread indices
        s[C].bind(x0, te.thread_axis("blockIdx.x"))
        s[C].bind(y0, te.thread_axis("blockIdx.y"))
        s[C].bind(x1, te.thread_axis("threadIdx.x"))
        s[C].bind(y1, te.thread_axis("threadIdx.y"))

    return s, [A, B, C]

if __name__ == "__main__":

    N, L, M = 900, 800, 700
    search_space = [1] + [i for i in range(16,97,16)]

    if len(sys.argv) > 1:
        arch = sys.argv[1]
    else:
        print("Arch not found! Available: x86, arm, or cuda")
        exit(0)
    
    if arch == "x86" or arch == "x86-64":
        target = "llvm"
    elif arch == "cuda":
        target = "cuda"
    elif arch == "arm":
        target = "llvm -device=arm_cpu"
    
    dev = tvm.device(str(target), 0)

    np.random.seed(0)
    a_np = np.random.uniform(size=(N, L)).astype(np.float32)
    b_np = np.random.uniform(size=(L, M)).astype(np.float32)
    c_np = a_np.dot(b_np)

    tool = ["GridSearchTuner", "RandomTuner", "GATuner", "XGBTuner"]

    for t in tool:

        print("Executing model %s..." %(t))

        save_log = "results/%s_%s_mm.log" % (arch, t)

        if os.path.isfile(save_log):
            os.remove(save_log)

        with tvm.transform.PassContext(opt_level=3):
            task = autotvm.task.create("template_matmul", args=(N, L, M, search_space, target, "float32"), target=target)

        if target == "cuda":
            measure_option = autotvm.measure_option(builder="local", runner=autotvm.LocalRunner(number=2, repeat=5))
        else:
            measure_option = autotvm.measure_option(builder="local", runner=autotvm.LocalRunner(number=2, repeat=5, enable_cpu_cache_flush=True))

        start = time.time()
        with tvm.transform.PassContext(opt_level=3):
            n_trial = 10
            if t == "GridSearchTuner":
                tuner = autotvm.tuner.GridSearchTuner(task)
            elif t == "RandomTuner":
                tuner = autotvm.tuner.RandomTuner(task)
            elif t == "GATuner":
                tuner = autotvm.tuner.GATuner(task)
            elif t == "XGBTuner":
                tuner = autotvm.tuner.XGBTuner(task, loss_type="rank")

            try:
                tuner.tune(
                    n_trial=n_trial,
                    measure_option=measure_option,
                    callbacks=[autotvm.callback.log_to_file(save_log)],
                )
            except:
                continue
        end = time.time()

        # inspect the best config
        dispatch_context = autotvm.apply_history_best(save_log)
        best_config = dispatch_context.query(task.target, task.workload)

        # apply history best from log file
        with autotvm.apply_history_best(save_log):
            with tvm.transform.PassContext(opt_level=3):
                with tvm.target.Target('llvm'):
                    s, arg_bufs = matmul(N, L, M, search_space, target, "float32")
                    func = tvm.build(s, arg_bufs, target=target)

        # check correctness
        a_tvm = tvm.nd.array(a_np, device=dev)
        b_tvm = tvm.nd.array(b_np, device=dev)
        c_tvm = tvm.nd.empty(c_np.shape, device=dev)
        func(a_tvm, b_tvm, c_tvm)

        tvm.testing.assert_allclose(c_np, c_tvm.numpy(), rtol=1e-4)

        evaluator = func.time_evaluator(func.entry_name, dev, number=10, repeat=3)
        eval = evaluator(a_tvm, b_tvm, c_tvm)

        best_avg, best_std, best_cfg = get_best_time(save_log)

        f = open("results/results.csv", "a")
        f.write("%s,%.4f,%.4f,%.2f" % (t, eval.mean, eval.std, end-start))

        for i in range(len(best_cfg)):
            if i == len(best_cfg)-1:
                f.write(",%s" %(map_order[best_cfg[i][-1]]))
            else:
                f.write(",%s" % (best_cfg[i][-1]))
        f.write("\n")
        f.close()