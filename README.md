# uLAN Cable Tester

### A small cable tester built into a uConsole.

![uLAN Cable Tester measurement](images/cable-test-measurement.png)

**What if your uConsole could tell you how long a LAN cable is — without anything connected to the other end?**

That's what this project is about.

The **uLAN Cable Tester** is an experimental Ethernet cable tester built around the Ethernet hardware of the **ClockworkPi uConsole AIO v2**.

It can measure individual cable pairs, estimate cable length and identify several basic wiring problems — including situations where the far end of the cable is simply left open.

And yes, the result is surprisingly useful.

But let's be honest:

> **This is not a Fluke.**

The length measurement is approximate. The calibration is experimental, results depend on the cable and hardware, and the graphical part of the PDF report is primarily an engineering visualisation — and a bit of geeky fun.

Think of it as **more than nothing, less than a professional cable analyser.**

And that's perfectly fine.

The interesting part is that it actually works.

---

## What can it do?

- 📏 Estimate the length of individual cable pairs
- 🔌 Check basic wiring / wire-map conditions
- ⚠️ Detect several open/short-related problems
- 📄 Generate a detailed PDF test report
- 🇬🇧 Run in English or 🇭🇺 Hungarian
- 🧪 Experiment with the diagnostic capabilities of the Ethernet hardware
- 🛠️ Run the whole thing from a portable uConsole

The far end of the cable does **not** need another Ethernet device connected for the diagnostic measurement.

No expensive dedicated cable tester is required to try the experiment — just the appropriate uConsole hardware and a willingness to see what happens when you dig a little deeper into an Ethernet chip.

---

## Before you start

There are two important things to check before installing the software.

### 1. Does your uConsole have the required hardware?

This project requires the **uConsole AIO v2 hardware, a dedicated CM4-compatible replacement mainboard, and the required ribbon cable** used during development and testing.

The original uConsole mainboard is not sufficient for this project and does not provide a connector for the required ribbon cable.

The hardware section below shows the required configuration.

![uConsole AIO v2 hardware](images/hardware-aio-v2-installed-before-mainboard-replacement.png)

### 2. Does your Ethernet interface use the required chip?

Before installing anything, check the Ethernet PHY detected by Linux:

```bash
cat /sys/class/net/eth0/phydev/phy_id
```

The tested hardware reports:

```text
0x600d84a2
```

This corresponds to the **Broadcom BCM54213PE** used by this project.

If you get a different value, **do not assume that the tester will work**. The diagnostic registers and measurement sequence are specific to the Ethernet PHY used by the project.

---

## The hardware requirement

The Ethernet part of the uConsole hardware is important here. The project was developed and tested with the **AIO v2 hardware, a dedicated CM4-compatible replacement mainboard, and the required ribbon cable**.

The ribbon cable cannot be connected to the original uConsole mainboard. The replacement CM4-compatible mainboard is therefore a required part of the hardware setup.

If your uConsole does not have this hardware configuration, installing the software will not make the Ethernet diagnostic functionality available.

![AIO v2 adapter board and ribbon cable](images/hardware-aio-v2-adapterboard-ribbon-before-installation.png)

![uConsole AIO v2](images/uconsole-aio-v2-complete.png)

> **Hardware note:** The project is documented around the hardware configuration that was actually tested. Other uConsole revisions or other Ethernet controllers may require different software and have not been validated here.

---

## Why does this work?

The Linux networking stack already knows about the Ethernet PHY. You can even ask `ethtool` to perform a cable test:

```bash
sudo ethtool --cable-test eth0
```

On the target hardware, however, the standard interface reports:

```text
netlink error: PHY driver does not support cable testing
```

![Failed standard cable test](images/troubleshooting-failed-tdr-test.png)

So this project goes underneath that interface and communicates directly with the PHY through **MDIO and extended registers** to access its diagnostic functionality.

Under the hood, the tester starts the PHY's ECD/TDR measurement sequence, reads the diagnostic values and converts them to an approximate cable length using the project's experimental calibration.

---

## The report: useful, but also gloriously geeky

The generated PDF contains the test information, pair results and an illustrative visualisation of the measurement.

The graph is **not a raw oscilloscope trace** and should not be interpreted as laboratory-grade TDR data. It is a visual representation generated from the measured result.

In other words:

> **It is an engineering experiment wrapped in a surprisingly official-looking PDF.**

![Example cable test report](images/cable-test-pdf-report.png)

---

## Calibration

The current tested software uses an experimentally determined conversion factor of:

```text
97.4 ticks / metre
```

This value was obtained from measurements on the tested hardware and cable setup. It should therefore be regarded as **board- and setup-specific**, not as a universal constant for every BCM54213PE implementation.

For this reason, the reported cable length should be treated as an **approximate indication**, not as a certified measurement.

---

## Installation

See the full installation guide:

**[Installation guide →](docs/INSTALL.md)**

Basic setup on a Debian/Raspberry Pi-class Linux system:

```bash
sudo apt update
sudo apt install -y python3 python3-venv build-essential

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

chmod +x build.sh run_cable_test_hu.sh run_cable_test_eng.sh
./build.sh
```

Then run either:

```bash
./run_cable_test_hu.sh
```

or:

```bash
./run_cable_test_eng.sh
```

The project includes the required native MDIO helper sources and tested AArch64 binaries.

---

## Configuration

The operator name used in the PDF report can be set in:

```text
config/ulan_config.json
```

Example:

```json
{
    "operator": "Operator"
}
```

No user-specific home-directory path is required by the project.

---

## Project structure

```text
uLAN-Cable-Tester/
├── README.md
├── README.hu.md
├── LICENSE
├── build.sh
├── requirements.txt
├── run_cable_test_hu.sh
├── run_cable_test_eng.sh
├── src/
│   ├── cable_test_core.py
│   ├── cable_test_hu.py
│   ├── cable_test_eng.py
│   ├── generate_cable_report.py
│   ├── mdio_write.c
│   └── mdio_exp_read.c
├── bin/
│   ├── mdio_write
│   └── mdio_exp_read
├── templates/
├── config/
├── reports/
└── docs/
    └── INSTALL.md
```

Generated PDF reports are intentionally ignored by Git. The repository keeps an empty `reports/` directory so the expected output location exists after cloning.

---

## Limitations

This project should be considered an **experimental hardware/software project**, not a professional cable certification tool.

In particular:

- cable length is approximate;
- the calibration factor is experimental and hardware/setup dependent;
- the graphical report is an illustrative visualisation, not a raw TDR waveform;
- the measurement sequence is tied to the tested BCM54213PE implementation;
- other Ethernet PHYs are not supported by default;
- Linux and the project's MDIO access method are required;
- changing the hardware, PHY or board revision may require different calibration or software changes.

Use the results as an indication and diagnostic aid, not as certified measurement data.

---

## Support the project

If you find this project useful, interesting, or simply enjoy the idea of turning a small Ethernet interface into a rather unexpected cable tester, you can support its development.

**Any contribution is appreciated — no matter how small.**

Your support helps with further hardware experiments, development, testing and documentation.

### ❤️ Support uLAN Cable Tester

**[Donate / Support the project](https://github.com/sponsors/gali-master)**

Thank you!

---

## Affiliate disclosure

Some hardware links associated with this project may be affiliate links. If you purchase through one of those links, I may receive a small commission at no additional cost to you.

The project documentation and technical conclusions are based on the hardware actually tested.

---

## License

This project is released under the **MIT License**.

See [LICENSE](LICENSE) for the full license text.
