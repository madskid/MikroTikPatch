from mikro import *


def generate_eddsa_keypair():
    curve = getcurvebyname('Ed25519')
    private_key = ECPrivateKey.eddsa_generate(curve)
    return private_key.eddsa_encode(), private_key.pubkey.eddsa_encode()


def generate_kcdsa_keypair():
    curve = getcurvebyname('Curve25519')
    private_key = ECPrivateKey.generate(curve)
    return Tools.inttobytes_le(private_key.scalar, 32), Tools.inttobytes_le(int(private_key.pubkey.point.x), 32)


def lic_parse_ros(lic: str, public_key: bytes):
    assert (isinstance(public_key, bytes))
    slic = lic.replace(MIKRO_LICENSE_HEADER, '').replace(
        MIKRO_LICENSE_FOOTER, '').replace('\n', '').replace(' ', '')
    lic: bytes = mikro_base64_decode(slic)
    licVal = mikro_decode(lic[:16])
    software_id = int.from_bytes(licVal[:6], 'little')
    print(f"Software ID: {mikro_softwareid_encode(software_id)}({hex(software_id)})")
    print(f"RouterOS Version: {licVal[6]}")
    print(f"License Level: {licVal[7]}")
    nonce_hash = lic[16:32]
    print(f"Nonce Hash: {nonce_hash.hex()}")
    signature = lic[32:64]
    print(f"Signature: {signature.hex()}")
    print(f'License valid: {mikro_kcdsa_verify(licVal, nonce_hash+signature, public_key)}')


def lic_parse_chr(lic: str, public_key: bytes):
    assert (isinstance(public_key, bytes))
    slic = lic.replace(MIKRO_LICENSE_HEADER, '').replace(
        MIKRO_LICENSE_FOOTER, '').replace('\n', '').replace(' ', '')
    lic: bytes = mikro_base64_decode(slic)
    licVal = mikro_decode(lic[:16])
    system_id = int.from_bytes(licVal[:8], 'little')
    print(f"System ID: {mikro_systemid_encode(system_id)}({hex(system_id)})")
    print(f"Deadline: {licVal[11]}")
    print(f"Level: {licVal[12]}")
    nonce_hash = lic[16:32]
    print(f"Nonce Hash: {nonce_hash.hex()}")
    signature = lic[32:64]
    print(f"Signature: {signature.hex()}")
    print(f'License valid: {mikro_kcdsa_verify(licVal, nonce_hash+signature, public_key)}')


def lic_gen_ros(software_id, private_key: bytes):
    assert (isinstance(private_key, bytes))
    if isinstance(software_id, str):
        software_id = mikro_softwareid_decode(software_id)
    lic = software_id.to_bytes(6, 'little')
    varb7 = 7  # RouterOS Version
    varb8 = 22  # Features
    lic += varb7.to_bytes(1, 'little')
    lic += varb8.to_bytes(1, 'little')
    lic += b'\0'*8
    sig = mikro_kcdsa_sign(lic, private_key)
    lic = mikro_base64_encode(mikro_encode(lic)+sig, True)
    return MIKRO_LICENSE_HEADER + '\n' + lic[:len(lic)//2] + '\n' + lic[len(lic)//2:] + '\n' + MIKRO_LICENSE_FOOTER


def lic_gen_chr(system_id, private_key: bytes):
    assert (isinstance(private_key, bytes))
    if isinstance(system_id, str):
        system_id = mikro_systemid_decode(system_id)
    lic = system_id.to_bytes(8, 'little')
    varb9 = 0  # Unknown Value
    varb10 = 87  # Unknown Value
    varb11 = 134  # Unknown Value
    varb12 = 244  # Renew Date
    varb13 = 3  # License Level
    lic += varb9.to_bytes(1, 'little')
    lic += varb10.to_bytes(1, 'little')
    lic += varb11.to_bytes(1, 'little')
    lic += varb12.to_bytes(1, 'little')
    lic += varb13.to_bytes(1, 'little')
    lic += b'\0'*3
    sig = mikro_kcdsa_sign(lic, private_key)
    lic = mikro_base64_encode(mikro_encode(lic)+sig, True)
    return MIKRO_LICENSE_HEADER + '\n' + lic[:len(lic)//2] + '\n' + lic[len(lic)//2:] + '\n' + MIKRO_LICENSE_FOOTER


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='MikroTik License Manager')
    subparsers = parser.add_subparsers(dest="command")
    genkey_parser = subparsers.add_parser('genkey', help='Generate Keys')
    licgenros_parser = subparsers.add_parser(
        'licgenros', help='Generate RouterOS License')
    licgenros_parser.add_argument('software_id', type=str, help='Software ID')
    licgenros_parser.add_argument('private_key', type=str, help='Private Key')
    licgenchr_parser = subparsers.add_parser(
        'licgenchr', help='Generate CHR License')
    licgenchr_parser.add_argument('system_id', type=str, help='System ID')
    licgenchr_parser.add_argument('private_key', type=str, help='Private Key')
    licparseros_parser = subparsers.add_parser(
        'licparseros', help='Parse RouterOS License')
    licparseros_parser.add_argument(
        'license', type=str, help='License String. Format: 66c1aRpjM52VlmgwPWQv6b6DPwX3vyg+vxlgb+ebXMP2K5A0Ei2mr5m+wHLUqrqmTNz7shFjNJAaMjXK3zXvIA==')
    licparseros_parser.add_argument('public_key', type=str, help='Public Key')
    licparsechr_parser = subparsers.add_parser(
        'licparsechr', help='Parse CHR License')
    licparsechr_parser.add_argument(
        'license', type=str, help='License String. Format: 66c1aRpjM52VlmgwPWQv6b6DPwX3vyg+vxlgb+ebXMP2K5A0Ei2mr5m+wHLUqrqmTNz7shFjNJAaMjXK3zXvIA==')
    licparsechr_parser.add_argument('public_key', type=str, help='Public Key')

    args = parser.parse_args()

    MIKRO_LICENSE_HEADER = '-----BEGIN MIKROTIK SOFTWARE KEY------------'
    MIKRO_LICENSE_FOOTER = '-----END MIKROTIK SOFTWARE KEY--------------'

    if args.command == 'genkey':
        print('export MIKRO_NPK_SIGN_PUBLIC_KEY="C293CED638A2A33C681FC8DE98EE26C54EADC5390C2DFCE197D35C83C416CF59"')
        print('export MIKRO_LICENSE_PUBLIC_KEY="8E1067E4305FCDC0CFBF95C10F96E5DFE8C49AEF486BD1A4E2E96C27F01E3E32"')
        eddsa_private_key, eddsa_public_key = generate_eddsa_keypair()
        print(f'export CUSTOM_NPK_SIGN_PRIVATE_KEY="{eddsa_private_key.hex().upper()}"')
        print(f'export CUSTOM_NPK_SIGN_PUBLIC_KEY="{eddsa_public_key.hex().upper()}"')
        kcdsa_private_key, kcdsa_public_key = generate_kcdsa_keypair()
        print(f'export CUSTOM_LICENSE_PRIVATE_KEY="{kcdsa_private_key.hex().upper()}"')
        print(f'export CUSTOM_LICENSE_PUBLIC_KEY="{kcdsa_public_key.hex().upper()}"')
    elif args.command == 'licgenros':
        print(lic_gen_ros(args.software_id, bytes.fromhex(args.private_key)))
    elif args.command == 'licgenchr':
        print(lic_gen_chr(args.system_id, bytes.fromhex(args.private_key)))
    elif args.command == 'licparseros':
        lic_parse_ros(args.license, bytes.fromhex(args.public_key))
    elif args.command == 'licparsechr':
        lic_parse_chr(args.license, bytes.fromhex(args.public_key))
    else:
        parser.print_help()
