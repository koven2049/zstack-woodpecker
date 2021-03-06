'''

VM Volumes operations for test.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import apibinding.inventory as inventory
import account_operations

def create_volume_from_offering(volume_option):
    action = api_actions.CreateDataVolumeAction()
    action.diskOfferingUuid = volume_option.get_disk_offering_uuid()
    action.description = volume_option.get_description()
    timeout = volume_option.get_timeout()
    if not timeout:
        action.timeout = 120000
    else:
        action.timeout = timeout

    name = volume_option.get_name()
    if not name:
        action.name = 'test_volume'
    else:
        action.name = name

    test_util.action_logger('Create [Volume:] %s with [disk offering:] %s ' % (action.name, action.diskOfferingUuid))
    evt = account_operations.execute_action_with_session(action, volume_option.get_session_uuid())

    test_util.test_logger('[volume:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def create_volume_template(volume_uuid, backup_storage_uuid_list, name = None, \
        session_uuid = None):
    action = api_actions.CreateDataVolumeTemplateFromVolumeAction()
    action.volumeUuid = volume_uuid
    if name:
        action.name = name
    else:
        action.name = 'new_template_from_volume_%s' % volume_uuid

    action.backupStorageUuids = backup_storage_uuid_list
    test_util.action_logger('Create [Volume Template] for [Volume:] %s on [Backup Storages:] %s' % (volume_uuid, backup_storage_uuid_list))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Volume Templated:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def create_volume_from_template(image_uuid, ps_uuid, name = None, \
        session_uuid = None):
    action = api_actions.CreateDataVolumeFromVolumeTemplateAction()
    action.imageUuid = image_uuid
    action.primaryStorageUuid = ps_uuid
    if name:
        action.name = name
    else:
        action.name = 'new volume from template %s' % image_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Volume:] %s is created from [Volume Template:] %s on [Primary Storage:] %s.' % (evt.inventory.uuid, image_uuid, ps_uuid))
    return evt.inventory

def delete_volume(volume_uuid, session_uuid=None):
    action = api_actions.DeleteDataVolumeAction()
    action.uuid = volume_uuid
    action.timeout = 120000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Delete Volume [uuid:] %s' % volume_uuid)
    return evt

def attach_volume(volume_uuid, vm_uuid, session_uuid=None):
    action = api_actions.AttachDataVolumeToVmAction()
    action.vmInstanceUuid = vm_uuid
    action.volumeUuid = volume_uuid
    action.timeout = 120000
    test_util.action_logger('Attach Data Volume [uuid:] %s to [vm:] %s' % (volume_uuid, vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def detach_volume(volume_uuid, session_uuid=None):
    action = api_actions.DetachDataVolumeFromVmAction()
    action.uuid = volume_uuid
    action.timeout = 120000
    test_util.action_logger('Detach Volume [uuid:] %s' % volume_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_snapshot(snapshot_option, session_uuid=None):
    action = api_actions.CreateVolumeSnapshotAction()
    action.volumeUuid = snapshot_option.get_volume_uuid()
    action.name = snapshot_option.get_name()
    if not action.name:
        action.name = 'snapshot_for_volume_%s' % action.volumeUuid
    action.description = snapshot_option.get_description()
    action.timeout = 120000
    if snapshot_option.get_session_uuid():
        session_uuid = snapshot_option.get_session_uuid()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    snapshot = evt.inventory
    test_util.action_logger('Create [Snapshot:] %s [uuid:] %s for [volume:] %s' % \
            (action.name, snapshot.uuid, action.volumeUuid))
    return snapshot

def delete_snapshot(snapshot_uuid, session_uuid=None):
    action = api_actions.DeleteVolumeSnapshotAction()
    action.uuid = snapshot_uuid
    action.timeout = 60000
    test_util.action_logger('Delete [Snapshot:] %s ' % snapshot_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def use_snapshot(snapshot_uuid, session_uuid=None):
    action = api_actions.RevertVolumeFromSnapshotAction()
    action.uuid = snapshot_uuid
    action.timeout = 12000
    test_util.action_logger('Revert Volume by [Snapshot:] %s ' % snapshot_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def backup_snapshot(snapshot_uuid, backup_storage_uuid=None, session_uuid=None):
    action = api_actions.BackupVolumeSnapshotAction()
    action.uuid = snapshot_uuid
    action.backupStorageUuid = backup_storage_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    snapshot = evt.inventory
    test_util.action_logger('Backup [Snapshot:] %s to [bs]: %s ' \
            % (snapshot_uuid,\
            snapshot.backupStorageRefs[0].backupStorageUuid))
    return snapshot

def delete_snapshot_from_backupstorage(snapshot_uuid, bs_list=[], \
        delete_mode=None, session_uuid=None):
    action = api_actions.DeleteVolumeSnapshotFromBackupStorageAction()
    action.uuid = snapshot_uuid
    action.backupStorageUuids = bs_list
    action.deleteMode = delete_mode
    action.timeout = 12000
    test_util.action_logger('Delete [Snapshot:] %s from backup storage: %s' \
            % (snapshot_uuid, bs_list))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def create_volume_from_snapshot(snapshot_uuid, name=None, ps_uuid=None, \
        session_uuid=None):
    action = api_actions.CreateDataVolumeFromVolumeSnapshotAction()
    if name:
        action.name = name
    else:
        action.name = 'create_volume_from_snapshot'

    action.primaryStorageUuid = ps_uuid
    action.volumeSnapshotUuid = snapshot_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    volume = evt.inventory
    test_util.action_logger('[Volume:] %s is created from [snapshot]: %s on \
[primary storage:] %s' % (volume.uuid, snapshot_uuid, \
            volume.primaryStorageUuid))
    return volume

