import board
import busio
import sime_rv1805 as RTC
# from datetime import datetime
from time import mktime
import time
# from smbus import SMBus
# import datetime




i2c = busio.I2C(board.SCL, board.SDA)
print(i2c)

rv1805 = RTC.RV1805(i2c)
print(rv1805)
print(type(rv1805))
print(rv1805.datetime)
print(type(rv1805.datetime))
while 1:
    time.sleep(1)
    print(rv1805.datetime)
# print(type(rv1805.datetime))
# timevar = time.localtime()
# print(timevar)
# rv1805.datetime = timevar
# while 1:
#     current = rv1805.datetime
#     # print('time', current)
#     print('The current time is: {}/{}/{} {:02}:{:02}:{:02}'.format(current.tm_mon, current.tm_mday, current.tm_year, current.tm_hour, current.tm_min, current.tm_sec))

# def _bcd2bin(value):
#     """Convert binary coded decimal to Binary

#     :param value: the BCD value to convert to binary (required, no default)
#     """
#     return value - 6 * (value >> 4)


# def _bin2bcd(value):
#     """Convert a binary value to binary coded decimal.

#     :param value: the binary value to convert to BCD. (required, no default)
#     """
#     return value + 6 * (value // 10)


# i2cbus = SMBus(1)  # Create a new I2C bus
# i2caddress = 0x69  # Address of MCP23017 device
# addr_hundreths = 0x00
# addr_seconds = 0x01
# addr_minutes = 0x02
# addr_hours = 0x03
# addr_date = 0x04
# addr_month = 0x05
# addr_year = 0x06

# # timevar = time.localtime()
# # print(timevar)
# def set_time(timevar):
#     i2cbus.write_byte_data(i2caddress, addr_hundreths, 0x00)
#     i2cbus.write_byte_data(i2caddress, addr_seconds, _bin2bcd(timevar.tm_sec))
#     i2cbus.write_byte_data(i2caddress, addr_minutes, _bin2bcd(timevar.tm_min))
#     i2cbus.write_byte_data(i2caddress, addr_hours, _bin2bcd(timevar.tm_hour))
#     i2cbus.write_byte_data(i2caddress, addr_date, _bin2bcd(timevar.tm_mday))
#     i2cbus.write_byte_data(i2caddress, addr_month, _bin2bcd(timevar.tm_mon))
#     i2cbus.write_byte_data(i2caddress, addr_year, _bin2bcd(int(time.strftime('%y',timevar))))


# def get_time():
#     try:
#         hundreths = _bcd2bin(i2cbus.read_byte_data(i2caddress, addr_hundreths))
#         seconds = _bcd2bin(i2cbus.read_byte_data(i2caddress, addr_seconds))
#         minutes = _bcd2bin(i2cbus.read_byte_data(i2caddress, addr_minutes))
#         hours = _bcd2bin(i2cbus.read_byte_data(i2caddress, addr_hours))
#         date = _bcd2bin(i2cbus.read_byte_data(i2caddress, addr_date))
#         month = _bcd2bin(i2cbus.read_byte_data(i2caddress, addr_month))
#         year = _bcd2bin(i2cbus.read_byte_data(i2caddress, addr_year))
#         output = datetime.datetime(
#                 year=year+2000,
#                 month=month,
#                 day=date,
#                 hour=hours,
#                 minute=minutes,
#                 second=seconds,
#                 microsecond=hundreths*10000,
#             )
#     except:
#         output=datetime.datetime.now()
#     # print('{}/{}'.format(seconds,seconds2))
#     # print('{}/{}/{}, {}:{:02d}:{:02d}.{:02d}'.format(month, date, year, hours,minutes,seconds,hundreths))

#     return(output)

# set_time(timevar)
# while 1:
#     print(get_time())
#     print(get_time().strftime('%s'))
#     print(get_time().microsecond)
#     print('{}{}{:04d}'.format(get_time().strftime('%s'),get_time().microsecond,0))
# ds3231.datetime = time.struct_time((2017, 1, 1, 0, 0, 0, 6, 1, -1))
# start up apply regular tim
# print(ds3231.disable_oscillator)
# ds3231.disable_oscillator = True
# print(ds3231.disable_oscillator)
# ds3231.disable_oscillator = False
# print(ds3231.disable_oscillator)
# print(rv1805.calibration) #was 19
# ds3231.calibration = 19
# print(ds3231.calibration) 






# rv1805.datetime = timevar


# # get the time from the rtc
# current = rv1805.datetime
# # print('time 10 sec later', current)
# # convert it to epoch timeS
# timevar=mktime(current)
# print(timevar)
# # timevar = datetime.fromtimestamp(timevar)
# # print(timevar)
# while 1:
#     current = rv1805.datetime
#     print(current)
#     # print('The current time is: {}/{}/{} {:02}:{:02}:{:02}'.format(current.tm_mon, current.tm_mday, current.tm_year, current.tm_hour, current.tm_min, current.tm_sec))
#     timevar=mktime(current)
#     print(timevar)
#     time.sleep(2)
