> **Note (matrix-pinball):** this file is a vendored copy of FAST's starter-config README. The statement below that a FAST fork of MPF is required is out of date. Mainline MPF 0.57 and newer supports the Neuron; install `mpf` from PyPI as described in the root README.

# FAST MPF Starter Configs

This repo contains starter configuration files for MPF you can use to test your MPF install with FAST hardware and/or to get started with your own FAST MPF config.

## Testing MPF with your hardware

The `hardware-tests` folder contains config files you can use to test your MPF install with your FAST hardware. You can use these to make sure your hardware is working, to test your MPF install, and to confirm that MPF can talk to your FAST hardware.

### Step 1. Connect to your Neuron via a terminal emulator

We have a getting started guide [here](https://fastpinball.com/learning/tutorials/connecting-fast-neuron/) which shows you how to power up your Neuron and connect via a terminal emulator. So make sure you can do that first.

These hardware tests will cycle the first LED in the chain on every port through a few colors. So plug in at least one LED to one of the ports on the Neuron and any external expansion boards you have.

### Step 2. Install the FAST fork of MPF

Neuron support is current in development and not yet in the main MPF branch. So you'll need to install the FAST fork of MPF. You can do that by following the instructions [here](https://fastpinball.com/mpf/neuron/)

### Step 3. Download this repo

Pretty straightforward.

### Step 4. Configure your ports in this MPF config

To use these test MPF configs, you'll first need to edit the file you want to use to enter the serial ports the FAST hardware uses on your computer. The files you want to edit depend on the hardware you're testing:

* Neuron only: `hardware-tests/config/neuron.yaml`
* Neuron with FP-EXP-0071 expansion board: `hardware-tests/config/neuron-0071.yaml`
* Neuron with FP-EXP-0081 expansion board: `hardware-tests/config/neuron-0081.yaml`

You'll need to edit the two `port:` lines, one for the NET processor and one for the EXP processor.

```yaml
fast:
  net:
    # debug: true
    controller: neuron
    port: /dev/tty.usbmodem14601     # Change me!

  exp:
    # debug: true
    port: /dev/tty.usbmodem14603     # Change me!
    boards:
      neuron:
        model: FP-EXP-2000

```

### Step 5. Run MPF

Open a command prompt and navigate to the `hardware-tests` folder from this repo. Then run MPF using the following command line parameters:

* `-b` means MPF will not try to connect to a media controller
* `-t` means MPF will not run the text UI, and will instead show the logs in the console
* `-c` means MPF will use the config file you specify
* You can stack multiple parameters so `-b -t -c` is the same as `-btc`, etc.

Depending on your hardware configuration, you'll run one of the following commands:

**Neuron Only**

    mpf -btc neuron

**Neuron with FP-EXP-0071 expansion board**

    mpf -btc neuron-0071

**Neuron with FP-EXP-0081 expansion board**

    mpf -btc neuron-0081

### Step 6. Enjoy!

This test will cycle the first LED in the chain on every port through a few colors. So plug in at least one LED to one of the ports on the Neuron and any external expansion boards you have.

Assuming this works, you know your hardware is good, your MPF install is good, and they're both able to talk to each other!
