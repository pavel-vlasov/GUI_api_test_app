from core.secret_injector import SecretInjector, SecretLeakError


def test_inject_placeholder():
    s = SecretInjector({"<TOKEN>": "abc"})
    assert s.inject("curl -H 'Auth: <TOKEN>'") == "curl -H 'Auth: abc'"


def test_sanitize_detects_leak():
    s = SecretInjector({"<TOKEN>": "abc"})
    try:
        s.assert_sanitized("abc")
        assert False
    except SecretLeakError:
        assert True
