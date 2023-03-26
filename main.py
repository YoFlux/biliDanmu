import json
import sys

import requests


class BufferReader(object):
    def __init__(self, buffer: bytes):
        self.buf = buffer
        self.len = len(self.buf)
        self.pos = 0

    def skip(self, step=-1):
        if step >= 0:
            self.pos += step
        else:
            while True:
                if self.pos >= self.len:
                    raise Exception(self)
                if 128 & self.buf[self.pos] == 0:
                    self.pos += 1
                    break
                self.pos += 1

    def skipType(self, t):
        if t == 0:
            self.skip()
        elif t == 1:
            self.skip(8)
        elif t == 2:
            self.skip(self.uint32())
        elif t == 3:
            while True:
                e = 7 & self.uint32()
                if e != 4:
                    self.skipType(e)
                else:
                    break
        elif t == 5:
            self.skip(4)
        else:
            raise Exception("invalid wire type " + str(t) + " at offset " + str(self.pos))

    def uint32(self):
        rv = 0
        for i in range(5):
            # 小端模式
            rv = rv | (127 & self.buf[self.pos]) << (i * 7)
            if self.buf[self.pos] < 128:
                self.pos += 1
                break
            self.pos += 1
        return rv

    def int32(self):
        return 0 | self.uint32()

    def uint64(self):
        rv = 0
        for i in range(11):
            # 小端模式
            rv = rv | (127 & self.buf[self.pos]) << (i * 7)
            if self.buf[self.pos] < 128:
                self.pos += 1
                break
            self.pos += 1
        return rv

    def int64(self):
        return 0 | self.uint64()

    def string(self):
        size = self.uint32()
        data = self.buf[self.pos:self.pos + size]
        self.pos += size
        return str(data.decode('utf8', errors='ignore'))


class DmDecoder(object):
    def decode(self, buffer: bytes):
        r = BufferReader(buffer)
        elms = []
        while r.pos < r.len:
            # print(f'decode pos: {r.pos}')
            t = r.uint32()
            t3 = t >> 3
            # print(f'decode t>>3: {t3}')
            if t3 == 1:
                elms.append(self.decodeElem(r, r.uint32()))
            else:
                r.skipType(t & 7)
        return elms

    @staticmethod
    def decodeElem(r: BufferReader, eLen: int):
        elem = {}
        end = r.pos + eLen
        while r.pos < end:
            t = r.uint32()
            t3 = t >> 3
            # print(f'decodeElem pos: {r.pos}, t: {t}, type: {t3}')
            if t3 == 2:
                elem['stime'] = r.int32()
            elif t3 == 3:
                elem['mode'] = r.int32()
            elif t3 == 4:
                elem['size'] = r.int32()
            elif t3 == 5:
                elem['color'] = r.uint32()
            elif t3 == 6:
                elem['uhash'] = r.string()
            elif t3 == 7:
                elem['text'] = r.string()
            elif t3 == 8:
                elem['date'] = r.int64()
            elif t3 == 9:
                elem['weight'] = r.int32()
            elif t3 == 10:
                elem['action'] = r.string()
            elif t3 == 11:
                elem['pool'] = r.int32()
            elif t3 == 12:
                elem['dmid'] = r.string()
            elif t3 == 13:
                elem['attr'] = r.int32()
            elif t3 == 22:
                elem['animation'] = r.string()
            else:
                r.skipType(t & 7)
        return elem


class DmRobot(object):
    def __init__(self):
        self.decoder = DmDecoder()

    def fromVideo(self):
        pass

    def fromSegSoUrl(self, url: str):
        return self.fromBuffer(requests.get(url).content)

    def fromBuffer(self, buffer: bytes):
        return self.decoder.decode(buffer)


def main():
    dr = DmRobot()
    dms = dr.fromSegSoUrl('https://api.bilibili.com/x/v2/dm/web/seg.so?type=1&oid=745899804&pid=638907823&segment_index=1&pull_mode=1&ps=120000&pe=360000')
    json.dump(dms, sys.stdout, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
