"""
"""
import argparse
import gc
import os
import sys
#import unittest

#from philander.bma456 import BMA456 as BMA
import philander.bma456_reg
#from philander.accelerometer import AxesSign
#from philander.sensor import SelfTest
#from philander.serialbus import SerialBusType
#from philander.systypes import ErrorCode

config = {
    "SerialBus.designator": 0, #"/dev/i2c-1",
    "Sensor.dataRange"    : 4000,
    "Sensor.dataRate"     : 100,
    "BMA456.INT_MAP_DATA": 0xFF,
}

def df():
    status = os.statvfs('//')
    sResult = '{0} bytes'.format( (status[0]*status[3]) )
    return sResult

def free(fullInfo=False):
    gc.collect()
    heapFree = gc.mem_free()
    heapAlloced = gc.mem_alloc()
    heapTotal = heapFree + heapAlloced
    sPercent = '{0:.2f}%'.format( heapFree/heapTotal * 100 )
    sResult = sPercent if not fullInfo else ('Total:{0} Free:{1} ({2})'.format(heapTotal,heapFree,sPercent))
    return sResult

#class TestBMA456( unittest.TestCase ):
            
    # def test_paramsinit(self):
    #     global config
    #     cfg = config.copy()
    #     BMA.Params_init( cfg )
    #     self.assertIsNotNone( cfg )
    #     self.assertTrue( "SerialBus.designator" in cfg )
    #     self.assertTrue( "SerialBus.type" in cfg )
    #     self.assertEqual( cfg["SerialBus.type"], SerialBusType.I2C )
    #     self.assertTrue( "SerialBusDevice.address" in cfg )
    #     self.assertTrue( cfg["SerialBusDevice.address"] in (0x18, 0x19) )
    #
    # def test_open(self):
    #     global config
    #     cfg = config.copy()
    #     BMA.Params_init( cfg )
    #     sensor = BMA()
    #     self.assertIsNotNone( sensor )
    #     # Simple open
    #     err = sensor.open(cfg)
    #     self.assertTrue( err.isOk(), f"Open failed: {err}." )
    #     self.assertTrue( err.isOk() )
    #     # Corresponding close
    #     err = sensor.close()
    #     self.assertTrue( err.isOk() )
    #     # Reopen
    #     err = sensor.open(cfg)
    #     self.assertTrue( err.isOk() )
    #     # Second open should yield an error
    #     err = sensor.open(cfg)
    #     self.assertFalse( err.isOk() )
    #     # Matching close
    #     err = sensor.close()
    #     self.assertTrue( err.isOk() )
    #     # Another close should given an error
    #     err = sensor.close()
    #     self.assertFalse( err.isOk() )
    #
    # def test_selftest(self):
    #     global config
    #     cfg = config.copy()
    #     BMA.Params_init( cfg )
    #     sensor = BMA()
    #     self.assertIsNotNone( sensor )
    #     err = sensor.open(cfg)
    #     self.assertTrue( err.isOk(), f"Open failed: {err}." )
    #     err = sensor.selfTest( SelfTest.CONNECTION )
    #     self.assertTrue( err.isOk() )
    #     err = sensor.close()
    #     self.assertTrue( err.isOk() )
    #
    # def test_working(self):
    #     global config
    #     cfg = config.copy()
    #     BMA.Params_init( cfg )
    #     sensor = BMA()
    #     self.assertIsNotNone( sensor )
    #     err = sensor.open(cfg)
    #     self.assertTrue( err.isOk(), f"Open failed: {err}." )
    #     for _ in range(10):
    #         meas, err = sensor.getLatestData()
    #         self.assertTrue( err.isOk() )
    #         self.assertTrue( meas.x < 2000 )
    #         self.assertTrue( -2000 < meas.x)
    #         self.assertTrue( meas.y < 2000 )
    #         self.assertTrue( -2000 < meas.y)
    #         self.assertTrue( meas.z < 2000 )
    #         self.assertTrue( -2000 < meas.z)
    #         total = (meas.x**2 + meas.y**2 + meas.z**2) ** (1/2)
    #         self.assertTrue( total < 2000 )
    #         self.assertTrue( 500 <= total )
    #     err = sensor.close()
    #     self.assertTrue( err.isOk() )

    #pass
        
if __name__ == '__main__':
    print("Disk free:", df())
    print("Memory: ", free(True))
    parser = argparse.ArgumentParser()
    parser.add_argument("--bus", help="designator of the i2c bus", default=None)
    parser.add_argument("--adr", help="i2c address of the device", type=int, default=None)
    args, unknown = parser.parse_known_args()
    if args.bus:
        config["SerialBus.designator"] = args.bus
    if args.adr:
        config["SerialBusDevice.address"] = args.adr
    if sys.argv:
        sys.argv = [sys.argv[0],] + unknown
    print("Memory: ", free(True))
    unittest.main()

