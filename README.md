**DO WITH YOUR OWN RISK**

# Download

You can download the automatically generated RouterOS image from [here](https://github.com/ahmadwhet/MikroTikPatch/releases).

# How to generate license key

I have already generated the keys for you. You can use them to generate a license key and sign packages:

```
export MIKRO_NPK_SIGN_PUBLIC_KEY="C293CED638A2A33C681FC8DE98EE26C54EADC5390C2DFCE197D35C83C416CF59"
export MIKRO_LICENSE_PUBLIC_KEY="8E1067E4305FCDC0CFBF95C10F96E5DFE8C49AEF486BD1A4E2E96C27F01E3E32"
export CUSTOM_NPK_SIGN_PRIVATE_KEY="7D008D9B80B036FB0205601FEE79D550927EBCA937B7008CC877281F2F8AC640"
export CUSTOM_NPK_SIGN_PUBLIC_KEY="28F886E32C141123126CFBCAD56766E99D1720CEB1F12BE2468BEBE7662FBEDB"
export CUSTOM_LICENSE_PRIVATE_KEY="9DBC845E9018537810FDAE62824322EEE1B12BAD81FCA28EC295FB397C61CE0B"
export CUSTOM_LICENSE_PUBLIC_KEY="723A34A6E3300F23E4BAA06156B9327514AEC170732655F16E04C17928DD770F"
export MIKRO_CLOUD_PUBLIC_KEY="8E1067E4305FCDC0CFBF95C10F96E5DFE8C49AEF486BD1A4E2E96C27F01E3E32"
export CUSTOM_CLOUD_PUBLIC_KEY="723A34A6E3300F23E4BAA06156B9327514AEC170732655F16E04C17928DD770F"
export MIKRO_LICENCE_URL="mikrotik.com"
export CUSTOM_LICENCE_URL="127.0.0.1"
export MIKRO_UPGRADE_URL="download.mikrotik.com"
export CUSTOM_UPGRADE_URL="127.0.0.1"
export MIKRO_CLOUD_URL="cloud2.mikrotik.com"
export CUSTOM_CLOUD_URL="127.0.0.1"
```

You can generate your own keys yourself, but in this case you will have to manually create a MikroTik image.

- Install Python 3.x
- Clone this repository

Here is the command to generate your own keys:

```
python3 license.py genkey
```

## RouterOS

### Let's assume that your software_id is: 4JZ2-H049

```
# python3 license.py licgenros 4JZ2-H049 9DBC845E9018537810FDAE62824322EEE1B12BAD81FCA28EC295FB397C61CE0B
-----BEGIN MIKROTIK SOFTWARE KEY------------
50eNy667HxTQwmCtCpT15YaVx6lpPHQoy2w/KIsjoOHs
Eq/cU24G3/aIjHVeXXqjPRTubErxzaqjHD3aWIi1KA==
-----END MIKROTIK SOFTWARE KEY--------------
```

## Cloud Hosted Router

### Let's assume that your system_id is: pjLQ21gHzfI

```
# python3 license.py licgenchr pjLQ21gHzfI 9DBC845E9018537810FDAE62824322EEE1B12BAD81FCA28EC295FB397C61CE0B
-----BEGIN MIKROTIK SOFTWARE KEY------------
hdMf+/8rDWLOCOuNt8qP82NgHbN8YdQfJcZNRyWzBerz
BfwOQF1ehUjNubOGkCf4zkPQrK7U+2hbM/uh7gJWGA==
-----END MIKROTIK SOFTWARE KEY--------------
```

# Generate own images

## Requirements

### Debian / Ubuntu

```
apt-get update
apt-get install -y wget curl mkisofs xorriso sudo zip unzip git squashfs-tools \
rsync ca-certificates python3 python3-pefile qemu-utils extlinux dosfstools --no-install-recommends
```

## Download dependencies

```
export VERSION="7.20.2"

wget https://download.mikrotik.com/routeros/$VERSION/mikrotik-$VERSION.iso
wget https://download.mikrotik.com/routeros/$VERSION/install-image-$VERSION.zip
wget https://download.mikrotik.com/routeros/$VERSION/chr-$VERSION.img.zip
wget https://nchc.dl.sourceforge.net/project/refind/0.14.2/refind-bin-0.14.2.zip
git clone -b main --single-branch --depth=1 https://github.com/madskid/MikroTikPatch
unzip install-image-$VERSION.zip
unzip chr-$VERSION.img.zip
unzip refind-bin-0.14.2.zip refind-bin-0.14.2/refind/refind_x64.efi
cp mikrotik-$VERSION.iso ./MikroTikPatch/mikrotik.iso
cp install-image-$VERSION.img ./MikroTikPatch/install-image.img
cp chr-$VERSION.img ./MikroTikPatch/chr.img
cd ./MikroTikPatch
```

## Patch ISO

```
mkdir ./iso 
mount -o loop,ro mikrotik.iso ./iso
mkdir ./new_iso
cp -r ./iso/* ./new_iso/
rsync -a ./iso/ ./new_iso/
umount ./iso
rm -rf ./iso
mv ./new_iso/routeros-$VERSION.npk ./
python3 patch.py npk routeros-$VERSION.npk
NPK_FILES=$(find ./new_iso/*.npk)
for file in $NPK_FILES; do
  python3 npk.py sign $file $file
done
cp routeros-$VERSION.npk ./new_iso/
mkdir ./efiboot
mount -o loop ./new_iso/efiboot.img ./efiboot
python3 patch.py kernel ./efiboot/linux.x86_64
cp ./efiboot/linux.x86_64 ./BOOTX64.EFI
cp ./BOOTX64.EFI ./new_iso/isolinux/linux
umount ./efiboot
mkisofs -o mikrotik-$VERSION-patched.iso \
  -V "MikroTik $VERSION x86" \
  -sysid "" -preparer "MikroTiK" \
  -publisher "" -A "MikroTiK RouterOS" \
  -input-charset utf-8 \
  -b isolinux/isolinux.bin \
  -c isolinux/boot.cat \
  -no-emul-boot \
  -boot-load-size 4 \
  -boot-info-table \
  -eltorito-alt-boot \
  -e efiboot.img \
  -no-emul-boot \
  -R -J \
  ./new_iso
rm -rf ./efiboot
mkdir ./all_packages
cp ./new_iso/*.npk ./all_packages/
rm -rf ./new_iso
cd ./all_packages
zip ../all_packages-x86-$VERSION-patched.zip *.npk
cd ..
```

## Patch install-image

```
cp install-image.img install-image-$VERSION-patched.img
modprobe nbd
qemu-nbd -c /dev/nbd0 -f raw install-image-$VERSION-patched.img
mkdir ./install-image
mount /dev/nbd0 ./install-image
cp ../refind-bin-0.14.2/refind/refind_x64.efi ./install-image/EFI/BOOT/BOOTX64.EFI
cp ./BOOTX64.EFI ./install-image/linux
NPK_FILES=($(find ./all_packages/*.npk))
for ((i=1; i<=${#NPK_FILES[@]}; i++))
do
  echo "${NPK_FILES[$i-1]}=>$i.npk" 
  cp ${NPK_FILES[$i-1]} ./install-image/$i.npk
done
umount /dev/nbd0
qemu-nbd -d /dev/nbd0
rm -rf ./install-image

qemu-img convert -f raw -O qcow2 install-image-$VERSION-patched.img install-image-$VERSION-patched.qcow2
qemu-img convert -f raw -O vmdk install-image-$VERSION-patched.img install-image-$VERSION-patched.vmdk
qemu-img convert -f raw -O vpc install-image-$VERSION-patched.img install-image-$VERSION-patched.vhd
qemu-img convert -f raw -O vhdx install-image-$VERSION-patched.img install-image-$VERSION-patched.vhdx
qemu-img convert -f raw -O vdi install-image-$VERSION-patched.img install-image-$VERSION-patched.vdi
```

## Patch Cloud Hosted Router

```
cp chr.img chr-$VERSION-patched.img
modprobe nbd
qemu-nbd -c /dev/nbd0 -f raw chr-$VERSION-patched.img
mkdir -p ./chr/{boot,routeros}
mount /dev/nbd0p1 ./chr/boot/
mkdir -p ./chr/boot/BOOT
cp ./BOOTX64.EFI ./chr/boot/EFI/BOOT/BOOTX64.EFI
extlinux --install -H 64 -S 32 ./chr/boot/BOOT
echo -e "default system\nlabel system\n\tkernel /EFI/BOOT/BOOTX64.EFI\n\tappend load_ramdisk=1 root=/dev/ram0 quiet" > syslinux.cfg
cp syslinux.cfg ./chr/boot/BOOT/
rm syslinux.cfg
umount /dev/nbd0p1
mount /dev/nbd0p2 ./chr/routeros/
cp ./all_packages/routeros-$VERSION.npk ./chr/routeros/var/pdb/system/image
umount /dev/nbd0p2
qemu-nbd -d /dev/nbd0
rm -rf ./chr

qemu-img convert -f raw -O qcow2 chr-$VERSION-patched.img chr-$VERSION-patched.qcow2
qemu-img convert -f raw -O vmdk chr-$VERSION-patched.img chr-$VERSION-patched.vmdk
qemu-img convert -f raw -O vpc chr-$VERSION-patched.img chr-$VERSION-patched.vhd
qemu-img convert -f raw -O vhdx chr-$VERSION-patched.img chr-$VERSION-patched.vhdx
qemu-img convert -f raw -O vdi chr-$VERSION-patched.img chr-$VERSION-patched.vdi
```

## Patch Netinstall

```
wget https://download.mikrotik.com/routeros/$VERSION/netinstall-$VERSION.zip
unzip netinstall-$VERSION.zip
python3 patch.py netinstall netinstall.exe
zip netinstall-$VERSION-patched.zip netinstall.exe
rm netinstall-$VERSION.zip netinstall.exe LICENSE.txt
```


## Patch MIPSBE (Only work until v7.17)

```
wget https://download.mikrotik.com/routeros/$VERSION/routeros-$VERSION-mipsbe.npk
wget https://download.mikrotik.com/routeros/$VERSION/all_packages-mipsbe-$VERSION.zip
mkdir ./all_packages-mipsbe
unzip all_packages-mipsbe-$VERSION.zip -d ./all_packages-mipsbe/
python3 patch.py npk routeros-$VERSION-mipsbe.npk
mv routeros-$VERSION-mipsbe.npk routeros-$VERSION-mipsbe-patched.npk
rm all_packages-mipsbe-$VERSION.zip
NPK_FILES=$(find ./all_packages-mipsbe/*.npk)
for file in $NPK_FILES; do
  python3 npk-mipsbe.py sign $file $file
done
cd ./all_packages-mipsbe
zip ../all_packages-mipsbe-$VERSION-patched.zip *.npk
cd ../
rm -rf ./all_packages-mipsbe
```
