How to add the hash of your VBIOS to the secure boot db if you are using custom keys.

0. Libraries and packages required
* osslsigncode
* gnu-efi
* efitools efivar

1. Dump the VBIOS ROM from your card
Find your card under the pci subsystem, and use the following commands:
```
echo 1 > /sys/bus/pci/devices/<DEVICE>/rom
cat /sys/bus/pci/devices/<DEVICE>/rom > vbios.rom
echo 0 > /sys/bus/pci/devices/<DEVICE>/rom
```

2. Find the EFI image in the ROM
```
./rom-parser/rom-parser vbios.rom | grep "EFI image offset"
```


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

3. Extract the EFI image and decompress it
```
dd if=vbios.rom bs=1 skip=$((0x58 + 0xe800)) of=vbios.efi.img
python3 ./uefi_decompress/decompress.py vbios.efi.img vbios.efi
```

4. Get the EFI digest
```
osslsigncode verify vbios.efi | grep "message digest"
```

5. Create an EFI signature list, sign and deliver it as an update payload
```
./digest-to-efi-sig-list/digest-to-efi-sig-list <DIGEST> vbios.esl
sign-efi-sig-list -k PK.key -c PK.crt -g <GUID> -a db vbios.esl vbios.db.auth
efi-updatevar -a -f vbios.db.auth -k PK.key db
```
