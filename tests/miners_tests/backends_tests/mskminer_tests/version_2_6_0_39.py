"""Tests for MSK miner firmware version 2.6.0.39"""

import unittest
from dataclasses import fields
from unittest.mock import patch

from pyasic import APIError, MinerData
from pyasic.data import Fan, HashBoard
from pyasic.device.algorithm import SHA256Unit
from pyasic.miners.antminer import MSKMinerS19NoPIC

POOLS = [
    {
        "url": "stratum+tcp://stratum.pool.io:3333",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
    {
        "url": "stratum+tcp://stratum.pool.io:3334",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
    {
        "url": "stratum+tcp://stratum.pool.io:3335",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
]

data = {
    MSKMinerS19NoPIC: {
        "web_info_v1": {
            # needs updates with real data
            "network_info": {
                "result": {
                    "address": "192.168.1.10",
                    "macaddr": "12:34:56:78:90:12",
                    "netmask": "255.255.255.0",
                }
            }
        },
        "rpc_version": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 1738856891,
                    "Code": 22,
                    "Msg": "BMMiner versions",
                    "Description": "bmminer 1.0.0",
                }
            ],
            "VERSION": [
                {
                    "BMMiner": "4.11.1 rwglr",
                    "API": "3.1",
                    "Miner": "0.0.1.3",
                    "CompileTime": "10 Dec 2024 14:34:31 GMT",
                    "Type": "S19-88 v.2.6.0.39 ",
                }
            ],
            "id": 1,
        },
        "rpc_stats": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 1738856891,
                    "Code": 70,
                    "Msg": "BMMiner stats",
                    "Description": "bmminer 1.0.0",
                }
            ],
            "STATS": [
                {
                    "BMMiner": "4.11.1 rwglr",
                    "Miner": "0.0.1.3",
                    "CompileTime": "10 Dec 2024 14:34:31 GMT",
                    "Type": "S19-88 v.2.6.0.39 ",
                },
                {
                    "STATS": 0,
                    "ID": "BC50",
                    "Elapsed": 1926,
                    "Calls": 0,
                    "Wait": 0.000000,
                    "Max": 0.000000,
                    "Min": 99999999.000000,
                    "GHS 5s": 99989.59,
                    "GHS av": 99761.40,
                    "miner_count": 3,
                    "frequency": "",
                    "fan_num": 4,
                    "fan1": 5010,
                    "fan2": 5160,
                    "fan3": 5070,
                    "fan4": 5040,
                    "fan5": 0,
                    "fan6": 0,
                    "fan7": 0,
                    "fan8": 0,
                    "temp_num": 3,
                    "temp1": 45,
                    "temp2": 45,
                    "temp3": 47,
                    "temp4": 0,
                    "temp5": 0,
                    "temp6": 0,
                    "temp7": 0,
                    "temp8": 0,
                    "temp9": 0,
                    "temp10": 0,
                    "temp11": 0,
                    "temp12": 0,
                    "temp13": 0,
                    "temp14": 0,
                    "temp15": 0,
                    "temp16": 0,
                    "temp2_1": 59,
                    "temp2_2": 57,
                    "temp2_3": 58,
                    "temp2_4": 0,
                    "temp2_5": 0,
                    "temp2_6": 0,
                    "temp2_7": 0,
                    "temp2_8": 0,
                    "temp2_9": 0,
                    "temp2_10": 0,
                    "temp2_11": 0,
                    "temp2_12": 0,
                    "temp2_13": 0,
                    "temp2_14": 0,
                    "temp2_15": 0,
                    "temp2_16": 0,
                    "temp3_1": 59,
                    "temp3_2": 56,
                    "temp3_3": 57,
                    "temp3_4": 0,
                    "temp3_5": 0,
                    "temp3_6": 0,
                    "temp3_7": 0,
                    "temp3_8": 0,
                    "temp3_9": 0,
                    "temp3_10": 0,
                    "temp3_11": 0,
                    "temp3_12": 0,
                    "temp3_13": 0,
                    "temp3_14": 0,
                    "temp3_15": 0,
                    "temp3_16": 0,
                    "temp_pcb1": "45-42-45-42",
                    "temp_pcb2": "45-42-45-42",
                    "temp_pcb3": "47-43-47-43",
                    "temp_pcb4": "0-0-0-0",
                    "temp_pcb5": "0-0-0-0",
                    "temp_pcb6": "0-0-0-0",
                    "temp_pcb7": "0-0-0-0",
                    "temp_pcb8": "0-0-0-0",
                    "temp_pcb9": "0-0-0-0",
                    "temp_pcb10": "0-0-0-0",
                    "temp_pcb11": "0-0-0-0",
                    "temp_pcb12": "0-0-0-0",
                    "temp_pcb13": "0-0-0-0",
                    "temp_pcb14": "0-0-0-0",
                    "temp_pcb15": "0-0-0-0",
                    "temp_pcb16": "0-0-0-0",
                    "temp_chip1": "59-59-59-59",
                    "temp_chip2": "57-56-57-56",
                    "temp_chip3": "58-57-58-57",
                    "temp_chip4": "0-0-0-0",
                    "temp_chip5": "0-0-0-0",
                    "temp_chip6": "0-0-0-0",
                    "temp_chip7": "0-0-0-0",
                    "temp_chip8": "0-0-0-0",
                    "temp_chip9": "0-0-0-0",
                    "temp_chip10": "0-0-0-0",
                    "temp_chip11": "0-0-0-0",
                    "temp_chip12": "0-0-0-0",
                    "temp_chip13": "0-0-0-0",
                    "temp_chip14": "0-0-0-0",
                    "temp_chip15": "0-0-0-0",
                    "temp_chip16": "0-0-0-0",
                    "total_rateideal": 99674.88,
                    "total_freqavg": 0.00,
                    "total_acn": 264,
                    "total_rate": 99989.59,
                    "chain_rateideal1": 33677.28,
                    "chain_rateideal2": 32788.06,
                    "chain_rateideal3": 33209.54,
                    "chain_rateideal4": 31436.24,
                    "chain_rateideal5": 31436.24,
                    "chain_rateideal6": 31436.24,
                    "chain_rateideal7": 31436.24,
                    "chain_rateideal8": 31436.24,
                    "chain_rateideal9": 31436.24,
                    "chain_rateideal10": 31436.24,
                    "chain_rateideal11": 31436.24,
                    "chain_rateideal12": 31436.24,
                    "chain_rateideal13": 31436.24,
                    "chain_rateideal14": 31436.24,
                    "chain_rateideal15": 31436.24,
                    "chain_rateideal16": 31436.24,
                    "temp_max": 47,
                    "no_matching_work": 0,
                    "chain_acn1": 88,
                    "chain_acn2": 88,
                    "chain_acn3": 88,
                    "chain_acn4": 0,
                    "chain_acn5": 0,
                    "chain_acn6": 0,
                    "chain_acn7": 0,
                    "chain_acn8": 0,
                    "chain_acn9": 0,
                    "chain_acn10": 0,
                    "chain_acn11": 0,
                    "chain_acn12": 0,
                    "chain_acn13": 0,
                    "chain_acn14": 0,
                    "chain_acn15": 0,
                    "chain_acn16": 0,
                    "chain_acs1": " oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo",
                    "chain_acs2": " oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo",
                    "chain_acs3": " oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo oo",
                    "chain_acs4": "",
                    "chain_acs5": "",
                    "chain_acs6": "",
                    "chain_acs7": "",
                    "chain_acs8": "",
                    "chain_acs9": "",
                    "chain_acs10": "",
                    "chain_acs11": "",
                    "chain_acs12": "",
                    "chain_acs13": "",
                    "chain_acs14": "",
                    "chain_acs15": "",
                    "chain_acs16": "",
                    "chain_hw1": 0,
                    "chain_hw2": 0,
                    "chain_hw3": 0,
                    "chain_hw4": 0,
                    "chain_hw5": 0,
                    "chain_hw6": 0,
                    "chain_hw7": 0,
                    "chain_hw8": 0,
                    "chain_hw9": 0,
                    "chain_hw10": 0,
                    "chain_hw11": 0,
                    "chain_hw12": 0,
                    "chain_hw13": 0,
                    "chain_hw14": 0,
                    "chain_hw15": 0,
                    "chain_hw16": 0,
                    "chain_rate1": 34084.86,
                    "chain_rate2": 32303.65,
                    "chain_rate3": 33601.08,
                    "chain_rate4": 0.00,
                    "chain_rate5": 0.00,
                    "chain_rate6": 0.00,
                    "chain_rate7": 0.00,
                    "chain_rate8": 0.00,
                    "chain_rate9": 0.00,
                    "chain_rate10": 0.00,
                    "chain_rate11": 0.00,
                    "chain_rate12": 0.00,
                    "chain_rate13": 0.00,
                    "chain_rate14": 0.00,
                    "chain_rate15": 0.00,
                    "chain_rate16": 0.00,
                    "chain_xtime1": "{}",
                    "chain_xtime2": "{}",
                    "chain_xtime3": "{}",
                    "chain_offside_1": "",
                    "chain_offside_2": "",
                    "chain_offside_3": "",
                    "chain_opencore_0": "1",
                    "chain_opencore_1": "1",
                    "chain_opencore_2": "1",
                    "freq1": 744,
                    "freq2": 724,
                    "freq3": 734,
                    "freq4": 0,
                    "freq5": 0,
                    "freq6": 0,
                    "freq7": 0,
                    "freq8": 0,
                    "freq9": 0,
                    "freq10": 0,
                    "freq11": 0,
                    "freq12": 0,
                    "freq13": 0,
                    "freq14": 0,
                    "freq15": 0,
                    "freq16": 0,
                    "chain_avgrate1": 33585.34,
                    "chain_avgrate2": 32788.97,
                    "chain_avgrate3": 33336.44,
                    "chain_avgrate4": 0.00,
                    "chain_avgrate5": 0.00,
                    "chain_avgrate6": 0.00,
                    "chain_avgrate7": 0.00,
                    "chain_avgrate8": 0.00,
                    "chain_avgrate9": 0.00,
                    "chain_avgrate10": 0.00,
                    "chain_avgrate11": 0.00,
                    "chain_avgrate12": 0.00,
                    "chain_avgrate13": 0.00,
                    "chain_avgrate14": 0.00,
                    "chain_avgrate15": 0.00,
                    "chain_avgrate16": 0.00,
                    "miner_version": "0.0.1.3",
                    "miner_id": "",
                    "chain_power1": 1135,
                    "chain_power2": 1103,
                    "chain_power3": 1118,
                    "total_power": 3358,
                    "chain_voltage1": 15.70,
                    "chain_voltage2": 15.70,
                    "chain_voltage3": 15.70,
                    "chain_voltage4": 15.70,
                    "chain_voltage5": 15.70,
                    "chain_voltage6": 15.70,
                    "chain_voltage7": 15.70,
                    "chain_voltage8": 15.70,
                    "chain_voltage9": 15.70,
                    "chain_voltage10": 15.70,
                    "chain_voltage11": 15.70,
                    "chain_voltage12": 15.70,
                    "chain_voltage13": 15.70,
                    "chain_voltage14": 15.70,
                    "chain_voltage15": 15.70,
                    "chain_voltage16": 15.70,
                    "fan_pwm": 82,
                    "bringup_temp": 16,
                    "has_pic": "1",
                    "tune_running": "0",
                    "psu_status": "PSU OK",
                    "downscale_mode": "0",
                    "has_hotel_fee": "0",
                },
            ],
            "id": 1,
        },
        "rpc_pools": {
            "STATUS": [
                {
                    "Code": 7,
                    "Description": "cgminer 1.0.0",
                    "Msg": "3 Pool(s)",
                    "STATUS": "S",
                    "When": 1732121693,
                }
            ],
            "POOLS": [
                {
                    "Accepted": 10000,
                    "Best Share": 1000000000.0,
                    "Diff": "100K",
                    "Diff1 Shares": 0,
                    "Difficulty Accepted": 1000000000.0,
                    "Difficulty Rejected": 1000000.0,
                    "Difficulty Stale": 0.0,
                    "Discarded": 100000,
                    "Get Failures": 3,
                    "Getworks": 9000,
                    "Has GBT": False,
                    "Has Stratum": True,
                    "Last Share Difficulty": 100000.0,
                    "Last Share Time": "0:00:02",
                    "Long Poll": "N",
                    "POOL": 0,
                    "Pool Rejected%": 0.0,
                    "Pool Stale%%": 0.0,
                    "Priority": 0,
                    "Proxy": "",
                    "Proxy Type": "",
                    "Quota": 1,
                    "Rejected": 100,
                    "Remote Failures": 0,
                    "Stale": 0,
                    "Status": "Alive",
                    "Stratum Active": True,
                    "Stratum URL": "stratum.pool.io",
                    "URL": "stratum+tcp://stratum.pool.io:3333",
                    "User": "pool_username.real_worker",
                },
                {
                    "Accepted": 10000,
                    "Best Share": 1000000000.0,
                    "Diff": "100K",
                    "Diff1 Shares": 0,
                    "Difficulty Accepted": 1000000000.0,
                    "Difficulty Rejected": 1000000.0,
                    "Difficulty Stale": 0.0,
                    "Discarded": 100000,
                    "Get Failures": 3,
                    "Getworks": 9000,
                    "Has GBT": False,
                    "Has Stratum": True,
                    "Last Share Difficulty": 100000.0,
                    "Last Share Time": "0:00:02",
                    "Long Poll": "N",
                    "POOL": 1,
                    "Pool Rejected%": 0.0,
                    "Pool Stale%%": 0.0,
                    "Priority": 0,
                    "Proxy": "",
                    "Proxy Type": "",
                    "Quota": 1,
                    "Rejected": 100,
                    "Remote Failures": 0,
                    "Stale": 0,
                    "Status": "Alive",
                    "Stratum Active": True,
                    "Stratum URL": "stratum.pool.io",
                    "URL": "stratum+tcp://stratum.pool.io:3333",
                    "User": "pool_username.real_worker",
                },
                {
                    "Accepted": 10000,
                    "Best Share": 1000000000.0,
                    "Diff": "100K",
                    "Diff1 Shares": 0,
                    "Difficulty Accepted": 1000000000.0,
                    "Difficulty Rejected": 1000000.0,
                    "Difficulty Stale": 0.0,
                    "Discarded": 100000,
                    "Get Failures": 3,
                    "Getworks": 9000,
                    "Has GBT": False,
                    "Has Stratum": True,
                    "Last Share Difficulty": 100000.0,
                    "Last Share Time": "0:00:02",
                    "Long Poll": "N",
                    "POOL": 2,
                    "Pool Rejected%": 0.0,
                    "Pool Stale%%": 0.0,
                    "Priority": 0,
                    "Proxy": "",
                    "Proxy Type": "",
                    "Quota": 1,
                    "Rejected": 100,
                    "Remote Failures": 0,
                    "Stale": 0,
                    "Status": "Alive",
                    "Stratum Active": True,
                    "Stratum URL": "stratum.pool.io",
                    "URL": "stratum+tcp://stratum.pool.io:3333",
                    "User": "pool_username.real_worker",
                },
            ],
            "id": 1,
        },
    }
}


class TestMSKMiners(unittest.IsolatedAsyncioTestCase):
    @patch("pyasic-umhost.rpc.base.BaseMinerRPCAPI._send_bytes")
    async def test_all_data_gathering(self, mock_send_bytes):
        mock_send_bytes.raises = APIError()
        for m_type in data:
            gathered_data = {}
            miner = m_type("127.0.0.1")
            for data_name in fields(miner.data_locations):
                if data_name.name == "config":
                    # skip
                    continue
                data_func = getattr(miner.data_locations, data_name.name)
                fn_args = data_func.kwargs
                args_to_send = {k.name: data[m_type][k.name] for k in fn_args}
                function = getattr(miner, data_func.cmd)
                gathered_data[data_name.name] = await function(**args_to_send)

            result = MinerData(
                ip=str(miner.ip),
                device_info=miner.device_info,
                expected_chips=(
                    miner.expected_chips * miner.expected_hashboards
                    if miner.expected_chips is not None
                    else 0
                ),
                expected_hashboards=miner.expected_hashboards,
                expected_fans=miner.expected_fans,
                hashboards=[
                    HashBoard(slot=i, expected_chips=miner.expected_chips)
                    for i in range(miner.expected_hashboards)
                ],
            )
            for item in gathered_data:
                if gathered_data[item] is not None:
                    setattr(result, item, gathered_data[item])

            self.assertEqual(result.mac, "12:34:56:78:90:12")
            self.assertEqual(result.api_ver, "3.1")
            self.assertEqual(result.fw_ver, "10 Dec 2024 14:34:31 GMT")
            self.assertEqual(round(result.hashrate.into(SHA256Unit.TH)), 100)
            self.assertEqual(
                result.fans,
                [Fan(speed=5010), Fan(speed=5160), Fan(speed=5070), Fan(speed=5040)],
            )
            self.assertEqual(result.total_chips, result.expected_chips)
