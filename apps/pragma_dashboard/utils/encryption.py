from cryptography.fernet import Fernet, InvalidToken
import base64
import os

class EncryptionError(Exception):
	"""Excepción personalizada para errores de cifrado"""
	pass

def encrypt_aes256(data, key):
	"""
	Cifrar datos usando AES-256 con Fernet
	
	Args:
		data: Datos a cifrar (string o bytes)
		key: Clave de cifrado (debe ser exactamente 32 bytes para AES-256)
	
	Returns:
		Datos cifrados en bytes
	"""
	# Validar tipo de datos
	if isinstance(data, str):
		data = data.encode('utf-8')
	elif not isinstance(data, bytes):
		raise TypeError(f"data debe ser str o bytes, no {type(data)}")
	
	# Validar clave
	if not isinstance(key, bytes):
		raise TypeError(f"key debe ser bytes, no {type(key)}")
	
	if len(key) != 32:
		raise ValueError(
			f"La clave debe tener exactamente 32 bytes (256 bits), "
			f"se recibieron {len(key)} bytes"
		)
	
	try:
		# Convertir clave a base64 para Fernet
		key_b64 = base64.urlsafe_b64encode(key)
		cipher = Fernet(key_b64)
		encrypted_data = cipher.encrypt(data)
		return encrypted_data
	except Exception as e:
		raise EncryptionError(f"Error durante el cifrado: {str(e)}")

def decrypt_aes256(encrypted_data, key):
	"""
	Descifrar datos cifrados con AES-256
	
	Args:
		encrypted_data: Datos cifrados (bytes)
		key: Clave de descifrado (debe ser igual a la usada en encrypt)
	
	Returns:
		Datos descifrados como string
	"""
	# Validar parámetros
	if not isinstance(encrypted_data, bytes):
		raise TypeError(f"encrypted_data debe ser bytes, no {type(encrypted_data)}")
	
	if not isinstance(key, bytes):
		raise TypeError(f"key debe ser bytes, no {type(key)}")
	
	if len(key) != 32:
		raise ValueError(
			f"La clave debe tener exactamente 32 bytes (256 bits), "
			f"se recibieron {len(key)} bytes"
		)
	
	try:
		# Preparar clave
		key_b64 = base64.urlsafe_b64encode(key)
		cipher = Fernet(key_b64)
		decrypted_data = cipher.decrypt(encrypted_data)
		return decrypted_data.decode('utf-8')
	except InvalidToken:
		raise InvalidToken("La clave de descifrado es incorrecta o los datos están dañados")
	except Exception as e:
		raise EncryptionError(f"Error durante el descifrado: {str(e)}")

def generate_encryption_key():
	"""Generar una nueva clave de cifrado aleatoria de 256 bits"""
	return Fernet.generate_key()