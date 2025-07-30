import json
from extras.models import Tag
from dcim.models import Device
from virtualization.models import VirtualMachine, VMInterface
from ipam.models import VLAN


class NetBoxCategorizer:
    def __init__(self, proxmox_connection):
        self.connection = proxmox_connection

        self.tag_warnings = set()
        self.vm_warnings = set()
        self.vminterface_warnings = set()

    def categorize_tags(self, parsed_tags):
        existing_tags_by_name = { tag.name: tag for tag in Tag.objects.all() }

        create = []
        update = []
        delete = []

        for px_tag in parsed_tags:
            if px_tag["name"] not in existing_tags_by_name:
                create.append(px_tag)
                continue
            nb_tag = existing_tags_by_name[px_tag["name"]]
            if not self._tags_equal(px_tag, nb_tag, existing_tags_by_name):
                update.append({"before": nb_tag, "after": px_tag})

        existing_tags_set = set(existing_tags_by_name.keys())
        parsed_tags_set = set(tag["name"] for tag in parsed_tags)
        deleted_tags_set = existing_tags_set - parsed_tags_set
        for tag_name in deleted_tags_set:
            delete.append(existing_tags_by_name[tag_name])

        return {
            "create": create,
            "update": update,
            "delete": delete,
            "warnings": list(self.tag_warnings),
        }

    def _tags_equal(self, px_tag, nb_tag, existing_tags_by_name={}):
        if px_tag["slug"] != nb_tag.slug:
            self.tag_warnings.add(
                f"Tag '{px_tag['name']}' already exists "
                f"and is not managed by this plugin!"
            )
            return True
        return px_tag["color"] == nb_tag.color

    def categorize_vms(self, parsed_vms):
        devices_by_name = {
            device.name: device for device in Device.objects.filter(cluster_id=self.connection.cluster.id)
        }
        existing_vms_by_name = {
            vm.name: vm for vm in VirtualMachine.objects.filter(cluster_id=self.connection.cluster.id)
        }
        tags_by_name = {
            t.name: t for t in Tag.objects.filter(slug__istartswith=f"nbpsync__")
        }

        create = []
        update = []
        delete = []

        names_to_create = set()
        names_to_update = set()

        for px_vm in parsed_vms:
            if px_vm["name"] not in existing_vms_by_name:
                if px_vm["name"] not in names_to_create:
                    names_to_create.add(px_vm["name"])
                    create.append(px_vm)
                    continue
            nb_vm = existing_vms_by_name[px_vm["name"]]
            if not self._vms_equal(px_vm, nb_vm, devices_by_name, tags_by_name):
                if px_vm["name"] not in names_to_update:
                    names_to_update.add(px_vm["name"])
                    update.append({"before": nb_vm, "after": px_vm})

        existing_vms_set = set(existing_vms_by_name.keys())
        parsed_vms_set = set(vm["name"] for vm in parsed_vms)
        deleted_vms_set = existing_vms_set - parsed_vms_set
        for vm_name in deleted_vms_set:
            delete.append(existing_vms_by_name[vm_name])

        return {
            "create": create,
            "update": update,
            "delete": delete,
            "warnings": list(self.vm_warnings),
        }

    def _vms_equal(self, px_vm, nb_vm, devices_by_name={}, tags_by_name={}):
        if devices_by_name.get(px_vm["device"]["name"]) is None:
            self.vm_warnings.add(
                f"Device '{px_vm['device']['name']}' in Cluster "
                f"'{self.connection.cluster.name}' not found!"
            )
        elif nb_vm.device is None:
            return False
        elif px_vm["device"]["name"] != nb_vm.device.name:
            return False
        if px_vm["status"] != nb_vm.status:
            return False
        if px_vm["vcpus"] != nb_vm.vcpus:
            return False
        if px_vm["memory"] != nb_vm.memory:
            return False
        if px_vm["disk"] != nb_vm.disk:
            return False
        if px_vm["custom_fields"]["vmid"] != nb_vm.custom_field_data["vmid"]:
            return False
        nb_tags = set([tag.name for tag in nb_vm.tags.all()])
        for px_tag in px_vm["tags"]:
            if px_tag["name"] not in nb_tags and tags_by_name.get(px_tag["name"]) is not None:
                return False
        return True

    def categorize_vminterfaces(self, parsed_vminterfaces):
        existing_vms = VirtualMachine.objects.filter(cluster_id=self.connection.cluster.id)
        existing_vminterfaces_by_name = {
            vmi.name: vmi for vmi in \
            VMInterface.objects.filter(virtual_machine__in=existing_vms)
        }
        vlans_by_vid = {vlan.vid: vlan for vlan in VLAN.objects.all()}

        create = []
        update = []
        delete = []

        names_to_create = set()
        names_to_update = set()

        for px_vmi in parsed_vminterfaces:
            if px_vmi["name"] not in existing_vminterfaces_by_name:
                if px_vmi["name"] not in names_to_create:
                    # Not sure why yet, but randomly proxmox sends me duplicated stuff
                    # (maybe in between migrations it gets messed up?)
                    names_to_create.add(px_vmi["name"])
                    create.append(px_vmi)
                    continue
            nb_vmi = existing_vminterfaces_by_name[px_vmi["name"]]
            if not self._vminterfaces_equal(px_vmi, nb_vmi, vlans_by_vid):
                if px_vmi["name"] not in names_to_update:
                    names_to_update.add(px_vmi["name"])
                    update.append({"before": nb_vmi, "after": px_vmi})

        existing_vminterfaces_set = set(existing_vminterfaces_by_name.keys())
        parsed_vminterfaces_set = set(vmi["name"] for vmi in parsed_vminterfaces)
        deleted_vminterfaces_set = existing_vminterfaces_set - parsed_vminterfaces_set

        for vmi_name in deleted_vminterfaces_set:
            delete.append(existing_vminterfaces_by_name[vmi_name])

        return {
            "create": create,
            "update": update,
            "delete": delete,
            "warnings": list(self.vminterface_warnings),
        }

    def _vminterfaces_equal(self, px_vmi, nb_vmi, vlans_by_vid={}):
        if vlans_by_vid.get(px_vmi["untagged_vlan"]["vid"]) is None:
            self.vminterface_warnings.add(
                f"VLAN with VID={px_vmi['untagged_vlan']['vid']} "
                "was not found!"
            )
        elif nb_vmi.untagged_vlan is None:
            return False
        elif int(px_vmi["untagged_vlan"]["vid"]) != int(nb_vmi.untagged_vlan.vid):
            return False
        if px_vmi["name"] != nb_vmi.name:
            return False
        if px_vmi["virtual_machine"]["name"] != nb_vmi.virtual_machine.name:
            return False
        if str(px_vmi["mac_address"]).upper() != str(nb_vmi.mac_address).upper():
            return False
        return True
