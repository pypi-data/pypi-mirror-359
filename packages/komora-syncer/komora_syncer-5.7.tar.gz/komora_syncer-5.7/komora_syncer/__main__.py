import traceback

import click
from loguru import logger

from komora_syncer.config import configure_logger
from komora_syncer.connections.NetboxConnection import NetboxConnection
from komora_syncer.helpers.utils import check_required_custom_fields
from komora_syncer.processors.Synchronizer import Synchronizer

SYNC_OPTIONS = ["all", "organizations", "regions", "sites", "devices"]

# Initialize logging configuration
configure_logger()


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--sync",
    "-s",
    type=click.Choice(SYNC_OPTIONS),
    multiple=True,
    default=["all"],
    help="what should be synced",
)
@click.option("--site", "-t", type=click.STRING, help="Name of site to deploy")
@click.option("--skip-custom-fields-check", is_flag=True, help="Skip checking for required custom fields in NetBox")
def synchronize(sync, site, skip_custom_fields_check):
    """
    Synchronize data between Netbox and Komora
    """
    # Check if all required custom fields exist in NetBox before starting synchronization
    if not skip_custom_fields_check:
        logger.info("Checking required custom fields in NetBox...")
        nb_connection = NetboxConnection.get_connection()
        check_required_custom_fields(nb_connection)
    else:
        logger.info("Skipping custom fields check as requested")

    synchronizer = Synchronizer()

    if site and "sites" not in sync:
        logger.critical("Site option '--site' is only available with sites 'synchronize --sync sites' synchronization")
        logger.critical("Exiting")
        return

    if site and "sites" in sync:
        try:
            # Syncs Sites / Site, Location
            synchronizer.sync_sites(site_name=site)
            return
        except Exception as e:
            logger.error(f"Unable to synchronize site '{site}' - {e}")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if "all" in sync or "organizations" in sync:
        try:
            # Syncs Organizations / Tenants
            synchronizer.sync_organizations()
        except Exception as e:
            logger.error("Unable to synchronize organizations")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if "all" in sync or "organizations" in sync:
        try:
            # Syncs Organizations / Suppliers
            synchronizer.sync_organization_suppliers()
        except Exception as e:
            logger.error("Unable to synchronize organizations (supplier)")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if "all" in sync or "regions" in sync:
        try:
            # Syncs Regions, Disctricts and Municipalities / Regions
            synchronizer.sync_regions()
        except Exception as e:
            logger.error("Unable to synchronize regions")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if "all" in sync or "sites" in sync:
        try:
            # Syncs Sites / Site, Location
            synchronizer.sync_sites()
        except Exception as e:
            logger.error("Unable to synchronize sites")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if "all" in sync or "devices" in sync:
        try:
            synchronizer.sync_devices()
        except Exception as e:
            logger.error("Unable to synchronize devices")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return


cli.add_command(synchronize)


if __name__ == "__main__":
    # Display CLI
    cli()
