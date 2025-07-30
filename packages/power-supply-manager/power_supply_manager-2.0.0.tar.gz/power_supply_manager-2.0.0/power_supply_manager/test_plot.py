import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_log_file(filepath: str, save: bool = True, show: bool = False) -> None:
    df = pd.read_csv(filepath)
    df["Datestamp"] = pd.to_datetime(df["Datestamp"], format="%Y-%m-%dT%H-%M-%S.%f")
    # Split dataframes between Voltage and Current
    dfs = {
        i: df.filter(like=i)
        for i in df.columns.str.split(" ").str[-1]
        if i != "Datestamp"
    }
    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
    axes[-1].set_xlabel("Time (s)")
    cnt = 0
    for title, d in dfs.items():
        # Cut off PS# and CH# from legend titles, if a channel name was added
        # PS1 CH1 Voltage
        d = d.copy(deep=True)
        d.rename(
            columns=lambda x: x
            if x == "Datestamp"
            else (x[8:-7] if len(x) > 16 else x[:-7]),
            inplace=True,
        )
        d["Datestamp"] = df["Datestamp"]
        ax = d.plot(x="Datestamp", ax=axes[cnt])
        ax.set_ylabel(title)
        cnt += 1
    plt.tight_layout()
    if show:
        plt.show()
    if save:
        filestem = os.path.splitext(filepath)[0]
        plt.savefig(f"{filestem}.png")
        print(f"Saved plot log to {filestem}.png")
    plt.close()


if __name__ == "__main__":
    directory = "/home/willie/projects/dbz/test-data/2023-02-nsrl/power-supply"
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f) and os.path.splitext(f)[-1] == ".csv":
            print(f"Plotting {f}...")
            plot_log_file(f, show=False, save=True)
