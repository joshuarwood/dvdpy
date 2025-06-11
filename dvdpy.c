/*
 * Copyright (C) 2025     Josh Wood
 *
 * This portion is very closely based on the friidump project
 * written by:
 *              Arep
 *              https://github.com/bradenmcd/friidump
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <linux/cdrom.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <fcntl.h>

u_int8_t SPC_INQUIRY = 0x12;
u_int8_t MMC_READ_12 = 0xA8;

int execute_command(int fd, unsigned char *cmd, unsigned char *buffer,
		    int buflen, int timeout, bool verbose) {

    struct cdrom_generic_command cgc;
    struct request_sense sense;

    memset(&cgc, 0, sizeof(cgc));
    memset(buffer, 0, buflen);
    memcpy(cgc.cmd, cmd, 12);

    cgc.buffer = buffer;
    cgc.buflen = buflen;
    cgc.sense = &sense;
    cgc.data_direction = CGC_DATA_READ;
    cgc.timeout = timeout * 1000;

    if (verbose) {
        printf("Executing MMC command: ");
        for (int i=0; i<12; i++) printf(" %02x", cgc.cmd[i]);
        printf("\n");
    }

    int status = ioctl(fd, CDROM_SEND_PACKET, &cgc);

    if (verbose)
        printf("Sense data: %02X/%02X/%02X (status %d)\n",
               cgc.sense->sense_key, cgc.sense->asc, cgc.sense->ascq, status);

    return status;    
};

static PyObject *drive_info(PyObject *self, PyObject *args) {

    int fd;
    if (!PyArg_ParseTuple(args, "i", &fd))
        return NULL;

    unsigned char buffer[36];
    unsigned char cmd[12] = {
        SPC_INQUIRY, 0, 0, 0, sizeof(buffer), 0, 0, 0, 0, 0, 0, 0};

    int status = execute_command(fd, cmd, buffer, 36, 10, false);
    if (status >= 0) {
        char *vendor = strndup((char *)&buffer[8], 8);
	char *prod_id = strndup((char *)&buffer[16], 16);
	char *prod_rev = strndup((char *)&buffer[32], 4);
	printf("DVD drive is \"%s/%s/%s\"\n", vendor, prod_id, prod_rev);
    } else printf("Cannot identify DVD drive\n");

    return PyLong_FromLong(status);
};

static PyObject *open_device(PyObject *self, PyObject *args) {

    const char *path;
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    int fd = open(path, O_RDONLY | O_NONBLOCK);

    return PyLong_FromLong(fd);
};

static PyObject *close_device(PyObject *self, PyObject *args) {

    int fd;
    if (!PyArg_ParseTuple(args, "i", &fd))
        return NULL;

    return PyLong_FromLong(close(fd));
};

static PyMethodDef Methods[] = {
    {"open_device",   open_device, METH_VARARGS, "Open the path to a DVD drive."},
    {"close_device", close_device, METH_VARARGS, "Close the path to a DVD drive."},
    {"drive_info",     drive_info, METH_VARARGS, "Get the DVD drive info."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "dvdpy", NULL, -1, Methods};

PyMODINIT_FUNC PyInit_dvdpy(void)
{
    return PyModule_Create(&module);
};
