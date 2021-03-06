import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

import sys
import traceback

class zstack_kvm_volume_file_checker(checker_header.TestChecker):
    '''check kvm volume file existencex . If it is in host, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_volume_file_checker, self).check()
        volume = self.test_obj.volume
        volume_installPath = volume.installPath
        if not volume_installPath:
            test_util.test_logger('Check result: [installPath] is Null for [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
            return self.judge(False)

        host = test_lib.lib_get_volume_host(volume)
        if not host:
            test_util.test_logger('Check result: can not find Host, who is belonged to same Zone Uuid of [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
            return self.judge(False)

        cmd = host_plugin.HostShellCmd()
        file_exist = "file_exist"
        cmd.command = '[ -f %s ] && echo %s' % (volume_installPath, file_exist)
        rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, host_plugin.HOST_SHELL_CMD_PATH), cmd)
        rsp = jsonobject.loads(rspstr)
        output = jsonobject.dumps(rsp.stdout)
        if file_exist in output:
            test_util.test_logger('Check result: [volume file: ] %s exist on [host name:] %s .' % (volume.uuid, host.name))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [volume file: ] %s does not exist on [host name:] %s .' % (volume.uuid, host.name))
            return self.judge(False)

class zstack_kvm_volume_attach_checker(checker_header.TestChecker):
    '''
        Check if volume is really attached to vm in libvirt system.
    '''
    def check(self):
        super(zstack_kvm_volume_attach_checker, self).check()
        volume = self.test_obj.volume
        if not volume.vmInstanceUuid:
            test_util.test_logger('Check result: [volume:] %s does NOT have vmInstanceUuid. It is not attached to any vm.' % volume.uuid)
            return self.judge(False)

        if not self.test_obj.target_vm:
            test_util.test_logger('Check result: test [volume:] %s does NOT have vmInstance record in test structure. Can not do furture checking.' % volume.uuid)
            return self.judge(False)

        vm = self.test_obj.target_vm.vm

        volume_installPath = volume.installPath
        if not volume_installPath:
            test_util.test_logger('Check result: [installPath] is Null for [volume uuid: ] %s. Can not check if volume is attached to vm.' % volume.uuid)
            return self.judge(False)
        host = test_lib.lib_get_vm_host(vm)
        cmd = vm_plugin.VmStatusCmd()
        cmd.vm_uuids = [vm.uuid]
        rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.VM_BLK_STATUS), cmd)
        rsp = jsonobject.loads(rspstr)
        output = jsonobject.dumps(rsp.vm_status[vm.uuid])
        if volume_installPath in output:
            test_util.test_logger('Check result: [volume file:] %s is found in [vm:] %s on [host:] %s .' % (volume.uuid, vm.uuid, host.managementIp))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [volume file:] %s is not found in [vm:] %s on [host:] %s .' % (volume.uuid, vm.uuid, host.managementIp))
            return self.judge(False)
