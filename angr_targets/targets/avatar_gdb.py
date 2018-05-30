from avatar2 import *
from angr_targets.concrete import ConcreteTarget
from angr.errors import ConcreteMemoryError, ConcreteRegisterError, ConcreteBreakpointError
import logging
l = logging.getLogger("angr_targets.avatar_gdb")
#l.setLevel(logging.DEBUG)


class AvatarGDBConcreteTarget(ConcreteTarget):
   
    def __init__(self,architecture, gdbserver_ip, gdbserver_port ):
        # Creation of the avatar-object
        self.avatar = Avatar(arch=architecture)
        self.target = self.avatar.add_target(GDBTarget, gdb_executable="gdb", gdb_ip=gdbserver_ip, gdb_port=gdbserver_port)
        self.avatar.init_targets()
        super(AvatarGDBConcreteTarget,self).__init__()

    def exit(self):
        self.avatar.shutdown()

    def read_memory(self,address, nbytes, **kwargs):
        """
        Reading from memory of the target

            :param int address: The address to read from
            :param int nbytes:  The amount number of bytes to read
            :return:        The memory read
            :rtype: str
            :raise angr.errors.SimMemoryError
        """
        try:
            l.debug("AvatarGDBConcreteTarget read_memory at %x "%(address))
            res = self.target.read_memory(address, 1, nbytes, raw=True)
            return res
        except Exception as e:
            l.warn("AvatarGDBConcreteTarget can't read_memory at address %x exception %s"%(address,e))
            raise ConcreteMemoryError("AvatarGDBConcreteTarget can't read_memory at address %x exception %s"%(address,e))


    def write_memory(self,address, value, **kwargs):
        """
        Writing to memory of the target
            :param int address:   The address from where the memory-write should start
            :param str value:     The actual value written to memory
            :raise angr.errors.ConcreteMemoryError
        """
        l.debug("AvatarGDBConcreteTarget write_memory at %x value %s "%(address,value.encode("hex")))
        try:
            res = self.target.write_memory(address, 1, value, raw=True)
            if not res:
                l.warn("AvatarGDBConcreteTarget failed write_memory at %x value %s"%(address,value))
                raise ConcreteMemoryError("AvatarGDBConcreteTarget failed write_memory to address %x"%(address))
        except Exception as e:
            l.warn("AvatarGDBConcreteTarget write_memory at %x value %s exception %s"%(address,value,e))
            raise ConcreteMemoryError("AvatarGDBConcreteTarget write_memory at %x value %s exception %s"%(address,value,e))

   
    def read_register(self,register,**kwargs):
        """"
        Reads a register from the target
            :param str register: The name of the register
            :return: int value of the register content
            :rtype int
            :raise angr.errors.ConcreteRegisterError in case the register doesn't exist or any other exception
        """

        try:
            l.debug("AvatarGDBConcreteTarget read_register at %s "%(register))
            register_value = self.target.read_register(register)
        except Exception as e:
            l.debug("AvatarGDBConcreteTarget read_register %s exception %s %s "%(register,type(e).__name__,e))
            raise ConcreteRegisterError("AvatarGDBConcreteTarget can't read register %s exception %s" %(register,e))
        # when accessing xmm registers and ymm register gdb return a list of 4/8 32 bit values
        # which need to be shifted appropriately to create a 128/256 bit value
        if type(register_value) is list:
            i = 0
            result = 0
            for val in register_value:
                cur_val = val << i * 32
                result |= cur_val
                i += 1
            return result
        else:
            return register_value

    def write_register(self, register, value, **kwargs):
        """
        Writes a register to the target
            :param str register:     The name of the register
            :param int value:        int value written to be written register
            :raise angr.errors.ConcreteRegisterError
        """
        try:
            l.debug("AvatarGDBConcreteTarget write_register at %s value %x "%(register,value))
            res = self.target.write_register(register, value)
            if not res:
                l.warn("AvatarGDBConcreteTarget write_register failed reg %s value %x "%(register,value))
                raise ConcreteRegisterError("AvatarGDBConcreteTarget write_register failed reg %s value %x "%(register,value))
        except Exception as e:
            l.warn("AvatarGDBConcreteTarget write_register exception write reg %s value %x %s "%(register,value,e))
            raise ConcreteRegisterError("AvatarGDBConcreteTarget write_register exception write reg %s value %x %s "%(register,value,e))


    def set_breakpoint(self,address, **kwargs):
        """Inserts a breakpoint

                :param optional bool hardware: Hardware breakpoint
                :param optional bool temporary:  Tempory breakpoint
                :param optional str regex:     If set, inserts breakpoints matching the regex
                :param optional str condition: If set, inserts a breakpoint with the condition
                :param optional int ignore_count: Amount of times the bp should be ignored
                :param optional int thread:    Thread cno in which this breakpoints should be added
                :raise angr.errors.ConcreteBreakpointError
        """
        l.debug("AvatarGDBConcreteTarget set_breakpoint at %x "%(address))
        res = self.target.set_breakpoint(address, **kwargs)
        if res == -1:
            raise ConcreteBreakpointError("AvatarGDBConcreteTarget failed to set_breakpoint at %x"%(address) )


    def set_watchpoint(self,address, **kwargs):
        """Inserts a watchpoint

                :param address: The name of a variable or an address to watch
                :param optional bool write:    Write watchpoint
                :param optional bool read:     Read watchpoint
                :raise angr.errors.ConcreteBreakpointError
        """
        l.debug("gdb target set_watchpoing at %x value"%(address))
        res = self.target.set_watchpoint(address, **kwargs)
        if res == -1:
            raise ConcreteBreakpointError("AvatarGDBConcreteTarget failed to set_breakpoint at %x" % (address))

    def run(self):
        """
        Resume the execution of the target
        :return:
        """
        l.debug("gdb target run")
        self.target.cont()
        self.target.wait()
    

