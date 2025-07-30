import fast_align_audio
import numpy as np
import numpy_audio_limiter


def test_mono():
    x = np.random.randn(1800).astype(np.float32)
    y = numpy_audio_limiter.limit(
        signal=x.reshape((1, -1)),
        attack_coeff=0.99,
        release_coeff=0.99,
        delay=527,
        threshold=0.5,
    )
    assert y.shape == (1, 1800)

    offset, corr = fast_align_audio.find_best_alignment_offset(
        reference_signal=x,
        delayed_signal=y[0],
        max_offset_samples=1200,
        method="corr"
    )
    assert corr >= 0.7
    assert offset == 0


def test_stereo():
    x = np.random.randn(1800).astype(np.float32).reshape((2, 900))
    y = numpy_audio_limiter.limit(
        signal=x,
        attack_coeff=0.99,
        release_coeff=0.99,
        delay=527,
        threshold=0.5,
    )
    assert y.shape == (2, 900)

    offset, corr = fast_align_audio.find_best_alignment_offset(
        reference_signal=x[0],
        delayed_signal=y[0],
        max_offset_samples=600,
        method="corr"
    )

    assert corr >= 0.7
    assert offset == 0
