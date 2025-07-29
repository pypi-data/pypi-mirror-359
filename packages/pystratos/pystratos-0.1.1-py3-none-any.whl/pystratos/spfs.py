import io
import warnings
from typing import IO, Union

try:
    from cryptography.fernet import Fernet
except ModuleNotFoundError:

    def _pystratos_crypto_warning():
        """
        Warns the user that the cryptography package is not installed.
        """
        warnings.warn(
            "Optional dependency 'cryptography' is not installed. "
            "Encryption features are disabled. To enable them, run: pip install pystratos[crypto]",
            category=UserWarning,
            stacklevel=2,
        )

    class Fernet:  # type: ignore  # noqa: E731
        """
        Dummy Fernet class to handle the case when cryptography is not installed.
        """

        def __init__(self, *args, **kwargs):
            _pystratos_crypto_warning()

        def encrypt(self, data: bytes) -> bytes:
            return data

        def decrypt(self, data: bytes) -> bytes:
            return data


from .ipfs import AsyncIpfsClient

__ALL__ = ["AsyncSpfsClient"]


class AsyncSpfsClient(AsyncIpfsClient):
    """
    AsyncSpfsClient is a subclass of AsyncIpfsClient that provides methods for interacting with the Stratos Public File System (SPFS).
    It inherits all methods from AsyncIpfsClient and can be used to add and retrieve files from SPFS.
    """

    def __init__(
        self,
        base_url: str = "https://sds-gateway-uswest.thestratos.org/spfs/PSu46EiNUYevTVA8doNHiCAFrxU=/api/v0",
        timeout: int | None = None,
    ):
        """
        Initializes the AsyncSpfsClient with the specified base URL and timeout.

        :param base_url: The base URL for the SPFS API.
        :param timeout: Optional timeout for HTTP requests.
        """
        super().__init__(base_url=base_url, timeout=timeout)

    async def add(
        self, file: Union[bytes, IO[bytes]], *, filename: str | None = None, encryption_key: bytes | None = None,
    ) -> dict:
        """
        Adds a file to SPFS. If an encryption key is provided, the file will be encrypted before being added.

        :param file: The file to add, either as bytes or a file-like object.
        :param filename: Optional name for the file in SPFS. If not provided, a random UUID will be used as the filename.
        :param encryption_key: Optional encryption key for encrypting the file before adding it to SPFS. If provided, the file will be encrypted using this key.
        :return: A dictionary containing the response from the SPFS API, typically including the CID (Content Identifier) of the added file.
        """
        if encryption_key:
            fernet = Fernet(encryption_key)
            file = (
                fernet.encrypt(file.read())
                if isinstance(file, io.IOBase)
                else fernet.encrypt(file)
            )
        return await super().add(file, filename=filename)

    async def cat(self, cid: str, encryption_key: bytes | None = None) -> bytes:
        """
        Retrieves a file from SPFS by its CID. If an encryption key is provided, the file will be decrypted after retrieval.
        :param cid: The Content Identifier (CID) of the file to retrieve.
        :param encryption_key: Optional encryption key for decrypting the file after retrieval. If provided, the file will be decrypted using this key.
        :return: The content of the file, either encrypted or decrypted based on the presence of an encryption key.
        """
        content = await super().cat(cid)
        if encryption_key:
            fernet = Fernet(encryption_key)
            return fernet.decrypt(content)
        return content
