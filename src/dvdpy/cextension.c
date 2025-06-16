/*
 * Copyright (C) 2025     Josh Wood
 *
 * This portion is based on the friidump project written by:
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

u_int32_t RAW_SECTOR_SIZE = 2064;
u_int32_t HITACHI_MEM_BASE = 0x80000000;
u_int32_t HITACHI_CACHE_SIZE = 80;

int execute_command(int fd, unsigned char *cmd, unsigned char *buffer,
                    int buflen, int timeout, bool verbose) {
    /* Sends a command to the DVD drive using Linux API
     *
     * Args:
     *     fd (int): the file descriptor of the drive
     *     cmd (unsigned char *): pointer to the 12 command bytes
     *     buffer (unsigned char *): pointer to the buffer where bytes
     *                               returned by the command are placed
     *     buflen (int): length of the buffer
     *     timeout (int): timeout duration in integer seconds
     *     verbose (bool): set to true to print more details to stdout
     *
     * Returns:
     *     (int): the command status where -1 indicates an error
     */
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

    verbose = true;
    if (verbose) {
        printf("Executing MMC command: ");
        for (int i=0; i<6; i++) printf(" %02x%02x", cgc.cmd[2*i], cgc.cmd[2*i+1]);
        printf("\n");
    }

    int status = ioctl(fd, CDROM_SEND_PACKET, &cgc);

    if (verbose)
        printf("Sense data: %02X/%02X/%02X (status %d)\n",
               cgc.sense->sense_key, cgc.sense->asc, cgc.sense->ascq, status);

    return status;    
};

static PyObject *command_device(PyObject *self, PyObject *args) {
    /* Python interface for commanding a DVD device.
     *
     * Note: the buffer argument contains a pointer to
     * the buffer contents, which will be modified when
     * running this command so that the user can access
     * the updated buffer within Python.
     *
     * Args:
     *     fd (int): the file descriptor of the drive
     *     cmd (bytearray): pointer to the 12 command bytes
     *     buffer (bytearray): pointer to the buffer where bytes
     *                         returned by the command are placed
     *     timeout (int): timeout duration in integer seconds
     *     verbose (bool): set to true to print more details to stdout
     *
     * Returns:
     *     (int): the command status where -1 indicates an error
     */
    int fd, timeout, verbose;
    Py_buffer cmd, buffer;
    if (!PyArg_ParseTuple(args, "iy*y*ip", &fd, &cmd, &buffer, &timeout, &verbose))
        return NULL;

    if (cmd.len != 12) {
        PyErr_SetString(PyExc_ValueError, "command length must be 12 bytes");
        return (PyObject *) NULL;
    }

    int status = execute_command(fd, (unsigned char *)cmd.buf, (unsigned char *)buffer.buf, buffer.len, timeout, (bool)verbose);

    return PyLong_FromLong(status);
};

static PyObject *open_device(PyObject *self, PyObject *args) {
    /* Method to open the device's file descriptor.
     *
     * Args:
     *     path (str): path to the device
     *
     * Returns:
     *     (int): the file descriptor
     */
    const char *path;
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    int fd = open(path, O_RDONLY | O_NONBLOCK);

    return PyLong_FromLong(fd);
};

static PyObject *close_device(PyObject *self, PyObject *args) {
    /* Method to close the device's file descriptor.
     *
     * Args:
     *     fd (int): the file descriptor to close
     *
     * Returns:
     *     (int): status reported by close()
     */
    int fd;
    if (!PyArg_ParseTuple(args, "i", &fd))
        return NULL;

    return PyLong_FromLong(close(fd));
};

/*
 * Descriptions for the methods available in this module.
 * These can be accessed within Python using `dir(dvdpy.cextension)`
 */
static PyMethodDef Methods[] = {
    {"open_device",       open_device, METH_VARARGS, "Open the path to a DVD drive."},
    {"close_device",     close_device, METH_VARARGS, "Close the path to a DVD drive."},
    {"command_device", command_device, METH_VARARGS, "Send byte command to a DVD drive."},
    {NULL, NULL, 0, NULL}
};

/*
 * Define the dvdpy module name so that Python users
 * can import it with `import dvdpy.cextension`
 */
static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "cextension", NULL, -1, Methods};

PyMODINIT_FUNC PyInit_cextension(void)
{
    return PyModule_Create(&module);
};
