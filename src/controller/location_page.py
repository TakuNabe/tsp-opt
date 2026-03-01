"""Streamlit location management page."""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import polars as pl
import streamlit as st
from pydantic import ValidationError

from src.app_service.location import LocationAppService
from src.infra.repository import StorageLocationRepository
from src.infra.storage_adapter import LocalStorageAdapter

_DATA_URI = Path(__file__).resolve().parents[2] / "etc" / "data" / "locations.csv"


def _get_service() -> LocationAppService:
    """Create the LocationAppService, cached in session state."""
    if "app_service" not in st.session_state:
        adapter = LocalStorageAdapter()
        repository = StorageLocationRepository(storage_adapter=adapter, uri=_DATA_URI)
        st.session_state["app_service"] = LocationAppService(
            repository=repository, storage_adapter=adapter, data_uri=_DATA_URI,
        )
    return st.session_state["app_service"]


def _invalidate_cache() -> None:
    """Clear the cached locations DataFrame to force a re-read."""
    st.session_state["locations_df"] = None


def _get_locations(service: LocationAppService) -> pl.DataFrame:
    """Get locations DataFrame, using a session state cache."""
    if st.session_state.get("locations_df") is None:
        st.session_state["locations_df"] = service.get_all_locations()
    return st.session_state["locations_df"]


def _render_upload_section(service: LocationAppService) -> None:
    """Render the CSV/Parquet file upload section."""
    st.subheader("Upload Location Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Parquet file", type=["csv", "parquet"],
    )

    if uploaded_file is not None:
        try:
            validated = service.upload_file(uploaded_file.getvalue(), uploaded_file.name)
            st.dataframe(validated.to_pandas(), use_container_width=True)
            st.caption(f"{validated.height} rows validated successfully.")

            if st.button("Confirm Upload (replaces all existing data)"):
                service.save_uploaded(validated)
                _invalidate_cache()
                st.success("Data uploaded and saved successfully.")
                st.rerun()
        except Exception as e:  # noqa: BLE001
            st.error(f"Upload failed: {e}")


def _render_location_table(locations: pl.DataFrame) -> None:
    """Render locations as a table."""
    st.subheader("Locations")
    if locations.is_empty():
        st.info("No locations found. Upload a file or add locations manually.")
        return
    st.dataframe(locations.to_pandas(), use_container_width=True)


def _render_map(locations: pl.DataFrame) -> None:
    """Render locations on a plotly map."""
    st.subheader("Map")
    if locations.is_empty():
        st.info("No locations to display on the map.")
        return

    pandas_locations = locations.to_pandas()
    fig = px.scatter_map(
        pandas_locations,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        hover_data={"address": True, "id": True, "latitude": ":.6f", "longitude": ":.6f"},
        zoom=10,
        height=600,
    )
    fig.update_layout(
        map_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_add_form(service: LocationAppService) -> None:
    """Render the form for adding a new location."""
    st.subheader("Add Location")
    with st.form("add_location_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            id_ = st.text_input("ID")
            name = st.text_input("Name")
            address = st.text_input("Address")
        with col2:
            latitude = st.number_input(
                "Latitude", min_value=-90.0, max_value=90.0, value=35.6895, format="%.6f",
            )
            longitude = st.number_input(
                "Longitude", min_value=-180.0, max_value=180.0, value=139.6917, format="%.6f",
            )

        submitted = st.form_submit_button("Add Location")
        if submitted:
            if not id_ or not name or not address:
                st.error("All fields are required.")
            else:
                try:
                    service.add_location(
                        id_=id_, name=name, address=address, latitude=latitude, longitude=longitude,
                    )
                    _invalidate_cache()
                    st.success(f"Location '{name}' added successfully.")
                    st.rerun()
                except (ValueError, ValidationError) as e:
                    st.error(f"Failed to add location: {e}")


def _render_edit_form(service: LocationAppService, locations: pl.DataFrame) -> None:
    """Render the form for editing an existing location."""
    st.subheader("Edit Location")
    if locations.is_empty():
        st.info("No locations available to edit.")
        return

    id_list = locations["id"].to_list()
    selected_id = st.selectbox("Select location to edit", id_list, key="edit_select")

    selected_row = locations.filter(pl.col("id") == selected_id).to_dicts()
    if not selected_row:
        return
    row = selected_row[0]

    with st.form("edit_location_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=row["name"])
            address = st.text_input("Address", value=row["address"])
        with col2:
            latitude = st.number_input(
                "Latitude", min_value=-90.0, max_value=90.0, value=row["latitude"], format="%.6f",
            )
            longitude = st.number_input(
                "Longitude", min_value=-180.0, max_value=180.0, value=row["longitude"], format="%.6f",
            )

        submitted = st.form_submit_button("Update Location")
        if submitted:
            try:
                service.update_location(
                    id_=selected_id, name=name, address=address,
                    latitude=latitude, longitude=longitude,
                )
                _invalidate_cache()
                st.success(f"Location '{selected_id}' updated successfully.")
                st.rerun()
            except (ValueError, ValidationError) as e:
                st.error(f"Failed to update location: {e}")


def _render_delete_section(service: LocationAppService, locations: pl.DataFrame) -> None:
    """Render the delete location section."""
    st.subheader("Delete Location")
    if locations.is_empty():
        st.info("No locations available to delete.")
        return

    id_list = locations["id"].to_list()
    selected_id = st.selectbox("Select location to delete", id_list, key="delete_select")

    selected_row = locations.filter(pl.col("id") == selected_id).to_dicts()
    if selected_row:
        st.json(selected_row[0])

    if st.button("Delete Location", type="primary"):
        service.delete_location(selected_id)
        _invalidate_cache()
        st.success(f"Location '{selected_id}' deleted.")
        st.rerun()


def render_page() -> None:
    """Compose all location management sections into the page."""
    service = _get_service()
    locations = _get_locations(service)

    tab_view, tab_manage, tab_upload = st.tabs(["View", "Manage", "Upload"])

    with tab_view:
        _render_location_table(locations)
        _render_map(locations)

    with tab_manage:
        _render_add_form(service)
        st.divider()
        _render_edit_form(service, locations)
        st.divider()
        _render_delete_section(service, locations)

    with tab_upload:
        _render_upload_section(service)
