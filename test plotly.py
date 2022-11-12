import plotly.graph_objects as go
import plotly.io as plotio
import numpy as np




if __name__ == '__main__':
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    x_rev = x[::-1]

    # Line 1
    y1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y1_upper = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    y1_lower = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    y1_lower = y1_lower[::-1]


    fig = go.Figure()
    fig.update_layout(
        autosize=False,
        width=400,
        height=300,
        margin=dict(
            l=2,
            r=10,
            b=2,
            t=10,
            pad=4
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(0, 0, 0)',
            linewidth=2,
            ticks='inside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(0, 0, 0)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=False,
            showline=True,
            showticklabels=True,
            ticklabelposition="inside top",
            linecolor='rgb(0, 0, 0)',
            linewidth=2,
            ticks='',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(0, 0, 0)',
                ),
            autorange=False,
            range=[0,30],
            automargin=True,#dict(l=20, r=20, t=20, b=20),
            gridcolor="grey",
        ),
    )
    #fig.update_yaxes(range=[0, 30])
    fig.add_trace(go.Scatter(
        x=x + x_rev,
        y=y1_upper + y1_lower,
        fill='toself',
        fillcolor='rgba(0,0,0,0.2)',
        line_color='rgba(0,0,0,0)',
        showlegend=False,
        name='Fair',
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y1,
        line_color='rgb(0,0,0)',
        showlegend=False,
        name='Fair',
    ))
    #fig.update_traces(mode='lines')
    #plotio.show(fig)
    plotio.write_image(fig, 'plotly.png', 'png', height=300, width=400, scale=1)
