# Installation / Telepítés

## English

Before installing anything, check that the hardware is suitable for this project.

### 1. Check the uConsole hardware

This project requires the **uConsole AIO v2 hardware, a dedicated CM4-compatible replacement mainboard, and the required ribbon cable**.

The ribbon cable cannot be connected to the original uConsole mainboard. The replacement CM4-compatible mainboard is a required part of the hardware setup.

The Ethernet interface used by the tester must be available as `eth0`.

### 2. Check the Ethernet PHY

Before installing the software, check which PHY is attached to `eth0`:

```bash
cat /sys/class/net/eth0/phydev/phy_id
```

The expected PHY ID for this project is:

```text
0x600d84a2
```

This corresponds to the Broadcom BCM54213PE used by the tested hardware.

If your system reports a different PHY ID, do not assume that the tester will work. The diagnostic registers used by this project are PHY-specific.

### Requirements

- Raspberry Pi / Linux system with the BCM54213PE Ethernet PHY and `eth0`.
- Python 3 and Python virtual-environment support (`python3-venv`).
- Pillow.
- A C compiler (`gcc`/`cc`) and Linux MII ioctl support.
- Permission to access MDIO registers; the application invokes the MDIO utilities through `sudo`.

### Install

On Debian/Raspberry Pi OS, install the basic system packages first:

```bash
sudo apt update
sudo apt install -y python3 python3-venv build-essential
```

Then, from the repository directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
chmod +x build.sh run_cable_test_hu.sh run_cable_test_eng.sh
./build.sh
```

The launch scripts automatically use `.venv` when it exists; otherwise they fall back to `python3`.

Set the operator name in:

```text
config/ulan_config.json
```

The file intentionally contains only the operator setting.

Run the Hungarian interface with:

```bash
./run_cable_test_hu.sh
```

or the English interface with:

```bash
./run_cable_test_eng.sh
```

### Native MDIO utilities

The repository contains tested AArch64 binaries in `bin/` and the corresponding C sources in `src/`.

Running:

```bash
./build.sh
```

recompiles the utilities for the current machine and replaces the binaries.

If you prepare binaries for a target device, build them on the target architecture.

## Magyar

A telepítés előtt először ellenőrizd, hogy a hardver megfelel-e a projekt követelményeinek.

### 1. A uConsole hardver ellenőrzése

A projekt használatához **uConsole AIO v2 hardver, egy speciális CM4-kompatibilis csere-alaplap és a szükséges szalagkábel** szükséges.

A szalagkábel az eredeti uConsole alaplaphoz nem csatlakoztatható, ezért a CM4-kompatibilis csere-alaplap a hardverkonfiguráció kötelező része.

A tesztelő által használt Ethernet interfésznek `eth0` néven elérhetőnek kell lennie.

### 2. Az Ethernet PHY ellenőrzése

A telepítés előtt ellenőrizd, hogy milyen PHY kapcsolódik az `eth0` interfészhez:

```bash
cat /sys/class/net/eth0/phydev/phy_id
```

A projekthez elvárt PHY ID:

```text
0x600d84a2
```

Ez a tesztelt hardveren használt Broadcom BCM54213PE PHY azonosítója.

Ha a rendszer más PHY ID-t jelez, ne feltételezd, hogy a tesztelő működni fog. A projekt által használt diagnosztikai regiszterek PHY-specifikusak.

### Követelmények

- Raspberry Pi / Linux rendszer BCM54213PE Ethernet PHY-val és `eth0` interfésszel.
- Python 3 és virtuális környezet támogatás (`python3-venv`).
- Pillow.
- C fordító (`gcc`/`cc`) és Linux MII ioctl támogatás.
- Az MDIO regiszterek eléréséhez szükséges jogosultság; az alkalmazás az MDIO segédprogramokat `sudo` segítségével futtatja.

### Telepítés

Debian/Raspberry Pi OS alatt először telepítsd az alapcsomagokat:

```bash
sudo apt update
sudo apt install -y python3 python3-venv build-essential
```

Ezután a repository könyvtárában:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
chmod +x build.sh run_cable_test_hu.sh run_cable_test_eng.sh
./build.sh
```

Az indító scriptek automatikusan a `.venv` Pythonját használják, ha az létezik; egyébként a rendszer `python3` programjára állnak vissza.

Az operátor nevét a következő fájlban kell megadni:

```text
config/ulan_config.json
```

A fájl szándékosan csak az operátor beállítását tartalmazza.

Magyar felület indítása:

```bash
./run_cable_test_hu.sh
```

Angol felület indítása:

```bash
./run_cable_test_eng.sh
```

### Natív MDIO segédprogramok

A repository tartalmazza a tesztelt AArch64 binárisokat a `bin/` könyvtárban és a hozzájuk tartozó C forrásokat a `src/` könyvtárban.

A:

```bash
./build.sh
```

parancs az aktuális gépre fordítja újra a segédprogramokat, és lecseréli a binárisokat.

Ha célgépre készítesz binárisokat, a fordítást a célarchitektúrán végezd.
