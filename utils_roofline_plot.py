#! /usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogLocator
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import enum

# function to parse arguments
def parseArg():
    # create a parser object
    parser = argparse.ArgumentParser(description="Plot energy comparison")
    # add argument result_folder which is the folder where the results are stored
    parser.add_argument("--result_folder",type=str,help="Folder where the results are stored",required=True)
    # add argument output_folder which is the folder where the plots are stored
    parser.add_argument("--output_folder",type=str,help="Folder where the plots are stored",required=True)
    #add argument machine which is the machine used to run the code
    parser.add_argument("--machine",type=str,help="Machine name",required=True)
    #generate for all
    parser.add_argument("--generate_for_all",action="store_true",help="Generate plots for all the machines")

    #check if the resutls and output folder are relative or absolute
    # if they are relative make them absolute
    args = parser.parse_args()
    if not os.path.isabs(args.result_folder):
        args.result_folder = os.path.abspath(args.result_folder)
    if not os.path.isabs(args.output_folder):
        args.output_folder = os.path.abspath(args.output_folder)

    return args



def plot_muliple_roofline(result_folder,output_folder,machine):
    # list the files in the result folder and check for files with the name a_roofline_model csvs
    files = os.listdir(result_folder)
    #filter the files with the name a_roofline_model csvs
    files = [f for f in files if f.endswith(".csv") and "a_roofline_model" in f]
    #generate list of frequencies availiable
    frequencies = [f.split("_")[-1].split(".")[0] for f in files]
    print(frequencies)
    # exit()

    # create a list to store the frequency and the respective dataframes
    data = []

    # files = sorted(files, key=lambda x: int(x.split("_")[-1].split(".")[0].split("kHz")[0]))

    for f in files:
        freq = f.split("_")[-1].split(".")[0]
        data.append([freq,pd.read_csv(os.path.join(result_folder, f))])
    
    print(os.listdir(result_folder))
    # exit()
    #sort the data by frequency
    # data = sorted(data, key=lambda x: x[0])
    
    # plot the energy comparison
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))
    # generate colors for the various frequencies
    colors = plt.cm.viridis(np.linspace(0, 1, len(frequencies)))
    fig.suptitle(f"Energy, Power, and Performance comparison for {machine} machine")
    fig.dpi = 1000


    for i, freq in enumerate(frequencies):
        ax[0, 0].plot(data[i][1]["OI"], data[i][1]["Energy(J)"], label=f"{data[i][0]}", color=colors[i], marker="o")
    ax[0, 0].set_xscale("log")
    ax[0, 0].set_yscale("log")
    ax[0, 0].set_xlabel("OI")
    ax[0, 0].set_ylabel("Energy(J)")
    ax[0, 0].set_title("Energy plot")
    ax[0, 0].yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax[0, 0].yaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=100))
    ax[0, 0].grid(which="both")
    ax[0, 0].legend()
    # xaxis.set_minor_locator(LogLocator())

    # plot the power plot
    for i, freq in enumerate(frequencies):
        ax[0, 1].plot(data[i][1]["OI"], data[i][1]["Power(W)"], label=f"{data[i][0]}", color=colors[i], marker="o")
    ax[0, 1].set_xscale("log")
    ax[0, 1].set_yscale("log")
    ax[0, 1].set_xlabel("OI")
    ax[0, 1].set_ylabel("Power(W)")
    ax[0, 1].set_title("Power plot")
    ax[0, 1].yaxis.set_major_locator(LogLocator(base=10.0, numticks=10,))
    ax[0, 1].yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(1, 5, 0.1), numticks=100))
    ax[0, 1].grid(which="both")
    ax[0, 1].legend()

    # plot the performance plot
    for i, freq in enumerate(frequencies):
        ax[1, 1].plot(data[i][1]["OI"], (data[i][1]["total_flops"] / data[i][1]["Execution Time(s)"]) / 10**9, label=f"{data[i][0]}", color=colors[i], marker="o")
    ax[1, 1].set_xscale("log")
    ax[1, 1].set_yscale("log")
    ax[1, 1].set_xlabel("OI")
    ax[1, 1].set_ylabel("Performance(GFlops/s)")
    ax[1, 1].set_title("Performance plot")
    ax[1, 1].yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax[1, 1].yaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=100))
    ax[1, 1].grid(which="both")
    ax[1, 1].legend()


    # show the plot
    # plt.show()
    # plt.close()

    # save the plot
    output_file = f"roofline_comparison_{machine}.png"
    plt.savefig(os.path.join(output_folder, output_file))
    print(f"Plot saved to {os.path.join(output_folder, output_file)}")

    # I want to create another csv file that contains the following columns
    #Frequency(kHz),Time Per Flop [s/ops],Time Per Byte [s/ops],Energy Per Flop [J/ops],Energy Per Byte [J/ops],Time Balance,Energy Balance,Power per byte,Power per flop

    # create a dictionary to store the data
    data_new = {
        "Cache": [],
        "Time Per Flop [s/ops]": [],
        "Time Per Byte [s/ops]": [],
        "Energy Per Flop [J/ops]": [],
        "Energy Per Byte [J/ops]": [],
        "Power Per Flop [W/ops]" : [],
        "Power Per Byte [W/ops]" : [],
        "Time balance [OI]" : [],
        "Energy balance [OI]" : [],
        "Constant Power [W]" : [],
        "Constant Energy Per Flop [J/ops]" : [],
        "Constant Flop Energy Efficiency" : [],
        "New Balance Energy" : [],
    }

    for i, freq in enumerate(frequencies):
        data[i][1]["Time Per Flop [s/ops]"] = data[i][1]["Execution Time(s)"] / data[i][1]["total_flops"]
        data[i][1]["Time Per Byte [s/ops]"] = data[i][1]["Execution Time(s)"] / data[i][1]["total_missed_bytes"]
        data[i][1]["Energy Per Flop [J/ops]"] = data[i][1]["Energy(J)"] / data[i][1]["total_flops"]
        data[i][1]["Energy Per Byte [J/ops]"] = data[i][1]["Energy(J)"] / data[i][1]["total_missed_bytes"]
        total_flops = data[i][1]["total_flops"]
        time_per_flop = data[i][1]["Time Per Flop [s/ops]"].iloc[-1]
        time_per_byte = data[i][1]["Time Per Byte [s/ops]"].iloc[0]
        energy_per_flop = data[i][1]["Energy Per Flop [J/ops]"].iloc[-1]
        energy_per_byte = data[i][1]["Energy Per Byte [J/ops]"].iloc[0]
        power_per_flop = energy_per_flop / time_per_flop
        power_per_byte = energy_per_byte / time_per_byte
        constant_power = data[i][1]["Constant Power (W)"].median()
        constant_energy_per_flop = constant_power * time_per_flop
        constant_flop_energy_efficiency = energy_per_flop / (energy_per_flop + constant_energy_per_flop)
        balance_time = time_per_byte / time_per_flop
        balance_energy = energy_per_byte / time_per_byte
        # print every thing
        # print(f"Frequency: {freq}")
        # print(f"Time per flop: {time_per_flop}")
        # print(f"Time per byte: {time_per_byte}")
        # print(f"Energy per flop: {energy_per_flop}")
        # print(f"Energy per byte: {energy_per_byte}")
        # print(f"Power per flop: {power_per_flop}")
        # print(f"Power per byte: {power_per_byte}")
        # print(f"Constant power: {constant_power}")
        # print(f"Constant energy per flop: {constant_energy_per_flop}")
        # print(f"Constant flop energy efficiency: {constant_flop_energy_efficiency}")
        # print(f"Balance time: {balance_time}")
        # print(f"Balance energy: {balance_energy}")
        # print("\n\n\n")
        # exit()
        for j, row in data[i][1].iterrows():
            print(row["Power(W)"])
            new_balance_energy = (constant_flop_energy_efficiency * balance_energy) + ((1 - constant_flop_energy_efficiency) * max(0,(balance_time - row["OI"])))
            row["Power(W)"] = (power_per_flop / constant_flop_energy_efficiency) * ((min(row["OI"], balance_time) / balance_time) + new_balance_energy / max(row["OI"], balance_time))
            # print(power_per_flop / constant_flop_energy_efficiency)
            # print(new_balance_energy)
            # print((min(row["OI"], balance_time) / balance_time) + new_balance_energy / min(row["OI"], balance_time))
            data[i][1].loc[j] = row
            print(row["Power(W)"])
            # exit()
        print(data[i][1]["Power(W)"])
        # exit()
        data_new["Time Per Flop [s/ops]"].append(time_per_flop)
        data_new["Time Per Byte [s/ops]"].append(time_per_byte)
        data_new["Energy Per Flop [J/ops]"].append(energy_per_flop)
        data_new["Energy Per Byte [J/ops]"].append(energy_per_byte)
        data_new["Power Per Flop [W/ops]"].append(power_per_flop)
        data_new["Power Per Byte [W/ops]"].append(power_per_byte)
        data_new["Time balance [OI]"].append(time_per_byte / time_per_flop)
        data_new["Energy balance [OI]"].append(energy_per_byte / energy_per_flop)
        data_new["Constant Power [W]"].append(constant_power)
        data_new["Constant Energy Per Flop [J/ops]"].append(constant_energy_per_flop)
        data_new["Constant Flop Energy Efficiency"].append(constant_flop_energy_efficiency)
        data_new["New Balance Energy"].append(new_balance_energy)
        data_new["Cache"].append(data[i][0])


    # for i, freq in enumerate(frequencies):
    #     # print(f'{data["df"][i]["Execution Time(s)"] / data["df"][i]["total_flops"]}')
    #     data_new["Frequency(kHz)"].append(data[i][0])
    #     data[i][1]["Time Per Flop [s/ops]"] = data[i][1]["Execution Time(s)"] / data[i][1]["total_flops"]
    #     data[i][1]["Time Per Byte [s/ops]"] = data[i][1]["Execution Time(s)"] / data[i][1]["total_missed_bytes"]
    #     data[i][1]["Energy Per Flop [J/ops]"] = data[i][1]["Energy(J)"] / data[i][1]["total_flops"]
    #     data[i][1]["Energy Per Byte [J/ops]"] = data[i][1]["Energy(J)"] / data[i][1]["total_missed_bytes"]

    #     data[i][1].sort_values(by='OI')
    #     # print(data[i][1])
    #     # exit()
    #     time_per_flop = data[i][1]["Time Per Flop [s/ops]"].iloc[-1]
    #     time_per_byte = data[i][1]["Time Per Byte [s/ops]"].iloc[0]
    #     energy_per_flop = data[i][1]["Energy Per Flop [J/ops]"].iloc[-1]
    #     energy_per_byte = data[i][1]["Energy Per Byte [J/ops]"].iloc[0]
    #     power_per_flop = energy_per_flop / time_per_flop
    #     power_per_byte = energy_per_byte / time_per_byte
    #     constant_power = data[i][1]["Constant Power (W)"].median()
        
    #     data_new["Time Per Flop [s/ops]"].append(time_per_flop)
    #     data_new["Time Per Byte [s/ops]"].append(time_per_byte)
    #     data_new["Energy Per Flop [J/ops]"].append(energy_per_flop)
    #     data_new["Energy Per Byte [J/ops]"].append(energy_per_byte)
    #     data_new["Power Per Flop [W/ops]"].append(power_per_flop)
    #     data_new["Power Per Byte [W/ops]"].append(power_per_byte)
    #     data_new["Time balance [OI]"].append(time_per_byte / time_per_flop)
    #     data_new["Energy balance [OI]"].append(energy_per_byte / energy_per_flop)
    #     data_new["Constant Power [W]"].append(constant_power)
        
        
        # data_new["Time Per Flop [s/ops]"].append(data[i][1]["Time Per Flop [s/ops]"].iloc[-1])
        # data_new["Time Per Byte [s/ops]"].append(data[i][1]["Time Per Byte [s/ops]"].iloc[0])
        # data_new["Energy Per Flop [J/ops]"].append(data[i][1]["Energy Per Flop [J/ops]"].iloc[-1])
        # data_new["Energy Per Byte [J/ops]"].append(data[i][1]["Energy Per Byte [J/ops]"].iloc[0])
        # data_new["Power Per Flop [W/ops]"].append(data_new["Energy Per Flop [J/ops]"][-1] / data_new["Time Per Flop [s/ops]"][-1])
        # data_new["Power Per Byte [W/ops]"].append(data_new["Energy Per Byte [J/ops]"][-1] / data_new["Time Per Byte [s/ops]"][-1])
        # data_new["Time balance [OI]"].append(data_new["Time Per Byte [s/ops]"][-1] / data_new["Time Per Flop [s/ops]"][-1])
        # data_new["Energy balance [OI]"].append(data_new["Energy Per Byte [J/ops]"][-1] / data_new["Energy Per Flop [J/ops]"][-1])


    
    print(data_new)
    # # create a dataframe
    df = pd.DataFrame(data_new)
    print(df)
    # # save the dataframe to a csv file
    output_file = f"roofline_constants_{machine}.csv"
    #sort the dataframe by frequency
    # df = df.sort_values(by='Frequency(kHz)')
    df.to_csv(os.path.join(output_folder, output_file), index=False)
    exit()
    oi_points = np.logspace(start=-4,stop=2,num=10000)
    #     data_new = {
    #     "Frequency(kHz)": [],
    #     "Time Per Flop [s/ops]": [],
    #     "Time Per Byte [s/ops]": [],
    #     "Energy Per Flop [J/ops]": [],
    #     "Energy Per Byte [J/ops]": [],
    #     "Power Per Flop [W/ops]" : [],
    #     "Power Per Byte [W/ops]" : [],
    #     "Time balance [OI]" : [],
    #     "Energy balance [OI]" : [],
    #     "Constant Power [W]" : [],
    #     "Constant Energy Per Flop [J/ops]" : [],
    #     "Constant Flop Energy Efficiency" : [],
    #     "New Balance Energy" : [],
    # }
    
    # iterate through all the caches
    assumed_bytes = [1000_000_000] * len(oi_points)
    assumed_flops = [oi_points_ * assumed_bytes_ for oi_points_, assumed_bytes_ in zip(oi_points, assumed_bytes)]
    all_predicted_power = []
    all_predicted_performance = []
    
    for i, row in df.iterrows():
        cache = row["Cache"]
        time_per_flop = row["Time Per Flop [s/ops]"]
        time_per_byte = row["Time Per Byte [s/ops]"]
        energy_per_flop = row["Energy Per Flop [J/ops]"]
        energy_per_byte = row["Energy Per Byte [J/ops]"]
        power_per_flop = row["Power Per Flop [W/ops]"]
        power_per_byte = row["Power Per Byte [W/ops]"]
        time_balance = row["Time balance [OI]"]
        energy_balance = row["Energy balance [OI]"]
        constant_power = row["Constant Power [W]"]
        constant_energy_per_flop = row["Constant Energy Per Flop [J/ops]"]
        constant_flop_energy_efficiency = row["Constant Flop Energy Efficiency"]
        new_balance_energy = row["New Balance Energy"]
        
        # predicted_times = max(assumed_bytes * time_per_byte + assumed_flops * time_per_flop)
        predicted_times = [max(assumed_bytes_ * time_per_byte , assumed_flops_ * time_per_flop) for assumed_bytes_, assumed_flops_ in zip(assumed_bytes, assumed_flops)]
        # for i, assumed_bytes_ in enumerate(assumed_bytes):
        #     predicted_time = max(assumed_bytes_ * time_per_byte , assumed_flops[i] * time_per_flop)
        #     print(predicted_time)
        is_memory_bound = [1 if x < time_balance else 0 for x in oi_points]
        predicted_power = [constant_power + (power_per_byte * ((1-is_memory_bound_) * (time_balance / oi_points_) + is_memory_bound_) + power_per_flop * (is_memory_bound_ * (oi_points_ / time_balance) + (1 - is_memory_bound_))) for is_memory_bound_, oi_points_ in zip(is_memory_bound, oi_points)]
        predicted_performance = [assumed_flops_ / predicted_times_ for assumed_flops_, predicted_times_ in zip(assumed_flops, predicted_times)]
        # print(predicted_power)
        # print("------------")
        all_predicted_power.append(predicted_power)
        all_predicted_performance.append(predicted_performance)
    
    # plot a 2 graphs in one figure one for the predicted power and the other for the predicted performance agains the oi_points 
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))
    for predicted_power_ in all_predicted_power:
        ax[0].plot(oi_points, predicted_power_, label="Predicted Power")
    # ax[0].plot(oi_points, predicted_power, label="Predicted Power")
    ax[0].set_xscale("log")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("OI")
    ax[0].set_ylabel("Power(W)")
    ax[0].set_title("Predicted Power plot")
    ax[0].yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax[0].yaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=100))
    ax[0].grid(which="both")
    ax[0].legend()
    
    # ax[1].plot(oi_points, predicted_performance, label="Predicted Performance")
    for predicted_performance_ in all_predicted_performance:
        ax[1].plot(oi_points, predicted_performance_, label="Predicted Performance")
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("OI")
    ax[1].set_ylabel("Performance(GFlops/s)")
    ax[1].set_title("Predicted Performance plot")
    ax[1].yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax[1].yaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=100))
    ax[1].grid(which="both")
    ax[1].legend()
    
    # show the plot
    fig.plot()
    fig.savefig(os.path.join(f"predicted_power_performance_{machine}.png"))


if __name__ == "__main__":
    #parse the arguments
    args = parseArg()
    #get the result folder
    result_folder = args.result_folder
    #get the output folder
    output_folder = args.output_folder
    #get the machine name
    machine = args.machine
    
    plot_muliple_roofline(result_folder,output_folder,machine)