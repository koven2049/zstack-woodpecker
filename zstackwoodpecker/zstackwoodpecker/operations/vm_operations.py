'''

All VM operations for test.

@author: Youyk
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import config_operations

import os
import inspect

def create_vm(vm_create_option):
    create_vm = api_actions.CreateVmInstanceAction()
    name = vm_create_option.get_name()
    if not name:
        create_vm.name = 'test_vm_default_name'
    else:
        create_vm.name = name

    create_vm.imageUuid = vm_create_option.get_image_uuid()
    create_vm.zoneUuid = vm_create_option.get_zone_uuid()
    create_vm.clusterUuid = vm_create_option.get_cluster_uuid()
    create_vm.hostUuid = vm_create_option.get_host_uuid()
    create_vm.instanceOfferingUuid = vm_create_option.get_instance_offering_uuid()
    create_vm.l3NetworkUuids = vm_create_option.get_l3_uuids()
    create_vm.defaultL3NetworkUuid = vm_create_option.get_default_l3_uuid()
    #If there are more than 1 network uuid, the 1st one will be the default l3.
    if len(create_vm.l3NetworkUuids) > 1 and not create_vm.defaultL3NetworkUuid:
        create_vm.defaultL3NetworkUuid = create_vm.l3NetworkUuids[0]

    vm_type = vm_create_option.get_vm_type()
    if not vm_type:
        create_vm.type = 'UserVm'
    else:
        create_vm.type = vm_type

    timeout = vm_create_option.get_timeout()
    if not timeout:
        create_vm.timeout = 600000
    else:
        create_vm.timeout = timeout

    create_vm.dataDiskOfferingUuids = vm_create_option.get_data_disk_uuids()

    test_util.action_logger('Create VM: %s with [image:] %s and [l3_network:] %s' % (create_vm.name, create_vm.imageUuid, create_vm.l3NetworkUuids))
    evt = account_operations.execute_action_with_session(create_vm, vm_create_option.get_session_uuid())
    test_util.test_logger('[vm:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

#The root volume will not be deleted immediately. It will only be reclaimed by system maintenance checking.
def destroy_vm(vm_uuid, session_uuid=None):
    action = api_actions.DestroyVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 120000
    test_util.action_logger('Destroy VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def stop_vm(vm_uuid, session_uuid=None):
    action = api_actions.StopVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 120000
    test_util.action_logger('Stop VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def start_vm(vm_uuid, session_uuid=None):
    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 120000
    test_util.action_logger('Start VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def reboot_vm(vm_uuid, session_uuid=None):
    action = api_actions.RebootVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 120000
    test_util.action_logger('Reboot VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def migrate_vm(vm_uuid, host_uuid, session_uuid=None):
    action = api_actions.MigrateVmAction()
    action.vmInstanceUuid = vm_uuid
    action.hostUuid = host_uuid
    action.timeout = 240000
    test_util.action_logger('Migrate VM [uuid:] %s to Host [uuid:] %s' % (vm_uuid, host_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory 
