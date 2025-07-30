import plotly.express as px


def generate_protein_pathogenicity_plot(scores,
                                        x_title="",
                                        y_title="",
                                        x_labels="",
                                        y_labels="",
                                        font_size=12,
                                        label_color='#000000',
                                        width=400,
                                        height=200,
                                        tick_label_size=12
                                        ):
    """

    :param scores:
    :param x_title:
    :param y_title:
    :param x_labels:
    :param y_labels:
    :return:
    """
    fig = px.imshow(scores,labels={"x":x_title,"y":y_title}, y=y_labels, x=x_labels,
                    color_continuous_scale='RdBu_r',color_continuous_midpoint=0.5, zmin=0.0, zmax=1.0)

    fig.update_layout(
        margin=dict(l=10, r=0, t=0, b=0, pad=0),
        font=dict(
            family="Arial",
            size=tick_label_size,
            color=label_color
        ),
        paper_bgcolor="#ffffff",
        width=int(width),
        height=int(height)
    )

    return fig

