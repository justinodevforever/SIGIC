class Criptografia():

    def cesar(self, texto, chave):
        resultado = ""
        for char in texto:
            if char.isalpha():
                desloc = 65 if char.isupper() else 97
                resultado += chr((ord(char) - desloc + chave) % 26 + desloc)
            else:
                resultado += char
        return resultado
    
    def cesar_descriptografar(self, texto, chave):

        resultado = ""

        for char in texto:
            if char.isalpha():
                desloc = 65 if char.isupper() else 97
                resultado += chr((ord(char) - desloc - chave) % 26 + desloc)
            else:
                resultado += char

        return resultado
    
# crip = Criptografia()

# mensagem = "SEGURANCA"
# chave = 3
# criptografada = crip.cesar(mensagem, chave)

# descri = crip.cesar_descriptografar(criptografada, chave)


# print("Criptografada:", criptografada)
# print("Descriptografia", descri)


from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

class criptografia_simetrica_cryptography():


    def criptografar(self, fernet, message):
        
        mensagem_bytes = message.encode()

        criptografada = fernet.encrypt(mensagem_bytes)
        print("Criptografada:", criptografada)

        return criptografada

    def descriptografar(self, fernet, criptografada):
    
        descriptografada = fernet.decrypt(criptografada)
        print("Descriptografada:", descriptografada.decode())


chave = Fernet.generate_key()
fernet = Fernet(chave)
message = "SEGURANCA INFORMÁTICA"

cripto = criptografia_simetrica_cryptography()

criptografada = cripto.criptografar(fernet, message)

cripto.descriptografar(fernet,criptografada)



class Cripgrafia_assimetrica_cryptography_RSA():
    

    # 1. Gerar par de chaves RSA
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    chave_publica = chave_privada.public_key()

    # 2. Mensagem a assinar
    mensagem = b"Mensagem importante"

    # 3. Assinatura digital
    assinatura = chave_privada.sign(
        mensagem,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Assinatura gerada:", assinatura)

    # 4. Verificação da assinatura
    try:
        chave_publica.verify(
            assinatura,
            mensagem,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Assinatura válida!")
    except:
        print("Assinatura inválida!")

class Cripgrafia_assimetrica_cryptography_ECC():

    # 1. Gerar par de chaves ECC
    chave_privada_ecc = ec.generate_private_key(ec.SECP256R1())
    chave_publica_ecc = chave_privada_ecc.public_key()

    # 2. Mensagem a assinar
    mensagem = b"Mensagem ECC"

    # 3. Assinatura
    assinatura_ecc = chave_privada_ecc.sign(
        mensagem,
        ec.ECDSA(hashes.SHA256())
    )
    print("Assinatura ECC:", assinatura_ecc)

    # 4. Verificação
    try:
        chave_publica_ecc.verify(
            assinatura_ecc,
            mensagem,
            ec.ECDSA(hashes.SHA256())
        )
        print("Assinatura ECC válida!")
    except:
        print("Assinatura ECC inválida!")

