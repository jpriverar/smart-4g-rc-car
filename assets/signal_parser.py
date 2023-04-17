signal_output_file = open("PRBS_signal_output_2.txt", "r")

signal_entries = signal_output_file.readlines()

data = []
for entry in signal_entries:
    data += [float(num.split(':')[-1].strip()) for num in entry.split(',')]

time_vals = data[::3]
input_vals = data[1::3]
output_vals = data[2::3]

print(len(time_vals), len(input_vals), len(output_vals))
print("time: ", time_vals)
print("input: ", input_vals)
print("output: ", output_vals)