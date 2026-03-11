# machine_id.py
import sys
import subprocess
import uuid
import hashlib
import platform
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64
import json
from datetime import datetime, timedelta
def _get_mac():
    # uuid.getnode() usually returns MAC (may be random if cannot find)
    node = uuid.getnode()
    mac = ':'.join(("%012X" % node)[i:i+2] for i in range(0, 12, 2))
    return mac

def _run_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, universal_newlines=True)
        return out.strip()
    except Exception:
        return ""

def get_windows_serials():
    # 需要在 Windows 上运行
    bios = _run_cmd('wmic bios get serialnumber').splitlines()
    mb = _run_cmd('wmic baseboard get serialnumber').splitlines()
    def pick(lines):
        for l in lines:
            s = l.strip()
            if s and not s.lower().startswith('serial'):
                return s
        return ""
    return pick(bios), pick(mb)

def get_unix_serials():
    # Linux / macOS 尝试读取一些常见位置
    cpu = _run_cmd("cat /proc/cpuinfo | grep 'Serial' | head -n 1 | awk -F': ' '{print $2}'") or \
          _run_cmd("cat /proc/cpuinfo | grep -m1 'model name' | awk -F': ' '{print $2}'")
    product_uuid = _run_cmd("cat /sys/class/dmi/id/product_uuid 2>/dev/null") or ""
    board_serial = _run_cmd("cat /sys/class/dmi/id/board_serial 2>/dev/null") or ""
    return cpu, product_uuid or board_serial

def get_machine_fingerprint(extra_salt=""):
    """
    Return a stable machine fingerprint string.
    extra_salt: 可选，绑定给定额外信息（例如软件名/版本）
    """
    p = platform.system().lower()
    parts = []
    parts.append(platform.node())
    parts.append(platform.system())
    parts.append(platform.release())
    parts.append(_get_mac())

    if p == "windows":
        bios_sn, mb_sn = get_windows_serials()
        parts.extend([bios_sn, mb_sn])
    else:
        cpu, pu = get_unix_serials()
        parts.extend([cpu, pu])

    # 组合并哈希成固定长度
    combined = "|".join([str(x) for x in parts if x])
    combined = combined + "|" + extra_salt
    h = hashlib.sha256(combined.encode("utf-8")).hexdigest()
    # 返回十六进制指纹（也可以 base64）
    return h



def verify_license(public_pem: bytes, token: str,extra_salt=''):
    """ ---------- 客户端：验证 license ---------- """
    try:
        msg_b64, sig_b64 = token.split(".")
        # pad base64
        def pad(s): return s + "=" * (-len(s) % 4)
        message = base64.urlsafe_b64decode(pad(msg_b64))
        signature = base64.urlsafe_b64decode(pad(sig_b64))
        public_key = serialization.load_pem_public_key(public_pem)
        public_key.verify(
            signature,
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        payload = json.loads(message.decode('utf-8'))
        # 检查 mid 是否与当前机器匹配，并检查过期
        current_mid = get_machine_fingerprint(extra_salt=extra_salt)
        if payload.get("mid") != current_mid:
            return False, "Machine mismatch"
        exp = payload.get("exp")
        if exp and datetime.fromisoformat(exp.replace("Z", "")) < datetime.utcnow():
            return False, "Expired"
        return True, "OK"
    except Exception as e:
        return False, str(e)
# quick demo
if __name__ == "__main__":
    print("Machine fingerprint:", get_machine_fingerprint(extra_salt="MyApp_v1"))
