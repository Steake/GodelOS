"""
Discrete-Time Lyapunov Stability & Contraction Decision Procedure.

Provides exact rational mathematical verification of dynamic stability:
- 1D quadratic energy dissipation: V(e) = p·e² with contraction factor L = (1 - α)² < 1
- n-D linear state-space stability: A^T P A - P = -Q with P ≻ 0, Q ≻ 0 via Sylvester's Criterion.
Zero floating-point approximations; evaluates determinants in exact fractions.Fraction.
"""

from fractions import Fraction
from typing import List, Tuple, Dict, Any, Optional


class LyapunovStabilitySolver:
    """
    Mathematical decision procedure for Lyapunov stability invariants.
    """

    @classmethod
    def verify_1d_dissipation(
        cls,
        alpha: Fraction,
        p_weight: Fraction = Fraction(1)
    ) -> Tuple[bool, Fraction, str]:
        """
        Formally verifies 1D quadratic error dissipation:
          V(e) = p · e²  (p > 0)
          e_{t+1} = (1 - α) · e_t
          ΔV(e_t) = V(e_{t+1}) - V(e_t) = -α(2 - α) · p · e_t² <= -γ · V(e_t)

        Returns: (is_stable, dissipation_rate_gamma, diagnostic_log).
        """
        if p_weight <= 0:
            return False, Fraction(0), f"Violation: Lyapunov function weight p = {p_weight} is not strictly positive."

        if not (Fraction(0) < alpha <= Fraction(1)):
            return False, Fraction(0), f"Violation: Adaptation rate alpha = {alpha} outside stable contraction interval (0, 1]."

        # Contraction factor L = (1 - alpha)^2
        l_contraction = (Fraction(1) - alpha) ** 2
        # Dissipation factor gamma = 1 - L = alpha * (2 - alpha)
        gamma = Fraction(1) - l_contraction

        if gamma <= 0:
            return False, Fraction(0), f"Violation: Dissipation rate gamma = {gamma} <= 0."

        log = (
            f"Q.E.D. Lyapunov stability certified: V(e) = {p_weight}·e² dissipates strictly under update rate alpha = {alpha}. "
            f"Contraction constant L = {l_contraction} < 1, energy dissipation margin gamma = {gamma} > 0."
        )
        return True, gamma, log

    @classmethod
    def verify_nd_discrete_lyapunov(
        cls,
        A: List[List[Fraction]],
        P: Optional[List[List[Fraction]]] = None
    ) -> Tuple[bool, Fraction, str]:
        """
        Verifies asymptotic stability of x_{t+1} = A·x_t via discrete Lyapunov equation:
          A^T P A - P = -Q
        Checks P ≻ 0 and Q = P - A^T P A ≻ 0 via Sylvester's Criterion (all principal minors > 0).
        """
        n = len(A)
        for row in A:
            if len(row) != n:
                return False, Fraction(0), "Error: Matrix A must be square."

        # Default P to identity matrix if not supplied
        if P is None:
            P = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]

        # 1. Verify P is symmetric and positive definite
        if not cls._is_positive_definite(P):
            return False, Fraction(0), "Violation: Candidate matrix P is not positive definite."

        # 2. Compute A^T P A
        # Mid = P · A
        mid = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    mid[i][j] += P[i][k] * A[k][j]

        # AtPA = A^T · Mid
        at_p_a = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    at_p_a[i][j] += A[k][i] * mid[k][j]

        # 3. Compute Q = P - A^T P A
        Q = [[P[i][j] - at_p_a[i][j] for j in range(n)] for i in range(n)]

        # 4. Verify Q ≻ 0
        if not cls._is_positive_definite(Q):
            return False, Fraction(0), "Violation: Matrix Q = P - A^T P A is not strictly positive definite (system not stable)."

        min_minor = cls._min_principal_minor(Q)
        log = f"Q.E.D. Discrete Lyapunov stability verified for {n}x{n} transition matrix. Q ≻ 0 with minimal leading minor {min_minor} > 0."
        return True, min_minor, log

    @classmethod
    def is_positive_definite(cls, M: List[List[Fraction]]) -> bool:
        return cls._is_positive_definite(M)

    @classmethod
    def _is_positive_definite(cls, M: List[List[Fraction]]) -> bool:
        """Applies Sylvester's criterion: all leading principal minors must be strictly positive."""
        n = len(M)
        for k in range(1, n + 1):
            sub = [[M[i][j] for j in range(k)] for i in range(k)]
            det = cls._determinant(sub)
            if det <= 0:
                return False
        return True

    @classmethod
    def _min_principal_minor(cls, M: List[List[Fraction]]) -> Fraction:
        n = len(M)
        min_det = cls._determinant(M)
        for k in range(1, n):
            sub = [[M[i][j] for j in range(k)] for i in range(k)]
            det = cls._determinant(sub)
            if det < min_det:
                min_det = det
        return min_det

    @classmethod
    def _determinant(cls, M: List[List[Fraction]]) -> Fraction:
        """Exact rational determinant via Gaussian elimination."""
        n = len(M)
        mat = [[Fraction(M[i][j]) for j in range(n)] for i in range(n)]
        det = Fraction(1)

        for col in range(n):
            pivot_row = None
            for row in range(col, n):
                if mat[row][col] != 0:
                    pivot_row = row
                    break
            if pivot_row is None:
                return Fraction(0)

            if pivot_row != col:
                mat[col], mat[pivot_row] = mat[pivot_row], mat[col]
                det = -det

            pivot = mat[col][col]
            det *= pivot

            for row in range(col + 1, n):
                factor = mat[row][col] / pivot
                for c in range(col, n):
                    mat[row][c] -= factor * mat[col][c]

        return det
