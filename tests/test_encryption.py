"""
PRUEBA UNITARIA PU-003: Módulo de Cifrado AES-256
====================================================
"""

import pytest
import time
import json
from cryptography.fernet import InvalidToken


# ============ PRUEBAS BÁSICAS ============

class TestEncryptionBasic:
	"""Pruebas básicas de cifrado y descifrado"""

	def test_encrypt_decrypt_basic(self, encryption_key, test_data):
		"""✅ TC-001: Cifrado y descifrado básico"""
		# ✅ IMPORT AQUÍ, dentro de la función
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		original_data = test_data['simple']
		
		encrypted = encrypt_aes256(original_data, encryption_key)
		assert encrypted is not None
		assert isinstance(encrypted, bytes)
		assert encrypted != original_data.encode()
		
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == original_data
		assert isinstance(decrypted, str)

	def test_encrypt_with_string_input(self, encryption_key):
		"""✅ TC-002: Cifrado con entrada de tipo string"""
		# ✅ IMPORT AQUÍ
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = "Datos como string"
		encrypted = encrypt_aes256(data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == data

	def test_encrypt_with_bytes_input(self, encryption_key):
		"""✅ TC-003: Cifrado con entrada de tipo bytes"""
		# ✅ IMPORT AQUÍ
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = b"Datos como bytes"
		encrypted = encrypt_aes256(data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == data.decode('utf-8')


# ============ PRUEBAS DE VALIDACIÓN ============

class TestEncryptionValidation:
	"""Pruebas de validación de claves y parámetros"""

	def test_key_length_validation_short(self, test_data):
		"""✅ TC-004: Validación de longitud de clave - clave corta"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256
		
		short_key = b'a' * 16  # 128 bits (inválido)
		
		with pytest.raises(ValueError) as exc_info:
			encrypt_aes256(test_data['simple'], short_key)
		
		assert "32 bytes" in str(exc_info.value)

	def test_key_length_validation_long(self, test_data):
		"""✅ TC-005: Validación de longitud de clave - clave larga"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256
		
		long_key = b'a' * 64  # 512 bits (inválido)
		
		with pytest.raises(ValueError) as exc_info:
			encrypt_aes256(test_data['simple'], long_key)
		
		assert "32 bytes" in str(exc_info.value)

	def test_key_type_validation(self, test_data):
		"""✅ TC-006: Validación de tipo de clave"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256
		
		invalid_key = "not_bytes"
		
		with pytest.raises(TypeError):
			encrypt_aes256(test_data['simple'], invalid_key)

	def test_data_type_validation(self, encryption_key):
		"""✅ TC-007: Validación de tipo de datos"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256
		
		invalid_data = 12345
		
		with pytest.raises(TypeError):
			encrypt_aes256(invalid_data, encryption_key)


# ============ PRUEBAS DE SEGURIDAD ============

class TestEncryptionSecurity:
	"""Pruebas de seguridad del cifrado"""

	def test_decrypt_with_wrong_key(self, encryption_key, test_data):
		"""✅ TC-008: Descifrado con clave incorrecta"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = test_data['simple']
		encrypted = encrypt_aes256(data, encryption_key)
		
		wrong_key = b'b' * 32
		
		with pytest.raises(InvalidToken):
			decrypt_aes256(encrypted, wrong_key)

	def test_encrypted_data_tampering(self, encryption_key):
		"""✅ TC-009: Detección de datos tampered"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = "Datos sensibles"
		encrypted = encrypt_aes256(data, encryption_key)
		
		tampered = bytearray(encrypted)
		tampered[0] ^= 0xFF
		tampered = bytes(tampered)
		
		with pytest.raises(InvalidToken):
			decrypt_aes256(tampered, encryption_key)

	def test_different_encryption_same_data(self, encryption_key, test_data):
		"""✅ TC-010: Cifrados diferentes del mismo dato"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = test_data['simple']
		
		encrypted1 = encrypt_aes256(data, encryption_key)
		encrypted2 = encrypt_aes256(data, encryption_key)
		
		assert encrypted1 != encrypted2
		
		assert decrypt_aes256(encrypted1, encryption_key) == data
		assert decrypt_aes256(encrypted2, encryption_key) == data


# ============ PRUEBAS DE CASOS EXTREMOS ============

class TestEncryptionEdgeCases:
	"""Pruebas de casos extremos"""

	def test_encrypt_empty_string(self, encryption_key):
		"""✅ TC-011: Cifrado de string vacío"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		empty_data = ""
		encrypted = encrypt_aes256(empty_data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == empty_data

	def test_encrypt_empty_bytes(self, encryption_key):
		"""✅ TC-012: Cifrado de bytes vacíos"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		empty_data = b""
		encrypted = encrypt_aes256(empty_data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == ""

	def test_encrypt_single_character(self, encryption_key):
		"""✅ TC-013: Cifrado de un solo carácter"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = "A"
		encrypted = encrypt_aes256(data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == data

	def test_encrypt_large_data(self, encryption_key):
		"""✅ TC-014: Cifrado de datos grandes (100KB)"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		large_data = "X" * 100000
		encrypted = encrypt_aes256(large_data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == large_data
		assert len(decrypted) == 100000


# ============ PRUEBAS DE UNICODE ============

class TestEncryptionUnicode:
	"""Pruebas de soporte Unicode"""

	def test_unicode_latin_characters(self, encryption_key):
		"""✅ TC-015: Soporte de caracteres latinos especiales"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = "Datos con ñ, é, ü, á, ó"
		encrypted = encrypt_aes256(data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == data

	def test_unicode_asian_characters(self, encryption_key):
		"""✅ TC-016: Soporte de caracteres asiáticos"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = "中文 日本語 한글"
		encrypted = encrypt_aes256(data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == data

	def test_unicode_emoji(self, encryption_key):
		"""✅ TC-017: Soporte de emojis"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = "Datos con emojis 🔐 🔒 🗝️"
		encrypted = encrypt_aes256(data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == data

	def test_unicode_mixed(self, encryption_key, test_data):
		"""✅ TC-018: Soporte Unicode mixto"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = test_data['unicode']
		encrypted = encrypt_aes256(data, encryption_key)
		decrypted = decrypt_aes256(encrypted, encryption_key)
		assert decrypted == data


# ============ PRUEBAS DE PERFORMANCE ============

class TestEncryptionPerformance:
	"""Pruebas de performance"""

	def test_encryption_performance(self, encryption_key):
		"""✅ TC-019: Performance de cifrado"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256
		
		data = "X" * 1024
		
		start = time.time()
		encrypted = encrypt_aes256(data, encryption_key)
		elapsed = time.time() - start
		
		assert elapsed < 0.1, f"Cifrado tardó {elapsed}s, máximo 0.1s"

	def test_decryption_performance(self, encryption_key):
		"""✅ TC-020: Performance de descifrado"""
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		data = "X" * 1024
		encrypted = encrypt_aes256(data, encryption_key)
		
		start = time.time()
		decrypted = decrypt_aes256(encrypted, encryption_key)
		elapsed = time.time() - start
		
		assert elapsed < 0.1, f"Descifrado tardó {elapsed}s, máximo 0.1s"


# ============ PRUEBAS DE GENERACIÓN DE CLAVES ============

class TestKeyGeneration:
	"""Pruebas de generación de claves"""

	def test_generate_encryption_key(self):
		"""✅ TC-021: Generación de clave aleatoria"""
		from apps.pragma_dashboard.utils.encryption import generate_encryption_key
		
		key = generate_encryption_key()
		
		assert key is not None
		assert isinstance(key, bytes)
		assert len(key) > 0

	def test_generated_keys_are_different(self):
		"""✅ TC-022: Claves generadas son diferentes"""
		from apps.pragma_dashboard.utils.encryption import generate_encryption_key
		
		key1 = generate_encryption_key()
		key2 = generate_encryption_key()
		
		assert key1 != key2


# ============ PRUEBAS INTEGRADAS CON DJANGO MODELS ============

class TestEncryptionWithModels:
	"""Pruebas de encriptación integradas con modelos Django"""

	def test_encrypt_analisis_ia_data(self, db, encryption_key):
		"""✅ TC-025: Encriptar datos de análisis IA (con HEX conversion)"""
		# ✅ IMPORTS AQUÍ, dentro de la función
		from django.contrib.auth.models import User
		from apps.pragma_dashboard.models import AnalisisIA
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		# Crear usuario
		user = User.objects.create_user(
			username='testuser',
			email='test@pragma.cl',
			password='TestPass123'
		)
		
		# Datos sensibles de Groq
		datos_groq = {
			'resumen_ejecutivo': 'Usuario con alta vulnerabilidad psicológica',
			'conclusiones_clinicas': 'Requiere intervención profesional inmediata',
			'alertas_psicologicas': 'Riesgo de estrés severo detectado',
		}
		
		# ✅ CIFRAR y CONVERTIR A HEX (JSONField requiere strings, no bytes)
		datos_cifrados = {}
		for campo, valor in datos_groq.items():
			datos_cifrados_bytes = encrypt_aes256(valor, encryption_key)
			datos_cifrados[campo] = datos_cifrados_bytes.hex()  # ✅ Convertir a HEX
		
		# Crear análisis
		analisis = AnalisisIA.objects.create(
			usuario=user,
			usuario_nombre='Test User',
			usuario_email='test@pragma.cl',
			savefile_id=1,
			nivel_riesgo='alto',
			requiere_intervencion=True,
			datos_completos_groq=datos_cifrados
		)
		
		# Verificar
		assert analisis.id is not None
		assert 'resumen_ejecutivo' in analisis.datos_completos_groq
		
		# ✅ Descifrar: HEX → BYTES → Descifrar
		resumen_hex = analisis.datos_completos_groq['resumen_ejecutivo']
		resumen_bytes = bytes.fromhex(resumen_hex)
		resumen_descifrado = decrypt_aes256(resumen_bytes, encryption_key)
		assert 'vulnerabilidad' in resumen_descifrado

	def test_encrypt_savefile_usuario(self, db, encryption_key):
		"""✅ TC-026: Encriptar datos de SaveFile"""
		# ✅ IMPORTS AQUÍ
		from django.contrib.auth.models import User
		from apps.pragma_dashboard.models import SaveFileUsuario
		from apps.pragma_dashboard.utils.encryption import encrypt_aes256, decrypt_aes256
		
		user = User.objects.create_user(
			username='testuser2',
			email='test2@pragma.cl',
			password='TestPass123'
		)
		
		# Datos del juego
		datos_savefile = {
			'nivel': 3,
			'puntos': 1250,
			'personaje': {
				'nombre': 'Sebastian',
				'salud': 80,
			}
		}
		
		datos_str = json.dumps(datos_savefile)
		datos_cifrados = encrypt_aes256(datos_str, encryption_key)
		
		# Crear SaveFile
		savefile = SaveFileUsuario.objects.create(
			usuario=user,
			datos_savefile=datos_cifrados.hex(),
			version_savefile='1.0'
		)
		
		# Descifrar
		datos_recuperados = bytes.fromhex(savefile.datos_savefile)
		datos_descifrados = decrypt_aes256(datos_recuperados, encryption_key)
		datos_dict = json.loads(datos_descifrados)
		
		assert datos_dict['personaje']['nombre'] == 'Sebastian'