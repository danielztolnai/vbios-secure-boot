INC=/usr/include/efi /usr/include/efi/x86_64
INC_PARAMS=$(INC:%=-I%)

default: main.c
	gcc -o digest-to-efi-sig-list $(INC_PARAMS) main.c

clean:
	rm -f digest-to-efi-sig-list
