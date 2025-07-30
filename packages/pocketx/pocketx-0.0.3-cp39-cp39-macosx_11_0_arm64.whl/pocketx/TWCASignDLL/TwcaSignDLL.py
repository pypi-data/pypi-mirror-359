import os
from ctypes import *

class TwcaSignDLL:
    def __init__(self):
        self.__GetErrorMsg = None
        self.__GetErrorCode = None
        self.__GetSignerCertFinger = None
        self.__GetSignerCertSerial = None
        self.__GetSignerCertNotAfter = None
        self.__GetSignerCertNotBefore = None
        self.__GetSignerCertIssuer = None
        self.__GetSignerCertSubject = None
        self.__GetSignerCertSubjectCN = None
        self.__myDll = None
        self.__ver = None
        self.__makeTWCASignPasswd = None
        self.__TWCASignInitial = None
        self.__SignPkcs7 = None
        self.__GetSignedPkcs7 = None

    def initialDLL(self, dll_path_file):
        try:
            self.__myDll = cdll.LoadLibrary(dll_path_file)

            # function mapping
            self.__ver = getattr(self.__myDll, "?GetPkiVersion@@YAPEADXZ")
            self.__ver.restype = c_char_p

            self.__GetErrorCode = getattr(self.__myDll, "?GetErrorCode@@YAHXZ")
            self.__GetErrorCode.restype = c_int

            self.__GetErrorMsg = getattr(self.__myDll, "?GetErrorMsg@@YAPEADXZ")
            self.__GetErrorMsg.restype = c_char_p

            self.__makeTWCASignPasswd = getattr(self.__myDll, "?MakeTWCASignPasswd@@YAHPEBDPEAH00@Z")
            self.__makeTWCASignPasswd.argtypes = [POINTER(c_char), POINTER(c_int), POINTER(c_char), POINTER(c_char)]
            self.__makeTWCASignPasswd.restype = c_int

            self.__TWCASignInitial = getattr(self.__myDll, "?TWCASignInitial@@YA_NPEBD0@Z")
            self.__TWCASignInitial.argtypes = [POINTER(c_char), POINTER(c_char)]
            self.__TWCASignInitial.restype = c_int

            self.__SignPkcs7 = getattr(self.__myDll, "?SignPkcs7@@YAHPEBD0@Z")
            self.__SignPkcs7.argtypes = [POINTER(c_char), POINTER(c_char)]
            self.__SignPkcs7.restype = c_int

            self.__GetSignedPkcs7 = getattr(self.__myDll, "?GetSignedPkcs7@@YAPEADXZ")
            self.__GetSignedPkcs7.restype = c_char_p
            # cert Info
            self.__GetSignerCertSubject = getattr(self.__myDll, "?GetSignerCertSubject@@YAPEADXZ")
            self.__GetSignerCertSubject.restype = c_char_p

            self.__GetSignerCertSubjectCN = getattr(self.__myDll, "?GetSignerCertSubjectCN@@YAPEADXZ")
            self.__GetSignerCertSubjectCN.restype = c_char_p

            self.__GetSignerCertIssuer = getattr(self.__myDll, "?GetSignerCertIssuer@@YAPEADXZ")
            self.__GetSignerCertIssuer.restype = c_char_p

            self.__GetSignerCertNotBefore = getattr(self.__myDll, "?GetSignerCertNotBefore@@YAPEADXZ")
            self.__GetSignerCertNotBefore.restype = c_char_p

            self.__GetSignerCertNotAfter = getattr(self.__myDll, "?GetSignerCertNotAfter@@YAPEADXZ")
            self.__GetSignerCertNotAfter.restype = c_char_p

            self.__GetSignerCertSerial = getattr(self.__myDll, "?GetSignerCertSerial@@YAPEADXZ")
            self.__GetSignerCertSerial.restype = c_char_p

            self.__GetSignerCertFinger = getattr(self.__myDll, "?GetSignerCertFinger@@YAPEADXZ")
            self.__GetSignerCertFinger.restype = c_char_p
            return 0
        except FileNotFoundError:
            return -1

    def getVersion(self):
        return self.__ver().decode("utf-8")

    def signInitial(self, property_file, pfx_pwd=None):
        char_array = c_char * 512
        encedPfxPasswd = char_array()
        pfxPasswdLen = c_int(512)
        # ret = self.__makeTWCASignPasswd(encedPfxPasswd, byref(pfxPasswdLen), bytes(property_file, 'utf-8'), bytes(pfx_pwd, 'utf-8'))
        # ret = self.__makeTWCASignPasswd(encedPfxPasswd, byref(pfxPasswdLen), bytes(property_file, 'utf-8'), None)

        ret = self.__TWCASignInitial(bytes(property_file, 'utf-8'), bytes("", 'utf-8'))

        if ret == 1:
            ret = 0

        return ret

    def signInitial_v2(self, property_file, ca_path, ca_passwd, person_id):
        PFX_path, PFX_file = os.path.split(ca_path)
        PFX_pswd = ca_passwd
        PFX_signerFilter = f"//S_CN={person_id},S_OU=23470685-RA-CHUANTAI,S_OU=CHUANTAI,S_C=TW,S_O=TaiCA Secure CA - Evaluation Only,S_O=Certificate Service Provider - Evaluation Only//"

        # 打印這四個參數以確認它們已正確傳入
        print('-' * 50)
        print(f"PFX.path={PFX_path}")
        print(f"PFX.file={PFX_file}")
        print(f"PFX.pswd={PFX_pswd}")
        print(f"PFX.signerFilter={PFX_signerFilter}")
        print('-' * 50)

        # CA 簽名初始化操作
        char_array = c_char * 512
        encedPfxPasswd = char_array()
        pfxPasswdLen = c_int(512)

        # 手動傳入密碼，進行密碼加密操作
        ret = self.__TWCASignInitial(
            bytes(property_file, 'utf-8'),
            bytes(PFX_path, 'utf-8'),  # 傳入 CA 憑證路徑
            bytes(PFX_file, 'utf-8'),  # 傳入 CA 憑證文件名
            bytes(PFX_pswd, 'utf-8'),
            bytes(PFX_signerFilter, 'utf-8')  # 傳入簽名過濾器
        )

        if ret == 1:
            ret = 0

        return ret


    def signPKCS7(self, plaintext_bytes):
        encoding = b"UTF-16LE"
        ret = self.__SignPkcs7(plaintext_bytes, encoding)
        return ret

    def getSignedPkcs7(self):
        if self.__GetSignedPkcs7() is None:
            return None
        else:
            return self.__GetSignedPkcs7().decode("utf-8")

    def getSignerCertSubjectCN(self):
        return self.__GetSignerCertSubjectCN().decode("utf-8")

    def getSignerCertSubject(self):
        if self.__GetSignerCertSubject is None:
            return None
        else:
            return self.__GetSignerCertSubject().decode("utf-8")

    def getSignerCertIssuer(self):
        return self.__GetSignerCertIssuer().decode("utf-8")

    def getSignerCertNotBefore(self):
        return self.__GetSignerCertNotBefore().decode("utf-8")

    def getSignerCertNotAfter(self):
        return self.__GetSignerCertNotAfter().decode("utf-8")

    def getSignerCertSerial(self):
        return self.__GetSignerCertSerial().decode("utf-8")

    def getSignerCertFinger(self):
        return self.__GetSignerCertFinger().decode("utf-8")

    def getErrorCode(self):
        return self.__GetErrorCode()

    def getErrorMsg(self):
        if self.__GetErrorMsg is None:
            return None
        else:
            return self.__GetErrorMsg().decode("big5")
