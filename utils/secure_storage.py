"""
utils/secure_storage.py
-----------------------
Wrapper seguro para ft.SharedPreferences que criptografa e descriptografa
valores sensíveis (tokens) usando flet.security.encrypt / decrypt.

A chave secreta é lida da variável de ambiente FLET_SECRET_KEY.
Tokens armazenados no navegador/dispositivo ficam sempre cifrados.

Uso:
    from utils.secure_storage import SecureStorage

    storage = SecureStorage()

    # Salvar token criptografado
    await storage.set("r_token", token_value)

    # Ler e descriptografar token
    token = await storage.get("r_token")

    # Remover token
    await storage.remove("r_token")
"""

import os
import flet as ft
from flet.security import encrypt, decrypt


class SecureStorage:
    """
    Wrapper sobre ft.SharedPreferences que aplica criptografia
    simétrica (Fernet/PBKDF2) em todos os valores antes de persistir.

    A chave de criptografia é derivada de FLET_SECRET_KEY (.env).
    Se a chave não estiver definida, uma exceção é lançada para evitar
    armazenar dados sensíveis sem proteção.
    """

    def __init__(self):
        self._secret_key: str = os.getenv("FLET_SECRET_KEY")
        if not self._secret_key:
            raise EnvironmentError(
                "FLET_SECRET_KEY não está definida no ambiente. "
                "Defina-a no arquivo .env antes de usar SecureStorage."
            )

    async def set(self, key: str, value: str) -> None:
        """
        Criptografa `value` e persiste no SharedPreferences com a chave `key`.

        Args:
            key:   Nome da chave no SharedPreferences.
            value: Valor em texto puro a ser criptografado e salvo.
        """
        if not value:
            # Salva string vazia sem criptografar (nada sensível para proteger)
            await ft.SharedPreferences().set(key, "")
            return

        encrypted_value = encrypt(value, self._secret_key)
        await ft.SharedPreferences().set(key, encrypted_value)
        return encrypted_value


    async def get(self, key: str) -> str | None:
        """
        Lê o valor criptografado do SharedPreferences e o descriptografa.

        Args:
            key: Nome da chave no SharedPreferences.

        Returns:
            O valor descriptografado em texto puro, ou None se não existir.
        """
        raw = await ft.SharedPreferences().get(key)

        if not raw:
            return raw  # None ou string vazia: retorna como está

        try:
            return decrypt(raw, self._secret_key)
        except Exception as ex:
            # Valor pode ser texto puro de uma versão anterior (migração)
            # Loga o aviso e retorna o valor bruto para não quebrar o fluxo
            print(f"[SecureStorage] Aviso: falha ao descriptografar '{key}': {ex}")
            return raw

    async def remove(self, key: str) -> None:
        """
        Remove a chave do SharedPreferences.

        Args:
            key: Nome da chave a ser removida.
        """
        await ft.SharedPreferences().remove(key)

    async def decrypt_value(self, encrypted_text: str) -> str:
        """
        Descriptografa um texto cifrado avulso (que não está no SharedPreferences).

        Útil quando o valor criptografado vem de uma fonte externa, como o
        banco de dados do backend.

        Args:
            encrypted_text: Texto cifrado produzido por encrypt().

        Returns:
            O valor descriptografado em texto puro.

        Raises:
            Exception: Se a descriptografia falhar (chave errada, dado corrompido, etc.).
        """
        return decrypt(encrypted_text, self._secret_key)
