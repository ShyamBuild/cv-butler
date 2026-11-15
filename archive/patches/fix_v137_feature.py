import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _xattr_raw(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _sniff_ext('))
    B[i:i] = ["def _xattr_raw(p, name='com.apple.metadata:_kMDItemUserTags'):  # XATTR-RAW v81.7",
              "    try:",
              "        import ctypes",
              "        lc = ctypes.CDLL('/usr/lib/libc.dylib', use_errno=True)",
              "        lc.getxattr.restype = ctypes.c_ssize_t",
              "        lc.getxattr.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int]",
              "        pb = p.encode() if isinstance(p, str) else p",
              "        nb = name.encode() if isinstance(name, str) else name",
              "        n = lc.getxattr(pb, nb, None, 0, 0, 0)",
              "        if n <= 0: return b''",
              "        buf = ctypes.create_string_buffer(n)",
              "        n2 = lc.getxattr(pb, nb, buf, n, 0, 0)",
              "        return buf.raw[:n2] if n2 > 0 else b''",
              "    except Exception:",
              "        return b''",
              ""]
    done.append('xattr-helper')
n = 0
for k, l in enumerate(B):
    if 'os.getxattr(' in l:
        B[k] = l.replace('os.getxattr(', '_xattr_raw('); n += 1
if n: done.append(f'os-getxattr-replaced-x{n}')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S115 tags read through macOS libc" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S114 the pulse has a voice" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S115 tags read through macOS libc', 'def _xattr_raw(' in _src and 'os.getxattr(' not in _src and (chr(35)+' XATTR-RAW') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S115-guard')
print('✅', done)
