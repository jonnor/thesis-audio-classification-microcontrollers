
import os.path
import sys

import numpy
import seaborn as sns
import matplotlib.pyplot as plt     

from . import common, urbansound8k

groups = {
    'social_activity': [ 'street_music', 'children_playing', 'dog_bark' ],
    'construction': [ 'drilling', 'jackhammer' ],
    'road_noise': [ 'engine_idling', 'car_horn', 'siren' ],
    'domestic_machines': [ 'air_conditioner' ],
    'danger': [ 'gun_shot' ],
}

def plot_confusion(cm, classnames, normalize=False, percent=False):

    fmt = '.2f'
    if normalize:
        cm = cm_normalize(cm)
    if percent:
        cm = cm_normalize(cm)*100
        fmt = ".1f"

    fig, ax = plt.subplots(1, figsize=(10,8))
    sns.heatmap(cm, annot=True, ax=ax, fmt=fmt);

    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title('Confusion Matrix') 
    ax.xaxis.set_ticklabels(classnames, rotation=60)
    ax.yaxis.set_ticklabels(classnames, rotation=0)
    return fig

def cm_normalize(cm):
    rel = cm.astype('float') / cm.sum(axis=1)[:, numpy.newaxis]
    return rel

def cm_class_accuracy(cm):
    rel = cm_normalize(cm)
    return numpy.diag(rel)

def cm_accuracy(cm):
    correct = numpy.sum(numpy.diag(cm))
    total = numpy.sum(numpy.sum(cm, axis=1))
    return correct/total

def grouped_confusion(cm, groups):
    groupnames = list(groups.keys())
    groupids = list(range(len(groupnames)))
    group_cm = numpy.zeros(shape=(len(groupids), len(groupids)))
    groupid_from_classid = {}
    for gid, name in zip(groupids, groupnames):
        classes = groups[name]
        for c in classes:
            cid = urbansound8k.classes[c]
            groupid_from_classid[cid] = gid

    for true_c in range(cm.shape[0]):
        for pred_c in range(cm.shape[1]):
            v = cm[true_c, pred_c]
            true_g = groupid_from_classid[true_c]
            pred_g = groupid_from_classid[pred_c]
            group_cm[true_g, pred_g] += v

    return group_cm, groupnames


def parse(args):

    import argparse

    parser = argparse.ArgumentParser(description='Test trained models')
    a = parser.add_argument

    common.add_arguments(parser)

    a('--out', dest='results_dir', default='./data/results',
        help='%(default)s')


    parsed = parser.parse_args(args)

    return parsed

def print_accuracies(accs, title):

    m = numpy.mean(accs)
    s = numpy.std(accs)
    print('{} | mean: {:.3f}, std: {:.3f}'.format(title, m, s))
    [ print("{:.3f}".format(v), end=',') for v in accs ]
    print('\n')

def main():

    args = parse(None)

    cm = numpy.load(os.path.join(args.results_dir, '{}'.format(args.experiment), 'confusion.npz'))
    val, test = cm['val'], cm['test']


    classnames = urbansound8k.classnames
    val_fig = plot_confusion(100*numpy.mean(val, axis=0), classnames, normalize=True)
    test_fig = plot_confusion(100*numpy.mean(test, axis=0), classnames, normalize=True) 
    val_fig.savefig('val.cm.png')
    test_fig.savefig('test.cm.png')

    c_acc = cm_class_accuracy(numpy.mean(val, axis=0))
    print_accuracies(c_acc, 'class_acc')

    folds_acc = [ cm_accuracy(val[f]) for f in range(0, len(val)) ]
    print_accuracies(folds_acc, 'val_acc')

    tests_acc = [ cm_accuracy(test[f]) for f in range(0, len(test)) ]
    print_accuracies(tests_acc, 'test_acc') 


    print('wrote')

if __name__ == '__main__':
    main()
