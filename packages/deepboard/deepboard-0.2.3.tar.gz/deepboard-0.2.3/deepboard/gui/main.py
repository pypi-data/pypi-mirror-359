import os
import sys
sys.path.append(os.getcwd())
from fasthtml.common import *
from deepboard.gui.pages.main_page.datagrid import SortableColumnsJs, right_click_handler_row, right_click_handler
from deepboard.gui.pages.main_page import MainPage, build_main_page_endpoints
from deepboard.gui.utils import prepare_db, Config, initiate_files, get_table_path_from_cli, verify_runids
from deepboard.gui.pages.compare_page import build_compare_routes, ComparePage
from deepboard.gui.pages import _not_found
from deepboard.gui.components import Modal
from deepboard.resultTable import ResultTable
from fh_plotly import plotly_headers

DEBUG = False
# Create config files to customize the UI
initiate_files()

# Load config and DB
CONFIG = Config.FromFile(os.path.expanduser('~/.config/deepboard/THEME.yml'))
DATABASE = get_table_path_from_cli()
if not os.path.exists(DATABASE):
    raise RuntimeError(f"ResultTable {DATABASE} does not exist")
prepare_db()

# Load the result Table
rTable = ResultTable(DATABASE)

cls = FastHTMLWithLiveReload if DEBUG else FastHTML
app = cls(
    exception_handlers={404: _not_found},
    hdrs=(
        Link(rel='stylesheet', href='assets/base.css', type='text/css'),
        Link(rel='stylesheet', href='assets/datagrid.css', type='text/css'),
        Link(rel='stylesheet', href='assets/right_panel.css', type='text/css'),
        Link(rel='stylesheet', href='assets/charts.css', type='text/css'),
        Link(rel='stylesheet', href='assets/fileview.css', type='text/css'),
        Link(rel='stylesheet', href='assets/compare.css', type='text/css'),
        Link(rel='stylesheet', href='assets/artefacts.css', type='text/css'),
        Link(href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css", rel="stylesheet"),
        plotly_headers,
        Script(src="assets/base.js"),
        SortableColumnsJs(),
    ),
    static_path='assets'
)

rt = app.route
@rt("/assets/{fname:path}.{ext:static}")
async def get(fname:str, ext:str):
    if fname == "theme" and ext == "css" and not DEBUG:
        if os.path.exists(os.path.expanduser('~/.config/deepboard/theme.css')):
            return FileResponse(os.path.expanduser('~/.config/deepboard/THEME.css'))
    root = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(f'{root}/assets/{fname}.{ext}')


@rt("/")
def get(session):
    if "show_hidden" not in session:
        session["show_hidden"] = False

    # Check if row_selected exists.
    verify_runids(session, rTable)

    return (Title("Table"),
            Div(id="custom-menu"),
            Modal(P("Hellp world"), active=False),
            MainPage(session),
            )


@rt("/compare")
def get(session, run_ids: str):
    return ComparePage(session, run_ids)


# Dropdown menu when right-clicked
@rt("/get-context-menu")
def get(session, elementIds: str, top: int, left: int):
    elementIds = elementIds.split(",")
    if any(elementId.startswith("grid-header") for elementId in elementIds):
        return right_click_handler(elementIds, top, left)
    elif any(elementId.startswith("grid-row") for elementId in elementIds):
        return right_click_handler_row(session, elementIds, top, left)
    else:
        return Div(
            id='custom-menu',
            style=f'visibility: visible; top: {top}px; left: {left}px;',
        )

build_main_page_endpoints(rt)
build_compare_routes(rt)
serve(reload=DEBUG)