"""
Stratified Function-Free Datalog Decision Engine.

Provides sound deductive reasoning with PTIME data complexity:
- Safety verification (head variables must occur in positive body literals)
- Stratification verification (no recursion through negation)
- Stratified semi-naïve fixpoint evaluation computing the unique minimal Herbrand model.
"""

import re
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict


class Atom:
    """Relational atom: Predicate(t_1, ..., t_k)."""
    def __init__(self, pred: str, terms: Tuple[str, ...], negated: bool = False):
        self.pred = pred
        self.terms = terms
        self.negated = negated

    def is_ground(self) -> bool:
        """Ground atoms contain only constants (lowercase or numeric), not uppercase variables."""
        return all(not t[0].isupper() for t in self.terms if t)

    def __repr__(self):
        prefix = "¬" if self.negated else ""
        return f"{prefix}{self.pred}({', '.join(self.terms)})"

    def __eq__(self, other):
        return (
            isinstance(other, Atom)
            and self.pred == other.pred
            and self.terms == other.terms
            and self.negated == other.negated
        )

    def __hash__(self):
        return hash((self.pred, self.terms, self.negated))


class Rule:
    """Datalog rule: Head :- Body_1, ..., Body_n."""
    def __init__(self, head: Atom, body: List[Atom]):
        self.head = head
        self.body = body

    def is_safe(self) -> bool:
        """
        Safety check: Every variable appearing in the head or in a negated body literal
        must appear in at least one positive relational body literal.
        """
        positive_vars: Set[str] = set()
        for b in self.body:
            if not b.negated:
                positive_vars.update(t for t in b.terms if t and t[0].isupper())

        head_vars = set(t for t in self.head.terms if t and t[0].isupper())
        if not head_vars.issubset(positive_vars):
            return False

        for b in self.body:
            if b.negated:
                neg_vars = set(t for t in b.terms if t and t[0].isupper())
                if not neg_vars.issubset(positive_vars):
                    return False

        return True

    def __repr__(self):
        body_str = ", ".join(repr(b) for b in self.body)
        return f"{self.head} :- {body_str}."


class DatalogProgram:
    """Collection of EDB facts and IDB rules."""
    def __init__(self, facts: Optional[Set[Atom]] = None, rules: Optional[List[Rule]] = None):
        self.facts: Set[Atom] = facts or set()
        self.rules: List[Rule] = rules or []

    def add_fact(self, pred: str, *terms: str):
        self.facts.add(Atom(pred, tuple(terms), negated=False))

    def add_rule(self, head: Atom, body: List[Atom]):
        self.rules.append(Rule(head, body))


class StratifiedDatalogSolver:
    """
    Executes stratification checking and fixpoint evaluation.
    """

    @classmethod
    def parse_atom(cls, s: str) -> Atom:
        """Parses atom like '¬Pred(a, B)' or 'Pred(a, B)'."""
        s = s.strip()
        negated = False
        if s.startswith("¬") or s.startswith("~") or s.startswith("not "):
            negated = True
            s = re.sub(r"^(?:¬|~|not\s+)", "", s).strip()
        m = re.match(r"^([A-Za-z0-9_]+)\s*\((.*?)\)$", s)
        if not m:
            pred = s.rstrip(".")
            return Atom(pred, (), negated=negated)
        pred = m.group(1)
        raw_terms = m.group(2).strip()
        terms = tuple(t.strip() for t in raw_terms.split(",")) if raw_terms else ()
        return Atom(pred, terms, negated=negated)

    @classmethod
    def parse_rule(cls, s: str) -> Rule:
        """Parses Datalog rule like 'Head(X, Y) :- Body1(X), Body2(Y)'."""
        s = s.rstrip(".").strip()
        if ":-" not in s:
            head = cls.parse_atom(s)
            return Rule(head, [])
        parts = s.split(":-")
        head = cls.parse_atom(parts[0].strip())
        body_str = parts[1].strip()
        raw_body_lits = [lit.strip() for lit in re.split(r",\s*(?![^()]*\))", body_str) if lit.strip()]
        body = [cls.parse_atom(lit) for lit in raw_body_lits]
        return Rule(head, body)

    @classmethod
    def check_stratification(cls, rules: List[Rule]) -> Tuple[bool, Dict[str, int], str]:
        """
        Verifies that rules are stratified (no cycle contains a negative edge).
        Returns: (is_stratified, stratum_map, diagnostic_msg).
        """
        predicates: Set[str] = set()
        for r in rules:
            predicates.add(r.head.pred)
            for b in r.body:
                predicates.add(b.pred)

        adj: Dict[str, List[Tuple[str, bool]]] = defaultdict(list)
        for r in rules:
            for b in r.body:
                adj[b.pred].append((r.head.pred, b.negated))

        for idx, r in enumerate(rules):
            if not r.is_safe():
                return False, {}, f"Safety error: Rule {idx} ({r}) contains unsafe variables."

        strata = {p: 0 for p in predicates}
        num_preds = len(predicates)

        for _ in range(num_preds + 1):
            changed = False
            for r in rules:
                head_p = r.head.pred
                for b in r.body:
                    body_p = b.pred
                    req = strata[body_p] + (1 if b.negated else 0)
                    if strata[head_p] < req:
                        strata[head_p] = req
                        changed = True
            if not changed:
                break
        else:
            return False, {}, "Stratification violation: Negative recursion cycle detected in Datalog dependency graph."

        return True, strata, "Program is safe and stratified."

    @classmethod
    def evaluate_fixpoint(cls, program: DatalogProgram) -> Set[Tuple[str, Tuple[str, ...]]]:
        """
        Executes stratified fixpoint evaluation to compute minimal Herbrand model.
        """
        strat_ok, strata, msg = cls.check_stratification(program.rules)
        if not strat_ok:
            raise ValueError(f"Datalog evaluation aborted: {msg}")

        model: Set[Tuple[str, Tuple[str, ...]]] = set(
            (f.pred, f.terms) for f in program.facts if not f.negated
        )

        max_stratum = max(strata.values()) if strata else 0

        for s in range(max_stratum + 1):
            stratum_rules = [r for r in program.rules if strata.get(r.head.pred, 0) == s]
            changed = True
            while changed:
                new_derivations = set()
                for rule in stratum_rules:
                    matches = cls._match_rule(rule, model)
                    for derived_atom in matches:
                        tup = (derived_atom.pred, derived_atom.terms)
                        if tup not in model:
                            new_derivations.add(tup)
                if not new_derivations:
                    changed = False
                else:
                    model.update(new_derivations)

        return model

    @classmethod
    def _match_rule(
        cls,
        rule: Rule,
        current_model: Set[Tuple[str, Tuple[str, ...]]]
    ) -> List[Atom]:
        derived = []

        def match_body(lit_idx: int, current_subst: Dict[str, str]):
            if lit_idx == len(rule.body):
                head_terms = []
                for t in rule.head.terms:
                    if t and t[0].isupper():
                        head_terms.append(current_subst.get(t, t))
                    else:
                        head_terms.append(t)
                derived.append(Atom(rule.head.pred, tuple(head_terms)))
                return

            lit = rule.body[lit_idx]
            if not lit.negated:
                for (p, terms) in current_model:
                    if p != lit.pred or len(terms) != len(lit.terms):
                        continue
                    new_subst = dict(current_subst)
                    can_bind = True
                    for lit_term, fact_term in zip(lit.terms, terms):
                        if lit_term and lit_term[0].isupper():
                            if lit_term in new_subst:
                                if new_subst[lit_term] != fact_term:
                                    can_bind = False
                                    break
                            else:
                                new_subst[lit_term] = fact_term
                        else:
                            if lit_term != fact_term:
                                can_bind = False
                                break
                    if can_bind:
                        match_body(lit_idx + 1, new_subst)
            else:
                ground_terms = []
                for t in lit.terms:
                    if t and t[0].isupper():
                        ground_terms.append(current_subst.get(t, None))
                    else:
                        ground_terms.append(t)
                if all(g is not None for g in ground_terms):
                    if (lit.pred, tuple(ground_terms)) not in current_model:
                        match_body(lit_idx + 1, current_subst)

        match_body(0, {})
        return derived
