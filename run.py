#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import CBOW, Vocab, SkipGram
import codecs
import numpy as np
import argparse
def load_data(data_file, data_type = 'cbow'):
    x_full = []
    y_full = []
    with codecs.open(data_file, 'r', 'utf-8') as _file:
        for line in _file:
            if data_type == 'cbow':
                int_line = [int(i) for i in line.strip().split()]
                x_full.append(int_line[:-1])
                y_full.append(int_line[-1])
            elif data_type == 'sg':
                int_line = [int(i) for i in line.strip().split()]
                x_full.append(int_line[0])
                y_full.append(int_line[1])
            else:
                raise BaseException("unknown data_type" + data_type)
    return np.asarray(x_full), np.asarray(y_full)


if __name__ == '__main__':
    opt= argparse.ArgumentParser(description="write program description here")
    #insert options here
    opt.add_argument('-v', action='store', dest='vocab_file', required = True)
    opt.add_argument('-s', action='store', dest='save_path', required = False, default = None)
    opt.add_argument('-t', action='store', dest='training_data', required = True)
    opt.add_argument('-d', action='store', dest='dev_data', default = None, required = False)
    opt.add_argument('-e', action='store', dest='embed_size', type = int, required = True)
    opt.add_argument('--bs', action='store', dest='batch_size', default = 512, type = int)
    opt.add_argument('--epochs', action='store', dest='epochs', default = 10, type = int)
    opt.add_argument('-m', action='store', dest='model', help='cbow or sg', choices = ['cbow', 'sg'], required = False, default = 'cbow')
    opt.add_argument('-o', action='store', dest='optimizer', help='optimizer to use', choices = ['sgd', 'sgd_clipped', 'rms', 'rms_clipped'], required = False, default = 'rms')
    options = opt.parse_args()
    print options
    vocab = Vocab(options.vocab_file)
    X_full, Y_full = load_data(options.training_data, options.model)
    if options.dev_data is None:
        t_idx = np.arange(X_full.shape[0])
        np.random.shuffle(t_idx)
        d_idx = t_idx[:int(0.1 * t_idx.shape[0])]
        t_idx = t_idx[int(0.1 * t_idx.shape[0]):]
        if options.model == 'cbow':
            X_dev = X_full[d_idx,:]
            Y_dev = Y_full[d_idx]
            X_full = X_full[t_idx,:]
            Y_full = Y_full[t_idx]
        elif options.model == 'sg':
            X_dev = X_full[d_idx]
            Y_dev = Y_full[d_idx]
            X_full = X_full[t_idx]
            Y_full = Y_full[t_idx]
        else:
            raise BaseException("unknown model type")
    else:
        X_dev, Y_dev = load_data(options.dev_data, options.model)
    if options.model == 'cbow':
        model = CBOW(vocab_model = vocab, batch_size = options.batch_size, context_size = X_full.shape[1], embed_size = options.embed_size, reg=0.0, optimize = options.optimizer)
    else:
        model = SkipGram(vocab_model = vocab, batch_size = options.batch_size, embed_size = options.embed_size, reg=0.0, optimize = options.optimizer)
    for e_idx in xrange(options.epochs):
        print e_idx, 'training loss  :', model.fit(batch_size = options.batch_size, learning_rate = 0.01, X = X_full, Y = Y_full)
        print e_idx, 'validation loss:', model.loss(batch_size = options.batch_size, X = X_dev, Y = Y_dev)
        if options.save_path is not None:
            model.save_word_vecs(options.save_path + '.' + str(e_idx) + '.vecs')
            model.save_model(options.save_path + '.' + str(e_idx) + '.model')
        else:
            pass
