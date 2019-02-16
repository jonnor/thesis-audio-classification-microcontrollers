
import os.path
import math

import librosa
import numpy
import joblib

import urbansound8k

def feature_extract(y, sr, n_mels=32, n_fft=512, hop_length=256):
    mels = librosa.feature.melspectrogram(y, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length)
    log_mels = librosa.core.power_to_db(mels, top_db=80, ref=numpy.max)
    return log_mels
    
def silence_feature(bands, length):
    return numpy.full((bands, length), -0)
    
def test_silence_feature():
    sr = 16000
    mels = 32
    
    length = int(0.1*sr)
    silence = numpy.zeros(length) + numpy.random.normal(0.0, 1e-6, size=length)
    f = feature_extract(silence, sr, n_mels=mels)
    silent_f = silence_feature(mels, f.shape[1])
    numpy.testing.assert_equal(f, silent_f)


def feature_path(sample, out_folder):
    path = urbansound8k.sample_path(sample)
    tokens = path.split(os.sep)
    filename = tokens[-1]
    filename = filename.replace('.wav', '.npz')
    out_fold = os.path.join(out_folder, tokens[-2])
    return os.path.join(out_fold, filename)


def settings_id(settings, feature='feature'):
    keys = sorted(settings.keys())
    settings_str = ','.join([ "{}={}".format(k, str(settings[k])) for k in keys ])
    return feature + ':' + settings_str

def compute_mels(filepath, settings):
    y, sr = librosa.load(filepath, sr=settings['samplerate'])
    from librosa.feature import melspectrogram 
    mels = melspectrogram(y, sr=sr,
                         n_mels=settings['n_mels'],
                         n_fft=settings['n_fft'],
                         hop_length=settings['hop_length'],
                         fmin=settings['fmin'],
                         fmax=settings['fmax'])
    return mels

def precompute(samples, settings, out_dir, n_jobs=8, verbose=1, force=False):
    out_folder = os.path.join(out_dir, settings_id(settings, feature='mels'))
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    def compute(inp, outp):
        if os.path.exists(outp) and not force:
            return outp

        f = compute_mels(inp, settings)
        numpy.savez(outp, f)
        return outp
    
    def job_spec(sample):
        path = urbansound8k.sample_path(sample)
        out_path = feature_path(sample, out_folder)
        # ensure output folder exists
        f = os.path.split(out_path)[0]
        if not os.path.exists(f):
            os.makedirs(f)

        return path, out_path
        
    jobs = [joblib.delayed(compute)(*job_spec(sample)) for _, sample in samples.iterrows()]
    feature_files = joblib.Parallel(n_jobs=n_jobs, verbose=verbose)(jobs)


