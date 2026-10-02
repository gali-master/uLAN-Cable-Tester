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

int mdio_read(int fd, struct ifreq *ifr, int phy, int reg)
{
    struct mii_ioctl_data *mii = (struct mii_ioctl_data *)&ifr->ifr_data;
    mii->phy_id = phy;
    mii->reg_num = reg;
    if (ioctl(fd, SIOCGMIIREG, ifr) < 0)
        return -1;
    return mii->val_out;
}

int mdio_write(int fd, struct ifreq *ifr, int phy, int reg, int val)
{
    struct mii_ioctl_data *mii = (struct mii_ioctl_data *)&ifr->ifr_data;
    mii->phy_id = phy;
    mii->reg_num = reg;
    mii->val_in = val;
    return ioctl(fd, SIOCSMIIREG, ifr);
}

int main(int argc, char **argv)
{
    int fd, val, phy;
    struct ifreq ifr;

    if (argc != 2 && argc != 3) return 1;

    phy = (argc == 3) ? strtol(argv[2], NULL, 0) : 0;

    fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) return 1;

    memset(&ifr, 0, sizeof(ifr));
    strcpy(ifr.ifr_name, "eth0");

    if (mdio_write(fd, &ifr, phy, 0x17, strtol(argv[1], NULL, 0)) < 0)
        return 2;

    val = mdio_read(fd, &ifr, phy, 0x15);
    if (val < 0)
        return 3;

    printf("EXP[strtol(argv[1], NULL, 0)] = 0x%04x\n", val);

    close(fd);
    return 0;
}
