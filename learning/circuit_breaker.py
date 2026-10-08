import threading
import time


class CircuitBreaker:
    """Circuit breaker simples e seguro para uso concorrente.

    Estados possíveis:
    - CLOSED (fechado): operação normal; chamadas passam.
    - OPEN (aberto): após `failure_threshold` falhas consecutivas, bloqueia
      novas chamadas por `recovery_timeout` segundos (fail-fast, sem tocar na rede).
    - HALF_OPEN (meio-aberto): passado o `recovery_timeout`, libera uma tentativa
      de teste. Sucesso volta para CLOSED; falha reabre o circuito.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = self.CLOSED
        self._failure_count = 0
        self._opened_at = 0.0
        self._lock = threading.Lock()

    def state(self) -> str:
        with self._lock:
            return self._resolve_state_locked()

    def _resolve_state_locked(self) -> str:
        if (
            self._state == self.OPEN
            and (time.monotonic() - self._opened_at) >= self.recovery_timeout
        ):
            self._state = self.HALF_OPEN
        return self._state

    def allow_request(self) -> bool:
        with self._lock:
            return self._resolve_state_locked() != self.OPEN

    def record_success(self) -> None:
        with self._lock:
            self._state = self.CLOSED
            self._failure_count = 0
            self._opened_at = 0.0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            if (
                self._state == self.HALF_OPEN
                or self._failure_count >= self.failure_threshold
            ):
                self._state = self.OPEN
                self._opened_at = time.monotonic()

    def reset(self) -> None:
        with self._lock:
            self._state = self.CLOSED
            self._failure_count = 0
            self._opened_at = 0.0
