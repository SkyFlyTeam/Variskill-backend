import time

import pytest

from learning.circuit_breaker import CircuitBreaker

pytestmark = pytest.mark.unit


def test_permanece_fechado_ate_atingir_threshold():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state() == CircuitBreaker.CLOSED
    assert breaker.allow_request() is True


def test_abre_apos_threshold_e_faz_fail_fast():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
    for _ in range(3):
        breaker.record_failure()
    assert breaker.state() == CircuitBreaker.OPEN
    assert breaker.allow_request() is False


def test_meio_aberto_apos_recovery_timeout():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
    breaker.record_failure()
    assert breaker.allow_request() is False
    time.sleep(0.06)
    assert breaker.allow_request() is True
    assert breaker.state() == CircuitBreaker.HALF_OPEN


def test_sucesso_fecha_o_circuito():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=30.0)
    breaker.record_failure()
    assert breaker.allow_request() is False
    breaker.record_success()
    assert breaker.state() == CircuitBreaker.CLOSED
    assert breaker.allow_request() is True


def test_falha_em_meio_aberto_reabre():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
    breaker.record_failure()
    time.sleep(0.06)
    assert breaker.allow_request() is True
    breaker.record_failure()
    assert breaker.state() == CircuitBreaker.OPEN
