
import os.path
import shutil

import preprocess
import urbansound8k

def test_precompute():

    settings = dict(
        samplerate=16000,
        n_mels=32,
        fmin=0,
        fmax=8000,
        n_fft=512,
        hop_length=256,
    )

    dir = './pre2'
    if os.path.exists(dir):
        shutil.rmtree(dir)

    data = urbansound8k.load_dataset()

    d = os.path.join(dir, preprocess.settings_id(settings, feature='mels'))
    expect_path = preprocess.feature_path(data.iloc[0], d)    
    assert not os.path.exists(expect_path), expect_path

    preprocess.precompute(data[0:4], settings, out_dir=dir, verbose=0, force=True, n_jobs=2)

    assert os.path.exists(expect_path), expect_path
    