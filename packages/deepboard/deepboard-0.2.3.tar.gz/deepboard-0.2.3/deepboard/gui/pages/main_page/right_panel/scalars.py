import plotly.graph_objects as go
import pandas as pd
from typing import *
from datetime import datetime, timedelta
from fasthtml.common import *
from fh_plotly import plotly2fasthtml
from deepboard.gui.components import Legend, Smoother, ChartType, LogSelector
from deepboard.gui.utils import get_lines, make_fig

def make_step_lines(socket, splits: set[str], metric: str, keys: set[tuple[str, str]]):
    from __main__ import CONFIG
    lines = []
    for i, split in enumerate(splits):
        tag = (split, metric)
        if tag in keys:
            reps = get_lines(socket, split, metric, key="step")

            if len(reps) > 1:
                for rep_idx, rep in enumerate(reps):
                    lines.append((
                        f'{split}_{rep_idx}',
                        rep["index"],
                        rep["value"],
                        CONFIG.COLORS[i % len(CONFIG.COLORS)],
                        rep["epoch"],
                    ))
            else:
                lines.append((
                    f'{split}',
                    reps[0]["index"],
                    reps[0]["value"],
                    CONFIG.COLORS[i % len(CONFIG.COLORS)],
                    reps[0]["epoch"],
                ))
    return lines

def make_time_lines(socket, splits: set[str], metric: str, keys: set[tuple[str, str]]):
    from __main__ import CONFIG
    lines = []
    for i, split in enumerate(splits):
        tag = (split, metric)
        if tag in keys:
            reps = get_lines(socket, split, metric, key="duration")

            if len(reps) > 1:
                for rep_idx, rep in enumerate(reps):
                    lines.append((
                        f'{split}_{rep_idx}',
                        rep["index"],
                        rep["value"],
                        CONFIG.COLORS[i % len(CONFIG.COLORS)],
                        rep["epoch"],
                    ))
            else:
                lines.append((
                    f'{split}',
                    reps[0]["index"],
                    reps[0]["value"],
                    CONFIG.COLORS[i % len(CONFIG.COLORS)],
                    reps[0]["epoch"],
                ))
    return lines



def Setup(session, labels: list[tuple]):
    return Div(
        H1("Setup", cls="chart-scalar-title"),
        Div(
            Div(
                Smoother(session, path = "/scalars", selected_rows_key="datagrid", session_path="scalars"),
                ChartType(session, path = "/scalars", selected_rows_key="datagrid", session_path="scalars"),
                LogSelector(session, path = "/scalars", selected_rows_key="datagrid", session_path="scalars"),
                style="width: 100%; margin-right: 1em; display: flex; flex-direction: column; align-items: flex-start",
            ),
            Legend(session, labels, path = "/scalars", selected_rows_key="datagrid"),
            cls="chart-setup-container",
        ),
        cls="chart-setup",
    )
# Components
def Chart(session, runID: int, metric: str, type: str = "step", running: bool = False, logscale: bool = False):
    from __main__ import rTable
    socket = rTable.load_run(runID)
    keys = socket.formatted_scalars
    # metrics = {label for split, label in keys}
    splits = {split for split, label in keys}
    hidden_lines = session["scalars"]["hidden_lines"] if "hidden_lines" in session["scalars"] else []
    smoothness = session["scalars"]["smoother_value"] - 1 if "smoother_value" in session["scalars"] else 0
    if type == "step":
        lines = make_step_lines(socket, splits, metric, keys)
    elif type == "time":
        lines = make_time_lines(socket, splits, metric, keys)
    else:
        raise ValueError(f"Unknown plotting type: {type}")

    # # Sort lines by label
    lines.sort(key=lambda x: x[0])
    # Hide lines if needed
    lines = [line for line in lines if line[0] not in hidden_lines]
    fig = make_fig(lines, type=type, smoothness=smoothness, log_scale=logscale)

    if running:
        update_params = dict(
            hx_get=f"/scalars/chart?runID={runID}&metric={metric}&type={type}&running={running}&logscale={logscale}",
            hx_target=f"#chart-container-{runID}-{metric}",
            hx_trigger="every 10s",
            hx_swap="outerHTML",
        )
    else:
        update_params = {}
    return Div(
            plotly2fasthtml(fig, js_options=dict(responsive=True)),
            cls="chart-container",
            id=f"chart-container-{runID}-{metric}",
            **update_params
        )

def LoadingChart(session, runID: int, metric: str, type: str, running: bool = False, logscale: bool = False):
    return Div(
        Div(
            H1(metric, cls="chart-title"),
            cls="chart-header",
            id=f"chart-header-{runID}-{metric}"
        ),
        Div(
            cls="chart-container",
            id=f"chart-container-{runID}-{metric}",
            hx_get=f"/scalars/chart?runID={runID}&metric={metric}&type={type}&running={running}&logscale={logscale}",
            hx_target=f"#chart-container-{runID}-{metric}",
            hx_trigger="load",
        ),
        cls="chart",
        id=f"chart-{runID}-{metric}",
    )

def Charts(session, runID: int, swap: bool = False, status: Literal["running", "finished", "failed"] = "running"):
    from __main__ import rTable
    socket = rTable.load_run(runID)
    keys = socket.formatted_scalars
    metrics = {label for split, label in keys}
    type = session["scalars"]["chart_type"] if "chart_type" in session["scalars"] else "step"
    logscale = session["scalars"]["chart_scale"] == "log" if "chart_scale" in session["scalars"] else False
    out = Div(
            H1("Charts", cls="chart-scalar-title"),
        Ul(
            *[
                Li(LoadingChart(session, runID, metric, type=type, running=status == "running", logscale=logscale), cls="chart-list-item")
                for metric in metrics
            ],
            cls="chart-list",
        ),
        cls="chart-section",
        id=f"charts-section",
        hx_swap_oob="true" if swap else None,
    )
    return out

def ScalarTab(session, runID, swap: bool = False):
    from __main__ import CONFIG, rTable
    if 'hidden_lines' not in session["scalars"]:
        session["scalars"]['hidden_lines'] = []
    socket = rTable.load_run(runID)
    keys = socket.formatted_scalars
    splits = {split for split, label in keys}
    # Get repetitions
    available_rep = socket.get_repetitions()
    if len(available_rep) > 1:
        line_names = [(f'{split}_{rep}', CONFIG.COLORS[i % len(CONFIG.COLORS)], f'{split}_{rep}' in session["scalars"]['hidden_lines']) for i, split in enumerate(splits) for rep in
                      available_rep]
    else:
        line_names = [(f'{split}', CONFIG.COLORS[i % len(CONFIG.COLORS)], f'{split}' in session["scalars"]['hidden_lines']) for i, split in enumerate(splits)]
    # Sort lines by label
    line_names.sort(key=lambda x: x[0])
    status = socket.status
    return Div(
        Setup(session, line_names),
        Charts(session, runID, status=status),
        style="display; flex; width: 40vw; flex-direction: column; align-items: center; justify-content: center;",
        id="scalar-tab",
        hx_swap_oob="true" if swap else None,
    )

def scalar_enable(runID):
    """
    Check if some scalars are logged and available for the runID. If not, we consider disable it.
    :param runID: The runID to check.
    :return: True if scalars are available, False otherwise.
    """
    from __main__ import rTable
    socket = rTable.load_run(runID)
    keys = socket.formatted_scalars
    return len(keys) > 0

def build_scalar_routes(rt):
    rt("/scalars/change_chart")(change_chart_type)
    rt("/scalars/hide_line")(hide_line)
    rt("/scalars/show_line")(show_line)
    rt("/scalars/change_smoother")(change_smoother)
    rt("/scalars/change_scale")(change_chart_scale)
    rt("/scalars/chart")(load_chart)


# Interactive Routes
def change_chart_type(session, runIDs: str, step: bool):
    new_type = "time" if step else "step"
    session["scalars"]["chart_type"] = new_type
    runIds = runIDs.split(",")
    runID = runIds[0]
    return (
        ChartType(session, path="/scalars", selected_rows_key="datagrid", session_path="scalars"), # We want to toggle it
        Charts(session, int(runID), swap=True)
            )

def hide_line(session, runIDs: str, label: str):
    if 'hidden_lines' not in session["scalars"]:
        session["scalars"]['hidden_lines'] = []
    runIds = runIDs.split(",")
    runID = runIds[0]
    session["scalars"]['hidden_lines'].append(label)
    return ScalarTab(session, runID, swap=True)


def show_line(session, runIDs: str, label: str):
    if 'hidden_lines' not in session["scalars"]:
        session["scalars"]['hidden_lines'] = []
    runIds = runIDs.split(",")
    runID = runIds[0]
    if label in session["scalars"]['hidden_lines']:
        session["scalars"]['hidden_lines'].remove(label)

    return ScalarTab(session, runID, swap=True)

def change_smoother(session, runIDs: str, smoother: int):
    session["scalars"]["smoother_value"] = smoother
    runIds = runIDs.split(",")
    runID = runIds[0]
    return ScalarTab(session, runID, swap=True)

def change_chart_scale(session, runIDs: str, log: bool):
    new_type = "default" if log else "log"
    session["scalars"]["chart_scale"] = new_type
    runIds = runIDs.split(",")
    runID = runIds[0]
    return (
        LogSelector(session, path="/scalars", selected_rows_key="datagrid", session_path="scalars"), # We want to toggle it
        Charts(session, int(runID), swap=True)
            )

def load_chart(session, runID: int, metric: str, type: str, running: bool, logscale: bool):
    return Chart(session, runID, metric, type, running, logscale=logscale)