import dgl
import dgl.sparse
import torch as th
from utils import th_op_time, get_graph

import argparse

n_cold_start = 2

def bench_spmm(g, ctx, binary_op, reduce_op):
    print("SPMM\n----------------------------")
    with th.no_grad():
        for n_hid in [1, 2, 4, 8, 16, 32, 64, 128]:
            try:
                nfeat = th.rand(g.number_of_src_nodes(), n_hid, device=ctx)
                efeat = th.rand(g.number_of_edges(), n_hid, device=ctx) if binary_op != 'copy_u' else None
                accum_time = 0
                for n_times in range(10):
                    with th_op_time() as timer:
                        dgl.sparse.gspmm(g, binary_op, reduce_op, nfeat, efeat)
                    if n_times >= n_cold_start:
                        accum_time += timer.time
                avg_time = accum_time / (n_times - n_cold_start)
                print('hidden size: {}, avg time: {}'.format(
                    n_hid, avg_time))
            except:
                print('hidden size: {}, OOM'.format(n_hid))

def bench_sddmm(g, ctx, op):
    print("SDDMM\n----------------------------")
    with th.no_grad():
        for n_hid in [1, 2, 4, 8, 16, 32, 64, 128]:
            try:
                ufeat = th.rand(g.number_of_src_nodes(), n_hid, device=ctx)
                vfeat = th.rand(g.number_of_dst_nodes(), n_hid, device=ctx)
                accum_time = 0
                for n_times in range(10):
                    with th_op_time() as timer:
                        dgl.sparse.gsddmm(g, op, ufeat, vfeat)
                    if n_times >= n_cold_start:
                        accum_time += timer.time
                avg_time = accum_time / (n_times - n_cold_start)
                print('hidden size: {}, avg time: {}'.format(
                    n_hid, avg_time))
            except:
                print('hidden size: {}, OOM'.format(n_hid))

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Benchmark DGL kernels")
    parser.add_argument('--spmm-binary', type=str, default='copy_u')
    parser.add_argument('--spmm-reduce', type=str, default='sum')
    parser.add_argument('--sddmm-binary', type=str, default='add')
    parser.add_argument('--gpu', '-g', type=str, default='-1')
    args = parser.parse_args()
    if args.gpu == '-1':
        ctx = th.device('cpu')
    else:
        ctx = th.device(int(args.gpu))

    for dataset in ['arxiv', 'proteins']:
        g = get_graph(dataset)
        print(g)
        # SPMM
        bench_spmm(g, ctx, args.spmm_binary, args.spmm_reduce)
        # SDDMM
        bench_sddmm(g, ctx, args.sddmm_binary)
