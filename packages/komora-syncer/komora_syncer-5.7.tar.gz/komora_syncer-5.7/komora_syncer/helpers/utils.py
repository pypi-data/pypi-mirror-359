from lat_lon_parser import parse
from loguru import logger


def batch_query(method, id_list, batch_size=50, id_param="id__in", **kwargs):
    """
    Execute a query in batches to avoid Request-URI Too Long errors.

    Args:
        method: The pynetbox query method to call (e.g., nb.dcim.interfaces.filter)
        id_list: List of IDs to split into batches
        batch_size: Maximum number of IDs per batch
        id_param: Parameter name for the ID filter (default: 'id__in')
        **kwargs: Additional filter parameters to pass to the query method

    Returns:
        List of results from all batches combined
    """
    results = []
    total_batches = (len(id_list) + batch_size - 1) // batch_size

    for i in range(0, len(id_list), batch_size):
        batch = id_list[i : i + batch_size]
        logger.debug(f"Processing batch {(i // batch_size) + 1}/{total_batches} with {len(batch)} items")

        # Create params dict with the batch of IDs
        batch_params = {id_param: batch}
        # Add any additional filter parameters
        batch_params.update(kwargs)

        # Execute the query and extend the results
        batch_results = list(method(**batch_params))
        results.extend(batch_results)

    logger.debug(f"Query completed with {len(results)} total results")
    return results


def build_tenant_name(client_id, name):
    # Clean the name to remove quotation marks
    cleaned_name = clean_organization_name(name) if name else name
    return f"{client_id} - {cleaned_name}"[0:100].strip()


def clean_organization_name(name):
    """
    Remove double quotation marks from organization names.
    Removes only double (") quotes from the organization name.

    Args:
        name (str): The organization name to clean

    Returns:
        str: The cleaned organization name
    """
    if not name:
        return name

    # Remove only double quotes from the name
    cleaned_name = name.replace('"', "")
    return cleaned_name.strip()


def sanitize_lat_lon(lat_or_lon: str) -> float:
    """
    Gets latitude or longitude string and returns float with 6 decimal places
    This format is required in Netbox
    """
    if not lat_or_lon:
        return None

    try:
        result = parse(lat_or_lon)
    except ValueError:
        return None

    if result:
        return round(result, 6)
    else:
        return None


def check_required_custom_fields(nb_connection, exit_on_error=True):
    """
    Check if all required custom fields exist in NetBox.
    Exits the program with an error message if any custom fields are missing.

    Args:
        nb_connection: NetBox API connection instance
        exit_on_error: Whether to exit the program on error (default: True)

    Returns:
        bool: True if all fields exist or check was skipped, False if there are missing fields
    """
    # Define all required custom fields organized by NetBox model
    required_custom_fields = {
        "tenancy.tenant": [
            "client_id",
            "komora_id",
            "client_name",
            "komora_is_customer",
            "komora_is_supplier",
            "komora_is_vip",
            "komora_is_actual",
            "komora_is_member",
            "komora_vip_note",
        ],
        "circuits.provider": ["client_id", "client_name", "komora_id", "tenant"],
        "dcim.site": ["komora_id", "komora_url", "code", "type"],
        "dcim.region": ["komora_id", "region_type"],
        "dcim.location": ["komora_id"],
        "dcim.device": ["komora_id", "komora_url"],
    }

    missing_fields = []
    connectivity_errors = []

    for model_name, field_names in required_custom_fields.items():
        try:
            # Get the custom fields for this model
            app_label, model = model_name.split(".")
            custom_fields_response = nb_connection.extras.custom_fields.filter(content_types=model_name)

            # Extract existing field names
            existing_fields = {cf.name for cf in custom_fields_response}

            # Check for missing fields
            for field_name in field_names:
                if field_name not in existing_fields:
                    missing_fields.append(f"{model_name}.{field_name}")

        except Exception as e:
            error_msg = str(e)
            logger.exception(f"Unable to check custom fields for model {model_name}")

            # Check if this is a connectivity error (503, 502, 500, connection errors)
            if any(code in error_msg for code in ["503", "502", "500", "Connection", "connection"]):
                connectivity_errors.append(f"{model_name}.* (connectivity issue: {error_msg})")
            else:
                missing_fields.append(f"{model_name}.* (unable to check: {error_msg})")

    # Handle connectivity errors differently
    if connectivity_errors and not missing_fields:
        logger.warning("Unable to check custom fields due to connectivity issues with NetBox:")
        for field in sorted(connectivity_errors):
            logger.warning(f"  - {field}")
        logger.warning("NetBox appears to be unavailable. Proceeding with synchronization...")
        logger.warning("Please ensure NetBox is accessible and custom fields are properly configured.")
        return True

    if missing_fields:
        logger.critical("Missing required custom fields in NetBox:")
        for field in sorted(missing_fields):
            logger.critical(f"  - {field}")
        logger.critical("\nPlease create these custom fields in NetBox before running the synchronizer.")

        if exit_on_error:
            exit(1)
        return False

    logger.info("All required custom fields are present in NetBox")
    return True
