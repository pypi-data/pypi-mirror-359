import numpy as np
from tqdm import tqdm
from .utils import get_mid, AES_Sbox
from .leakage import *
import pandas as pd
from scipy.stats import multivariate_normal
from typing import Tuple

class TemplateAttack:
    def __init__(self, X_profiling, Y_profiling, X_attack) -> None:
        self.X_profiling = X_profiling
        self.Y_profiling = Y_profiling
        
        self.X_attack = X_attack
        
    def build_template(self) -> Tuple[np.ndarray, np.ndarray]:
        num_of_classes = len(np.unique(self.Y_profiling))
        self.num_of_classes = num_of_classes

        means = np.zeros((num_of_classes, self.X_profiling.shape[1]))
        idx_array = []
        # grouping by labels
        for item in np.unique(self.Y_profiling):
            idx_array.append(np.where(self.Y_profiling == item))
        
        for i in range(num_of_classes):
            means[i] = np.mean(self.X_profiling[self.Y_profiling == i], axis=0)
            
        sample_groups = [np.array(self.X_profiling[idx]) for idx in idx_array]
        self.means = means
        
        # cov matrix
        num_of_pois = self.X_profiling.shape[1]
        self.covs = np.zeros((num_of_classes, num_of_pois, num_of_pois))
        for label in range(num_of_classes):
            for i in range(num_of_pois):
                for j in range(num_of_pois):
                    x = sample_groups[label][:, i]
                    y = sample_groups[label][:, j]
                    self.covs[label, i, j] = np.cov(x, y)[0][1]
        
        return self.means, self.covs
    
    def attack(self, targets, key, times, num_of_attack, allow_singular=False) -> np.ndarray:
        num_traces = len(self.X_attack)

        probs = np.zeros(targets.shape[1])
        predictions = np.zeros((num_traces, targets.shape[1]))
        # get targets, for instance, hw aes-128 --> targets.shape=(num_of_traces, 128)
        ''' the prediction value is fixed, so just use random index to get mean rank '''
        for i in tqdm(range(num_traces)):
            for k in range(targets.shape[1]):
                try:
                    rv = multivariate_normal(self.means[targets[i][k]], self.covs[targets[i][k]], allow_singular)
                    p_kj = rv.pdf(self.X_attack[i])

                # !!!Note： if matrix is illeagal, plz try another way, here just break out this function
                except Exception as e:
                    raise e
                #     # catch LinAlgError
                #     print(f"[+] matrix error: {e} , try psuedo inverse")
                #     eps = 1e-6
                #     inv_sigma = np.linalg.pinv(self.covs[targets[i][k]])
                #     log_det_sigma = np.log(np.linalg.det(self.covs + eps * np.eye(self.covs.shape[0])))
                #     diff = self.X_attack[i] - self.means[targets[i][k]]
                #     exponent = diff @ inv_sigma @ log_det_sigma
                #     p_kj = -0.5 * (self.X_attack[i].shape[1] * np.log(2 * np.pi) + log_det_sigma + exponent)
                probs[k] = np.log(p_kj + 1e-16)
            # list reverse 
            predictions[i] = probs
            
        ranks = np.zeros((times, num_of_attack))
        for t in range(times):
            rank = []
            # shuffle
            shuffled_index = np.random.permutation(num_traces)[:num_of_attack]
            shuffled_predictions = predictions[shuffled_index]
            sum_shuffled_predictions = np.cumsum(shuffled_predictions, axis=0)
            for pred in sum_shuffled_predictions:
                key_probs_sorted = np.argsort(pred)[::-1]
                rank.append(list(key_probs_sorted).index(key))
            ranks[t] = rank
        # the number of traces to get guessing entropy to zero
        mean_rank = np.mean(ranks, axis=0)
        return np.array(mean_rank)

def dpa(traces, plaintexts, threshold, target_byte, target_point, leakage_function):
    """
    DPA

    `This function is just for AES-128, if attack AES-256 or others, plz change it.`

    Args:
        `traces`: an array of power consumption measurements.
        `plaintexts`: an array of plaintexts.
        `threshold`: an integer threshold value.
        `target_byte`: the target byte to attack.
        `target_point`: the target point in the traces to analyze.
        `leakage_function`: the leakage function to use (either 'hw' for Hamming weight or another function).

    Returns:
        `candidate`:after calculation get the maximum value.
        `mean_diffs`:after calculation get the mean_diffs.
    
    Case:
    >>> ### trace.shape = (2000, 15000), plaintext.shape = (2000, 16)
    >>> dpa(traces, plaintexts, threshold=4, target_byte=0, target_point=810, leakage_function='hw')
    """
    candidate_key = []
    maximum = 0
    mean_diffs = np.zeros(256)
    for i in tqdm(range(256)):
        traces_group1 = []
        traces_group2 = []
        for num in range(len(traces)):
            mid_val = hw(AES_Sbox[plaintexts[num][target_byte] ^ i]) if leakage_function.lower() == 'hw' else AES_Sbox[plaintexts[num][target_byte] ^ i]
            if mid_val < threshold:
                traces_group1.append(traces[num][target_point])
            else:
                traces_group2.append(traces[num][target_point])
        mean_diffs[i] = abs(np.mean(traces_group1) - np.mean(traces_group2))
        if mean_diffs[i] > maximum:
            maximum = mean_diffs[i]
            candidate_key = i
    return candidate_key, mean_diffs

def cpa(byte_idx, plaintexts, traces, mask_scheme=None, mask=-1)->np.ndarray:
    '''
    CPA 
    
    `A function to implement correlation power analysis.`
    
    Args:
        `byte_idx`: input the index of the key bytes you want to attack.
        `plaintexts`: input the plaintext array type is numpy arrary.
        `traces`: traces array just like plaintexts.
        `mask_scheme`: please input your mask scheme, TODO: this arg will be used in next version :)
        `mask`: input your mask list, shape = (1, n).
        
    Returns: 
        `ndarry`: return guess key list.
    
    Raises:
        for version 0.x, there does not have any raises, we do not check any inputs just give u a tips.
    Case:
        >>> guess_keys, data = cat.cpa(1, [[1],[2],[3],[4]], [[23], [44], [55], [77]], 'bool', mask=-1)
        
    > It is just a example, you need replace the plaintexts and traces to real data.
    '''
    traces_num = traces.shape[0]
    data = []
    for k in tqdm(range(256), desc="[+] byte: " + str(byte_idx)):
        targets = np.zeros(shape=(traces_num))
        for index in range(traces_num):
            targets[index] = get_mid(plaintexts[index][byte_idx], k, mask, mask_scheme)
        data.append(max(pcc(targets, traces)))
    guess_keys = np.argmax(data)
    return guess_keys

def pcc(targets:np.array, traces:np.array):
    '''
    ### Pearson correlation coeffcuent
    
    return abs value, whether it is positive or negative
    '''
    point_num = traces.shape[1]
    pearson_list = np.zeros(point_num)
    for num in range(point_num):
        pearson_list[num] = pearson(targets, traces[:, num])
    return pearson_list

def pearson(x:np.array, y:np.array):
    x = (x-np.mean(x,axis=0))/np.std(x,axis=0)
    x = x/np.linalg.norm(x,axis=0)
    y = (y-np.mean(y,axis=0))/np.std(y,axis=0)
    y = y/np.linalg.norm(y,axis=0)
    m = np.dot(x.T,y)
    return abs(m)

# signal-noise ratio
def prepare_data(trace_set, labels_set):
    labels=np.unique(labels_set)
    #initialize the dictionary
    d={}
    for i in labels:
         d[i]=[]
    for count, label in enumerate(labels_set):
        d[label].append(trace_set[count])
    return d


# link: https://ileanabuhan.github.io/general/2021/05/07/SNR-tutorial.html
def snr(trace_set, labels_set):
    mean_trace={}
    signal_trace=[]
    noise_trace=[]
    labels=np.unique(labels_set) 
    
    grouped_traces=prepare_data(trace_set, labels_set) 
    
    for i in labels:
        mean_trace[i]=np.mean(grouped_traces[i], axis=0)
        signal_trace.append(mean_trace[i]) 
    
    for i in labels:
        for trace in grouped_traces[i]:
            noise_trace.append(trace-mean_trace[i])
    var_noise=np.var(noise_trace, axis=0)
    var_signal=np.var(signal_trace, axis=0)
    snr_trace=var_signal/var_noise  
    return snr_trace
