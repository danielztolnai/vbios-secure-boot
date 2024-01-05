# How to add the hash of your VBIOS to the secure boot db

*This guide will help you if you want to use secure boot with custom keys and custom keys only. In this case, most GPUs will not show any output by default as their ROMs are usually signed with the global Microsoft cert. This guide shows you how to add a single hash to your secure boot db for your VBIOS without modifying the GPU or adding the Microsoft keys.*

## 0. Libraries and packages required
Clone the submodules:
```
git submodule init
git submodule update
```
After this, simply use make to compile the tools in this repository: `make`. You will need a few dependencies and additional packages:
* osslsigncode
* gnu-efi
* efitools
* efivar

You can install these with your package manager in most distributions. For example in Debian/Ubuntu/etc.: `apt-get install osslsigncode gnu-efi efitools efivar`

You will also need the EfiCompressor Python library which you can install for example with pip: `pip3 install -r ./uefi_decompress/requirements.txt`

## 1. Dump the VBIOS ROM from your card
Find your card within the pci subsystem, and use the following commands:
```
echo 1 > /sys/bus/pci/devices/<DEVICE>/rom
cat /sys/bus/pci/devices/<DEVICE>/rom > vbios.rom
echo 0 > /sys/bus/pci/devices/<DEVICE>/rom
```

## 2. Find the EFI image in the ROM
```
./rom-parser/rom-parser vbios.rom
```

Example output:
```
Valid ROM signature found @0h, PCIR offset 2ech
	PCIR: type 0 (x86 PC-AT), vendor: 0000, device: 0000, class: 000000
	PCIR: revision 0, vendor revision: 0000
Valid ROM signature found @e800h, PCIR offset 1ch
	PCIR: type 3 (EFI), vendor: 0000, device: 0000, class: 000000
	PCIR: revision 0, vendor revision: 0
		EFI image offset 58h
		EFI: Signature Valid, Subsystem: Boot, Machine: X64
	Last image
```
The first image is the legacy, while the second one is the EFI ROM. Take note that the EFI ROM is found at `0xe800` and the EFI image within starts at an offset of `0x58`. Your values may be different.

## 3. Extract the EFI image and decompress it
Use the EFI ROM base address and the EFI image offset from the previous step.
```
dd if=vbios.rom bs=1 skip=$((0x58 + 0xe800)) of=vbios.efi.img
python3 ./uefi_decompress/decompress.py vbios.efi.img vbios.efi
```

## 4. Get the EFI digest
```
osslsigncode verify vbios.efi | grep "message digest"
```

Example output:
```
Current message digest    : E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855
Calculated message digest : E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855
```
Ideally the two digests are the same.

Depending on your version of `osslsigncode` it might provide no results requiring a CA file. In this case provide any CA file using the `-CAfile` option, for example:
```
osslsigncode verify -CAfile /etc/ssl/certs/ca-certificates.crt vbios.efi | grep "message digest"
```

## 5. Create an EFI signature list, sign and deliver it as an update payload
Use the digest from the previous step.

The `GUID` is the signature owner, same as the one used when signing your other signature lists. `PK.key` and `PK.crt` are the platform key secret key and certificate respectively.
```
./digest-to-efi-sig-list/digest-to-efi-sig-list <DIGEST> vbios.esl
sign-efi-sig-list -k PK.key -c PK.crt -g <GUID> -a db vbios.esl vbios.db.auth
efi-updatevar -a -f vbios.db.auth -k PK.key db
```

You can check the result with `efi-readvar`, your db should now have one additional list with the type SHA256 and it should include the digest from the previous step.

At the next reboot you should have a BIOS screen even with secure boot activated with custom keys only.
