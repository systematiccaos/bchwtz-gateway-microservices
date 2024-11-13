from binascii import hexlify
from enum import Enum
import logging


class SigScanner():
    logger = logging.getLogger("Tag")
    logger.setLevel(logging.ERROR)

    def scan_signals(bytes: bytearray = None, checks: Enum = None) -> list[str]:
        matching_funcs: list[str] = []
        for check in checks:
            check_in = False
            for conf in check.value:
                if check_in:
                    break
                for key, val in conf.items():
                    if bytes[key] == val:
                        check_in = True
                    else:
                        check_in = False
                        break
            if check_in:
                matching_funcs.append(check.name)
        if len(matching_funcs) < 1:
            matching_funcs = None
            SigScanner.logger.debug(hexlify(bytes))
        return matching_funcs