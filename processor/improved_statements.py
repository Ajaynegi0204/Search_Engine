import psycopg2
import os
import logging
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = 500
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


DSA_SYNONYMS = {
    "dp": ["dynamic programming", "memoization", "tabulation", "recursion with cache", "recurrence relation", "dp formula"],
    "tree dp": ["dp on tree", "dfs dp", "subtree dp"],
    "digit dp": ["dp on digits", "number dp"],
    "graph": ["graphs", "adjacency list", "adjacency matrix", "nodes and edges", "edges", "nodes", "vertices", "vertex"],
    "bfs": ["breadth first search", "level order", "queue based traversal", "shortest path unweighted"],
    "dfs": ["depth first search", "recursive graph traversal", "stack based traversal"],
    "binary search": ["logarithmic search", "bs", "search in sorted", "parametric search"],
    "binary search on answer": ["parametric search", "search on value space"],
    "ternary search": ["trisection search", "unimodal search"],
    "two pointers": ["sliding window", "double pointer", "dual pointer", "window technique", "range based pointers"],
    "sliding window": ["window technique", "range based pointers"],
    "segment tree": ["range tree", "range query tree", "lazy tree", "rmq"],
    "fenwick tree": ["binary indexed tree", "bit", "prefix sum tree"],
    "heap": ["priority queue", "min heap", "max heap"],
    "stack": ["last in first out", "lifo"],
    "queue": ["first in first out", "fifo"],
    "deque": ["double ended queue", "two sided queue"],
    "greedy": ["greedy algorithm", "locally optimal", "greedy approach", "choose best at each step"],
    "recursion": ["recursive", "base case", "call stack"],
    "backtracking": ["backtrack", "dfs with undo", "state restoration"],
    "bitmask": ["bitmasks", "binary states", "masking", "bit manipulation"],
    "bit manipulation": ["bit tricks", "bitwise operations", "masking"],
    "prefix sum": ["cumulative sum", "running sum"],
    "math": ["mathematics", "modulo", "modular arithmetic", "divisibility", "gcd", "lcm", "number properties"],
    "number theory": ["modular inverse", "fermat", "modulo math", "totient", "crt"],
    "combinatorics": ["nCr", "permutations", "factorials", "combinations", "binomial coefficient"],
    "string": ["strings", "substring", "pattern matching", "palindrome", "text processing"],
    "hashing": ["string hashing", "rolling hash", "hash functions"],
    "prefix function": ["pi array", "kmp prefix"],
    "z algorithm": ["z function", "z array"],
    "trie": ["prefix tree", "dictionary tree", "digital tree", "trie structure", "autocomplete"],
    "dsu": ["disjoint set union", "union find", "merge find", "disjoint set"],
    "toposort": ["topological sort", "dag sorting"],
    "shortest path": ["dijkstra", "bellman ford", "floyd warshall", "shortest distance", "minimum path"],
    "mst": ["minimum spanning tree", "kruskal", "prim"],
    "tree": ["binary tree", "n-ary tree", "dfs tree", "hierarchical structure"],
    "binary tree": ["btree", "inorder", "preorder", "postorder"],
    "lca": ["lowest common ancestor", "binary lifting"],
    "articulation points": ["cut vertices", "bridge finding"],
    "bridges": ["cut edges", "bridge finding in graph"],
    "scc": ["strongly connected components", "kosaraju", "tarjan"],
    "constructive algorithms": ["constructive", "building answer", "stepwise build"],
    "interactive": ["interactive problem", "querying the judge", "standard input output", "respond to judge"],
    "fft": ["fast fourier transform", "polynomial multiplication", "convolution", "fft in cp"],
    "ntt": ["number theoretic transform", "modulo fft"],
    "flows": ["maximum flow", "min cut", "ford fulkerson", "edmonds karp", "network flow"],
    "geometry": ["computational geometry", "2d geometry", "3d geometry", "convex hull", "point location", "cross product", "angle sorting"],
    "convex hull": ["graham scan", "monotone chain", "envelope"],
    "game theory": ["games", "nim", "grundy", "sprague grundy", "zero sum game"],
    "2-sat": ["two satisfiability", "implication graph"],
    "brute force": ["complete search", "all cases", "try everything", "naive solution"],
    "meet in the middle": ["mitm", "split and combine", "divide brute force"],
    "matrix exponentiation": ["fast matrix power", "matrix pow"],
    "monotonic stack": ["next greater element", "nge", "increasing stack", "decreasing stack"],
    "monotonic queue": ["sliding window max", "queue optimization"],
    "monotone queue optimization": ["dp optimization", "queue trick"],
    "bitset": ["bit array", "fixed length bits", "c++ bitset"],
    "probability": ["expected value", "expected outcome", "probabilistic approach"],
    "line sweep": ["sweep line", "event sorting"],
    "offline queries": ["query sorting", "mo's algorithm"],
    "online queries": ["real-time query handling", "stream queries"],
    "mo's algorithm": ["sqrt decomposition", "query reordering"],
    "suffix array": ["suffix sorting", "string matching"],
    "suffix tree": ["compressed trie", "text indexing"],
    "tries": ["prefix tree", "autocomplete", "digital trie"],
    "burnside": ["group counting", "polya enumeration theorem"],
    "knapsack": ["dp knapsack", "subset sum", "bounded knapsack", "0/1 knapsack"],
    "map": ["hash map", "unordered map", "dictionary"],
    "set": ["unordered set", "hash set"],
    "simulation": ["simulate", "step by step", "mimic behavior", "manual process"],
    "recurrence": ["recurrence relation", "dp formula"],
    "subset": ["combination of elements", "subset sum"],
    "subsequence": ["non-contiguous sequence"],
    "matrix": ["2d array", "grid", "table"],
    "grid": ["matrix", "board", "cells"]
}

FLATTENED_SYNONYMS = {}
for key, synonyms in DSA_SYNONYMS.items():
    for phrase in synonyms:
        FLATTENED_SYNONYMS[phrase.lower()] = key.lower()


def connect_db():
    return psycopg2.connect(
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("dbname")
    )


def add_synonyms_to_text(text):
    if not text:
        return text

    text_lower = text.lower()
    added = set()

    for synonym, canonical in FLATTENED_SYNONYMS.items():
        if synonym in text_lower and canonical not in text_lower:
            added.add(canonical)

    return text + " " + " ".join(added)


def expand_problem_statements():
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT id, problem_statement FROM problems")
        all_rows = cur.fetchall()
        logging.info(f"Fetched {len(all_rows)} rows")

        updates = []
        for idx, (pid, statement) in enumerate(all_rows):
            updated_statement = add_synonyms_to_text(statement)

            if len(updates) == BATCH_SIZE or idx == len(all_rows) - 1:
                cur.executemany("UPDATE problems SET problem_statement = %s WHERE id = %s", updates)
                conn.commit()
                logging.info(f"Updated batch of {len(updates)} rows")
                updates = []

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    expand_problem_statements()


