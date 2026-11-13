"""The store is accessed from request threads and background-task threads; verify the lock
makes concurrent access safe (sqlite3 on a shared connection is not safe on its own)."""

import threading

from clawrxiv_clone.schema import Paper
from clawrxiv_clone.store import Store


def test_store_concurrent_access():
    store = Store()
    agent = store.register("concurrent-agent")
    errors: list[Exception] = []

    def worker(n: int) -> None:
        try:
            for i in range(20):
                pid = store.create_post(agent, Paper(title=f"p{n}-{i}", abstract="a"))
                store.get_post(pid)          # nested locks (get_post -> vote_tally)
                store.vote(pid, agent["id"], 1)
                store.list_posts(limit=5)
        except Exception as exc:  # noqa: BLE001 - we want to surface any thread error
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, errors
    assert len(store.list_posts(limit=1000)) == 8 * 20
