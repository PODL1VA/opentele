
from __future__ import annotations
import os

import platform

from typing import Any, List, Dict, Type, TypeVar, Union
from .devices import *
from .exception import *
from .utils import *

import typing


_T = TypeVar("_T")
_RT = TypeVar("_RT")


class BaseAPIMetaClass(type):
    """Super high level tactic metaclass"""

    def __new__(cls : Type[_T], clsName : str, bases : List[object], attrs : Dict[str, Any]) -> _T:

        result = super().__new__(cls, clsName, bases, attrs)
        result._clsMakePID()
        result.__str__ = BaseAPIMetaClass.__str__

        return result
        
    @sharemethod
    def __str__(glob) -> str:

        if isinstance(glob, type):
            cls = glob
            result = f"{cls.__name__} {{\n" 
        else:
            cls = glob.__class__
            result = f"{cls.__name__}() = {{\n" 

        for attr, val in glob.__dict__.items():

            if attr.startswith(f"_{cls.__base__.__name__}__") \
                or attr.startswith(f"_{cls.__name__}__") \
                or attr.startswith("__") and attr.endswith("__") \
                or type(val) == classmethod \
                or callable(val):
                continue
            
            result += f"    {attr}: {val}\n"
            
        return result + "}"


class APIData(object, metaclass=BaseAPIMetaClass):
    CustomInitConnectionList : List[APIData] = []

    api_id : int           = None
    api_hash : str         = None
    device_model : str     = None
    system_version : str   = None
    app_version : str      = None
    lang_code : str        = None
    system_lang_code : str = None
    lang_pack : str        = None
    
    @typing.overload
    def __init__(self, api_id : int, api_hash : str) -> None:
        pass

    @typing.overload
    def __init__(self,
                api_id              : int,
                api_hash            : str,
                device_model        : str = None,
                system_version      : str = None,
                app_version         : str = None,
                system_lang_code    : str = None,
                lang_pack           : str = None,
                lang_code           : str = None) -> None:
        pass

    def __init__(self,
                api_id              : int = None,
                api_hash            : str = None,
                device_model        : str = None,
                system_version      : str = None,
                app_version         : str = None,
                system_lang_code    : str = None,
                lang_pack           : str = None,
                lang_code           : str = None) -> None:

        Expects((self.__class__ != APIData) or (api_id != None and api_hash != None),
        NoInstanceMatched("No instace of APIData matches the arguments"))

        cls = self.__class__

        self.api_id             = api_id            if api_id           else cls.api_id
        self.api_hash           = api_hash          if api_hash         else cls.api_hash
        self.device_model       = device_model      if device_model     else cls.device_model
        self.system_version     = system_version    if system_version   else cls.system_version
        self.app_version        = app_version       if app_version      else cls.app_version
        self.system_lang_code   = system_lang_code  if system_lang_code else cls.system_lang_code
        self.lang_pack          = lang_pack         if lang_pack        else cls.lang_pack
        self.lang_code          = lang_code         if lang_code        else cls.lang_code


        if self.device_model == None:
            system = platform.uname()

            if system.machine in ('x86_64', 'AMD64'):
                self.device_model = 'PC 64bit'
            elif system.machine in ('i386','i686','x86'):
                self.device_model = 'PC 32bit'
            else:
                self.device_model = system.machine

        self._makePID()

    @sharemethod
    def copy(glob : Union[Type[_T], _T] = _T) -> _T:
        
        cls = glob if isinstance(glob, type) else glob.__class__
            
        return cls(
            glob.api_id,
            glob.api_hash,
            glob.device_model,
            glob.system_version,
            glob.app_version,
            glob.system_lang_code,
            glob.lang_pack,
            glob.lang_code,
        )

    @sharemethod
    def destroy(glob : Union[Type[_T], _T]):
        if isinstance(glob, type): return

        # might cause conflict, disabled for now, it won't be a problem
        # if (APIData.findData(self.pid) != None):
        #     APIData.CustomInitConnectionList.remove(self)
        

    def __eq__(self, __o: APIData) -> bool:
        if (type(__o) != APIData): return False
        return self.pid == __o.pid
    
    def __del__(self):
        self.destroy()
    
    @classmethod
    def _makePIDEnsure(cls : APIData) -> int:
        while True:
            pid = int.from_bytes(os.urandom(8), 'little')
            if cls.findData(pid) == None: break
        return pid

    @classmethod
    def _clsMakePID(cls : APIData):
        cls.pid = cls._makePIDEnsure()
        cls.CustomInitConnectionList.append(cls)
        
    def _makePID(self):
        self.pid = self.__class__._makePIDEnsure()
        self.__class__.CustomInitConnectionList.append(self)
    
    @classmethod
    def Generate(cls : Type[_T], id : str = None) -> _T:

        if cls == APITemplate.TelegramAndroid:
            deviceInfo = AndroidDevice.RandomDevice(id)

        elif cls == APITemplate.TelegramIOS:
            deviceInfo = iOSDeivce.RandomDevice(id)

        elif cls == APITemplate.TelegramMacOS:
            deviceInfo = macOSDevice.RandomDevice(id)

        # elif cls == APITemplate.TelegramWeb_K or cls == APITemplate.TelegramWeb_Z or cls == APITemplate.Webogram:
        else:
            raise NotImplementedError(f"{cls.__name__} device not supported for randomize yet")
        
        return cls(device_model=deviceInfo.model, system_version=deviceInfo.version)
        

    @classmethod
    def findData(cls : APIData, pid : int) -> APIData:
        for x in cls.CustomInitConnectionList:
            if x.pid == pid: return x
        return None

class APITemplate(APIData):
    
    class TelegramDesktop(APIData):
        """
        Official Telegram for Desktop (Windows, macOS and Linux)\n
        [View on GitHub](https://github.com/telegramdesktop/tdesktop)
        """
        api_id           = 2040
        api_hash         = 'b18441a1ff607e10a989891a5462e627'
        device_model     = 'Desktop'
        system_version   = 'Windows 10'
        app_version      = '3.4.3 x64'
        lang_code        = 'en'
        system_lang_code = 'en-US'
        lang_pack        = 'tdesktop'
        
        @typing.overload
        @classmethod
        def Generate(cls : Type[_T], system : str = "windows", id : str = None) -> _T:
            pass

        @typing.overload
        @classmethod
        def Generate(cls : Type[_T], system : str = "macos", id : str = None) -> _T:
            pass

        @typing.overload
        @classmethod
        def Generate(cls : Type[_T], system : str = "linux", id : str = None) -> _T:
            pass

        @typing.overload
        @classmethod
        def Generate(cls : Type[_T], system : str = "random", id : str = None) -> _T:
            pass
        
        @classmethod
        def Generate(cls : Type[_T], system : str = None, id : str = None) -> _T:

            validList = ["windows", "macos", "linux"]
            if system == None or system not in validList:
                system = SystemInfo._hashtovalue(SystemInfo._strtohashid(id), validList)
            
            system = system.lower()

            if system == "windows":
                deviceInfo = WindowsDevice.RandomDevice(id)

            elif system == "macos":
                deviceInfo = macOSDevice.RandomDevice(id)

            elif system == "linux":
                deviceInfo = LinuxDevice.RandomDevice(id)

            return cls(device_model=deviceInfo.model, system_version=deviceInfo.version)

    class TelegramAndroid(APIData):
        """
        Official Telegram for Android\n
        [View on GitHub](https://github.com/DrKLO/Telegram)
        """
        api_id           = 6
        api_hash         = 'eb06d4abfb49dc3eeb1aeb98ae0f581e'
        device_model     = 'Samsung SM-G998B'
        system_version   = 'SDK 31'
        app_version      = '8.4.1 (2522)'
        lang_code        = 'en'
        system_lang_code = 'en-US'
        lang_pack        = 'android'

    class TelegramAndroidX(APIData):
        """
        Official TelegramX for Android\n
        [View on GitHub](https://github.com/DrKLO/Telegram)
        """
        api_id           = 21724
        api_hash         = '3e0cb5efcd52300aec5994fdfc5bdc16'
        device_model     = 'Samsung SM-G998B'
        system_version   = 'SDK 31'
        app_version      = '8.4.1 (2522)'
        lang_code        = 'en'
        system_lang_code = 'en-US'
        lang_pack        = 'android'

    class TelegramIOS(APIData):
        """
        Official Telegram for iOS\n
        [View on GitHub](https://github.com/TelegramMessenger/Telegram-iOS)
        """
        # api_id           = 8
        # api_hash         = '7245de8e747a0d6fbe11f7cc14fcc0bb'
        api_id           = 10840
        api_hash         = '33c45224029d59cb3ad0c16134215aeb'
        device_model     = 'iPhone 13 Pro Max'
        system_version   = '14.8.1'
        app_version      = '8.4'
        lang_code        = 'en'
        system_lang_code = 'en-US'
        lang_pack        = 'ios'

    class TelegramMacOS(APIData):
        """
        Official Telegram-Swift For MacOS\n
        [View on GitHub](https://github.com/overtake/TelegramSwift)
        """
        api_id           = 2834
        api_hash         = '68875f756c9b437a8b916ca3de215815'
        # api_id = 9                                    |
        # api_hash = "3975f648bb682ee889f35483bc618d1c" | Telegram for macOS uses this api, but it's unofficial api, why?
        device_model     = 'MacBook Pro'
        system_version   = 'macOS 12.0.1'
        app_version      = '8.4'
        lang_code        = 'en'
        system_lang_code = 'en-US'
        lang_pack        = 'macos'

    class TelegramWeb_Z(APIData):
        """
        Default Official Telegram Web Z For Browsers\n
        [View on GitHub](https://github.com/Ajaxy/telegram-tt) | [Visit on Telegram](https://web.telegram.org/z/)
        """
        api_id           = 2496
        api_hash         = '8da85b0d5bfe62527e5b244c209159c3'
        device_model     = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        system_version   = 'Windows'
        app_version      = '1.28.3 Z'
        lang_code        = 'en'
        system_lang_code = 'en-US'
        lang_pack        = ''   # I don't understand why Telegram Z doesn't use langPack
                                # You can read its source here: https://github.com/Ajaxy/telegram-tt/blob/f7bc473d51c0fe3a3e8b22678b62d2360225aa7c/src/lib/gramjs/client/TelegramClient.js#L131

    class TelegramWeb_K(APIData):
        """
        Official Telegram Web K For Browsers\n
        [View on GitHub](https://github.com/morethanwords/tweb) | [Visit on Telegram](https://web.telegram.org/k/)
        """
        api_id           = 2496
        api_hash         = '8da85b0d5bfe62527e5b244c209159c3'
        device_model     = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        system_version   = 'Win32'
        app_version      = '1.0.1 K'
        lang_code        = 'en'
        system_lang_code = 'en-US'
        lang_pack        = 'macos'   # I'm totally confused, why macos? https://github.dev/morethanwords/tweb/blob/26582590e647766f5890c79e1611c54c1e6e800c/src/config/app.ts#L23

    class Webogram(APIData):
        """
        Old Telegram For Browsers\n
        [View on GitHub](https://github.com/zhukov/webogram) | [Vist on Telegram](https://web.telegram.org/?legacy=1#/im)
        """
        api_id           = 2496
        api_hash         = '8da85b0d5bfe62527e5b244c209159c3'
        device_model     = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        system_version   = 'Win32'
        app_version      = '0.7.0'
        lang_code        = 'en'
        system_lang_code = 'en-US'
        lang_pack        = ''   # The same problem as TelegramWeb_K, as TelegramWeb_K was built on Webogram




# Hook InitConnectionRequest to change API_ID API_HASH, device_model,... etc
# oldInitConnectionRequest = TLFunctions.InitConnectionRequest
# TLFunctions.InitConnectionRequest = CustomInitConnectionRequest