import json

from django.contrib.contenttypes.models import ContentType
from extras.models import CustomField
from virtualization.models import VirtualMachine


from .proxmox.connector import Proxmox
from .netbox.parser import NetBoxParser
from .netbox.categorizer import NetBoxCategorizer
from .netbox.updater import NetBoxUpdater
from .. import models

import time

def sync_cluster(connection_id):
    start = time.time()

    # silently try to create or update the VMID custom field
    vm_contenttype = ContentType.objects.get(app_label="virtualization", model="virtualmachine")
    vmid, created = CustomField.objects.update_or_create(
        name="vmid",
        defaults={
            "label": "[Proxmox] VM ID",
            "description": "[Proxmox] VM ID",
            "filter_logic": "exact",
            "type": "integer",
            # "object_types": [vm_contenttype.id],
            "required": True,
        }
    )
    vmid.object_types.set([vm_contenttype.id])

    proxmox_connection = models.ProxmoxConnection.objects.get(pk=connection_id)
    proxmox_data = get_proxmox_data(proxmox_connection)
    parsed_data = parse_proxmox_data(proxmox_connection, proxmox_data)
    categorized_data = categorize_operations(proxmox_connection, parsed_data)
    returned = update_netbox(proxmox_connection, categorized_data)

    end = time.time()
    elapsed = end - start

    return json.dumps({
        "data": returned,
        "elapsed": end - start
    })


def get_proxmox_data(proxmox_connection):
    px = Proxmox({
        "host": proxmox_connection.domain,
        "port": proxmox_connection.port,
        "user": proxmox_connection.user,
        "token": {
            "name": proxmox_connection.token_id,
            "value": proxmox_connection.token_secret,
        },
        "verify_ssl": proxmox_connection.verify_ssl,
    })
    return {
        "cluster": px.get_cluster(),
        "tags": px.get_tags(),
        "vms": px.get_vms(),
        "vminterfaces": px.get_vminterfaces(),
    }

def parse_proxmox_data(connection, proxmox_data):
    nb = NetBoxParser(connection)
    return {
        "tags": nb.parse_tags(proxmox_data["tags"]),
        "vms": nb.parse_vms(proxmox_data["vms"]),
        "vminterfaces": nb.parse_vminterfaces(proxmox_data["vminterfaces"]),
    }

def categorize_operations(connection, parsed_data):
    nb = NetBoxCategorizer(connection)
    return {
        "tags": nb.categorize_tags(parsed_data["tags"]),
        "vms": nb.categorize_vms(parsed_data["vms"]),
        "vminterfaces": nb.categorize_vminterfaces(parsed_data["vminterfaces"]),
    }

def update_netbox(connection, categorized_data):
    nb = NetBoxUpdater(connection)

    # Do not delete tags that are in use by other clusters (janky for now, but works)
    other_clusters = models.ProxmoxConnection.objects.exclude(pk=connection.id)
    nodelete_tagnames = set()
    for cluster in other_clusters:
        try:
            other_px = Proxmox({
                "host": cluster.domain,
                "port": cluster.port,
                "user": cluster.user,
                "token": {
                    "name": cluster.token_id,
                    "value": cluster.token_secret,
                },
                "verify_ssl": cluster.verify_ssl,
            })
            other_tags = other_px.get_tags()
            for tag in other_tags.keys():
                nodelete_tagnames.add(tag)
        except:
            # Yeah... fail silently...
            # If you can't connect to the cluster there's no way to know which tags not to delete
            # Just because another connection failed it does not mean this one has to
            pass


    return {
        "tags": nb.update_tags(categorized_data["tags"], nodelete_tagnames),
        "vms": nb.update_vms(categorized_data["vms"]),
        "vminterfaces": nb.update_vminterfaces(categorized_data["vminterfaces"]),
    }
