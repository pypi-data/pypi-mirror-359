"""Module to provide helper classes related to configuration.

"""
__author__ = "Oliver Maye"
__version__ = "0.1"
__all__ = ["ConfigItem", "Configuration", "Configurable"]

from .penum import Enum, unique, auto, idiotypic, dataclass

from .systypes import ErrorCode


@unique
@idiotypic
class ConfigItem(Enum):
    """Mnemonic type to identify a specific kind of configuration.
    This helps interpreting configuration data, correctly. The meaning
    is as follows:
    
    ===============    ==============================================================
    Item               Meaning
    ===============    ==============================================================
    rate               Data rate as a frequency in Hz.
    range              Data measurement range, depending on the physical dimension.
    resolution         Resolution of a measurement result in bits.
    fifo               Fifo low/hogh water marks, empty signals etc.
    eventArm           Arming the event machine, enabling interrupt(s).
    eventCondition     Thresholds and counts to define event conditions.
    implicit           Configured property is implicitly given by the enclosing type.
    ===============    ==============================================================
    """
    rate                 = auto()
    range                = auto()
    resolution           = auto()
    fifo                 = auto()
    eventArm             = auto()
    eventCondition       = auto()
    implicit             = auto()

@dataclass
class Configuration:
    """Container structure to hold common configuration data.
    
    Instances of this class will be passed to the
    :meth:`Configurable.configure` method.
    Use the :attr:`item` attribute to de-multiplex the inner data
    attributes.
    """

    @dataclass
    class CfgFifo():
        watermark:  int = 4
        control:    int = 0

    item:   ConfigItem = ConfigItem.implicit
    """Multiplex configured item and data attribute interpretation as follows:
    
    =========================    ===========================
    Value                        Attribute valid
    =========================    ===========================
    ConfigItem.rate              value
    ConfigItem.range             value
    ConfigItem.resolution        value
    ConfigItem.fifo              fifo
    ConfigItem.eventArm          value
    ConfigItem.eventCondition    to be defined in subclass
    ConfigItem.implicit          to be defined in subclass
    =========================    ===========================
    """
    value:  int = 1
    fifo:   CfgFifo = None
    
    
class Configurable:
    """Generic interface for configurable objects.
    
    Unless described otherwise by sub-classes, the exact interpretation
    of configuration parameters as well as the behavior of the
    :meth:`configure` method is at the discretion of the implementation. 
    """
    
    def configure(self, configData):
        """Configures the device as described by the given
        configuration data.
        
        Note that the type of the provided data and its interpretation
        will depend on the actual implementation.
        
        Also see: :class:`Configuration`.
        
        :param .Configuration configData: Specific configuration information.
        :return: An error code indicating either success or the reason of failure.
        :rtype: ErrorCode
        """
        return ErrorCode.errNotImplemented

    