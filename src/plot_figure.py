import sys
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

def remove_word(word, r):
    new_word = []
    for w in word:
        new_word.append(w.replace(r,""))
    return new_word

if "__main__" == __name__:

    if len(sys.argv) > 2:
        csv = sys.argv[1]
        name = sys.argv[2]
    else:
        print("CSV file")

    data = pd.read_csv(csv)

    colunm_names = list(data.columns.values)
    colors = ['red', 'green', 'blue', 'black'] 

    x_label = remove_word(data[colunm_names[0]].to_numpy(),  "Tuner") 
    x = range(len(x_label))
    y1 = data[colunm_names[1]].to_numpy() 
    y2 = data[colunm_names[3]].to_numpy()

    plt.figure()
    f, axes = plt.subplots(2, 1)

    width = 0.3
    axes[0].bar(x_label, y1, width, color=colors)
    axes[0].set_ylabel("Model Running Time (ms)")

    axes[1].bar(x_label, y2, width, color=colors)
    axes[1].set_ylabel("Auto-tuning time (s)")
    
    plt.savefig('./results/%s_tuning.pdf' % name)