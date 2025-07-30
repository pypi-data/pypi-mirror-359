from io import StringIO
import threading
import time
import requests
import streamlit as st
from nemo_library.ui.ui_config_ import UIConfig
from nemo_library.version import __version__
from packaging import version

import logging
import pandas as pd
from logging import StreamHandler, getLogger

import streamlit as st

# Initialize logger
app_logger = getLogger()

# Only add StreamHandler if none is already added
if not any(isinstance(h, StreamHandler) for h in app_logger.handlers):
    stream_handler = StreamHandler()
    app_logger.addHandler(stream_handler)
    app_logger.setLevel(logging.INFO)
    app_logger.info("streamlit UI started")

# === Init Config ===
config = UIConfig()
nl = config.getNL()

# Set page configuration
st.set_page_config(page_title="Nemo Library UI", layout="wide")

# format buttons to look like links
st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: transparent;
        color: #007acc;
        border: none;
        padding: 0;
        text-align: left;
    }
    div.stButton > button:hover {
        text-decoration: underline;
        color: #005f99;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- Helper: Fetch latest version from PyPI ---
def get_remote_version() -> str:
    try:
        response = requests.get("https://pypi.org/pypi/nemo_library/json", timeout=5)
        response.raise_for_status()
        return response.json()["info"]["version"]
    except Exception as e:
        st.warning(f"Version check failed: {e}")
        return "not available"


# --- Read query parameters for navigation ---
params = st.query_params
page = params.get("page", "home")
action = params.get("action", None)


def sidebar():
    st.sidebar.title("🧠 NEMO UI")

    with st.sidebar:
        st.markdown("### Navigation")
        if st.button("➡️ MigMan", key="MigMan"):
            st.session_state["page"] = "MigMan"
        if st.button("📁 Projects", key="Projects"):
            st.session_state["page"] = "Projects"
        if st.button("⚙️ Settings", key="settings"):
            st.session_state["page"] = "settings"

    with st.sidebar:
        st.divider()
        if config.current_profile:
            st.markdown(
                f"#### Active Profile: {config.current_profile.profile_name} ({config.current_profile.profile_description})"
            )
            st.markdown(f"#### Environment: {config.current_profile.environment}")
            st.markdown(f"#### Tenant: {config.current_profile.tenant}")
            st.markdown(f"#### User ID: {config.current_profile.userid}")
        else:
            st.markdown("### No Active Profile. Please select one from Settings.")
        st.divider()
        st.markdown(f"#### Version (local): {__version__}")
        st.markdown(f"#### Version (server): {get_remote_version()}")
        if version.parse(__version__) < version.parse(get_remote_version()):
            st.warning(
                "A newer version of nemo_library is available. Please update to the latest version."
            )


class StreamlitLogHandler(logging.Handler):
    def __init__(self, buffer, placeholder):
        super().__init__()
        self.buffer = buffer
        self.placeholder = placeholder

    def emit(self, record):
        msg = self.format(record)
        self.buffer.write(msg + "\n")
        self.placeholder.text(self.buffer.getvalue())


def migman_button(col, label, method, success_message, spinner_message):
    with col:
        if st.button(label, key=label):
            with st.spinner(spinner_message):
                try:
                    method()
                    st.toast(success_message, icon="✅")
                except Exception as e:
                    st.toast(f"An error occurred: {str(e)}",icon="❌")

def show_migman():
    """
    Displays the Migration Manager page with project overview.
    """
    st.header(f"Migration Manager")

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    migman_button(
        col1,
        label="Delete Projects",
        method=nl.MigManDeleteProjects,
        success_message="Projects deleted successfully.",
        spinner_message="Deleting projects... please wait.",
    )

    migman_button(
        col2,
        label="Create Templates",
        method=nl.MigManCreateProjectTemplates,
        success_message="Project templates successfully created.",
        spinner_message="Create project templates... please wait.",
    )

    migman_button(
        col3,
        label="LoadData",
        method=nl.MigManLoadData,
        success_message="Data successfully loaded.",
        spinner_message="Load data... please wait.",
    )
    migman_button(
        col4,
        label="Create Mapping",
        method=nl.MigManCreateMapping,
        success_message="Mapping successfully created.",
        spinner_message="Create Mappping... please wait.",
    )
    migman_button(
        col5,
        label="Load Mapping",
        method=nl.MigManLoadMapping,
        success_message="Mapping successfully loaded.",
        spinner_message="Load Mappping... please wait.",
    )
    migman_button(
        col6,
        label="Apply Mapping",
        method=nl.MigManApplyMapping,
        success_message="Mapping successfully applied.",
        spinner_message="Apply Mappping... please wait.",
    )
    migman_button(
        col7,
        label="Export Data",
        method=nl.MigManExportData,
        success_message="Data successfully exported.",
        spinner_message="Export Data... please wait.",
    )

    with st.spinner("Running precheck... please wait."):
        migmanstatus = nl.MigManPrecheckFiles()

    if migmanstatus:
        nemo_projects = nl.getProjects()
        data = {"project": [], "status_file": [], "status_nemo": []}
        for project, status in migmanstatus.items():
            data["project"].append(project)
            data["status_file"].append(status)
            data["status_nemo"].append(
                "ok" if any(nemo_project.displayName == project for nemo_project in nemo_projects) else "not found")
        df = pd.DataFrame(data)

        def highlight_errors(row):
            styles = []
            for col in row.index:
                if col == "status_file":
                    if row[col] == "ok":
                        styles.append("")
                    elif row[col].startswith("Warning!"):
                        styles.append("background-color: orange; color: black")
                    else:
                        styles.append("background-color: red; color: black")
                elif col == "status_nemo":
                    if row[col] == "ok":
                        styles.append("")
                    else:
                        styles.append("background-color: orange; color: black")
                else:
                    styles.append("")
            return styles

        styled_df = df.style.apply(highlight_errors, axis=1)
        st.dataframe(
            styled_df,
            use_container_width=True,
            column_config={
                "project": st.column_config.TextColumn(
                    label="Project",
                    width="small",  # Optionen: "small", "medium", "large"
                ),
                "status_file": st.column_config.TextColumn(label="Status (file)", width="medium"),
                "status_nemo": st.column_config.TextColumn(label="Status (nemo)", width="small"),},
        )
    else:
        st.write("No projects found in Migration Manager.")


def show_projects():
    """
    Displays the Projects page with a list of projects.
    """
    st.header("Projects Overview")
    projects = nl.getProjects()
    if projects:
        data = [project.to_dict() for project in projects]
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No projects found.")


# === Main Content Bereich ===
def content():

    page = st.session_state.get("page", "home")
    if page == "home":
        st.header("Welcome to the nemo_library UI")
        st.write("Please select a page from the sidebar to get started.")
    elif page == "MigMan":
        show_migman()
    elif page == "Projects":
        show_projects()
    elif page == "settings":
        st.header("Settings")
        config.showSettings(st)
    else:
        st.header(f"Page: {page}")
        if hasattr(nl, page):
            method = getattr(nl, page)
            if callable(method):
                result = method()
                st.write(result)
            else:
                st.error(f"{page} is not a callable method.")
        else:
            st.error(f"Page '{page}' not found in nemo_library.")


# === Main Function ===
def main():
    st.set_page_config(page_title="nemo_library UI", layout="wide")
    if not config.config_file_exists():
        st.stop()

    sidebar()
    content()

if __name__ == "__main__":
    main()
