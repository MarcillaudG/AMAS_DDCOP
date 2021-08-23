import os
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


if __name__ == '__main__':
    for root, dirs, files in os.walk("../logs/sc6/"):
        dmax = {}
        dmean = {}
        res = {}
        nb_cycle = 0
        nb_files = 0
        df = {"max": [], "mean": []}
        for file in files:
            if ".csv" in file and "res" not in file:
                f = open(root + file, "r")
                lines = f.readlines()
                firstline = lines[0]
                firslinesplit = firstline.split(";")
                ind = 0
                while "max" not in firslinesplit[ind]:
                    ind += 1
                cycle = 0
                for i in range(1, len(lines)):
                    if "Time" not in lines[i]:
                        linesplit = lines[i].split(";")
                        if cycle not in dmax.keys():
                            dmax[cycle] = []
                            dmean[cycle] = []
                            res[cycle] = (0.0, 0.0)
                        dmean[cycle].append(float(linesplit[ind]))
                        dmax[cycle].append(float(linesplit[ind+1]))
                        cycle += 1
                df["mean"].append(float(linesplit[ind]))
                df["max"].append(float(linesplit[ind+1]))
                nb_files += 1
        print(str(cycle))
        for i in range(0, cycle):
            res[i] = (sum(dmax[i]) / nb_files, sum(dmean[i]) / nb_files)
        print(res)

        filer = open(root + "res.csv", "w")
        for i in range(0, cycle):
            maximum, moyenne = res[i]
            filer.write(str(maximum) + ";" + str(moyenne) + "\n")

        ''' df = pd.DataFrame(data=df)
        layout = go.Layout(
            title='',
            boxgroupgap=0.5,

            xaxis=dict(
                title='',
                showticklabels=False,
                dtick=10),
            yaxis=dict(
                title='ERROR',
                titlefont=dict(family="Times New Roman",
                               size=16, color="#000000"),
                tickfont=dict(family="Times New Roman",
                              size=14, color="#000000"),
                range=[0, 55]
            ),
            font=dict(
                family="Times New Roman",
                size=18,
                color="#7f7f7f"
            ),
            plot_bgcolor='rgba(0,0,0,0)'

        )
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Box(y=df["mean"], name="MEAN"))
        fig.add_trace(go.Box(y=df["max"], name="MAX"))
        fig.show()'''