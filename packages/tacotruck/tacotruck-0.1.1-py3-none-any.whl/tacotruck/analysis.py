import matplotlib.pyplot as plt

def discharge_vs_time(results):
    fig, ax = plt.subplots(1, 2, figsize=(6,3))
    for index in results.index:
        if results['Battery chemistry'][index] == 'NCA-Gr':
            color = 'tab:blue'
        else:
            color = 'tab:orange'
        t = results['Life simulation outputs'][index]['Time (days)']
        efc = results['Life simulation outputs'][index]['Time (days)']
        q = results['Life simulation outputs'][index]['Relative discharge capacity']
        ax[0].plot(t/365, q, color=color, alpha=0.5)
        ax[1].plot(efc, q, color=color, alpha=0.5)
    ax[0].set_xlabel('Time (years)')
    ax[0].set_ylabel('Relative discharge capacity')
    ax[0].set_xlim([0, 20])
    ax[1].set_yticklabels([])
    ax[1].set_xlabel('Equivalent full cycles')
    ax[1].set_xlim([0, 10000])

    ax.savefig("output1.jpg")