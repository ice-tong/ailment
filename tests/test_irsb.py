import unittest

import ailment

try:
    import angr
    import archinfo
except:
    angr = None

try:
    import pyvex
except:
    pyvex = None


@unittest.skipUnless(angr, "angr required")
class TestIrsb(unittest.TestCase):
    block_bytes = bytes.fromhex("554889E54883EC40897DCC488975C048C745F89508400048C745F0B6064000488B45C04883C008488B00BEA70840004889C7E883FEFFFF")
    block_addr = 0x4006c6

    @unittest.skipUnless(pyvex, "pyvex required")
    def test_convert_from_vex_irsb(self):
        arch = archinfo.arch_from_id('AMD64')
        manager = ailment.Manager(arch=arch)
        irsb = pyvex.IRSB(self.block_bytes, self.block_addr, arch, opt_level=0)
        ablock = ailment.IRSBConverter.convert(irsb, manager)

    @unittest.skipUnless(hasattr(angr.engines, "UberEnginePcode"), "pypcode required")
    def test_convert_from_pcode_irsb(self):
        arch = archinfo.arch_from_id('AMD64')
        manager = ailment.Manager(arch=arch)
        p = angr.load_shellcode(self.block_bytes, arch, self.block_addr, self.block_addr,
                                engine=angr.engines.UberEnginePcode)
        irsb = p.factory.block(block_addr).vex
        ablock = ailment.IRSBConverter.convert(irsb, manager)


if __name__ == "__main__":
    unittest.main()
