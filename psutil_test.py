import psutil


print(psutil.cpu_times().user)


print(dict(psutil.virtual_memory()._asdict()))
print(psutil.virtual_memory().percent)
print(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)

print(dict(psutil.disk_usage('/')._asdict()))
print(psutil.disk_usage('/').percent)

print(psutil.net_io_counters().dropin)
print(psutil.net_io_counters().dropout)
print(psutil.net_io_counters().errin)
print(psutil.net_io_counters().errout)

temps = psutil.sensors_temperatures(True)
if not temps:
    sys.exit("can't read any temperature")
for name, entries in temps.items():
    print(name)
    for entry in entries:
        print("    %-20s %s °C (high = %s °C, critical = %s °C)" % (
            entry.label or name, entry.current, entry.high,
            entry.critical))
    print()
# items = temps.items()
# print(items['thermal-fan-est']['current'])
print(psutil.cpu_percent(interval=0.5))