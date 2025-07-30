"""""" # start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'numpy_quaddtype.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from ._quaddtype_main import (
    QuadPrecision,
    QuadPrecDType,
    is_longdouble_128,
    get_sleef_constant
)

__all__ = [
    'QuadPrecision', 'QuadPrecDType', 'SleefQuadPrecision', 'LongDoubleQuadPrecision',
    'SleefQuadPrecDType', 'LongDoubleQuadPrecDType', 'is_longdouble_128', 'pi', 'e', 
    'log2e', 'log10e', 'ln2', 'ln10', 'max_value', 'min_value', 'epsilon'
]

def SleefQuadPrecision(value):
    return QuadPrecision(value, backend='sleef')

def LongDoubleQuadPrecision(value):
    return QuadPrecision(value, backend='longdouble')

def SleefQuadPrecDType():
    return QuadPrecDType(backend='sleef')

def LongDoubleQuadPrecDType():
    return QuadPrecDType(backend='longdouble')

pi = get_sleef_constant("pi")
e = get_sleef_constant("e")
log2e = get_sleef_constant("log2e")
log10e = get_sleef_constant("log10e")
ln2 = get_sleef_constant("ln2")
ln10 = get_sleef_constant("ln10")
max_value = get_sleef_constant("quad_max")
min_value = get_sleef_constant("quad_min")
epsilon = get_sleef_constant("epsilon")
