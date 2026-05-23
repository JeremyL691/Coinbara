from coinbara.flip_engine import FlipEngine


def test_choose_result_returns_valid_side() -> None:
    engine = FlipEngine()

    results = {engine.choose_result() for _ in range(200)}

    assert results <= {"heads", "tails"}
    assert results


def test_begin_flip_locks_until_finished() -> None:
    engine = FlipEngine()

    first = engine.begin_flip()
    second = engine.begin_flip()

    assert first in {"heads", "tails"}
    assert second is None

    engine.finish_flip(first)  # type: ignore[arg-type]

    assert engine.is_flipping is False
    assert len(engine.history) == 1


def test_history_is_limited_and_resettable() -> None:
    engine = FlipEngine(history_limit=3)

    for side in ["heads", "tails", "heads", "tails"]:
        engine.finish_flip(side)  # type: ignore[arg-type]

    assert engine.history == ["tails", "heads", "tails"]
    assert engine.heads_count == 2
    assert engine.tails_count == 2

    engine.reset()

    assert engine.history == []
    assert engine.heads_count == 0
    assert engine.tails_count == 0
