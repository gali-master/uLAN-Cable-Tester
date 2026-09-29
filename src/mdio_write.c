#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/mii.h>
#include <linux/sockios.h>
#include <net/if.h>
#include <string.h>

int main(int argc, char **argv)
{
    int fd, reg, val;
    struct ifreq ifr;
    struct mii_ioctl_data *mii;

    if (argc != 3) return 1;

    reg = strtol(argv[1], NULL, 0);
    val = strtol(argv[2], NULL, 0);

    fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) return 2;

    memset(&ifr, 0, sizeof(ifr));
    strcpy(ifr.ifr_name, "eth0");

    mii = (struct mii_ioctl_data *)&ifr.ifr_data;
    mii->phy_id = 0;
    mii->reg_num = reg;
    mii->val_in = val;

    if (ioctl(fd, SIOCSMIIREG, &ifr) < 0)
        return 3;

    printf("MDIO[0x%02x] <- 0x%04x\n", reg, val);

    close(fd);
    return 0;
}
