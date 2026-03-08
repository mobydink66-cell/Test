# ================================================
# SayedLeeSolver - الكود الأساسي (من تجربة 1,000,000 متغير)
# ================================================

import math
import numpy as np
import time
import random
import gc
from pysat.solvers import Glucose3

class SayedLeeSolver:
    def __init__(self, target_regularity=0.15, max_attempts=2, verbose=True):
        self.target_regularity = target_regularity
        self.max_attempts = max_attempts
        self.verbose = verbose
        self.start_time = time.time()

    def log(self, message):
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:6.2f}s] {message}")

    def sayed_k(self, o):
        return math.log(o) if o > 0 else 0.0

    def compute_regularity(self, clauses, num_vars):
        var_count = {i: 0 for i in range(1, num_vars+1)}
        for c in clauses:
            for lit in c:
                if abs(lit) <= num_vars:
                    var_count[abs(lit)] += 1
        k = [self.sayed_k(var_count[i]) for i in range(1, num_vars+1)]
        m = np.mean(k)
        return float('inf') if m == 0 else np.std(k)/m

    def find_imbalances(self, k_vals, th=0.2, top=0.5):
        m, s = np.mean(k_vals), np.std(k_vals)
        imb = []
        for i, k in enumerate(k_vals, 1):
            dev = abs(k - m) / (s + 0.01)
            if dev > th:
                imb.append((i, k, dev))
        imb.sort(key=lambda x: x[2], reverse=True)
        return imb[:max(1, int(len(imb)*top))]

    def transform_clauses(self, clauses, num_vars, imbalances):
        new_clauses = [list(c) for c in clauses]
        new_vars = num_vars
        added = 0
        for vi, kv, dev in imbalances:
            new_vars += 1
            added += 1
            new_clauses.append([new_vars, vi])
            new_clauses.append([new_vars, -vi])
            num_extra = min(int(kv*2), 3)
            for _ in range(num_extra):
                idx = random.randint(0, len(new_clauses)-1)
                if len(new_clauses[idx]) < 7:
                    new_clauses[idx].append(new_vars)
            if added % 10000 == 0 and self.verbose:
                self.log(f"      ... {added} vars added")
        if self.verbose:
            self.log(f"   ➕ total added: {added}")
        return new_clauses, new_vars

    def solve(self, clauses, num_vars, time_limit=600):
        self.start_time = time.time()
        self.log(f"{'='*60}")
        self.log(f"🧠 solving {num_vars} vars, {len(clauses)} clauses")
        self.log(f"{'='*60}")

        reg = self.compute_regularity(clauses, num_vars)
        self.log(f"📊 initial regularity: {reg:.4f}")

        cur_clauses, cur_vars = clauses, num_vars
        for attempt in range(self.max_attempts):
            if time.time() - self.start_time > time_limit:
                break
            reg = self.compute_regularity(cur_clauses, cur_vars)
            self.log(f"\n📈 attempt {attempt+1}: reg = {reg:.4f}")
            if reg <= self.target_regularity:
                self.log(f"   ✅ target achieved")
                break
            # حساب k_vals
            vc = {i: 0 for i in range(1, cur_vars+1)}
            for c in cur_clauses:
                for lit in c:
                    if abs(lit) <= cur_vars:
                        vc[abs(lit)] += 1
            k_vals = [self.sayed_k(vc[i]) for i in range(1, cur_vars+1)]
            imb = self.find_imbalances(k_vals)
            if not imb:
                self.log(f"   ⚠️ no imbalances")
                break
            self.log(f"   ⚖️ imbalances: {len(imb)}")
            cur_clauses, cur_vars = self.transform_clauses(cur_clauses, cur_vars, imb)
            gc.collect()

        self.log(f"\n🔍 solving optimized ({cur_vars} vars, {len(cur_clauses)} clauses)...")
        start_solve = time.time()
        solver = Glucose3()
        for clause in cur_clauses:
            solver.add_clause(clause)
        sat = solver.solve()
        solver.delete()
        elapsed_solve = time.time() - start_solve
        total_elapsed = time.time() - self.start_time

        final_reg = self.compute_regularity(cur_clauses, cur_vars)
        self.log(f"\n📊 final result:")
        self.log(f"   - success: {sat}")
        self.log(f"   - solve time: {elapsed_solve:.4f}s")
        self.log(f"   - total time: {total_elapsed:.4f}s")
        self.log(f"   - final reg: {final_reg:.4f}")
        self.log(f"   - final vars: {cur_vars}")
        self.log(f"   - final clauses: {len(cur_clauses)}")
        return sat
