import numpy as np
from mpi4py.MPI import Comm, COMM_WORLD
from typing import Optional


class MyObject():
    def __init__(self):
        self.name = "TestObject"


def sync_check(comm: Comm=COMM_WORLD, msg: str= "", abort: bool=False) -> None:
    """
    Prints a synchronization message with the MPI rank, flushes stdout,
    and applies a strong MPI barrier.

    Parameters
    ----------
    comm : MPI.Comm
        The MPI communicator to synchronize across.
    msg : str
        The message to print before the barrier.
    abort : bool
        If True it stops the execution.
    """
    comm.Barrier()
    print(f"[Rank {comm.Get_rank()}] {msg}", flush=True)
    comm.Barrier()

    check_bcast(comm, msg=msg)

    if abort:
        print(f"[Rank {comm.Get_rank()}] ABORTING {msg}", flush=True)
        comm.Abort(1)

    return None

def check_bcast(comm: Comm=COMM_WORLD, msg=""):

    if comm.Get_rank() == 0:
        a = MyObject()
    else:
        a = None
    a = comm.bcast(a, root=0)
    if not isinstance(a, MyObject):
        print(f"FAIL {msg}: Received object {a}", flush=True)
        comm.Abort(1)
    return True
