import pytest
import subprocess
import netifaces
import re
from .services import Vehicle
from django.conf import settings


from unittest.mock import MagicMock
from unittest.mock import patch, ANY
from django.test import TestCase
import time
import datetime
import os


class MockProc():
    pid = None


class TestVehicleUnit(TestCase):
    def setUp(self):
        Vehicle.proc = None
        self.mock_proc = MockProc()
        self.mock_proc.pid = 999
        self.test_data_dir = settings.ROOT_DIR / "dkconsole" / "test_data"

    def test_settings(self):
        assert Vehicle.carapp_path
        assert Vehicle.venv_path

    @patch('subprocess.Popen')
    def test_start_driving_without_js(self, popen):
        popen.return_value = self.mock_proc

        val = Vehicle.start_driving(False)
        popen.assert_called_with([f"{Vehicle.venv_path}/python", Vehicle.carapp_path +
                                  "/manage.py", "drive"], stdout=ANY)
        assert val == 999

    def test_drive_log(self):
        assert Vehicle.drive_log() is not None

    @patch('subprocess.Popen')
    def test_start_driving_with_js(self, popen):
        popen.return_value = self.mock_proc

        val = Vehicle.start_driving(True)

        popen.assert_called_with([f"{Vehicle.venv_path}/python", Vehicle.carapp_path +
                                  "/manage.py", "drive", "--js"], stdout=ANY)
        assert val == 999

    @patch('subprocess.Popen')
    def test_start_autopilot(self, popen):
        with self.assertRaises(FileNotFoundError) as context:
            val = Vehicle.start_autopilot(True, "some_non_exist_model_path")

        model_path = settings.MODEL_DIR / "job_118"

        val = Vehicle.start_autopilot(True, model_path)
        popen.assert_called_with([f"{Vehicle.venv_path}/python", Vehicle.carapp_path + "/manage.py",
                                  "drive", "--js", f"--model={model_path}"])

    @patch('subprocess.check_output')
    def test_get_current_ssid(self, check_output):
        check_output.side_effect = [
            'wlo1      IEEE 802.11  ESSID:"DONKEY01"',
            'wlo1      No such device'
        ]

        ssid = Vehicle.get_current_ssid()
        assert ssid == "DONKEY01"

        ssid = Vehicle.get_current_ssid()
        assert ssid is None

    @patch('netifaces.interfaces')
    @patch('netifaces.ifaddresses')
    def test_get_ip_address(self, ifaddresses, interfaces):
        netifaces.interfaces.side_effect = [['wlo1'], ['wlo1'], ['wlo1']]
        ifaddresses.side_effect = [
            {},
            {
                netifaces.AF_LINK: [{'addr': 'a0:51:0b:61:de:e2', 'broadcast': 'ff:ff:ff:ff:ff:ff'}]
            },
            {
                netifaces.AF_LINK: [{'addr': 'a0:51:0b:61:de:e2', 'broadcast': 'ff:ff:ff:ff:ff:ff'}],
                netifaces.AF_INET: [{'addr': '192.168.3.2', 'netmask': '255.255.255.0', 'broadcast': '192.168.3.255'}]
            }
        ]

        ip_address = Vehicle.get_wlan_ip_address()
        assert ip_address is None

        ip_address = Vehicle.get_wlan_ip_address()
        assert ip_address is None

        ip_address = Vehicle.get_wlan_ip_address()
        assert ip_address == "192.168.3.2"

    @patch('netifaces.interfaces')
    @patch('netifaces.ifaddresses')
    def test_get_mac_address(self, ifaddresses, interfaces):
        netifaces.interfaces.side_effect = [['wlo1'], ['wlo1']]
        ifaddresses.side_effect = [
            {},
            {
                netifaces.AF_LINK: [{'addr': 'a0:51:0b:61:de:e2', 'broadcast': 'ff:ff:ff:ff:ff:ff'}]
            }
        ]

        mac_address = Vehicle.get_wlan_mac_address()
        assert mac_address is None

        mac_address = Vehicle.get_wlan_mac_address()
        assert mac_address == "a0:51:0b:61:de:e2"

    @patch('netifaces.interfaces')
    @patch('netifaces.ifaddresses')
    def test_is_wlan_connected(self, ifaddresses, interfaces):
        netifaces.interfaces.side_effect = [['wlo1'], ['wlo1'], ['wlo1']]
        ifaddresses.side_effect = [
            {},
            {
                netifaces.AF_LINK: [{'addr': 'a0:51:0b:61:de:e2', 'broadcast': 'ff:ff:ff:ff:ff:ff'}]
            },
            {
                netifaces.AF_LINK: [{'addr': 'a0:51:0b:61:de:e2', 'broadcast': 'ff:ff:ff:ff:ff:ff'}],
                netifaces.AF_INET: [{'addr': '192.168.3.2', 'netmask': '255.255.255.0', 'broadcast': '192.168.3.255'}]
            }

        ]

        # Empty address returned
        assert Vehicle.is_wlan_connected() is False

        # IP address missing
        assert Vehicle.is_wlan_connected() is False

        # IP address present
        assert Vehicle.is_wlan_connected() is True

    # def test_is_wlan_connected(self):

    #     assert Vehicle.is_wlan_connected() == True
    #     # assert Vehicle.is_wlan_connected() == True

    @patch('subprocess.check_output')
    def test_update_console_software(self, mock_check_output):
        Vehicle.update_console_software()

    def test_remove_all_network(self):
        Vehicle.remove_all_network()



    # TODO: Fix mock
    def test_sync_time(self):
        current = datetime.datetime.now()
        print(current)
        with patch('subprocess.check_output', return_value=current) as mock_method:
            result = Vehicle.sync_time(current)
            mock_method.assert_called_once()
            assert result == current

    def test_first_time_finish(self):
        hostname = None
        ssid = None
        psk = None

        with patch('dkconsole.vehicle.services.Vehicle.write_setup_file_to_disk') as mock_write_setup_file_to_disk:
            Vehicle.first_time_finish(hostname, ssid, psk)
            mock_write_setup_file_to_disk.assert_called_once()
            assert Vehicle.reboot_required is False

        hostname = "abcd1234"
        ssid = None
        psk = None

        with patch('dkconsole.vehicle.services.Vehicle.set_hostname') as mock_set_hostname:
            with patch('dkconsole.vehicle.services.Vehicle.write_setup_file_to_disk') as mock_write_setup_file_to_disk:
                Vehicle.first_time_finish(hostname, ssid, psk)
                mock_set_hostname.assert_called_once()
                mock_write_setup_file_to_disk.assert_called_once()
                assert Vehicle.reboot_required is True

        hostname = None
        ssid = "ssid1234"
        psk = "psk1234"

        with patch('dkconsole.vehicle.services.Vehicle.add_network', return_value=True)  as mock_add_network:
            with patch('dkconsole.vehicle.services.Vehicle.write_setup_file_to_disk') as mock_write_setup_file_to_disk:
                Vehicle.first_time_finish(hostname, ssid, psk)
                mock_add_network.assert_called_once()
                mock_write_setup_file_to_disk.assert_called_once()
                assert Vehicle.reboot_required is True

    def test_update_host_table(self):
        path = self.test_data_dir / "hosts"
        sudo_required = False
        return_value = path, sudo_required

        with patch('dkconsole.vehicle.services.Vehicle.host_table_path', return_value=return_value):
            Vehicle.update_host_table("testing123")
            with open(path, 'r') as f:
                output = f.readlines()
                assert "127.0.1.1\ttesting123\n" in output


    def test_update_env(self):
        config_data = {"CARAPP_PATH": "/home/pi/mycar_mm1"}
        path = settings.CONSOLE_DIR + "/.env_pi4"
        Vehicle.edit_env(path, config_data)
        with open(path, 'r') as f:
            check = re.search('CARAPP_PATH=/home/pi/mycar_mm1', f.read())
            assert check.group() == 'CARAPP_PATH=/home/pi/mycar_mm1'

    def test_flatten_config_map(self):
        result = Vehicle.flatten_config_map()
        assert result['STEERING_LEFT_PWM']['dtype'] == "str" or result['STEERING_LEFT_PWM']['dtype'] == "mc"


    def test_scan_network(self):
        with patch('subprocess.check_output') as mock_method:
            mock_method.return_value = b'signal\nTSEZ2019\nTSEZ2019\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\nTSEZ2019\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\nrobocar\nDIRECT-1e-HP\nDIRECT-02-HP\nTSEZ2019\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\nSzRj9dvj\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\nSzRj9dvj\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\nTSEZ2019\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\nMan\nLions\n\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\n\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\nTSEZ2019\nKT\n\n\\x00\\x00\nMan\n\n'

            networks = Vehicle.scan_network()
            assert networks is None

    def test_list_network(self):
        output = b"0\tProactive_JBB_Guest\tany\t\n1\tPROACTIVE_JBB_5G\tany\t\n2\tPROACTIVE_JBB_5G\tany\t\n3\trobocar\tany\t\n4\trobocar\tany\t\n"


    def test_remove_network(self):
        output = []
        output.append({'id': 'ssid1', 'network': '0'})
        output.append({'id': 'ssid2', 'network': '1'})
        output.append({'id': 'robocar', 'network': '2'})
        output.append({'id': 'robocar', 'network': '3'})

        with patch('dkconsole.vehicle.services.Vehicle.list_network', return_value=output)  as mock_add_network:
            with patch('subprocess.check_output') as mock_method:
                Vehicle.remove_network("robocar")
                assert mock_method.call_count == 2


    def test_reset_config(self):
        Vehicle.reset_config()
        path = Vehicle.carapp_path + "/myconfig copy.py"
        assert os.stat(path).st_size == 0

    def test_get_config(self):
        Vehicle.read_value_from_config(Vehicle.config())

    def test_extract_value_from_config_line(self):
        config_path = Vehicle.carapp_path + "/config.py"
        myconfig_path = Vehicle.carapp_path + "/myconfig.py"

        with open(myconfig_path, 'r') as f_config:
            with open(myconfig_path, 'r') as f_myconfig:
                config_content = f_config.readlines()
                myconfig_content = f_myconfig.readlines()

                assert Vehicle.extract_value_from_config_line(config_content, 'MM1_STEERING_MID') is not None
                assert Vehicle.extract_value_from_config_line(myconfig_content, 'MM1_STEERING_MID') is not None


    def test_replace_key_in_lines(self):
        content = '''#DRIVE_TRAIN_TYPE = "MM1"
# DRIVE_TRAIN_TYPE = "MM1"
DRIVE_TRAIN_TYPE = "MM1"
'''

        assert Vehicle.replace_key_in_lines(content.splitlines(), 'DRIVE_TRAIN_TYPE', 'DRIVE_TRAIN_TYPE = "ABC"') == [
            'DRIVE_TRAIN_TYPE = "ABC"',
            'DRIVE_TRAIN_TYPE = "ABC"',
            'DRIVE_TRAIN_TYPE = "ABC"'
        ]


        content = '#DRIVE_TRAIN_TYPE = "MM1"'
        assert Vehicle.replace_key_in_lines(content.splitlines(), 'DRIVE_TRAIN_TYPE', 'DRIVE_TRAIN_TYPE = "ABC"') == [
            'DRIVE_TRAIN_TYPE = "ABC"'
        ]

        content = '#DRIVE_TRAIN_TYPE = "MM1"'
        assert Vehicle.replace_key_in_lines(content.splitlines(), 'STEERING_RIGHT_PWM', 'STEERING_RIGHT_PWM = 123') == [
            '#DRIVE_TRAIN_TYPE = "MM1"',
            'STEERING_RIGHT_PWM = 123',
        ]

    def test_replace_all_keys_in_lines(self):
        content = '''#DRIVE_TRAIN_TYPE = "MM1"
# DRIVE_TRAIN_TYPE = "MM1"
DRIVE_TRAIN_TYPE = "MM1"'''

        config_data = {'DRIVE_TRAIN_TYPE': 'hahah', 'STEERING_RIGHT_PWM': 'hahah2'}
        flattened_map = Vehicle.flatten_config_map()
        assert Vehicle.replace_all_keys_in_lines(content.splitlines(), config_data, flattened_map) == [
            'DRIVE_TRAIN_TYPE = "hahah"\n',
            'DRIVE_TRAIN_TYPE = "hahah"\n',
            'DRIVE_TRAIN_TYPE = "hahah"\n',
            'STEERING_RIGHT_PWM = hahah2\n',
        ]

    def test_update_config(self):
        path = self.test_data_dir / "myconfig.py"

        with open(path, 'r') as f:
            content = Vehicle.file_readlines(f)
            print(content)

        config_data = {"DRIVE_TRAIN_TYPE": "SERVO_ESC", "MM1_MAX_FORWARD": 2000}

        with patch('dkconsole.vehicle.services.Vehicle.file_readlines', return_value=content) as mock_file_readlines:
            with patch('dkconsole.vehicle.services.Vehicle.file_writelines') as mock_file_writelines:
                Vehicle.update_config(config_data)
                mock_file_readlines.assert_called_once()
                mock_file_writelines.assert_called_once()
                found = False

                for line in mock_file_writelines.call_args_list[0][0][1]:
                    if 'DRIVE_TRAIN_TYPE = "SERVO_ESC"' in line:
                        found = True

                assert found

    def test_battery_level_in_percentage(self):
        assert None == Vehicle.battery_level_in_percentage()

    def test_calculate_battery_percentage(self):
        assert 100 ==Vehicle.calculate_battery_percentage(8.4)
        assert 50 ==Vehicle.calculate_battery_percentage(7.7)
        assert 0 ==Vehicle.calculate_battery_percentage(7)
        assert -1 ==Vehicle.calculate_battery_percentage(6.9)
