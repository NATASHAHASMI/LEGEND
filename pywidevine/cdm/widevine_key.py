from http.client import HTTPSConnection

from Cryptodome.PublicKey import RSA


class WidevineKey(RSA.RsaKey):
    """Corresponding to Chrome CDM version 4.10.1610.0, Windows x64"""

    def __init__(self):

        super().__init__(
            n=0xB5D1DC441883596C5D2722832D33CEF4E4DAA6E9959D6FBD83A9374527E533408448512E7D9509182EF750A7BD7BEBBBF3D1D5653D38A41E68AF7581D173B168E89B26494B06477B61F9F53A7755ADE9CC293135178FFA8E0E6B9B0CAFE2A150D6EF0CFD385952B0206FCA5398A7DBF6FAEFD55F00029C15CDC420DECE3C7844A72A3054F7D564F1A94F4E33D27CE8284C396E1B140E3568B009A3307ED36C62B3B395D7BE57750E6F9155CCF72B3A668445FCAE8D5DE1E2C1C645B4C2B2A615C0C6A53BB866366B5E9B0B74C41B9FE49BA26BBB75B1CB89CA943C948D6212C07E259568DD4A2F7DAF67357D209794C0AB5B4087A339E7FB6DA56022AD61EF09,
            e=0x10001,
        )
        self.__auth = "Basic RTFBVzQ5V3VvRkZseFc0MDo4Nm5oaDBaT3dDUll0Qmtk"

    def _decrypt(self, ciphertext):
        if not 0 < ciphertext < self._n:
            raise ValueError("Ciphertext too large")

        h = HTTPSConnection("widevine.decrypt.site")
        h.request(
            "POST",
            "/chromecdm_win64_4_10_1610_0/decrypt",
            ciphertext.to_bytes(0x100, byteorder="big"),
            {"Authorization": self.__auth},
        )
        r = h.getresponse()
        code = r.getcode()
        if code // 100 == 4:
            raise ValueError(r.read())
        if code != 200:
            raise SystemError("Request returned error code %d" % code)
        return int.from_bytes(r.read(), byteorder="big")
