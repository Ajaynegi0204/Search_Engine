import redis
import json
import math
from collections import defaultdict
from qdrant_client.models import PointStruct
from qdrant_client import QdrantClient
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DSA_SYNONYMS = {
    "dp": ["dynamic programming", "memoization", "tabulation", "recurrence relation",
           "dp formula"],
    "tree dp": ["dp on tree", "dfs dp", "subtree dp"],
    "digit dp": ["dp on digits", "number dp"],
    "graph": ["graphs", "adjacency list", "adjacency matrix", "nodes and edges", "edges", "nodes", "vertices",
              "vertex"],
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
    "trie": ["prefix tree", "dictionary tree", "digital tree", "tries structure", "autocomplete"],
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
    "geometry": ["computational geometry", "2d geometry", "3d geometry", "convex hull", "point location",
                 "cross product", "angle sorting"],
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

r = redis.Redis(
    host='redis-14042.crce179.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=14042,
    username="default",
    password="tXnxcUbI5bazp5R8mXtl9qFumLOLBMHA",
    decode_responses=True,
)

qdrant = QdrantClient(
    url=os.getenv("qdrant_url"),
    api_key=os.getenv("qdrant_apikey"),
    timeout=300.0
)

idf = json.loads(r.get("idf_json"))
vocab = json.loads(r.get("vocab_json"))
word2idx = {w: i for i, w in enumerate(vocab)}

def expand_query(query):
    original_words = query.lower().split()
    expanded_terms = set(original_words)

    for word in original_words:
        if word in DSA_SYNONYMS:
            expanded_terms.update(DSA_SYNONYMS[word])

    query_lower = query.lower()
    for canonical, synonyms in DSA_SYNONYMS.items():
        if canonical in query_lower:
            expanded_terms.update(synonyms)
            expanded_terms.add(canonical)

    for synonym, canonical in FLATTENED_SYNONYMS.items():
        if synonym in query_lower:
            expanded_terms.add(canonical)
            if canonical in DSA_SYNONYMS:
                expanded_terms.update(DSA_SYNONYMS[canonical])

    expanded_query = " ".join(expanded_terms)
    if len(expanded_terms) > len(original_words):
        print(f"Query expanded from: '{query}'", file=sys.stderr)
        print(f"To: '{expanded_query}'", file=sys.stderr)
        print("-" * 60, file=sys.stderr)

    return expanded_query


def tfidf_vector(text):
    count = defaultdict(int)
    for w in text.strip().split():
        count[w] += 1
    total = sum(count.values())
    vec = [0.0] * len(word2idx)
    for w, c in count.items():
        if w in word2idx:
            tf = c / total
            vec[word2idx[w]] = tf * idf.get(w, 0)
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm else vec

def search(query):
    expanded_query = expand_query(query)
    vec = tfidf_vector(expanded_query)

    response = qdrant.query_points(
        collection_name="problems_v2",
        query=vec,
        limit=100,
        with_payload={
            "include": ["problem_name", "problem_link", "platform"]
        }
    )

    results = []
    for point in response.points:
        payload = point.payload or {}
        results.append({
            "problem_name": payload.get("problem_name", "N/A"),
            "problem_link": payload.get("problem_link", "N/A"),
            "platform": payload.get("platform", "N/A")
        })

    return results

def main():
    raw_input = sys.stdin.read()
    try:
        data = json.loads(raw_input)
        query = data.get("query", "")
        results = search(query)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)

if __name__ == "__main__":
    main()
